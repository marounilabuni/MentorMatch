from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time


def setup_driver():
    """Setup and return a Chrome webdriver with appropriate options."""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def scrape_mentor_profile(url, driver):
    """Scrape additional details from a mentor's profile."""
    try:
        driver.get(url)
        time.sleep(2)  # Allow time for the page to load

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        try:
            bio = soup.find('div', class_='bio-section').text.strip()
        except:
            bio = ""

        try:
            reviews = soup.find('div', class_='reviews-section').text.strip()
        except:
            reviews = ""

        try:
            skills = [skill.text.strip() for skill in soup.find_all('span', class_='skill-tag')]
        except:
            skills = []

        return {
            'Profile URL': url,
            'Bio': bio,
            'Reviews': reviews,
            'Skills': ', '.join(skills)
        }
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return {
            'Profile URL': url,
            'Bio': '',
            'Reviews': '',
            'Skills': ''
        }


def scrape_profiles_from_csv(input_csv, output_csv):
    """Scrape mentor profiles using URLs from a CSV file."""
    print(f"Reading URLs from {input_csv}...")
    mentors_df = pd.read_csv(input_csv)

    # Ensure the column 'url' exists
    if 'url' not in mentors_df.columns:
        print("Error: 'url' column not found in CSV.")
        return

    urls = mentors_df['url'].dropna().unique()
    print(f"Found {len(urls)} unique mentor profile URLs.")

    driver = setup_driver()

    try:
        profile_details = []
        for i, url in enumerate(urls[:10]):
            print(f"Scraping profile {i + 1}/{len(urls)}: {url}")
            profile_data = scrape_mentor_profile(url, driver)
            profile_details.append(profile_data)

        # Combine with existing data
        profiles_df = pd.DataFrame(profile_details)

        # Merge scraped details back into the original dataset for better context
        final_df = mentors_df.merge(profiles_df, left_on='url', right_on='Profile URL', how='left')

        # Save the combined data to a new CSV
        final_df.to_csv(output_csv, index=False, encoding='utf-8')
        print(f"Profile data saved to {output_csv}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        driver.quit()


if __name__ == "__main__":
    # Specify input and output files
    input_csv = 'mentorcruise_data.csv'  # Replace with your input CSV file
    output_csv = 'mentor_profiles_data.csv'  # Output CSV file for profile data

    scrape_profiles_from_csv(input_csv, output_csv)
