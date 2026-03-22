import uuid
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Request

from db import init_db
from license_service import (
    extend_license,
    list_licenses,
    revoke_license,
    validate_license,
)
from schemas import (
    ExtendLicenseRequest,
    LicenseValidateRequest,
    LicenseValidateResponse,
)

app = FastAPI(title="Desktop Licensing Starter API", version="1.0.0")

# 🔥 временное хранилище лицензий (анти-дубль)
licenses = {}


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/api/v1/license/validate", response_model=LicenseValidateResponse)
def api_validate_license(payload: LicenseValidateRequest):
    return validate_license(payload.license_key, payload.device_id)


@app.post("/api/v1/admin/licenses")
async def create_license(request: Request):
    data = await request.json()

    days = data.get("days", 30)
    plan = data.get("plan", "basic")
    user_id = data.get("user_id")

    # ❗ защита от кривых данных
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    user_id = str(user_id)

    # 🔥 проверка: уже есть ключ у пользователя
    for lic in licenses.values():
        if lic.get("user_id") == user_id:
            return lic

    # 🔥 создаём новый ключ
    license_key = str(uuid.uuid4()).upper()
    expires_at = datetime.utcnow() + timedelta(days=int(days))

    license_data = {
        "license_key": license_key,
        "plan": plan,
        "status": "active",
        "device_id": None,
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": expires_at.isoformat(),
        "last_check_at": None,
    }

    licenses[license_key] = license_data

    return license_data


@app.get("/api/v1/admin/licenses")
def api_list_licenses():
    return {"items": list(licenses.values())}


@app.post("/api/v1/admin/licenses/{license_key}/extend")
def api_extend_license(license_key: str, payload: ExtendLicenseRequest):
    updated = extend_license(license_key, payload.days)
    if not updated:
        raise HTTPException(status_code=404, detail="License not found")
    return updated


@app.post("/api/v1/admin/licenses/{license_key}/revoke")
def api_revoke_license(license_key: str):
    ok = revoke_license(license_key)
    if not ok:
        raise HTTPException(status_code=404, detail="License not found")
    return {"ok": True, "license_key": license_key}
