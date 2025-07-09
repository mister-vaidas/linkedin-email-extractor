# main.py

from linkedin.login import login_linkedin

def main():
    driver = login_linkedin()
    if driver:
        print("[INFO] Ready to scrape...")
        # TODO: Call scraper logic here
        driver.quit()

if __name__ == "__main__":
    main()
