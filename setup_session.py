from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

URL = os.getenv("DVR_URL")
SESSION_DIR = str(Path(__file__).parent / "session")

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        SESSION_DIR,
        headless=False,
        accept_downloads=True
    )
    page = browser.new_page()
    page.goto(URL)
    input("Log in manually in the browser, then press Enter here to save the session...")
    browser.close()
    print("Session saved!")