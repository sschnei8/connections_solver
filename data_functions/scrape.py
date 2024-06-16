# %%
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import re
from dotenv import load_dotenv
import os

def scrape_connections(child:int):

    load_dotenv()
    raw_data_location = os.getenv('raw_data_path')
    histoircal_connections_url = os.getenv('connections_url')

    # Set up the Firefox driver provide URL to historical connections 
    driver = webdriver.Firefox()
    driver.get(histoircal_connections_url)

    # Wait for the page to load
    wait = WebDriverWait(driver, 3)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # Get the initial URL
    initial_url = driver.current_url

    # This is the unqiue CSS Selector for the plus sign button that contains a month's worht of historical connections
    # Each month is opened with the selector remaining the same except for the first child div which is incremented by one
    target_buttons_selector = f".accordion-slice > div:nth-child({child}) > div:nth-child(1) > button:nth-child(2)"
    target_buttons = driver.find_elements(By.CSS_SELECTOR, target_buttons_selector)

    for button in target_buttons:
        # Check if the button navigates to a new URL
        driver.execute_script("arguments[0].click();", button)
        if driver.current_url == initial_url:
            # Button didn't navigate, continue to the next button
            continue
        else:
            # Button navigated, go back to the initial URL
            driver.back()

    # Define the date pattern
    date_pattern = re.compile(r"\d{1,2}, \d{4}")

    # Find all paragraphs containing a date
    # Once we find a date paragraph the next 4 paragraphs always contain the connections data
    date_paragraphs = [p.text for p in driver.find_elements(By.TAG_NAME, "p") if date_pattern.search(p.text)]
    data = []  # Create an empty list to store the data

    if not date_paragraphs:
        print("No dates found on the website.")
    else:
        for date_paragraph in date_paragraphs:
            # Extract the date
            date_text = date_paragraph.split()[0:3]
            date = " ".join(date_text)

            # Find all paragraphs after the date paragraph
            next_paragraphs = driver.find_elements(By.TAG_NAME, "p")
            start_index = [p.text for p in next_paragraphs].index(date_paragraph) + 1

            # Extract the text from the next four paragraphs
            data.append(f"Date: {date}")
            for paragraph in next_paragraphs[start_index:start_index + 4]:
                data.append(paragraph.text.strip())
            data.append("-" * 20)  # Add a separator for readability

    driver.quit()

    # Write the data to a file
    with open(raw_data_location, "a", encoding="utf-8") as file:
        file.write("\n".join(data))
    print("Data written to connections_data.txt")
