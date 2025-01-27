# shine-jobs-scraping
# Data Science Jobs Scraper

## Overview
This script automates the process of scraping job listings from Shine.com for data science positions. It navigates through the job listings, extracting detailed information including job title, company name, experience required, job type, and job description.

## Features
- Pagination handling up to a specified number of pages.
- Detailed logging of operations and errors.
- Dynamic extraction of job details using Selenium for accurate, real-time data.

## Requirements
To install the required packages, run the following command:
pip install -r requirements.txt

markdown
Copy

## Configuration
Edit the `config.ini` file to specify the maximum number of pages (`MaxPages`) and the path to your Selenium WebDriver (`DriverPath`).

Example:

[DEFAULT] MaxPages = 10 DriverPath = path/to/your/chromedriver.exe

bash
Copy

## Running the Script
To run the script, use the following command:
python scrape_jobs.py


Ensure that Python and all required packages are installed, and that you are in the directory containing the script.

## Logging
Errors and information are logged to `BharadwajKamepalli_Errors.log`, which includes details about URL accesses, data extraction issues, and other runtime events.

## Limitations
- The script is dependent on the structure of the website. Changes to the website may require updates to the script.
- Designed to run on websites without advanced anti-bot protections.

## Author
Bharadwaj Kamepalli
