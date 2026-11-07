import os
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

load_dotenv()

BUCKET = os.getenv("INFLUX_BUCKET")

client = InfluxDBClient(
    url=os.getenv("INFLUX_URL"),
    token=os.getenv("INFLUX_TOKEN"),
    org=os.getenv("INFLUX_ORG"),
)
write_api = client.write_api(write_options=SYNCHRONOUS)


def write_points(points):
    """Write a list of influxdb Point objects to the bucket."""
    write_api.write(bucket=BUCKET, record=points)