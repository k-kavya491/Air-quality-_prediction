

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.postgres import get_db
from schemas.user import (
    HealthProfileOut,
    HealthProfileUpdate,
    UserCreate,
    UserOut,
    UserLogin,
    UserNameUpdate,
    PasswordChange,
)
from services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if user_service.get_user_by_email(db, data.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    try:
        return user_service.create_user(db, data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")


@router.get("/{user_id}", response_model=UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/profile", response_model=HealthProfileOut)
def read_profile(user_id: int, db: Session = Depends(get_db)):
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.profile


@router.post("/login", response_model=UserOut)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = user_service.authenticate_user(
        db, data.email, data.password
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return user


@router.put("/{user_id}/profile", response_model=HealthProfileOut)
def update_profile(
    user_id: int,
    data: HealthProfileUpdate,
    db: Session = Depends(get_db),
):
    profile = user_service.update_user_profile(db, user_id, data)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="User or profile not found"
        )

    return profile


@router.put("/{user_id}", response_model=UserOut)
def update_name(
    user_id: int,
    data: UserNameUpdate,
    db: Session = Depends(get_db),
):
    user = user_service.update_user_name(
        db, user_id, data.name
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.put("/{user_id}/password")
def change_password(
    user_id: int,
    data: PasswordChange,
    db: Session = Depends(get_db),
):
    result = user_service.change_user_password(
        db,
        user_id,
        data.current_password,
        data.new_password,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if result is False:
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect",
        )

    return {"message": "Password updated successfully"}
