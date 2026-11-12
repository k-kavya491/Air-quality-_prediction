from fastapi import APIRouter, HTTPException, Query

from services import environment

router = APIRouter(prefix="/environmental", tags=["environmental data"])


@router.get("/current")
def current_environmental_data(
    lat: float = Query(..., ge=-90, le=90, allow_inf_nan=False),
    lon: float = Query(..., ge=-180, le=180, allow_inf_nan=False),
):
    if lat == 0 and lon == 0:
        raise HTTPException(
            status_code=422,
            detail="Coordinates 0,0 are not valid"
        )

    try:
        return environment.get_current_environmental_data(lat, lon)

    except environment.NoEnvironmentalData as exc:
        raise HTTPException(status_code=503, detail=str(exc))