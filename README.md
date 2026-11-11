Quick Start & Complete User Guide
This complete guide covers setup, file structures, webhook configuration, and execution instructions for your repository.
## 🛠️ Prerequisites & Dependencies
Before running the application, make sure you have **Python 3.10+** installed on your system. 
Open your terminal in the project directory and run the following commands to install the required tools:
1. **Install core dependencies:**

   Path to the folder location of where you saved this file and type in these two commands. This will install what you need to get this app running.
      pip install -r requirements.txt
   
      playwright install

3. 📁 File Structure & Local Storage
Make sure the following files sit in the same exact folder as app_gui.py:

app_gui.py — The core application script, GUI, and threading daemon.

artists.txt — (Auto-generated on first run) Stores your target artist watchlist, with one artist name per line.

cookies.txt — (Auto-generated or user-provided) Stores your active Ticketmaster session cookies for HTTP requests.

Note: If artists.txt or cookies.txt do not exist when you first boot the app, the system will automatically generate baseline files for you.

3. ⚙️ Configuration & Customization
Adding Your Discord Webhook
To receive real-time inventory alerts straight to your Discord channel:

Open app_gui.py in your preferred text editor (like VS Code or Notepad).

Locate the global configuration variable for your Discord webhook URL near the top of the script:

Python
DISCORD_WEBHOOK_URL = "YOUR_WEBHOOK_URL_HERE"
Paste your actual Discord webhook URL inside the quotes and save the file.

2. Managing Your Watchlist
You can add or remove artists dynamically straight from the graphical user interface while the app is running, or you can open artists.txt in a text editor and type your target artists manually (one per line).

▶️ Running the Application
Once your dependencies are installed and your webhook is configured, launch the desktop dashboard by running:

Bash
python app_gui.py
How to Use the UI:
Watchlist Panel: View, add, or delete target artists from the sidebar.

Monitor Control: Click ▶ Start Monitor to initiate the asynchronous background scan loop.

Telemetry Feed: Monitor live status logs, event counts, and HTTP responses directly in the main console view.
