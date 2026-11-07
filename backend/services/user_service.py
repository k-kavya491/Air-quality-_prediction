from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from db.models import HealthProfile, User
from schemas.user import UserCreate
from services.security import hash_password
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