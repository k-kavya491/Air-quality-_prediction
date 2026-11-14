

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from db.models import HealthProfile, User
from schemas.user import UserCreate, HealthProfileUpdate
from services.security import hash_password, verify_password
from services.thresholds import compute_threshold


def get_user_by_email(db: Session, email: str):
    return db.scalar(select(User).where(User.email == email.lower()))


def get_user(db: Session, user_id: int):
    return db.scalar(
        select(User).options(joinedload(User.profile)).where(User.id == user_id)
    )


def create_user(db: Session, data: UserCreate):
    p = data.profile
    user = User(
        name=data.name,
        email=data.email.lower(),
        password_hash=hash_password(data.password),
    )
    user.profile = HealthProfile(
        has_asthma=p.has_asthma,
        is_elderly=p.is_elderly,
        is_child=p.is_child,
        alert_threshold=compute_threshold(
            p.has_asthma, p.is_elderly, p.is_child, p.alert_threshold
        ),
        alert_enabled=p.alert_enabled,
        notify_push=p.notify_push,
        notify_email=p.notify_email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def update_user_profile(
    db: Session, user_id: int, data: HealthProfileUpdate
):
    user = get_user(db, user_id)

    if not user or not user.profile:
        return None

    p = data
    user.profile.has_asthma = p.has_asthma
    user.profile.is_elderly = p.is_elderly
    user.profile.is_child = p.is_child
    user.profile.alert_threshold = compute_threshold(
        p.has_asthma, p.is_elderly, p.is_child, p.alert_threshold
    )
    user.profile.alert_enabled = p.alert_enabled
    user.profile.notify_push = p.notify_push
    user.profile.notify_email = p.notify_email

    db.commit()
    db.refresh(user)

    return user.profile


def update_user_name(db: Session, user_id: int, name: str):
    user = get_user(db, user_id)

    if not user:
        return None

    user.name = name
    db.commit()
    db.refresh(user)

    return user
def change_user_password(
    db: Session,
    user_id: int,
    current_password: str,
    new_password: str,
):
    user = get_user(db, user_id)

    if not user:
        return None

    if not verify_password(current_password, user.password_hash):
        return False

    user.password_hash = hash_password(new_password)

    db.commit()
    db.refresh(user)

    return True
