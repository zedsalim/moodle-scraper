# University Moodle Scraper

Automate the process of downloading course materials from your university's Moodle website with this Python script. The script securely logs in using provided credentials, navigates through specified course URLs, and efficiently downloads all relevant materials to a designated local directory.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Requirements

- [Python](https://www.python.org/) (version 3.6 or later)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) (bs4)
- [Requests](https://docs.python-requests.org/en/latest/) library

## Installation

1. Clone the repository to your local machine:

```bash
git clone https://github.com/zedsalim/moodle-scraper.git
cd moodle-scraper
```

2. Optionally, create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use 'venv\Scripts\activate'
```

3. Install the required dependencies:

```bash
pip install beautifulsoup4 requests
```

## Usage

### 1. Configuration (config.py):

#### Credentials (config.py)

Update the `username` and `password` variables with your Moodle login credentials:

```python
# Credentials
username = "your_username"
password = "your_password"
```

#### Course URLs (config.py)

To obtain the `login_url`, navigate to your university's Moodle website and copy the URL of the login page. It typically looks like "http://.........../login/index.php."

For `course_urls`, follow these steps:

1. Log in to your university's Moodle platform.
1. Click on the name of the course you want to scrape.
1. Once on the course page, copy the URL from the address bar.

Update the `login_url` with the copied login URL and the `course_urls` list with the URLs of the courses you want to scrape:

```python
# URLs examples
login_url = "http://university-moodle-website.edu/login/index.php"
course_urls = [
    "http://university-moodle-website.edu/course/view.php?id=80",
    "http://university-moodle-website.edu/course/view.php?id=81",
    # Add more course URLs as needed
]
```

#### Download Path (config.py)

Update the `download_path` variable with the local directory path to store the downloaded files:

```python
# Download path
download_path = "/path/to/download/files"
```

### 2. Run the main.py script:

```bash
python main.py
```

The script will log in, navigate through the specified courses, and download all course materials to the designated directory.

# Important Note:

This script is for personal and educational use only. Do not engage in unauthorized or malicious activities.

## License

This project is licensed under the [MIT License](LICENSE).
[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
Feel free to modify and enhance the scraper according to your needs!
