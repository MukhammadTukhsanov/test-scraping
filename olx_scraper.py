# scraper.py

import os
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

json_file_path = 'scraped_data.json'
TELEGRAM_BOT_TOKEN = '7582125550:AAGymmAhLkFAj_cxqUx5HQeFg4rc2-TMbPw'
TELEGRAM_CHAT_ID = '959945390'

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    print(f"sending message")
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

def scrap_olx_data():
    # Setup ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Load existing data
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            scraped_data = json.load(json_file)
    else:
        scraped_data = []

    new_items_count = 0

    def scrape_ads():
        nonlocal new_items_count
        ads = driver.find_elements(By.CLASS_NAME, "css-qfzx1y")
        for ad in ads:
            try:
                title = ad.find_element(By.CLASS_NAME, "css-1g61gc2").text
                send_to_telegram(f"Scraping...")
                if not any(item['title'] == title for item in scraped_data):
                    scraped_data.append({"title": title})
                    new_items_count += 1
                    send_to_telegram(f"New Ad: {title}")
                    if len(scraped_data) >= 10:
                        return True
            except Exception as e:
                print(f"Error extracting data from an ad: {e}")
        return False

    driver.get("https://www.olx.uz/elektronika/kompyutery/q-%D0%B1-%D1%83-%D0%BA%D0%BE%D0%BC%D0%BF%D1%8C%D1%8E%D1%82%D0%B5%D1%80/?currency=UZS")
    time.sleep(3)

    if scrape_ads():
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(scraped_data, json_file, ensure_ascii=False, indent=4)

    while len(scraped_data) < 10:
        try:
            next_page_button = driver.find_element(By.CSS_SELECTOR, "a[data-cy='pageNext']")
            next_page_button.click()
            time.sleep(3)
            if scrape_ads():
                with open(json_file_path, 'w', encoding='utf-8') as json_file:
                    json.dump(scraped_data, json_file, ensure_ascii=False, indent=4)
                break
        except Exception as e:
            print(f"Error navigating to the next page: {e}")
            break

    driver.quit()
    return {"new_items_added": new_items_count}
