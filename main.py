import os
import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config import username, password, course_urls, login_url, download_path

def load_downloaded_files(course_folder_path):
    downloaded_files_path = os.path.join(course_folder_path, "downloaded_files.json")
    if os.path.exists(downloaded_files_path):
        with open(downloaded_files_path, 'r') as file:
            return json.load(file)
    else:
        return []

def save_downloaded_files(course_folder_path, downloaded_files):
    downloaded_files_path = os.path.join(course_folder_path, "downloaded_files.json")
    with open(downloaded_files_path, 'w') as file:
        json.dump(downloaded_files, file, indent=4)

def download_course_files(course_url):
    session = requests.Session()

    login_page_response = session.post(login_url)
    login_page_soup = BeautifulSoup(login_page_response.text, 'html.parser')
    logintoken = login_page_soup.find('input', {'name': 'logintoken'}).get('value')

    login_payload = {
        'username': username,
        'password': password,
        'logintoken': logintoken
    }

    login_response = session.post(login_url, data=login_payload)
    if "Invalid login" in login_response.text:
        print("Login failed. Check your credentials.")
        exit()

    response = session.get(course_url)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')

    course_title = soup.select_one('.page-context-header h1').text.strip()
    clean_course_title = ''.join(c if c.isalnum() or c.isspace() else '_' for c in course_title)
    course_folder_path = os.path.join(download_path, clean_course_title)
    os.makedirs(course_folder_path, exist_ok=True)

    downloaded_files = load_downloaded_files(course_folder_path)

    def print_colored(message, color):
        colors = {
            'green': '\033[92m',
            'blue': '\033[94m', 
            'end': '\033[0m'    
        }
        print(colors[color] + message + colors['end'])

    for index, subtitle in enumerate(soup.select('.content h3'), start=1):
        subtitle_text = subtitle.text.strip()
        clean_subtitle = f"{index:02d}_{''.join(c if c.isalnum() or c.isspace() else '_' for c in subtitle_text)}"

        subtitle_folder_path = os.path.join(course_folder_path, clean_subtitle)
        os.makedirs(subtitle_folder_path, exist_ok=True)

        for file_index, file_item in enumerate(subtitle.find_next('ul', {'class': 'section'}).select('li'), start=1):
            instancename = file_item.select_one('.instancename')
            if instancename:
                file_name = instancename.text.strip()
                is_folder = 'Folder' in file_name
                actual_file_name = re.sub(r'\s*Folder\s*', '', file_name).strip()
                file_name = f"{file_index:02d}_{''.join(c if c.isalnum() or c.isspace() else '_' for c in actual_file_name)}"

                file_path = os.path.join(clean_course_title, clean_subtitle, file_name)

                if file_path not in downloaded_files:
                    if is_folder:
                        file_name += '_FOLDER'

                        folder_url = urljoin(course_url, file_item.select_one('a')['href'])
                        folder_response = session.get(folder_url)
                        folder_soup = BeautifulSoup(folder_response.text, 'html.parser')

                        folder_subtitle_folder_path = os.path.join(subtitle_folder_path, file_name)
                        os.makedirs(folder_subtitle_folder_path, exist_ok=True)

                        for link in folder_soup.select('.fp-filename-icon a'):
                            file_url = urljoin(course_url, link['href'])
                            file_name = link.select_one('.fp-filename').text.strip()
                            file_name = ''.join(c if c.isalnum() or c.isspace() else '_' for c in file_name)
                            download_file(session, course_url, file_url, os.path.join(folder_subtitle_folder_path, file_name))

                            downloaded_files.append(file_path)
                            print_colored('Downloaded folder: ' + file_path, 'blue')
                    else:
                        download_file(session, course_url, urljoin(course_url, file_item.select_one('a')['href']), os.path.join(subtitle_folder_path, file_name))
                        downloaded_files.append(file_path)
                        print_colored('Downloaded file: ' + file_path, 'green')
                else:
                    print_colored('Skipped (already exists): ' + file_path, 'blue')

    save_downloaded_files(course_folder_path, downloaded_files)
    session.close()

def download_file(session, course_url, file_url, file_path):
    response = session.get(file_url)

    content_disposition = response.headers.get('Content-Disposition')
    if content_disposition and 'filename=' in content_disposition:
        matches = re.findall('filename="(.*?)"', content_disposition)
        if matches:
            file_name = matches[0]
            _, file_extension = os.path.splitext(file_name)
            file_path_with_extension = f"{file_path}{file_extension}"
        else:
            file_path_with_extension = f"{file_path}.html"
    else:
        file_path_with_extension = f"{file_path}.html"

    with open(file_path_with_extension, 'wb') as file:
        file.write(response.content)

for course_url in course_urls:
    download_course_files(course_url)
