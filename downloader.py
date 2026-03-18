import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

URL = os.getenv("DVR_URL")
DOWNLOAD_DIR = os.getenv("DVR_DOWNLOAD_DIR")
SESSION_DIR = str(Path(__file__).parent / "session")
LOG_FILE = str(Path(__file__).parent / "downloaded.log")
ERROR_LOG = str(Path(__file__).parent / "error.log")

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
        context = p.chromium.launch_persistent_context(
            SESSION_DIR,
            headless=True,
            accept_downloads=True
        )
        page = context.new_page()
        page.goto(URL.replace("/login", ""))

        try:
            page.wait_for_selector("[id^='list-download-']", timeout=15000)
        except:
            print("Could not load recordings page. Session may have expired.")
            with open(ERROR_LOG, "a") as f:
                f.write(f"{datetime.now()} - Session expired or recordings page failed to load.\n")
            context.close()
            return

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

run()