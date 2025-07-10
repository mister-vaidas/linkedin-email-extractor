# linkedin/scraper.py
import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException


# ──────────────────────────────────────────────────────────────
def open_connections_page(driver):
    """Navigate to the LinkedIn Connections page."""
    print("[INFO] Opening Connections page…")
    driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
    time.sleep(3)


# ──────────────────────────────────────────────────────────────
def scroll_to_load_all(driver, scroll_pause: float = 1.7, max_idle_loops: int = 6):
    """
    Load every connection card on the page.

    Strategy:
        • Scroll viewport to bottom (Keys.END).
        • Click any visible button containing “Show more” or “Load more”.
        • Repeat until card-count stops growing and no buttons remain.
        • Resilient to StaleElementReferenceException.
    """
    print("[INFO] Scrolling to load all connections…")
    last_count, idle_loops = 0, 0

    while True:
        # 1️⃣ Scroll viewport to bottom
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(scroll_pause)

        # 2️⃣ Click all current “show / load more” buttons
        btn_xpath = (
            "//button[not(@disabled) and "
            "(contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'show more') "
            "or contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'load more'))]"
        )
        buttons = driver.find_elements(By.XPATH, btn_xpath)

        clicked_any = False
        for btn in buttons:
            try:
                if btn.is_displayed():
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center'});", btn
                    )
                    driver.execute_script("arguments[0].click();", btn)
                    clicked_any = True
                    print(
                        "  ↪ clicked:",
                        re.sub(r"\s+", " ", btn.text.strip())[:40] or "<no-text>",
                    )
            except StaleElementReferenceException:
                # DOM updated; ignore and continue
                continue

        # 3️⃣ Count cards now in DOM
        cards = driver.find_elements(By.CSS_SELECTOR, ".mn-connection-card")
        current_count = len(cards)
        print(f"  └─ Visible cards: {current_count}")

        # 4️⃣ Exit condition
        if current_count == last_count and not clicked_any:
            idle_loops += 1
            if idle_loops >= max_idle_loops:
                break
        else:
            last_count, idle_loops = current_count, 0

    print(f"[INFO] Finished scrolling. Total loaded: {last_count}")


# ──────────────────────────────────────────────────────────────
def extract_connection_data(driver):
    """Return list of dicts: {name, location, profile_url} for every visible card."""
    print("[INFO] Extracting connection info…")
    time.sleep(3)  # ensure DOM stable
    cards = driver.find_elements(By.CSS_SELECTOR, ".mn-connection-card")
    connections = []

    for card in cards:
        try:
            name = card.find_element(
                By.CLASS_NAME, "mn-connection-card__name"
            ).text.strip()
            location = card.find_element(
                By.CLASS_NAME, "mn-connection-card__details"
            ).text.strip()
            profile_url = (
                card.find_element(By.TAG_NAME, "a").get_attribute("href").split("?")[0]
            )
            connections.append(
                {"name": name, "location": location, "profile_url": profile_url}
            )
        except Exception:
            continue  # skip malformed cards

    print(f"[INFO] Extracted {len(connections)} connections.")
    return connections


# ──────────────────────────────────────────────────────────────
def extract_email_from_profile(driver, profile_url):
    """
    Visit profile ➜ open Contact info ➜ return first email or None.
    """
    print(f"[VISIT] {profile_url}")
    try:
        driver.get(profile_url)
        time.sleep(3)

        driver.find_element(By.PARTIAL_LINK_TEXT, "Contact").click()
        time.sleep(2)

        mail_links = driver.find_elements(
            By.XPATH, '//a[starts-with(@href,"mailto:")]'
        )
        for link in mail_links:
            email = link.get_attribute("href").replace("mailto:", "")
            if "@" in email:
                return email
    except Exception:
        pass
    return None
