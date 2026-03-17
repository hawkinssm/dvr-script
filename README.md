# DVR Auto-Downloader

A Python script that automates the download of recorded media from a DVR recording service. It runs on a daily schedule, logs in automatically, identifies new recordings, and downloads them — skipping anything already retrieved.

---

## How It Works

The script uses [Playwright](https://playwright.dev/python/) to drive a real browser session. It logs in, waits for the recordings list to load, and clicks the download button for each title not already present in the download log. Login is retried up to 3 times to account for intermittent server-side issues.

---

## Requirements

### Python Dependencies

Install dependencies using the project virtual environment:

```bash
pip install playwright python-dotenv
playwright install chromium
```

### Required Files

The following files must be present in the same directory as `downloader.py` before running the script:

| File | Purpose                                                                                                    |
|---|------------------------------------------------------------------------------------------------------------|
| `.env` | Stores login credentials and configuration (see below)                                                     |
| `downloaded.log` | Tracks previously downloaded titles to prevent re-downloading. Create as an empty file prior to first run. |
| `error.log` | Captures login failure events. Create as an empty file prior to first run.                                 |

> ⚠️ `.env`, `downloaded.log`, and `error.log` are excluded from version control via `.gitignore` and must be created manually on each machine.

---

## Configuration

Create a `.env` file in the project root with the following variables:

```
DVR_EMAIL=your@email.com
DVR_PASSWORD=yourpassword
DVR_URL=https://www.fakedvrlist.com/list/
DVR_DOWNLOAD_DIR=/path/to/your/download/folder
```

---

## Scheduled Execution

This script is designed to run once daily via cron. To configure, run `crontab -e` and add the following line, replacing the paths with your own:

```
0 9 * * * /home/your-username/PycharmProjects/dvr-script/.venv/bin/python /home/your-username/PycharmProjects/dvr-script/downloader.py
```

This runs the script every day at 9:00am. The full path to the virtual environment's Python binary is required so cron uses the correct interpreter with all dependencies available.

---

## Logging

- **`downloaded.log`** — appended with the recording ID of each successfully downloaded title
- **`error.log`** — appended with a timestamped entry if all 3 login attempts fail on a given run