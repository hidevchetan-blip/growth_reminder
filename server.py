# server.py - Your central server
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid
from datetime import datetime
import uvicorn
import hmac
import hashlib
import subprocess

app = FastAPI(title="Growth Reminder Installer")

SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "secret@321")

# In-memory storage (use database in production)
users_db = {}

# Create directories if they don't exist
os.makedirs("installers", exist_ok=True)
os.makedirs("scripts", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("logs", exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def landing_page():
    """Serve the main landing page"""
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Growth Reminder</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                .btn { display: inline-block; padding: 15px 30px; margin: 10px; 
                       background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; }
                .btn:hover { background: #45a049; }
                .container { text-align: center; }
                .features { text-align: left; background: #f9f9f9; padding: 20px; border-radius: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📈 Growth Reminder</h1>
                <p>Get daily motivation right on your desktop!</p>
                
                <div style="margin: 30px 0;">
                    <a href="/install/windows" class="btn">⬇️ Download for Windows</a>
                    <a href="/install/linux" class="btn">🐧 Download for Linux</a>
                </div>
                
                <div class="features">
                    <h3>✨ Features:</h3>
                    <ul>
                        <li>Daily motivational quotes daily</li>
                        <li>Beautiful desktop notifications</li>
                        <li>Sound alerts</li>
                        <li>Automatic scheduling (cron/Task Scheduler)</li>
                        <li>Works offline after installation</li>
                    </ul>
                    
                    <h3>📋 How to install:</h3>
                    <ol>
                        <li>Click download button for your OS</li>
                        <li>Run the downloaded installer</li>
                    </ol>
                    
                    <p><small>⚡ Test it now: After installation, run the script manually to see a sample notification</small></p>
                </div>
            </div>
        </body>
        </html>
        """)


@app.get("/install/{os_type}")
async def download_installer(os_type: str, request: Request):
    """Serve the appropriate installer based on OS"""

    user_id = str(uuid.uuid4())

    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "Unknown")

    users_db[user_id] = {
        "ip": client_ip,
        "user_agent": user_agent,
        "os": os_type,
        "downloaded_at": datetime.now().isoformat(),
        "installed": False
    }

    with open("logs/downloads.log", "a") as f:
        f.write(f"{datetime.now()},{user_id},{client_ip},{os_type},{user_agent}\n")

    if os_type.lower() == "windows":

        installer_path = "./installers/install_windows.bat"

        if not os.path.exists(installer_path):
            raise HTTPException(status_code=404, detail="Installer not found")

        return FileResponse(
            path=installer_path,
            filename=f"growth_reminder_install_{user_id[:8]}.bat",
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename=growth_reminder_install_{user_id[:8]}.bat"
            }
        )

    elif os_type.lower() == "linux":

        installer_path = "./installers/install_linux.sh"

        if not os.path.exists(installer_path):
            raise HTTPException(status_code=404, detail="Installer not found")

        return FileResponse(
            path=installer_path,
            filename=f"growth_reminder_install_{user_id[:8]}.sh",
            media_type="application/x-sh",
            headers={
                "Content-Disposition": f"attachment; filename=growth_reminder_install_{user_id[:8]}.sh"
            }
        )

    else:
        raise HTTPException(status_code=400, detail="Unsupported OS. Please choose Windows or Linux.")


@app.get("/script.py")
async def download_python_script(request: Request):

    script_path = "./scripts/growth_reminder.py"

    if not os.path.exists(script_path):
        raise HTTPException(status_code=404, detail="Script not found")

    with open(script_path, "r", encoding="utf-8") as f:
        script_content = f.read()

    base_url = str(request.base_url).rstrip('/')

    script_content = script_content.replace(
        "YOUR_SERVER_URL_PLACEHOLDER",
        base_url
    )

    return Response(
        content=script_content,
        media_type="text/plain",
        headers={
            "Content-Disposition": "attachment; filename=growth_reminder.py"
        }
    )


@app.post("/api/ping")
async def receive_ping(data: dict):

    user_id = data.get("user_id")
    status = data.get("status", "unknown")

    if user_id and user_id in users_db:

        users_db[user_id]["last_seen"] = datetime.now().isoformat()
        users_db[user_id]["status"] = status
        users_db[user_id]["installed"] = True

        with open("logs/pings.log", "a") as f:
            f.write(f"{datetime.now()},{user_id},{status}\n")

        return JSONResponse({"status": "received", "user_id": user_id})

    return JSONResponse({"status": "error", "message": "User not found"}, status_code=404)


@app.get("/api/quote")
async def get_fallback_quote():

    quotes = [
        "The only way to do great work is to love what you do. — Steve Jobs",
        "Success is not final, failure is not fatal: it is the courage to continue that counts. — Winston Churchill",
        "Your time is limited, don't waste it living someone else's life. — Steve Jobs",
        "The future depends on what you do today. — Mahatma Gandhi",
        "Don't watch the clock; do what it does. Keep going. — Sam Levenson",
        "The only limit to our realization of tomorrow is our doubts of today. — Franklin D. Roosevelt",
        "It does not matter how slowly you go as long as you do not stop. — Confucius",
        "Everything you've ever wanted is on the other side of fear. — George Addair"
    ]

    import random

    return JSONResponse({"quote": random.choice(quotes)})


@app.get("/api/stats")
async def get_stats():

    total_downloads = len(users_db)

    installed = sum(1 for u in users_db.values() if u.get("installed"))

    active_today = sum(
        1 for u in users_db.values()
        if u.get("last_seen") and
        (datetime.now() - datetime.fromisoformat(u["last_seen"])).days < 1
    )

    windows_count = sum(1 for u in users_db.values() if u.get("os") == "windows")
    linux_count = sum(1 for u in users_db.values() if u.get("os") == "linux")

    return {
        "total_downloads": total_downloads,
        "successful_installs": installed,
        "active_today": active_today,
        "os_breakdown": {
            "windows": windows_count,
            "linux": linux_count
        }
    }


def verify_signature(payload, signature):

    mac = hmac.new(SECRET.encode(), payload, hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()

    return hmac.compare_digest(expected, signature)


@app.post("/webhook")
async def webhook(request: Request):

    signature = request.headers.get("X-Hub-Signature-256")

    if not signature:
        raise HTTPException(status_code=403)

    payload = await request.body()

    if not verify_signature(payload, signature):
        raise HTTPException(status_code=403)

    event = request.headers.get("X-GitHub-Event")

    if event != "push":
        return {"status": "ignored"}

    data = await request.json()

    if data["ref"] == "refs/heads/main":

        subprocess.run(["git", "pull", "origin", "main"])
        return {"status": "deployed"}

    return {"status": "ignored"}


@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check():

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=5000)