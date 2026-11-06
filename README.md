# Air-quality-_prediction
# AirSense: AI-Powered Air Quality Prediction and Smart Mobility

A full-stack web application that predicts localized Air Quality Index (AQI) values and gives route-based health advisories. It combines live location, AQI data, weather and traffic data to warn users when their travel route passes through high-pollution zones.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Frontend | React (Vite), Axios, Leaflet |
| Time-series database | InfluxDB |
| User database | PostgreSQL |
| Data sources | WAQI, OpenAQ, OpenWeatherMap |
| Tools | Docker, Git |

## Project structure

```
airsense/
├── backend/
│   ├── api/            API routes (health, users, location)
│   ├── db/             database clients and models
│   ├── ingestion/      AQI, weather and traffic fetchers
│   ├── main.py         FastAPI entry point
│   ├── requirements.txt
│   └── .env            API keys (not committed)
├── frontend/
│   └── src/
│       ├── components/ reusable UI pieces
│       ├── pages/      app pages
│       └── services/   API calls (api.js)
├── docker-compose.yml  InfluxDB and PostgreSQL
└── README.md
```

## Prerequisites

- Git
- Python 3.10 or newer
- Node.js (LTS)
- Docker Desktop (engine must be running)

## Setup and startup

### 1. Start the databases

From the project root:

```
docker compose up -d
```

- InfluxDB: http://localhost:8086
- PostgreSQL: port 5432

### 2. Configure environment variables

Create `backend/.env` with your own keys:

```
WAQI_TOKEN=your_waqi_token
OWM_KEY=your_openweathermap_key
OPENAQ_KEY=your_openaq_key
INFLUX_URL=http://localhost:8086
INFLUX_TOKEN=my-super-token
INFLUX_ORG=airsense
INFLUX_BUCKET=aqi_readings
POSTGRES_URL=postgresql://airsense:airsense123@localhost:5432/airsense_db
```

Create `frontend/.env`:

```
VITE_API_URL=http://localhost:8000/api
```

Never commit these files. The development passwords and token above must be changed before any deployment.

### 3. Run the backend

```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs

### 4. Run the frontend

In a second terminal:

```
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

## Health check

`GET /api/health` returns:

```
{"status": "ok", "service": "airsense-backend", "time": "..."}
```

The frontend home page calls this endpoint and shows "Backend status: Connected (ok)" when both servers are running and CORS is configured correctly.

## Data ingestion

Run the AQI fetcher manually from the `backend` folder with the virtual environment active:

```
python -m ingestion.aqi_fetcher
```

Readings are stored in the `aqi_readings` bucket in InfluxDB. View them at http://localhost:8086 under Data Explorer.

## Data sources and attribution

- Air quality data: World Air Quality Index project (WAQI) and OpenAQ
- Weather data: OpenWeatherMap

## Development configuration notes

- CORS allows the frontend origin `http://localhost:5173` (set in `backend/main.py`).
- Python files and folders use `snake_case`. React components use `PascalCase`.
- Commands run in a terminal. Code goes in files.

## Status

Weeks 1-2 (in progress):

- [x] Development environment and repository
- [x] Backend and frontend skeletons
- [x] Frontend to backend connection (health check)
- [x] InfluxDB and PostgreSQL running in Docker
- [ ] WAQI and OpenAQ data fetchers
- [ ] Weather and traffic fetchers
- [ ] Scheduler for automatic data collection
- [ ] Location consent flow
- [ ] User registration and health profiles

## Known limitations

- Project is at an early stage. Prediction, route advisory and notifications come in later weeks.
- Free API tiers have rate limits. Check each provider's current terms before commercial use.