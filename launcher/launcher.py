import requests
import subprocess
import json
import os
import sys

CONFIG_FILE = "config.json"


def load_config():
    if not os.path.exists(CONFIG_FILE):
        print("config.json not found")
        sys.exit(1)

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_device_id():
    # простой device_id (можно потом улучшить)
    return os.getenv("COMPUTERNAME", "unknown-device")


def validate_license(server_url, license_key):
    url = f"{server_url}/api/v1/license/validate"

    payload = {
        "license_key": license_key,
        "device_id": get_device_id(),
        "app_version": "1.0.0"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        return {"valid": False, "message": str(e)}


def run_target(exe_path):
    if not os.path.exists(exe_path):
        print("EXE not found:", exe_path)
        return

    try:
        subprocess.Popen(exe_path)
    except Exception as e:
        print("Failed to start EXE:", e)


def main():
    config = load_config()

    server_url = config["server_url"]
    exe_path = config["target_executable"]

    license_key = input("Enter license key: ").strip()

    print("Checking license...")

    result = validate_license(server_url, license_key)

    print("Server response:", result)

    if result.get("valid"):
        print("✅ License valid! Launching app...")
        run_target(exe_path)
    else:
        print("❌ License invalid:", result.get("message", "Unknown error"))

    input("Press Enter to exit...")


if __name__ == "__main__":
    main()