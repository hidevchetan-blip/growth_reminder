# Growth Reminder

## Overview

A FastAPI-based web application that serves as a distribution platform for the Growth Reminder desktop app — a tool that delivers daily motivational notifications to users' desktops.

## Project Structure

```
.
├── server.py              # Main FastAPI application (entry point)
├── requirements.txt       # Python dependencies
├── installers/
│   ├── install_linux.sh   # Linux installer script
│   └── install_windows.bat # Windows installer script
├── scripts/
│   └── growth_reminder.py # The Python reminder script distributed to users
├── templates/
│   └── index.html         # Landing page HTML (optional, has fallback)
└── logs/
    ├── downloads.log      # Tracks installer downloads
    └── pings.log          # Tracks installed client pings
```

## Tech Stack

- **Language**: Python 3.12
- **Framework**: FastAPI
- **Server**: Uvicorn (dev), Gunicorn (production)
- **Storage**: In-memory (users_db dict) — resets on restart

## Running the App

**Development:**
```
python server.py
```
Runs on `http://0.0.0.0:5000`

**Production:**
```
gunicorn --bind=0.0.0.0:5000 --reuse-port server:app
```

## Key Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Landing page (HTML) |
| `/install/windows` | GET | Download Windows installer (.bat) |
| `/install/linux` | GET | Download Linux installer (.sh) |
| `/script.py` | GET | Download the growth reminder Python script |
| `/api/ping` | POST | Client check-in after installation |
| `/api/quote` | GET | Get a random motivational quote |
| `/api/stats` | GET | View download/install statistics |
| `/webhook` | POST | GitHub webhook for auto-deployment |
| `/health` | GET | Health check |

## Configuration

- `GITHUB_WEBHOOK_SECRET` env var — secret for GitHub webhook validation (defaults to `secret@321`)

## Deployment

- Target: VM (always-running, since it uses in-memory state)
- Run: `gunicorn --bind=0.0.0.0:5000 --reuse-port server:app`
