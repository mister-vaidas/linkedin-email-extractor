# main.py

from linkedin.login import login_linkedin
from linkedin.scraper import (
    open_connections_page,
    scroll_to_load_all,
    extract_connection_data,
    extract_email_from_profile,
)
from linkedin.parser import filter_uk_connections
from db.database import init_db, save_email

def main():
    # Initialize PostgreSQL table
    init_db()

    # Login to LinkedIn
    driver = login_linkedin()
    if not driver:
        return

    try:
        # Go to My Connections
        open_connections_page(driver)
        scroll_to_load_all(driver)
        all_connections = extract_connection_data(driver)

        # Filter only UK-based
        uk_connections = filter_uk_connections(all_connections)

        # Visit each profile and extract email
        for conn in uk_connections:
            profile_url = conn["profile_url"]
            email = extract_email_from_profile(driver, profile_url)

            if email:
                save_email(profile_url, email)
            else:
                print(f"[SKIP] {profile_url} — no email found")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
