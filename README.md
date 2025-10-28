# Automated Weekly Marketing Report Generator

This project contains a Python script that automatically generates a weekly performance report in PDF format. It pulls key metrics from Google Analytics 4 (GA4), Google Search Console (GSC), and Google Business Profile (GMB) to give a comprehensive overview of your online presence.

## Features

-   **All-in-One Report:** Combines data from GA4, GSC, and GMB into a single PDF.
-   **Key Metrics:** Focuses on the metrics that matter most to business owners.
-   **Automated & Weekly:** Designed to be run on a schedule to provide a consistent weekly overview.
-   **Secure:** Uses standard OAuth 2.0 for secure authentication with Google's services.

---

## Setup and Usage

Follow these steps carefully to set up and run the report generator.

### Step 1: Prerequisites

-   Make sure you have Python 3.6 or higher installed on your system.

### Step 2: Install Dependencies

Navigate to the project directory in your terminal and run the following command to install the necessary Python libraries:

```bash
pip install -r requirements.txt
```

### Step 3: Get Google API Credentials

This is the most important step. You need to get a `credentials.json` file to allow the script to access your Google data.

1.  **Go to the Google Cloud Console:** [https://console.cloud.google.com/](https://console.cloud.google.com/)
2.  **Create a New Project:** If you don't have one already, create a new project (e.g., "My Weekly Reporter").
3.  **Enable the necessary APIs:**
    -   In the search bar at the top, find and enable each of the following APIs for your project:
        -   **Google Analytics Data API**
        -   **Google Search Console API**
        -   **Business Profile Performance API**
        -   **My Business Business Reviews API**
4.  **Create OAuth 2.0 Credentials:**
    -   Go to "APIs & Services" > "Credentials" in the left-hand menu.
    -   Click "+ CREATE CREDENTIALS" and select "OAuth client ID".
    -   If prompted, configure the "OAuth consent screen".
        -   Choose **External** for the User Type.
        -   Fill in the required fields (App name, User support email, Developer contact information). You can use your own email for all.
        -   You do not need to add scopes on this screen.
        -   Add your email address as a **Test User**. This is important, otherwise the app won't work until it's published.
    -   Go back to the "Credentials" screen and create the OAuth client ID.
    -   Select **Desktop app** for the Application type.
    -   Click "Create".
5.  **Download and Rename:**
    -   A window will pop up showing your Client ID and Secret. Click **DOWNLOAD JSON**.
    -   Rename the downloaded file to `credentials.json`.
    -   Move this `credentials.json` file into the root folder of this project.

### Step 4: Configure Your Property IDs

The script needs to know which properties to pull data from. You must set these as **environment variables**.

-   `GA4_PROPERTY_ID`: Your Google Analytics 4 Property ID.
    -   *How to find:* In GA4, go to Admin > Property Settings > Property ID (it's a string of numbers).
-   `GSC_SITE_URL`: Your Google Search Console property URL.
    -   *How to find:* It must be the exact URL as it appears in the property dropdown in GSC, including the trailing slash if it's there (e.g., `https://example.com/` or `sc-domain:example.com`).
-   `GMB_ACCOUNT_ID` and `GMB_LOCATION_ID`: Your Google Business Profile IDs.
    -   *How to find:* Log in to [Google Business Profile](https://business.google.com/). If you manage multiple locations, select the one you want. Look at the URL in your browser's address bar. It will be in the format `https://business.google.com/dashboard/l/ACCOUNT_ID/LOCATION_ID`. Copy the numbers.

**How to set environment variables:**

-   **On macOS/Linux (for the current session):**
    ```bash
    export GA4_PROPERTY_ID="123456789"
    export GSC_SITE_URL="https://example.com/"
    export GMB_ACCOUNT_ID="9876543210987654321"
    export GMB_LOCATION_ID="1234567890123456789"
    ```
-   **On Windows (Command Prompt, for the current session):**
    ```cmd
    set GA4_PROPERTY_ID="123456789"
    set GSC_SITE_URL="https://example.com/"
    set GMB_ACCOUNT_ID="9876543210987654321"
    set GMB_LOCATION_ID="1234567890123456789"
    ```
*(To set them permanently, you'll need to edit your shell profile (`.bashrc`, `.zshrc`) or use the System Properties dialog in Windows.)*

### Step 5: Run the Report Generator

1.  **First-Time Authorization:**
    -   Run the `auth.py` script directly from your terminal:
        ```bash
        python auth.py
        ```
    -   This will open a new tab in your web browser.
    -   Choose the Google account you added as a Test User.
    -   You may see a "Google hasn't verified this app" warning. Click "Advanced" and then "Go to (unsafe)". This is expected because you are the developer.
    -   Grant the script permission to access your data.
    -   Once you approve, the page will say "Authentication successful". You can close the browser tab.
    -   A new file named `token.json` will be created in your project folder. This securely stores your authorization.

2.  **Generate Your Report:**
    -   Now you can run the main script:
        ```bash
        python main.py
        ```
    -   The script will print its progress and, when finished, you will find a new PDF file in the project folder (e.g., `Weekly_Report_123456789_2023-10-27.pdf`).

### (Optional) Step 6: Automation

You can schedule this script to run automatically.

-   **On macOS/Linux:** Use `cron`. Open your crontab with `crontab -e` and add a line like this to run the report every Monday at 8 AM:
    ```cron
    0 8 * * 1 /usr/bin/python3 /path/to/your/project/main.py
    ```
-   **On Windows:** Use the Task Scheduler. Create a new task that runs `python.exe` with the argument `/path/to/your/project/main.py` on your desired schedule.

---

## Command-line Task Manager

This repository also includes a standalone task manager CLI application that you can use to keep track of personal to-dos. The tool stores data in a local SQLite database (`tasks.db`) that lives next to the script.

### Quick Start

Run the commands below from the project root:

```bash
python task_manager.py add "Draft client proposal" --due 2024-05-15 -p high
python task_manager.py list
```

### Available Commands

| Command | Description | Example |
| --- | --- | --- |
| `add` | Create a task with optional description, due date, and priority (`high`, `medium`, `low` or `1-3`). | `python task_manager.py add "Pay invoices" -d "Clients A & B" --due 2024-05-01 -p low` |
| `list` | Display pending tasks by default. Use `--all` to include completed ones, `--completed` to show only finished work, or `--overdue` to focus on late tasks. | `python task_manager.py list --overdue --sort priority` |
| `complete` | Mark a task as completed. | `python task_manager.py complete 3` |
| `update` | Modify title, description, due date, priority, or status. Combine with `--clear-due` to remove an existing due date. | `python task_manager.py update 2 --priority high --status completed` |
| `delete` | Remove a task permanently. | `python task_manager.py delete 5` |

The application prints a compact table so you can quickly scan task status. Data is saved automatically after every command, so you can exit and return later without losing progress.
