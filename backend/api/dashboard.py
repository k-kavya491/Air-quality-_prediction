from fastapi import APIRouter, HTTPException, Query

from core.cities import CITIES, DEFAULT_CITY
from ingestion.errors import ExternalAPIError
from schemas.dashboard import DashboardOverview
from services import dashboard

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/cities")
def list_cities():
    return [{"key": k, "label": v["label"]} for k, v in CITIES.items()]


@router.get("/overview", response_model=DashboardOverview)
def overview(city: str = Query(DEFAULT_CITY)):
    key = city.lower()
    if key not in CITIES:
        raise HTTPException(status_code=404, detail="Unknown city")
    try:
        return dashboard.get_overview(key)
    except ExternalAPIError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except dashboard.NoDashboardData as e:
        raise HTTPException(status_code=404, detail=str(e))