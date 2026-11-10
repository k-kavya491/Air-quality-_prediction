from fastapi import APIRouter, HTTPException, Query

from schemas.air_quality import AirQualityResponse
from services import air_quality

router = APIRouter(prefix="/air-quality", tags=["air quality"])


@router.get("/current", response_model=AirQualityResponse)
def current_air_quality(
    lat: float = Query(..., ge=-90, le=90, allow_inf_nan=False),
    lon: float = Query(..., ge=-180, le=180, allow_inf_nan=False),
):
    if lat == 0 and lon == 0:
        raise HTTPException(status_code=422, detail="Coordinates 0,0 are not valid")
    try:
        return air_quality.get_current_air_quality(lat, lon)
    except air_quality.NoAirQualityData as e:
        raise HTTPException(
            status_code=503 if e.unavailable else 404, detail=str(e)
        )