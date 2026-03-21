@echo off
cd /d %~dp0\..\server
if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate
pip install -r requirements.txt
python admin_cli.py create --days 30 --plan monthly
