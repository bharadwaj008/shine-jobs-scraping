import requests
from bs4 import BeautifulSoup
import pandas as pd
import configparser
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re

# Read configuration
config = configparser.ConfigParser()
config.read('config.ini')
max_pages = config.getint('DEFAULT', 'MaxPages')
driver_path = config.get('DEFAULT', 'DriverPath')

# Setup logging
logging.basicConfig(filename='BharadwajKamepalli_Errors.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_days(days_text):
    try:
        return int(days_text.split()[0])
    except ValueError as e:
        logging.error(f"Error parsing days from text '{days_text}': {e}")
        return None

def get_job_details(driver, url):
    """Fetches the job description, job type, and company name from the job's detail page using Selenium."""
    driver.get(url)
    job_description = job_type = company_name = "Not specified"
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'jobDetail_jsrpRightDetail_text__jqs8a')]"))
        )
        description_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'jobDetail_jsrpRightDetail_text__jqs8a')]//span")
        job_description = " ".join([elem.text for elem in description_elements if elem.text.strip()])

        # Extract Job Type from Other Details
        job_type_element = driver.find_element(By.XPATH, "//span[contains(@class, 'jobDetail_DetailWidth__2Aw2z') and contains(text(), 'Job Type')]/following-sibling::span")
        job_type = job_type_element.text if job_type_element else "Not specified"

        # Extract Company Name from Recruiter Details
        company_element = driver.find_element(By.XPATH, "//span[contains(@class, 'jobDetail_DetailWidth__2Aw2z') and contains(text(), 'Recruiter Details')]/following-sibling::span")
        company_name = company_element.text if company_element else "Unknown"
    except Exception as e:
        print(f"Could not load job details: {e}")
    return job_description, job_type, company_name


def configure_driver():
    """Sets up the Selenium WebDriver."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36")
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrape_jobs(base_url):
    driver = configure_driver()
    current_page = 1
    retries = 3  # Number of retries for loading a page

    while current_page <= max_pages:
        url = f"{base_url}-{current_page}" if current_page > 1 else base_url
        success = False

        for attempt in range(retries):
            logging.info(f"Accessing URL: {url} - Attempt {attempt + 1}")
            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "jobCard"))
                )
                success = True
                break  # Exit retry loop if page loads successfully
            except Exception as e:
                logging.error(f"Failed to load URL: {url} on attempt {attempt + 1}: {e}")

        if not success:
            logging.error(f"Failed to load URL after {retries} attempts: {url}")
            current_page += 1
            continue

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_cards = soup.find_all('div', class_='jobCard')

        if not job_cards:
            logging.info(f"No job cards found on page {current_page}. URL: {url}")
            current_page += 1
            continue

        jobs_data = []
        for job_card in job_cards:
            days_ago_tag = job_card.find('span', string=re.compile(r'\b\d+ days ago\b'))
            if not days_ago_tag or parse_days(days_ago_tag.text) > 7:
                continue

            title_tag = job_card.find('strong').find('p').find('a')
            if not title_tag:
                continue
            title = title_tag.text.strip()
            job_url = requests.compat.urljoin(base_url, title_tag['href'])

            company_tag = job_card.find('div', class_='jobCard_jobCard_cName__mYnow')
            company = company_tag.text.strip() if company_tag else "Unknown"

            experience_tag = job_card.find('div', string=re.compile(r'\d+ to \d+ Yrs'))
            experience = experience_tag.text.strip() if experience_tag else "Not specified"

            job_description, job_type, company = get_job_details(driver, job_url)
            jobs_data.append({
            'Job Title': title,
            'Company Name': company,
            'Experience Required': experience,
            'Job Type': job_type,
            'Job Description': job_description,
            'Days Ago': parse_days(days_ago_tag.text),
            'Job URL': job_url
            })


        if jobs_data:
            df = pd.DataFrame(jobs_data)
            df.to_csv(f'BharadwajKamepalli_shine_Output_page_{current_page}.csv', index=False)
            logging.info(f"Data written for page {current_page}.")
        else:
            logging.info(f"No recent job postings found on page {current_page}.")

        current_page += 1

    driver.quit()

def main():
    base_url = 'https://www.shine.com/job-search/data-science-jobs'
    scrape_jobs(base_url)

if __name__ == '__main__':
    main()
