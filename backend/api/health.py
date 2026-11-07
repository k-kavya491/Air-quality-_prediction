from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from db.influx_client import influx_is_up
from db.postgres import get_db

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "airsense-backend",
        "time": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health/db")
def database_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        postgres_ok = True
    except Exception:
        postgres_ok = False

    influx_ok = influx_is_up()
    return {
        "status": "ok" if postgres_ok and influx_ok else "degraded",
        "postgres": postgres_ok,
        "influxdb": influx_ok,
    }