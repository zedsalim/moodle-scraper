<h1 align="center">Moodle Content Automator</h1>
<p align="center">
    <img alt="life" width="550" src="moodle-scraper.gif">
</p>

Automate the process of downloading course materials from your university's Moodle website with this Python script. The script securely logs in using provided credentials, automatically detects new content across all enrolled courses, and efficiently downloads all relevant materials to a designated local directory.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Requirements

- [Python](https://www.python.org/) (version 3.6 or later)
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
pip install requests
```

## Usage

### 1. Configuration (config.py):

#### Credentials (config.py)

Update the `MOODLE_USERNAME` and `MOODLE_PASSWORD` variables with your Moodle login credentials:

```python
# Credentials
MOODLE_USERNAME = "your_username"
MOODLE_PASSWORD = "your_password"
```

#### Moodle URL (config.py)

Update the `MOODLE_URL` with your university's Moodle platform URL:

```python
# Moodle URL
MOODLE_URL = "https://elearning.university-site.edu"
```

#### Download Path (config.py)

Update the `DOWNLOAD_DIR` variable with the local directory path to store the downloaded files:

```python
# Download path
DOWNLOAD_DIR = "moodle_downloads"
STATE_FILE = "last_check.json"
```

### 2. Run the moodle-scraper.py script:

```bash
python moodle-scraper.py
```

The script will authenticate, automatically scan all your enrolled courses, and download new or missing course materials to the designated directory.

# Important Note:

This script is for personal and educational use only. Do not engage in unauthorized or malicious activities.

## License

This project is licensed under the [MIT License](LICENSE).
[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
Feel free to modify and enhance the scraper according to your needs!
