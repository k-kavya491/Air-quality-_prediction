# AirSense: AI-Powered Air Quality Prediction and Smart Mobility

A full-stack application for monitoring localized Air Quality Index (AQI), weather and traffic conditions. AirSense combines environmental data with location information to support future pollution-aware travel recommendations and health advisories.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite |
| HTTP Client | Axios |
| Backend | Python, FastAPI |
| Time-series Database | InfluxDB 2.7 |
| User Database | PostgreSQL 16 |
| Air Quality Data | WAQI, OpenAQ |
| Weather Data | OpenWeatherMap |
| Traffic Data | TomTom |
| Containerization | Docker, Docker Compose |
| Version Control | Git, GitHub |
| API Testing | Postman |

## Project Structure

```text
airsense/
├── backend/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── ingestion/
│   ├── schemas/
│   ├── services/
│   ├── tests/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/
│       ├── hooks/
│       ├── pages/
│       ├── services/
│       └── utils/
├── .postman/
├── docs/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Prerequisites

- Git
- Python 3.10 or newer
- Node.js (LTS) and npm
- Docker Desktop
- VS Code (recommended)

## Setup and Startup

### 1. Start Docker databases

From the project root:

```powershell
docker compose up -d
```

The root `.env` file must contain the Docker Compose configuration variables:

```dotenv
INFLUXDB_INIT_USERNAME=your_username
INFLUXDB_INIT_PASSWORD=your_password
INFLUXDB_INIT_ORG=airsense
INFLUXDB_INIT_BUCKET=aqi_readings
INFLUXDB_INIT_ADMIN_TOKEN=your_admin_token

POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=airsense_db
```

These are example variable names. Use the credentials configured for your own database containers.

Check the containers:

```powershell
docker compose ps
```

Services:
- InfluxDB: http://localhost:8086
- PostgreSQL: localhost:5432

### 2. Configure backend environment variables

Create `backend/.env` with your own API keys and database connection settings:

```dotenv
WAQI_TOKEN=your_waqi_token
OWM_KEY=your_openweathermap_key
OPENAQ_KEY=your_openaq_key
TOMTOM_API_KEY=your_tomtom_api_key

INFLUX_URL=http://localhost:8086
INFLUX_TOKEN=your_influx_token
INFLUX_ORG=airsense
INFLUX_BUCKET=aqi_readings

POSTGRES_URL=your_postgresql_connection_url

FRONTEND_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Use credentials matching your local database configuration. Do not share or commit environment files.

### 3. Configure frontend environment variables

Create `frontend/.env` if needed:

```dotenv
VITE_API_URL=http://localhost:8000/api
```

### 4. Run the backend

Open a terminal:

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend:
- API: http://localhost:8000
- Interactive API documentation: http://localhost:8000/docs

### 5. Run the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## API Health Check

The backend health endpoint is:

```http
GET /api/health
```

Test it using:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

## Environmental Data Integration

The backend integrates the following data sources:

- **WAQI:** Air Quality Index information.
- **OpenAQ:** Pollutant measurements such as PM2.5, PM10, NO2, O3 and CO, where available.
- **OpenWeatherMap:** Temperature, humidity, pressure, wind and weather conditions.
- **TomTom:** Traffic speed and travel-time information.

The combined environmental endpoint is:

```http
GET /api/environmental/current?lat=17.6868&lon=83.2183
```

It retrieves environmental information for the requested coordinates, processes the available data, and attempts to store historical readings in InfluxDB.

## Data Storage

- InfluxDB stores historical environmental readings.
- PostgreSQL is configured for relational application data.
- Docker Compose manages both database services.

InfluxDB Data Explorer: http://localhost:8086

## Development Notes

- Python files and folders use `snake_case`.
- React components use `PascalCase`.
- Frontend source files currently use TypeScript (`.ts` and `.tsx`).
- Keep API keys and credentials in environment files.
- Do not commit `.env` files.
- Use the API documentation at `/docs` to inspect and test backend endpoints.

## API Endpoints

