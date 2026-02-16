import json
import os
from datetime import datetime

import requests

import config

# Use configuration from config.py
MOODLE_URL = config.MOODLE_URL
DOWNLOAD_DIR = config.DOWNLOAD_DIR
STATE_FILE = config.STATE_FILE

# Global token variable
TOKEN = None


def get_token(username, password):
    """Get authentication token from Moodle"""
    token_url = f"{MOODLE_URL}/login/token.php"
    params = {
        "username": username,
        "password": password,
        "service": "moodle_mobile_app",
    }

    try:
        response = requests.get(token_url, params=params)
        data = response.json()

        if "token" in data:
            return data["token"]
        elif "error" in data:
            print(f"❌ Login error: {data['error']}")
            if "errorcode" in data:
                print(f"   Error code: {data['errorcode']}")
            return None
        else:
            print(f"❌ Unexpected response: {data}")
            return None

    except Exception as e:
        print(f"❌ Failed to get token: {e}")
        return None


def call_moodle_api(function, params={}):
    """Call Moodle Web Service API"""
    url = f"{MOODLE_URL}/webservice/rest/server.php"
    params.update(
        {"wstoken": TOKEN, "wsfunction": function, "moodlewsrestformat": "json"}
    )
    response = requests.get(url, params=params)
    return response.json()


def get_enrolled_courses():
    """Get all enrolled courses"""
    # First get your user ID
    user_info = call_moodle_api("core_webservice_get_site_info")
    userid = user_info["userid"]

    # Get enrolled courses
    courses = call_moodle_api("core_enrol_get_users_courses", {"userid": userid})
    return courses


def get_course_contents(course_id):
    """Get all contents of a course"""
    contents = call_moodle_api("core_course_get_contents", {"courseid": course_id})
    return contents


def download_file(file_url, file_path):
    """Download file from Moodle"""
    # Add token to file URL
    download_url = f"{file_url}&token={TOKEN}"

    response = requests.get(download_url, stream=True)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    return False


def load_state():
    """Load last check state"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state):
    """Save current state"""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def file_exists(file_path):
    """Check if file exists on disk"""
    return os.path.isfile(file_path)


def clean_state(state):
    """Remove entries from state where files no longer exist"""
    cleaned_state = {}
    removed_count = 0

    for key, value in state.items():
        # Skip module-only keys (they don't have file paths)
        if "_" in key and not key.count("_") > 2:
            cleaned_state[key] = value
            continue

        # For file keys, check if they contain actual file tracking info
        if isinstance(value, dict) and "path" in value:
            if file_exists(value["path"]):
                cleaned_state[key] = value
            else:
                removed_count += 1
                print(f"  🗑️  Removed missing file from state: {value['path']}")
        else:
            cleaned_state[key] = value

    if removed_count > 0:
        print(f"📊 Cleaned {removed_count} missing files from state\n")

    return cleaned_state


def main():
    global TOKEN

    # Get credentials from config file
    username = config.MOODLE_USERNAME
    password = config.MOODLE_PASSWORD

    # Get token
    print("🔑 Authenticating...")
    TOKEN = get_token(username, password)

    if not TOKEN:
        print("❌ Failed to authenticate. Please check your credentials in config.py")
        return

    print("✅ Authentication successful!")
    print("🔍 Checking for new Moodle content...")

    # Create download directory
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Load previous state
    state = load_state()

    # Clean state - remove entries for deleted files
    state = clean_state(state)

    is_first_run = len(state) == 0

    if is_first_run:
        print("📦 First run - downloading all content")

    new_items = []
    redownloaded_items = []
    courses = get_enrolled_courses()

    for course in courses:
        course_id = course["id"]
        course_name = course["fullname"]
        print(f"\n📚 Course: {course_name}")

        # Get course contents
        contents = get_course_contents(course_id)

        for section in contents:
            section_name = section["name"]

            if "modules" in section:
                for module in section["modules"]:
                    module_id = module["id"]
                    module_name = module["name"]
                    module_type = module["modname"]

                    # Check if this is new
                    module_key = f"{course_id}_{module_id}"
                    is_new = module_key not in state

                    if is_new or is_first_run:
                        new_items.append(
                            {
                                "course": course_name,
                                "section": section_name,
                                "name": module_name,
                                "type": module_type,
                            }
                        )

                    # Download files if available
                    if "contents" in module:
                        for content in module["contents"]:
                            if content["type"] == "file":
                                file_name = content["filename"]
                                file_url = content["fileurl"]

                                # Create safe file path
                                safe_course = "".join(
                                    c
                                    for c in course_name
                                    if c.isalnum() or c in (" ", "-", "_")
                                )
                                file_path = os.path.join(
                                    DOWNLOAD_DIR, safe_course, section_name, file_name
                                )

                                # Check if file is new or missing
                                file_key = f"{module_key}_{file_name}"
                                file_in_state = file_key in state
                                file_exists_on_disk = file_exists(file_path)

                                # Download if: new file OR file was deleted
                                should_download = (
                                    not file_in_state
                                    or not file_exists_on_disk
                                    or is_first_run
                                )

                                if should_download:
                                    # Determine if this is a redownload
                                    if file_in_state and not file_exists_on_disk:
                                        print(
                                            f"  🔄 Re-downloading deleted file: {file_name}"
                                        )
                                        redownloaded_items.append(file_name)
                                    else:
                                        print(f"  ⬇️  Downloading: {file_name}")

                                    if download_file(file_url, file_path):
                                        state[file_key] = {
                                            "path": file_path,
                                            "downloaded": datetime.now().isoformat(),
                                            "course": course_name,
                                            "module": module_name,
                                        }
                                        print(f"  ✅ Downloaded to {file_path}")
                                    else:
                                        print(f"  ❌ Failed to download")
                                else:
                                    # File exists, just verify it's still there
                                    pass

                    # Mark module as seen
                    if module_key not in state:
                        state[module_key] = datetime.now().isoformat()

    # Save state
    save_state(state)

    # Summary
    print("\n" + "=" * 50)

    if redownloaded_items:
        print(f"🔄 Re-downloaded {len(redownloaded_items)} deleted files:")
        for item in redownloaded_items:
            print(f"  • {item}")
        print()

    if new_items:
        print(f"📬 Found {len(new_items)} new items:")
        for item in new_items:
            print(f"  • [{item['type']}] {item['name']} in {item['course']}")
    else:
        if not redownloaded_items:
            print("✅ No new content found")

    print(f"\n💾 Downloads saved to: {DOWNLOAD_DIR}/")


if __name__ == "__main__":
    main()
