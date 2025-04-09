import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options  # Import Options for Chrome
import time

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Initialize the driver with options
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Path to the JSON file
json_file_path = 'scraped_data.json'

# Load existing data from the JSON file if it exists
if os.path.exists(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        scraped_data = json.load(json_file)
else:
    scraped_data = []

# Count of newly added items
new_items_count = 0

# Function to scrape ads from a single page
def scrape_ads():
    global new_items_count
    ads = driver.find_elements(By.CLASS_NAME, "css-qfzx1y")
    for ad in ads:
        try:
            # Extract ad title
            title = ad.find_element(By.CLASS_NAME, "css-1g61gc2").text
            # Check if the title is already in the scraped data
            if not any(item['title'] == title for item in scraped_data):
                # Append the new ad data to the list
                scraped_data.append({"title": title})
                new_items_count += 1  # Increment the count for new items

                # Stop after scraping 10 items
                if len(scraped_data) >= 10:
                    return True
        except Exception as e:
            print(f"Error extracting data from an ad: {e}")
    return False

# Open the first page
driver.get("https://www.olx.uz/elektronika/kompyutery/q-%D0%B1-%D1%83-%D0%BA%D0%BE%D0%BC%D0%BF%D1%8C%D1%8E%D1%82%D0%B5%D1%80/?currency=UZS")

# Wait for the page to load
time.sleep(3)

# Scrape the first page
if scrape_ads():
    # If we've scraped 10 items, save them to a JSON file
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(scraped_data, json_file, ensure_ascii=False, indent=4)

# If we haven't scraped enough items, go to the next page and continue
while len(scraped_data) < 10:
    # Find and click the next page button
    try:
        next_page_button = driver.find_element(By.CSS_SELECTOR, "a[data-cy='pageNext']")
        next_page_button.click()
        time.sleep(3)
        
        # Scrape the next page
        if scrape_ads():
            # If we've scraped 10 items, save them to a JSON file
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(scraped_data, json_file, ensure_ascii=False, indent=4)
            break
    except Exception as e:
        print(f"Error navigating to the next page: {e}")
        break

# Print the count of new items added
print(f"New items added: {new_items_count}")

# Close the browser
driver.quit()
