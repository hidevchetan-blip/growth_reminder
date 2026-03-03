#!/usr/bin/env python3
"""
Growth Reminder - Daily Motivational Quotes
Runs at scheduled times to show inspirational quotes
"""

import requests
import platform
import subprocess
import os
import html
import json
import sys
from pathlib import Path
from datetime import datetime
import random

# Configuration
CONFIG_FILE = Path.home() / ".growth_reminder_config.json"
SERVER_URL = "YOUR_SERVER_URL_PLACEHOLDER"  # Will be replaced during download

# Fallback quotes in case API fails
FALLBACK_QUOTES = [
    {"q": "The only way to do great work is to love what you do.", "a": "Steve Jobs"},
    {"q": "Success is not final, failure is not fatal", "a": "Winston Churchill"},
    {"q": "Your time is limited, don't waste it", "a": "Steve Jobs"},
    {"q": "The future depends on what you do today", "a": "Mahatma Gandhi"},
    {"q": "Don't watch the clock; do what it does. Keep going.", "a": "Sam Levenson"},
    {"q": "Everything you've ever wanted is on the other side of fear.", "a": "George Addair"},
    {"q": "Execution beats perfection. Ship today.", "a": "Unknown"}
]

def load_config():
    """Load or create user configuration"""
    default_config = {
        "user_id": generate_user_id(),
        "server_url": SERVER_URL,
        "sound_enabled": True,
        "notifications_enabled": True,
        "first_run": True,
        "installed_at": datetime.now().isoformat()
    }
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = {**default_config, **json.load(f)}
        except:
            config = default_config
    else:
        config = default_config
        save_config(config)
    
    return config

def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except:
        pass

def generate_user_id():
    """Generate a unique user ID"""
    import uuid
    return str(uuid.uuid4())

def get_ceo_tip():
    """Fetch a random quote"""
    try:
        # Try primary API
        response = requests.get("https://zenquotes.io/api/random", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data[0]["q"], data[0]["a"]
    except:
        pass
    
    try:
        # Try fallback to server
        config = load_config()
        if config["server_url"] != "YOUR_SERVER_URL_PLACEHOLDER":
            response = requests.get(f"{config['server_url']}/api/quote", timeout=3)
            if response.status_code == 200:
                quote_data = response.json()
                return quote_data["quote"], "Unknown"
    except:
        pass
    
    # Use local fallback
    quote = random.choice(FALLBACK_QUOTES)
    return quote["q"], quote["a"]

def show_notification(quote, author):
    """Show system notification based on platform"""
    message = f"{quote}\n\n— {author}"
    system = platform.system()
    
    # Escape for shell
    quote_escaped = html.escape(quote)
    author_escaped = html.escape(author)
    message_escaped = html.escape(message)
    
    try:
        if system == "Windows":
            # Windows notification
            try:
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(
                    "📈 Growth Reminder 💼",
                    message,
                    duration=10,
                    threaded=True
                )
            except ImportError:
                # Fallback to message box
                import ctypes
                ctypes.windll.user32.MessageBoxW(
                    0, 
                    message, 
                    "📈 Growth Reminder 💼", 
                    0x40 | 0x0
                )
        
        elif system == "Linux":
            # Linux notification
            try:
                # Try notify-send
                subprocess.run([
                    'notify-send',
                    '--urgency=normal',
                    '--expire-time=10000',
                    '📈 Growth Reminder 💼',
                    message_escaped
                ], check=False)
                
                # Play sound if available
                subprocess.run([
                    'canberra-gtk-play',
                    '--id=message-new-instant'
                ], check=False, stderr=subprocess.DEVNULL)
                
            except:
                # Try zenity
                subprocess.run([
                    'zenity',
                    '--info',
                    '--title=📈 Growth Reminder 💼',
                    f'--text={message_escaped}',
                    '--width=400',
                    '--height=200'
                ], check=False)
        
        elif system == "Darwin":  # macOS
            subprocess.run([
                'osascript',
                '-e',
                f'display notification "{quote_escaped}" with title "Growth Reminder" subtitle "{author_escaped}"'
            ], check=False)
    
    except Exception as e:
        # Last resort: print to console
        print("\n" + "="*50)
        print("📈 Growth Reminder 💼")
        print("="*50)
        print(message)
        print("="*50)

def report_to_server(config):
    """Optional: report execution back to server"""
    if config["server_url"] != "YOUR_SERVER_URL_PLACEHOLDER":
        try:
            requests.post(
                f"{config['server_url']}/api/ping",
                json={
                    "user_id": config["user_id"],
                    "status": "success",
                    "timestamp": datetime.now().isoformat()
                },
                timeout=2
            )
        except:
            pass  # Silent fail

def main():
    """Main execution function"""
    config = load_config()
    
    # Get quote
    quote, author = get_ceo_tip()
    
    # Show notification
    show_notification(quote, author)
    
    # Report back (optional)
    report_to_server(config)
    
    # Update config if first run
    if config.get("first_run"):
        config["first_run"] = False
        save_config(config)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
