# Naukri Profile Updater

This script automatically updates your Naukri.com profile (specifically the "Resume Headline" section) to keep your profile active and "Just Updated" in recruiter searches.

## Prerequisites

1.  **Python**: Ensure Python is installed. [Download Python](https://www.python.org/downloads/)
2.  **Google Chrome**: Ensure Chrome is installed.

## Installation

1.  Open a terminal (Command Prompt or PowerShell) in this folder.
2.  Install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```

## Setup & First Run

The script uses a persistent Chrome profile so you only need to log in once.

1.  Run the script manually for the first time:
    ```bash
    python naukri_updater.py
    ```
2.  A Chrome window will open.
3.  **Manually Log In** to your Naukri account in that window.
4.  Once logged in, the script should detect the profile page and attempt to update the "Resume Headline".
5.  Watch the terminal output. If it says "Update Successful!", you are all set.

## Scheduling (Windows Task Scheduler)

To run this daily automatically:

1.  Open **Windows Task Scheduler** ("Task Scheduler" in Start Menu).
2.  Click **Create Basic Task** in the right sidebar.
3.  **Name**: `NaukriDailyUpdate` (or similar). Click Next.
4.  **Trigger**: Select **Daily**.
    *   Set the **Start time** (e.g., 9:00 AM).
    *   Recur every **1 days**.
5.  **Action**: **Start a program**.
6.  **Program/Script**: Path to your `python.exe`.
    *   To find this, run `where python` in your terminal.
    *   Example: `C:\Users\YourName\AppData\Local\Programs\Python\Python39\python.exe`
7.  **Add arguments**: `naukri_updater.py`
8.  **Start in (Optional but Recommended)**: The full path to this folder.
    *   Example: `C:\Users\shree\Desktop\naukri_updater`
9.  Click **Finish**.

### Running Twice Daily
To run it twice a day (e.g., 9 AM and 5 PM):
1.  Find your task in the list, Right-click > **Properties**.
2.  Go to the **Triggers** tab.
3.  Click **New**.
4.  Set another **Daily** trigger for the second time (e.g., 5:00 PM).

### Running in Background
If you don't want the browser window to pop up every time, open `naukri_updater.py` and uncomment the line:
```python
# options.add_argument("--headless=new")
```
(Remove the `#` at the start). **Note:** Only do this AFTER you have successfully logged in once.
