import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
    INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
    INFLUX_ORG = os.getenv("INFLUX_ORG", "airsense")
    INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "aqi_readings")
    POSTGRES_URL = os.getenv("POSTGRES_URL")

    WAQI_TOKEN = os.getenv("WAQI_TOKEN")
    OWM_KEY = os.getenv("OWM_KEY")
    OPENAQ_KEY = os.getenv("OPENAQ_KEY")
    GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_KEY")

    FRONTEND_ORIGINS = os.getenv(
        "FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")


settings = Settings()