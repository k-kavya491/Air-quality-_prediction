from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import db.models  # noqa: F401  (registers the tables)
from api.air_quality import router as air_quality_router
from api.dashboard import router as dashboard_router
from api.health import router as health_router
from api.location import router as location_router
from api.users import router as users_router
from core.config import settings
from db.postgres import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="AirSense API", version="0.3.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(location_router, prefix="/api")
app.include_router(air_quality_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "AirSense API is running"}