from pydantic import BaseModel, Field
from typing import Optional


class LicenseValidateRequest(BaseModel):
    license_key: str = Field(min_length=8, max_length=128)
    device_id: str = Field(min_length=8, max_length=256)
    app_version: Optional[str] = "1.0.0"


class LicenseValidateResponse(BaseModel):
    valid: bool
    message: str
    status: str
    expires_at: Optional[str] = None
    plan: Optional[str] = None
    device_bound: Optional[bool] = None


class CreateLicenseRequest(BaseModel):
    days: int = Field(ge=1, le=3650)
    plan: str = Field(min_length=1, max_length=64)
    notes: Optional[str] = None


class ExtendLicenseRequest(BaseModel):
    days: int = Field(ge=1, le=3650)


class LicenseRecord(BaseModel):
    license_key: str
    plan: str
    status: str
    device_id: Optional[str] = None
    created_at: str
    expires_at: str
    last_check_at: Optional[str] = None
    notes: Optional[str] = None
