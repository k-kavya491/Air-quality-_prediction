from db.influx_client import client

query = '''
from(bucket: "aqi_readings")
  |> range(start: -30d, stop: 2d)
  |> filter(fn: (r) => r._measurement == "aqi_readings")
  |> keep(columns: ["_time", "_field", "_value", "station_id"])
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 15)
'''

tables = client.query_api().query(query)
count = 0
for table in tables:
    for rec in table.records:
        count += 1
        print(rec.get_time(), rec.values.get("station_id"), rec.get_field(), rec.get_value())
print("Rows found:", count)