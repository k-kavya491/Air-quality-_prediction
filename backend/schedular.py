from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from core.cities import CITIES, TRACKED_CITIES
from ingestion import aqi_fetcher, weather_fetcher
from services import environment, environment_storage


def run_all():
    print(f"--- Run at {datetime.now():%Y-%m-%d %H:%M:%S} ---")
    jobs = [
        ("AQI", aqi_fetcher.fetch_and_store),
        ("Weather", weather_fetcher.fetch_and_store),
    ]
    for name, job in jobs:
        try:
            job()
        except Exception as e:
            print(f"{name} fetch failed: {e}")


def store_tracked():
    print(f"--- Environment snapshot at {datetime.now():%Y-%m-%d %H:%M:%S} ---")
    for key in TRACKED_CITIES:
        city = CITIES[key]
        lat, lon = city["center"]
        try:
            env = environment.get_environment(lat, lon)
            count = environment_storage.store_environment(env)
            print(f"{city['label']}: stored {count} points")
        except Exception as e:
            print(f"{city['label']}: failed ({e})")


if __name__ == "__main__":
    run_all()
    store_tracked()
    scheduler = BlockingScheduler()
    scheduler.add_job(run_all, "interval", minutes=30, max_instances=1)
    scheduler.add_job(store_tracked, "interval", minutes=60, max_instances=1)
    print("Scheduler started. Press Ctrl+C to stop.")
    scheduler.start()