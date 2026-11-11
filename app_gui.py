import time
import os
import random
import json
import requests
import threading
import sys
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import customtkinter as ctk

# Set global CustomTkinter appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- CYBER-OPS PALETTE ---
COLOR_BG = "#0b0f19"          # Deep space black/blue
COLOR_CARD = "#131b2e"        # Dark slate container
COLOR_ACCENT = "#00F3FF"      # Ice Blue / Cyber Cyan
COLOR_HOVER = "#0284c7"       # Muted Ice Blue hover
COLOR_BORDER = "#1e293b"      # Subtle dark border
COLOR_TEXT_MUTED = "#94a3b8"

# --- GLOBAL CONFIGURATION & STATE ---
ARTISTS_FILE = "artists.txt"
COOKIES_FILE = "cookies.txt"
DEFAULT_WEBHOOK = ""

artist_known_events = {}

class TextRedirector:
    """Redirects print statements to the CustomTkinter Textbox console widget."""
    def __init__(self, textbox):
        self.textbox = textbox

    def write(self, str_val):
        self.textbox.after(0, self._append_text, str_val)

    def _append_text(self, str_val):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", str_val)
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def flush(self):
        pass

# --- CORE BOT FUNCTIONS ---

def load_watchlist():
    if not os.path.exists(ARTISTS_FILE):
        with open(ARTISTS_FILE, "w", encoding="utf-8") as f:
            f.write("Taylor Swift\n")
            
    artists = []
    with open(ARTISTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            cleaned_line = line.strip()
            if cleaned_line and not cleaned_line.startswith("#"):
                artists.append(cleaned_line)
    return artists

def save_watchlist(artists_list):
    with open(ARTISTS_FILE, "w", encoding="utf-8") as f:
        for artist in artists_list:
            f.write(f"{artist}\n")

def remove_artist_from_watchlist(artist_name):
    artists = load_watchlist()
    cleaned_target = artist_name.strip()
    updated_artists = [a for a in artists if a.lower() != cleaned_target.lower()]
    
    if len(updated_artists) < len(artists):
        save_watchlist(updated_artists)
        print(f"[GUI] Successfully removed '{cleaned_target}' from watchlist.")
        return True
    else:
        print(f"[GUI] Warning: '{cleaned_target}' was not found in the watchlist.")
        return False

def harvest_fresh_cookies():
    print("[AUTO-COOKIE] Harvesting fresh Ticketmaster session cookies via Playwright...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            page.goto("https://www.ticketmaster.com", timeout=30000)
            page.wait_for_load_state("networkidle", timeout=10000)
            
            cookies = context.cookies("https://www.ticketmaster.com")
            browser.close()
            
            if not cookies:
                print("[AUTO-COOKIE] Warning: No cookies captured.")
                return None
                
            cookie_strs = [f"{c['name']}={c['value']}" for c in cookies]
            cookie_string = "; ".join(cookie_strs)
            
            with open(COOKIES_FILE, "w", encoding="utf-8") as f:
                f.write(cookie_string)
                
            print("[AUTO-COOKIE] Successfully saved fresh cookies to 'cookies.txt'!")
            return cookie_string
    except Exception as e:
        print(f"[AUTO-COOKIE] Error harvesting cookies: {e}")
        return None

def load_cookie():
    if not os.path.exists(COOKIES_FILE) or os.path.getsize(COOKIES_FILE) == 0:
        print(f"[INFO] '{COOKIES_FILE}' is missing or empty. Triggering harvester...")
        harvested = harvest_fresh_cookies()
        return harvested if harvested else "BID=PLACEHOLDER_COOKIE;"
            
    with open(COOKIES_FILE, "r", encoding="utf-8") as f:
        return f.read().strip().replace("\n", " ").replace("\r", "")

def send_discord_alert(webhook_url, artist, event_name, event_date, event_id):
    if not webhook_url or webhook_url == "YOUR_WEBHOOK_URL_HERE":
        print("[WARNING] Discord Webhook URL is invalid or not set.")
        return

    event_url = f"https://www.ticketmaster.com/event/{event_id}"
    query = artist.strip().replace(" ", "+")
    search_url = f"https://www.ticketmaster.com/search?q={query}"

    payload = {
        "username": "NEXUS // RADAR",
        "avatar_url": "https://images.credly.com/images/0594fa6a-653a-4da2-a4f5-5fd8fc3cf1b9/node-js-development.png",
        "embeds": [
            {
                "title": f"⚡ [SYS_ALERT] NEW EVENT INJECTION DETECTED",
                "description": f"```ini\n[ TARGET ACQUIRED ]\nArtist: {artist}\nEvent:  {event_name}\n```\n**[{event_name}]({event_url})**",
                "color": 0x00F3FF,
                "fields": [
                    {"name": "📡 TELEMETRY", "value": f"```prolog\nDATE   : {event_date}\nID     : {event_id}\nSTATUS : LIVE_VERIFIED\n```", "inline": False},
                    {"name": "🌐 ACCESS GATES", "value": f"🔹 **[Direct Event Node]({event_url})**\n🔸 **[Search Matrix Query]({search_url})**", "inline": False}
                ],
                "footer": {"text": "NEXUS PROTOCOL // SECURE AUTOMATION FEED", "icon_url": "https://images.credly.com/images/0594fa6a-653a-4da2-a4f5-5fd8fc3cf1b9/node-js-development.png"},
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
        ]
    }
    try:
        res = requests.post(webhook_url, json=payload, timeout=10)
        if res.status_code == 204:
            print("[DISCORD] Cyber-ops alert successfully deployed!")
        else:
            print(f"[DISCORD] Alert failed. Status code: {res.status_code}")
    except Exception as e:
        print(f"[DISCORD] Error sending webhook: {e}")

def create_configured_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "Cookie": load_cookie()
    })
    return session

def fetch_ticketmaster_events(artist, session, use_mock=False):
    if use_mock:
        time.sleep(0.5)
        return [{"id": f"EVT_{artist[:3].upper()}_01", "name": f"{artist} - Live in Concert", "date": "2026-12-01 @ 8:00 PM"}]
    
    extracted_events = []
    query = artist.strip().replace(" ", "+")
    page_num = 0
    max_pages = 10

    while page_num < max_pages:
        target_url = f"https://www.ticketmaster.com/search?q={query}&limit=200&page={page_num}"
        print(f"[LIVE] Hitting page {page_num} for '{artist}'...")
        try:
            response = session.get(target_url, timeout=10)
            if response.status_code == 403:
                print(f"[WARNING] 403 Forbidden. Harvesting fresh cookies...")
                new_cookie = harvest_fresh_cookies()
                if new_cookie:
                    session.headers.update({"Cookie": new_cookie})
                    response = session.get(target_url, timeout=10)

            if response.status_code != 200:
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            script_tags = soup.find_all('script')
            page_events_found = 0
            
            for script in script_tags:
                content = script.string
                if content and ('events' in content.lower() or 'initialState' in content or '__NEXT_DATA__' in content):
                    try:
                        json_str = content.strip()
                        if "=" in json_str[:50]:
                            json_str = json_str.split("=", 1)[1].strip().rstrip(";")
                    
                        data = json.loads(json_str)
                        queries = data.get("props", {}).get("pageProps", {}).get("initialReduxState", {}).get("api", {}).get("queries", {})
                        
                        for q_key, q_val in queries.items():
                            if q_key.startswith("searchEvents") or "search" in q_key.lower():
                                search_data = q_val.get("data", {})
                                if search_data:
                                    for evt in search_data.get("events", []):
                                        evt_id = evt.get("id")
                                        evt_name = evt.get("name") or evt.get("title") or "Live Event"
                                        evt_dates = evt.get("dates", {})
                                        start_date = evt_dates.get("start", {}).get("localDate", "TBD")
                                        start_time = evt_dates.get("start", {}).get("localTime", "")
                                        date_str = f"{start_date} @ {start_time}".strip() if start_time else start_date
                                        
                                        if evt_id:
                                            event_obj = {"id": evt_id, "name": evt_name, "date": date_str}
                                            if event_obj not in extracted_events:
                                                extracted_events.append(event_obj)
                                                page_events_found += 1
                    except Exception:
                        pass
            if page_events_found == 0:
                break
            page_num += 1
            time.sleep(random.uniform(1.0, 2.0))
        except Exception as e:
            print(f"[ERROR] Live fetch failed: {e}")
            break
            
    print(f"[LIVE] Total unique events compiled for {artist}: {len(extracted_events)}")
    return extracted_events

def check_artist_shows(artist, session, webhook_url, use_mock=False):
    print(f"\n--- Checking: {artist} ---")
    current_events = fetch_ticketmaster_events(artist, session, use_mock)
    
    if artist not in artist_known_events:
        artist_known_events[artist] = set()
        
    known_set = artist_known_events[artist]
    if not current_events:
        print(f"[INFO] No events parsed yet for {artist}.")
        return
        
    if len(known_set) == 0:
        print(f"[BASELINE] Establishing baseline for {artist} ({len(current_events)} events loaded)...")
        for event in current_events:
            known_set.add(event["id"])
        return
        
    for event in current_events:
        event_id = event["id"]
        if event_id not in known_set:
            print(f"\n🚨 [ALERT!] NEW SHOW DETECTED FOR {artist.upper()}! 🚨")
            print(f"Event: {event['name']} | Date: {event['date']} | ID: {event_id}\n")
            known_set.add(event_id)
            send_discord_alert(webhook_url, artist, event['name'], event['date'], event_id)
        else:
            print(f"[OK] Already tracked: {event['name']} ({event_id})")

# --- CUSTOMTKINTER GUI CLASS ---

class TicketmasterBotApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Nexus Cyber-Ops // Ticketmaster Radar v13")
        self.geometry("980x700")
        self.configure(fg_color=COLOR_BG)

        self.is_running = False
        self.bot_thread = None

        # --- TOP TITLE BAR ---
        self.title_label = ctk.CTkLabel(
            self, 
            text="⚡ NEXUS CYBER-OPS // TICKETMASTER RADAR", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_ACCENT
        )
        self.title_label.pack(padx=20, pady=(15, 5), anchor="w")

        # --- MAIN GRID LAYOUT ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(padx=15, pady=10, fill="both", expand=True)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=2)
        self.main_container.grid_rowconfigure(0, weight=1)

        # --- LEFT PANEL (SETTINGS & WATCHLIST) ---
        self.left_panel = ctk.CTkFrame(self.main_container, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        self.left_panel.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Controls Section
        ctk.CTkLabel(self.left_panel, text="CONTROL MATRIX", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(padx=15, pady=(12, 5), anchor="w")
        
        self.start_button = ctk.CTkButton(
            self.left_panel, 
            text="▶ Start Monitor", 
            fg_color=COLOR_ACCENT, 
            text_color="#0b0f19", 
            hover_color=COLOR_HOVER,
            font=ctk.CTkFont(weight="bold"),
            command=self.start_bot
        )
        self.start_button.pack(padx=15, pady=5, fill="x")

        self.stop_button = ctk.CTkButton(
            self.left_panel, 
            text="⏹ Stop Monitor", 
            fg_color="#1e293b", 
            text_color="#f87171", 
            hover_color="#334155", 
            state="disabled", 
            command=self.stop_bot
        )
        self.stop_button.pack(padx=15, pady=5, fill="x")

        self.test_btn = ctk.CTkButton(
            self.left_panel, 
            text="⚡ Send Test Alert", 
            fg_color="#1e293b", 
            text_color=COLOR_ACCENT,
            hover_color="#334155", 
            command=self.send_test_alert
        )
        self.test_btn.pack(padx=15, pady=5, fill="x")

        self.cookie_btn = ctk.CTkButton(
            self.left_panel, 
            text="🍪 Harvest Cookies", 
            fg_color="#1e293b", 
            text_color="#38bdf8",
            hover_color="#334155", 
            command=self.trigger_cookie_harvest
        )
        self.cookie_btn.pack(padx=15, pady=5, fill="x")

        # Settings
        ctk.CTkLabel(self.left_panel, text="DISCORD WEBHOOK URL", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(padx=15, pady=(12, 2), anchor="w")
        
        webhook_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        webhook_frame.pack(padx=15, pady=2, fill="x")
        webhook_frame.grid_columnconfigure(0, weight=1)
        webhook_frame.grid_columnconfigure(1, weight=0)

        self.webhook_entry = ctk.CTkEntry(webhook_frame, placeholder_text="Webhook URL...", fg_color="#0b0f19", border_color=COLOR_BORDER)
        self.webhook_entry.insert(0, DEFAULT_WEBHOOK)
        self.webhook_entry.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.set_webhook_btn = ctk.CTkButton(
            webhook_frame, 
            text="Set", 
            width=50, 
            fg_color="#1e293b", 
            text_color=COLOR_ACCENT,
            hover_color="#334155", 
            command=self.set_webhook_url
        )
        self.set_webhook_btn.grid(row=0, column=1, sticky="e")

        self.mock_toggle = ctk.CTkCheckBox(self.left_panel, text="Use Mock Test Data", text_color=COLOR_TEXT_MUTED, checkbox_width=18, checkbox_height=18, fg_color=COLOR_ACCENT, hover_color=COLOR_HOVER)
        self.mock_toggle.pack(padx=15, pady=10, anchor="w")

        # Watchlist Section
        ctk.CTkLabel(self.left_panel, text="ARTIST WATCHLIST", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(padx=15, pady=(10, 5), anchor="w")
        
        self.artist_entry = ctk.CTkEntry(self.left_panel, placeholder_text="Enter artist name...", fg_color="#0b0f19", border_color=COLOR_BORDER)
        self.artist_entry.pack(padx=15, pady=2, fill="x")

        self.add_artist_btn = ctk.CTkButton(
            self.left_panel, 
            text="+ Add Artist", 
            fg_color="#1e293b", 
            text_color=COLOR_ACCENT,
            hover_color="#334155", 
            command=self.add_artist
        )
        self.add_artist_btn.pack(padx=15, pady=5, fill="x")

        # Scrollable Frame for Watchlist items with individual delete buttons
        self.watchlist_scroll = ctk.CTkScrollableFrame(self.left_panel, height=130, fg_color="#0b0f19", border_color=COLOR_BORDER, border_width=1)
        self.watchlist_scroll.pack(padx=15, pady=5, fill="x")
        self.refresh_watchlist_ui()

        # --- RIGHT PANEL (LIVE CONSOLE LOG) ---
        self.right_panel = ctk.CTkFrame(self.main_container, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        self.right_panel.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        ctk.CTkLabel(self.right_panel, text="LIVE TELEMETRY CONSOLE", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(padx=15, pady=(12, 5), anchor="w")

        self.console_box = ctk.CTkTextbox(
            self.right_panel, 
            font=ctk.CTkFont(family="Consolas", size=11), 
            text_color=COLOR_ACCENT,
            fg_color="#0b0f19",
            border_color=COLOR_BORDER,
            border_width=1
        )
        self.console_box.pack(padx=15, pady=(5, 15), fill="both", expand=True)
        self.console_box.configure(state="disabled")

        # Redirect standard output to Tkinter Console Box
        sys.stdout = TextRedirector(self.console_box)
        print("[SYS_INIT] GUI Dashboard Initialized. Ready for monitoring loop.")

    def set_webhook_url(self):
        new_url = self.webhook_entry.get().strip()
        if new_url and new_url.startswith("https://"):
            print(f"[GUI] Active Discord Webhook URL updated successfully.")
        else:
            print(f"[GUI] Warning: Please enter a valid Discord webhook URL.")

    def refresh_watchlist_ui(self):
        for widget in self.watchlist_scroll.winfo_children():
            widget.destroy()

        artists = load_watchlist()
        if not artists:
            lbl = ctk.CTkLabel(self.watchlist_scroll, text="No artists in watchlist.", text_color=COLOR_TEXT_MUTED)
            lbl.pack(padx=5, pady=5, anchor="w")
            return

        for artist in artists:
            row_frame = ctk.CTkFrame(self.watchlist_scroll, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)

            name_lbl = ctk.CTkLabel(row_frame, text=artist, anchor="w", text_color="#e2e8f0")
            name_lbl.pack(side="left", padx=5, fill="x", expand=True)

            del_btn = ctk.CTkButton(
                row_frame, 
                text="✕", 
                width=26, 
                height=24, 
                fg_color="#1e293b", 
                text_color="#f87171",
                hover_color="#334155", 
                command=lambda a=artist: self.remove_artist(a)
            )
            del_btn.pack(side="right", padx=2)

    def add_artist(self):
        new_artist = self.artist_entry.get().strip()
        if new_artist:
            artists = load_watchlist()
            if new_artist not in artists:
                artists.append(new_artist)
                save_watchlist(artists)
                self.refresh_watchlist_ui()
                self.artist_entry.delete(0, "end")
                print(f"[GUI] Added '{new_artist}' to watchlist.")

    def remove_artist(self, artist_name):
        success = remove_artist_from_watchlist(artist_name)
        if success:
            self.refresh_watchlist_ui()

    def start_bot(self):
        self.is_running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        
        self.bot_thread = threading.Thread(target=self.run_bot_loop, daemon=True)
        self.bot_thread.start()

    def stop_bot(self):
        self.is_running = False
        print("\n[GUI] Stopping monitor... Completing current operations...")
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def trigger_cookie_harvest(self):
        threading.Thread(target=harvest_fresh_cookies, daemon=True).start()

    def send_test_alert(self):
        webhook = self.webhook_entry.get().strip()
        print("[GUI] Deploying manual test alert to Discord...")
        send_discord_alert(
            webhook, 
            artist="Taylor Swift", 
            event_name="The Eras Tour - Added Stadium Date (GUI Test)", 
            event_date="2026-11-15 @ 7:00 PM", 
            event_id="MOCK_TEST_GUI_999"
        )

    def run_bot_loop(self):
        print("\n[MONITOR] Background execution thread started.")
        bot_session = create_configured_session()
        cycle_count = 1

        while self.is_running:
            print(f"\n==================================================")
            print(f"=== Check Cycle #{cycle_count} @ {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
            print(f"==================================================")

            webhook_url = self.webhook_entry.get().strip()
            use_mock = self.mock_toggle.get() == 1
            watchlist = load_watchlist()

            print(f"Watchlist: {watchlist}")
            for i, artist in enumerate(watchlist):
                if not self.is_running:
                    break
                try:
                    check_artist_shows(artist, bot_session, webhook_url, use_mock)
                except Exception as e:
                    print(f"⚠️ [ERROR] Failed checking '{artist}': {e}")

                if i < len(watchlist) - 1 and self.is_running:
                    delay = random.randint(5, 10) if use_mock else random.randint(30, 60)
                    print(f"-> Waiting {delay}s before checking next artist...")
                    time.sleep(delay)

            cycle_count += 1
            if self.is_running:
                print("\nCycle complete. Waiting 30s before next scan...")
                time.sleep(30)

        print("[MONITOR] Monitoring thread stopped.")

if __name__ == "__main__":
    app = TicketmasterBotApp()
    app.mainloop()