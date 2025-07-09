# linkedin/login.py

import os
import time
import pickle
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

load_dotenv()

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
COOKIE_PATH = "linkedin_cookies.pkl"

def create_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)
    return driver

def login_linkedin():
    driver = create_driver(headless=False)  # Show browser for login verification

    if os.path.exists(COOKIE_PATH):
        print("[INFO] Loading cookies...")
        driver.get("https://www.linkedin.com")
        with open(COOKIE_PATH, "rb") as f:
            cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(2)
        if "feed" in driver.current_url:
            print("[INFO] Logged in via cookies.")
            return driver

    print("[INFO] Logging in manually...")
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)

    driver.find_element(By.ID, "username").send_keys(LINKEDIN_EMAIL)
    driver.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD)
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()
    time.sleep(5)

    if "feed" in driver.current_url:
        with open(COOKIE_PATH, "wb") as f:
            pickle.dump(driver.get_cookies(), f)
        print("[INFO] Login successful. Cookies saved.")
    else:
        print("[ERROR] Login failed. Check credentials or security challenge.")
        driver.quit()
        return None

    return driver