The AirSense backend provides the following FastAPI endpoints.

| Category | Endpoint | Purpose |
|---|---|---|
| Health | `/api/health` | Backend health check |
| Health | `/api/health/db` | Database health check |
| Users | `/api/users/register` | User registration |
| Users | `/api/users/login` | User login |
| Users | `/api/users/{user_id}` | User details and updates |
| Users | `/api/users/{user_id}/profile` | Health sensitivity and notification preferences |
| Users | `/api/users/{user_id}/password` | Password updates |
| Location | `/api/location` | Submit location information |
| Location | `/api/location/{user_id}/latest` | Retrieve the latest saved location |
| Air Quality | `/api/air-quality/current` | Current AQI and pollutant measurements |
| Dashboard | `/api/dashboard/cities` | Supported city information |
| Dashboard | `/api/dashboard/overview` | Dashboard overview data |
| Environmental | `/api/environmental/current` | Combined air quality, weather, and traffic information |

Interactive API documentation: `http://localhost:8000/docs`

## Testing and Verification

### Backend Testing

Run automated tests from the backend directory:

```powershell
python -m pytest tests -v
```

Latest verified result: **17 tests passed**, with one deprecation warning.

### Frontend Testing

Run the frontend production build:

```powershell
npm run build
```

The frontend production build completed successfully.

### Integration Testing

The following functionality has been verified:

- User profile updates and password changes
- AQI and pollutant display
- Weather and traffic information
- City selection and dashboard updates
- Browser geolocation and interactive pollution map
- Combined environmental API response
- Availability of air quality, weather, and traffic data
- Invalid latitude and longitude validation
- Historical environmental records in InfluxDB
- Frontend-to-backend communication

## Development Status

### Day 1 — Project Setup

- [x] Development environment configured
- [x] Git repository initialized
- [x] React frontend and FastAPI backend initialized
- [x] Frontend/backend communication established
- [x] Initial project documentation created

### Day 2 — Database and User Management

- [x] PostgreSQL and InfluxDB configured
- [x] Database connection settings configured
- [x] User registration and login implemented
- [x] User profile management implemented
- [x] Health sensitivity settings implemented
- [x] Initial dashboard developed

### Day 3 — Location and Air Quality Integration

- [x] Browser geolocation integration
- [x] Location permission and error handling
- [x] Location API integration
- [x] WAQI and OpenAQ integration
- [x] Pollutant data processing
- [x] Current air quality API
- [x] Frontend AQI and pollutant display

### Day 4 — Environmental Data Integration

- [x] OpenWeatherMap weather integration
- [x] TomTom traffic integration
- [x] Environmental data cleaning and aggregation
- [x] Combined environmental API
- [x] Historical environmental data storage
- [x] Automated backend tests
- [x] Integration testing for available environmental sources

### Day 5 — Dashboard and Integration

- [x] Environmental dashboard
- [x] AQI and pollutant display
- [x] Interactive pollution map
- [x] Frontend/backend API integration
- [x] Application error handling implemented
- [x] Database records verified
- [x] Dashboard end-to-end testing passed
- [x] API endpoints verified
- [x] Technical documentation updated

Milestone demonstration and final submission remain pending.

## Known Limitations

- The machine-learning AQI forecasting model has not yet been implemented.
- The dashboard displays a forecasting-pending message instead of unverified predictions.
- Pollution-aware route recommendations are planned for future development.
- Health advisories and automated notifications require further development or verification.
- External APIs may experience rate limits, network failures, or unavailable measurements.
- Additional provider failure scenarios and automatic collection scheduling require verification.
- Environmental data availability varies by location and provider.

## Milestone 1 Summary

AirSense is a full-stack environmental monitoring application developed using React, TypeScript, FastAPI, PostgreSQL, and InfluxDB.

The application integrates air quality, weather, traffic, and location information into an environmental dashboard. It supports user management, pollutant visualization, historical environmental data storage, and an interactive pollution map.

The core Day 1–5 implementation and integration tests have been completed. Final demonstration and submission remain.