import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db import init_db
from license_service import (
    extend_license,
    revoke_license,
    validate_license,
)
from schemas import (
    ExtendLicenseRequest,
    LicenseValidateRequest,
    LicenseValidateResponse,
)

app = FastAPI(title="Desktop Licensing Starter API", version="1.0.0")

# временное хранилище лицензий
licenses = {}


class CreateLicenseRequest(BaseModel):
    user_id: int
    duration_days: int = 30
    plan: str = "basic"


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
def api_create_license(payload: CreateLicenseRequest):
    user_id = str(payload.user_id)
    days = int(payload.duration_days)
    plan = payload.plan

    # проверка: уже есть ключ у пользователя
    for lic in licenses.values():
        if lic.get("user_id") == user_id:
            return lic

    # создаём новый ключ
    license_key = str(uuid.uuid4()).upper()
    expires_at = datetime.utcnow() + timedelta(days=days)

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
