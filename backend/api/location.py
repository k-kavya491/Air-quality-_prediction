from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.postgres import get_db
from schemas.location import LocationIn, LocationOut
from services import location_service, user_service

router = APIRouter(prefix="/location", tags=["location"])


@router.post("", response_model=LocationOut)
def submit_location(data: LocationIn, db: Session = Depends(get_db)):
    if data.user_id is not None and not user_service.get_user(db, data.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return location_service.process_location(data)


@router.get("/{user_id}/latest", response_model=LocationOut)
def latest_location(user_id: int, db: Session = Depends(get_db)):
    if not user_service.get_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    loc = location_service.get_latest_location(user_id)
    if not loc:
        raise HTTPException(status_code=404, detail="No saved location for this user")
    return loc