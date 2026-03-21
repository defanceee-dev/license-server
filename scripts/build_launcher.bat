@echo off
cd /d %~dp0\..\launcher
if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed launcher.py --name AppLauncher
