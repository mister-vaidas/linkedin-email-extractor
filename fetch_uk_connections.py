# fetch_uk_connections.py  (phase-1)

from linkedin.login import login_linkedin
from linkedin.scraper import (
    open_connections_page,
    scroll_to_load_all,
    extract_connection_data,
)
from linkedin.parser import filter_uk_connections
from db.database import init_db, save_uk_connection
from utils.location_logger import log   # already created earlier

def main():
    init_db()

    driver = login_linkedin()
    if not driver:
        return

    try:
        open_connections_page(driver)
        scroll_to_load_all(driver, scroll_pause=1.7)   # you can bump to 2.0s if needed
        all_connections = extract_connection_data(driver)

        uk_connections = filter_uk_connections(all_connections)

        for conn in uk_connections:
            save_uk_connection(conn)      # ← stores only genuine UK matches

        # optional: log anything that *didn't* match
        for conn in all_connections:
            if conn not in uk_connections:
                log(conn["location"])

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
