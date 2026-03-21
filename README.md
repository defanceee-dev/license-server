# Generic Desktop Licensing Starter Project

This is a **generic** starter project for a legitimate desktop app that needs:
- a Windows launcher with license key entry
- online license validation
- device binding
- subscription expiry
- simple key management

## What is included

### 1) Launcher (`launcher/`)
Python desktop launcher with Tkinter:
- asks for a license key
- generates a device fingerprint
- validates against your server
- stores local session state
- launches the target app only after a valid check

### 2) License server (`server/`)
FastAPI + SQLite:
- create license keys
- validate keys
- bind first device automatically
- revoke licenses
- extend licenses
- inspect existing licenses

### 3) Helper scripts (`scripts/`)
- build launcher to `.exe` with PyInstaller
- start the API server
- seed an example license

---

## Important limitations

This project is **not strong DRM**. It is a practical licensing starter.
A launcher can always be bypassed if somebody can run the protected executable directly.
For stronger protection, move critical logic to a server you control.

---

## Quick start

## Server

1. Create a virtual environment
2. Install dependencies
3. Start the server

```bash
cd server
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

## Create a test license

From the `server/` folder:

```bash
python admin_cli.py create --days 30 --plan monthly
```

## Launcher

1. Open `launcher/config.json`
2. Edit:
   - `api_base_url`
   - `target_executable`
3. Install dependencies and run:

```bash
cd launcher
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python launcher.py
```

---

## Build launcher as `.exe`

```bash
cd launcher
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed launcher.py --name AppLauncher
```

The built file will appear in:

```text
dist/AppLauncher.exe
```

---

## API overview

### Health
`GET /health`

### Validate license
`POST /api/v1/license/validate`

Request:

```json
{
  "license_key": "ABCDEF12-3456-7890-ABCD-EF1234567890",
  "device_id": "some-device-fingerprint",
  "app_version": "1.0.0"
}
```

### Create license
`POST /api/v1/admin/licenses`

### Extend license
`POST /api/v1/admin/licenses/{license_key}/extend`

### Revoke license
`POST /api/v1/admin/licenses/{license_key}/revoke`

### List licenses
`GET /api/v1/admin/licenses`

---

## Database

SQLite database file:

```text
server/licenses.db
```

Table stores:
- key
- plan
- status
- bound device
- created_at
- expires_at
- last_check_at
- notes

---

## Safer deployment tips

- Put the API behind HTTPS before real use.
- Add admin authentication before exposing admin routes publicly.
- Keep your target executable in a non-obvious path.
- Add rate limiting and request logging.
- Sign server responses if you later harden the launcher.
- Keep a support flow for device resets.

---

## Suggested next step

Use this as a base for a legitimate app you own. Replace the placeholder target path in `launcher/config.json`, test local validation, then build the launcher.
