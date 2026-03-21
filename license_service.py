from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, List

from db import get_conn

UTC = timezone.utc


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def make_key() -> str:
    raw = secrets.token_hex(16).upper()
    return f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:32]}"


def create_license(days: int, plan: str, notes: Optional[str] = None) -> dict:
    created_at = datetime.now(UTC).replace(microsecond=0)
    expires_at = created_at + timedelta(days=days)
    row = {
        "license_key": make_key(),
        "plan": plan,
        "status": "active",
        "device_id": None,
        "created_at": created_at.isoformat(),
        "expires_at": expires_at.isoformat(),
        "last_check_at": None,
        "notes": notes,
    }

    conn = get_conn()
    try:
        conn.execute(
            """
            INSERT INTO licenses (
                license_key, plan, status, device_id, created_at, expires_at, last_check_at, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["license_key"],
                row["plan"],
                row["status"],
                row["device_id"],
                row["created_at"],
                row["expires_at"],
                row["last_check_at"],
                row["notes"],
            ),
        )
        conn.commit()
        return row
    finally:
        conn.close()


def get_license(license_key: str) -> Optional[dict]:
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM licenses WHERE license_key = ?",
            (license_key.strip(),),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_licenses() -> List[dict]:
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM licenses ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def revoke_license(license_key: str) -> bool:
    conn = get_conn()
    try:
        cur = conn.execute(
            "UPDATE licenses SET status = 'revoked' WHERE license_key = ?",
            (license_key.strip(),),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def extend_license(license_key: str, days: int) -> Optional[dict]:
    existing = get_license(license_key)
    if not existing:
        return None

    current_expiry = datetime.fromisoformat(existing["expires_at"])
    base = max(current_expiry, datetime.now(UTC))
    new_expiry = base + timedelta(days=days)

    conn = get_conn()
    try:
        conn.execute(
            "UPDATE licenses SET expires_at = ? WHERE license_key = ?",
            (new_expiry.replace(microsecond=0).isoformat(), license_key.strip()),
        )
        conn.commit()
    finally:
        conn.close()

    return get_license(license_key)


def validate_license(license_key: str, device_id: str) -> dict:
    record = get_license(license_key)
    if not record:
        return {
            "valid": False,
            "message": "License key not found.",
            "status": "missing",
            "expires_at": None,
            "plan": None,
            "device_bound": False,
        }

    if record["status"] != "active":
        return {
            "valid": False,
            "message": f"License status is {record['status']}.",
            "status": record["status"],
            "expires_at": record["expires_at"],
            "plan": record["plan"],
            "device_bound": bool(record.get("device_id")),
        }

    expiry = datetime.fromisoformat(record["expires_at"])
    if expiry < datetime.now(UTC):
        return {
            "valid": False,
            "message": "Subscription expired.",
            "status": "expired",
            "expires_at": record["expires_at"],
            "plan": record["plan"],
            "device_bound": bool(record.get("device_id")),
        }

    if record.get("device_id") and record["device_id"] != device_id:
        return {
            "valid": False,
            "message": "License is already bound to another device.",
            "status": "device_mismatch",
            "expires_at": record["expires_at"],
            "plan": record["plan"],
            "device_bound": True,
        }

    conn = get_conn()
    try:
        if not record.get("device_id"):
            conn.execute(
                "UPDATE licenses SET device_id = ?, last_check_at = ? WHERE license_key = ?",
                (device_id, now_iso(), license_key.strip()),
            )
        else:
            conn.execute(
                "UPDATE licenses SET last_check_at = ? WHERE license_key = ?",
                (now_iso(), license_key.strip()),
            )
        conn.commit()
    finally:
        conn.close()

    return {
        "valid": True,
        "message": "License is valid.",
        "status": "active",
        "expires_at": record["expires_at"],
        "plan": record["plan"],
        "device_bound": True,
    }
