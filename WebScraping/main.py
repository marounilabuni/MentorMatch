from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import re


def setup_driver():
    """Setup and return a Chrome webdriver with appropriate options."""
    chrome_options = Options()
    if 0 :
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def scroll_to_load_more(driver):
    """Scroll down and click 'Show more' until all mentors are loaded."""
    SCROLL_PAUSE_TIME = 2

    for i in range(1000):
        print(f"\nstarting iteration number {i}")
        try:
            # Wait for the "Show more" button to appear
            show_more = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'ais-InfiniteHits-loadMore'))
            )

            print("button found")

            # Scroll to the button to ensure it's clickable
            driver.execute_script("arguments[0].scrollIntoView(true);", show_more)
            time.sleep(1)  # Small pause to let scrolling finish

            # Click the button
            show_more.click()
            print("button have been clicked")
            time.sleep(SCROLL_PAUSE_TIME)
        except Exception as e:
            # If the button is not found or no more content to load
            print("No more 'Show more' button or error occurred:", str(e))
            print()
            time.sleep(20)
            break


def extract_mentor_data(mentor_element):
    """Extract data from a single mentor element."""
    try:
        # Extract profile URL (href)
        profile_url = mentor_element.find('a', href=True)['href']
        # Ensure the full URL is created
        if not profile_url.startswith('http'):
            profile_url = f"https://mentorcruise.com{profile_url}"
    except:
        profile_url = ""


    try:
        # Extract name
        name = mentor_element.find('h3', class_='title').text.split('🇬')[0].strip()
    except:
        name = ""

    try:
        # Extract role and company
        position_element = mentor_element.find(class_='text-base')
        if position_element:
            position_text = position_element.text
            if ' at ' in position_text:
                role, company = position_text.split(' at ', 1)
                company = company.strip()
            else:
                role = position_text
                company = ""
        else:
            role = ""
            company = ""
    except:
        role = ""
        company = ""

    try:
        # Extract rating
        rating_element = mentor_element.find(attrs={'data-rating': True})
        rating = rating_element['data-rating'] if rating_element else ""
    except:
        rating = ""

    try:
        # Extract number of reviews
        reviews_text = mentor_element.find(class_='rating-display')
        if reviews_text:
            reviews_match = re.search(r'\((\d+)\s+review', reviews_text.text)
            reviews = reviews_match.group(1) if reviews_match else "0"
        else:
            reviews = "0"
    except:
        reviews = "0"

    try:
        # Extract price
        price_element = mentor_element.find(class_='price-element')
        price = price_element.text.replace('$', '').strip() if price_element else ""
    except:
        price = ""

    try:
        # Extract country
        country_element = mentor_element.find('span', title=True)
        country = country_element['title'] if country_element else ""
    except:
        country = ""

    try:
        # Extract bio
        bio_element = mentor_element.find(id='bio-formatted')
        bio = bio_element.text.strip() if bio_element else ""
    except:
        bio = ""

    try:
        # Extract tags/skills
        tags = [tag.text.strip() for tag in mentor_element.find_all(class_='tag-sm')]
        tags_str = ', '.join(tags)
    except:
        tags_str = ""

    try:
        # Check if Top Mentor
        is_top_mentor = "Yes" if mentor_element.find('a', string='Top Mentor') else "No"
    except:
        is_top_mentor = "No"

    try:
        # Check if Quick Responder
        is_quick_responder = "Yes" if mentor_element.find(id='quickresponder') else "No"
    except:
        is_quick_responder = "No"

    try:
        # Extract spots left
        spots_element = mentor_element.find(class_='absolute top-0 -m-4 right-12')
        if spots_element:
            spots_match = re.search(r'Only (\d+) Spots? Left', spots_element.text)
            spots_left = spots_match.group(1) if spots_match else ""
        else:
            spots_left = ""
    except:
        spots_left = ""


    return {
        'Name': name,
        'Role': role,
        'Company': company,
        'Rating': rating,
        'Reviews': reviews,
        'Price': price,
        'Country': country,
        'Bio': bio,
        'Skills': tags_str,
        'Top Mentor': is_top_mentor,
        'Quick Responder': is_quick_responder,
        'Spots Left': spots_left,
        'url': profile_url,
    }


def scrape_mentorcruise():
    """Main function to scrape MentorCruise data."""
    print("Starting the scraper...")

    # Initialize the web driver
    driver = setup_driver()

    try:
        # Navigate to MentorCruise
        url = "https://mentorcruise.com/mentor/browse/"
        driver.get(url)
        print("Loaded the webpage...")

        # Wait for the first mentor card to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ais-InfiniteHits-item"))
        )

        # Scroll to load more mentors
        print("Loading more mentors...")
        scroll_to_load_more(driver)

        # Get the page source after all content is loaded
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find all mentor cards
        mentor_cards = soup.find_all(class_='ais-InfiniteHits-item')
        print(f"Found {len(mentor_cards)} mentor cards.")

        # Extract data from each mentor card
        mentors_data = []
        for card in mentor_cards:
            mentor_data = extract_mentor_data(card)
            mentors_data.append(mentor_data)

        # Create DataFrame and save to CSV
        df = pd.DataFrame(mentors_data)
        output_file = 'mentorcruise_data.csv'
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Data saved to {output_file}")

        # Print preview
        print("\nFirst few entries:")
        print(df.head())
        print(f"\nTotal mentors scraped: {len(df)}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_mentorcruise()
