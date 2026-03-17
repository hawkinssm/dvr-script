import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("DVR_EMAIL")
PASSWORD = os.getenv("DVR_PASSWORD")
URL = os.getenv("DVR_URL")
DOWNLOAD_DIR = os.getenv("DVR_DOWNLOAD_DIR")
LOG_FILE = "downloaded.log"

def load_log():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def save_to_log(entry):
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

def run():
    already_downloaded = load_log()
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # set True later once it's working
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        # Try logging in up to 3 times if needed
        max_retries = 3
        logged_in = False

        for attempt in range(max_retries):
            print(f"Login attempt {attempt + 1} of {max_retries}...")
            page.goto(URL)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(3000)
            page.get_by_role("textbox", name="Email").click()
            page.get_by_role("textbox", name="Email").fill(EMAIL)
            page.get_by_role("textbox", name="Password").click()
            page.get_by_role("textbox", name="Password").fill(PASSWORD)
            page.wait_for_timeout(1000)
            page.get_by_role("button", name="Log In").focus()
            page.wait_for_timeout(500)
            page.keyboard.press("Enter")
            page.wait_for_load_state("networkidle")

            if "login" not in page.url:
                print("Login successful.")
                logged_in = True
                break
            else:
                print(f"Login failed. Waiting 60 seconds before retry...")
                page.wait_for_timeout(60000)

        if not logged_in:
            print("All login attempts failed. Exiting.")
            with open("error.log", "a") as f:
                from datetime import datetime
                f.write(f"{datetime.now()} - Login failed after {max_retries} attempts.\n")
            context.close()
            browser.close()
            return

        # Give the list some time to load before determining there are no new titles
        page.wait_for_selector("[id^='list-download-']", timeout=15000)

        # Find all download buttons on the page
        download_buttons = page.locator("[id^='list-download-']").all()
        print(f"Found {len(download_buttons)} titles to check.")

        for button in download_buttons:
            recording_id = button.get_attribute("id")

            if recording_id in already_downloaded:
                print(f"Skipping {recording_id} - already downloaded.")
                continue

            print(f"Downloading {recording_id}...")
            with page.expect_download() as download_info:
                button.click()
            download = download_info.value
            download.save_as(os.path.join(DOWNLOAD_DIR, download.suggested_filename))
            save_to_log(recording_id)
            print(f"Saved: {download.suggested_filename}")

        context.close()
        browser.close()

run()