Quick Start & Complete User Guide
This complete guide covers setup, file structures, webhook configuration, and execution instructions for your repository.
## 🛠️ Prerequisites & Dependencies
Before running the application, make sure you have **Python 3.10+** installed on your system. 
Open your terminal in the project directory and run the following commands to install the required tools:
**Install core dependencies:**
1.   Save app_gui.py and requirements.txt in a new folder. Name it TM Add Bot or whatever you like.
   
2.  Open up command prompt. Path to the folder location of where you saved this file.

3.  Type each command into dos one at a time and hit the enter button.
   
      pip install -r requirements.txt
   
      playwright install
4. Type python app_gui.py and wait for the UI to load.

5. Once the UI loads add your own discord webhook in and give it a test fire.

6. Add artists name you want to search for. Start off with like 1-2 to make sure its working right.

7. Start monitor. This is the step I need help with and some feedback on. If you do succesfully have playwright installed
   and the cookies still won't load out of your local profile that is a big problem. Whenever you have to query a site like
   TM you want to have a very nice TLS shake and to maintain current cookies no matter what TM drops on us.    

📁 File Structure & Local Storage
Make sure the following files sit in the same exact folder as app_gui.py:

app_gui.py — The core application script, GUI, and threading daemon.

artists.txt — (Auto-generated on first run) Stores your target artist watchlist, with one artist name per line.

cookies.txt — (Auto-generated or user-provided) Stores your active Ticketmaster session cookies for HTTP requests.

Note: If artists.txt or cookies.txt do not exist when you first boot the app, the system will automatically generate baseline files for you.

⚙️ Configuration & Customization
The easiest way to add your webhook is directly through the UI. You have a few more options though.

Adding Your Discord Webhook
To receive real-time inventory alerts straight to your Discord channel:

Open app_gui.py in your preferred text editor (like VS Code or Notepad).

Locate the global configuration variable for your Discord webhook URL near the top of the script:

Python
DISCORD_WEBHOOK_URL = "YOUR_WEBHOOK_URL_HERE"
Paste your actual Discord webhook URL inside the quotes and save the file.

Managing Your Watchlist
You can add or remove artists dynamically straight from the graphical user interface while the app is running, or you can open artists.txt in a text editor and type your target artists manually (one per line).

▶️ Running the Application

