# India Weather Data Platform

A Python-based data engineering pipeline that collects current weather observations for six Indian cities, stores raw API responses as JSON, and loads structured records into Microsoft SQL Server for analytics.

## Project Overview

This project demonstrates an end-to-end local data pipeline, from API ingestion to relational storage and SQL-based analysis. It focuses on reliable ingestion, duplicate prevention, basic data validation, logging, testing, and scheduled execution.

### Cities Covered

Hyderabad, Delhi, Mumbai, Chennai, Bengaluru, and Kolkata.

## Architecture

```text
Open-Meteo Weather API
          |
          v
   Python Extraction
  - HTTP requests
  - Retry handling
  - Data validation
          |
          v
    Raw JSON Files
      data/raw/
          |
          v
   Python SQL Loader
  - Timestamp conversion
  - Duplicate checks
  - Transaction handling
          |
          v
 Microsoft SQL Server
   WeatherObservations
          |
          v
     SQL Analytics
  - Latest city weather
  - Daily city summaries
  - Temperature comparisons
  - Data-quality checks
```

## Tech Stack

- **Language:** Python
- **API:** Open-Meteo
- **Database:** Microsoft SQL Server Express
- **Database connectivity:** `pyodbc` with Microsoft ODBC Driver 18
- **Data processing:** JSON and Python standard library
- **Testing:** pytest
- **Automation:** Windows Task Scheduler
- **Development tools:** Visual Studio Code and SQL Server Management Studio

## Features

- Collects current weather data for six Indian cities.
- Stores raw API responses as timestamped JSON files.
- Retries failed HTTP requests.
- Validates key weather measurements.
- Loads structured observations into SQL Server.
- Prevents duplicate city-and-observation-time records.
- Uses database transactions and rollback handling.
- Logs pipeline stages and failures.
- Includes automated tests for extraction and loading behavior.
- Provides reusable SQL views for latest observations and daily summaries.
- Includes SQL checks for missing cities, invalid measurements, and duplicate records.
- Supports scheduled execution through Windows Task Scheduler.

## Database Schema

The main table is `dbo.WeatherObservations`.

|        Column           |              Description              |
|-------------------------|---------------------------------------|
| `ObservationID`         | Generated primary key                 |
| `City`                  | City name                             |
| `Latitude`, `Longitude` | Geographic coordinates                | 
| `ObservationTime`       | Timestamp supplied by the weather API |
| `TemperatureC`          | Air temperature in °C                 |
| `FeelsLikeC`            | Apparent temperature in °C            |
| `HumidityPercent`       | Relative humidity                     |
| `PrecipitationMM`       | Precipitation in millimetres          |
| `WeatherCode`           | Weather condition code                |
| `WindSpeedKmh`          | Wind speed in km/h                    |
| `IngestedAtUtc`         | Database ingestion timestamp in UTC   |

A unique index on `(City, ObservationTime)` helps prevent duplicate observations.

## SQL Analytics

SQL scripts are maintained in the `sql/` directory.

- `analytics.sql` — creates reusable views for latest city weather and daily summaries.
- `data_quality.sql` — checks expected city coverage, measurement validity, duplicate records, and observation counts.

The analytics currently operate on the observations collected so far. They are not a long-term climate analysis or an official heat-warning system.

## Project Structure

```text
india-weather-data-platform/
├── data/
│   └── raw/
├── logs/
├── src/
│   ├── db.py
│   ├── extract.py
│   ├── load.py
│   └── pipeline.py
├── sql/
│   ├── analytics.sql
│   └── data_quality.sql
├── tests/
│   ├── test_extract.py
│   └── test_load.py
├── .gitignore
├── README.md
└── requirements.txt
```

Raw data files and logs are generated during execution. They may not be included in the repository.

## Prerequisites

- Windows
- Python 3.13 or a compatible Python version
- Microsoft SQL Server Express
- SQL Server Management Studio (SSMS)
- Microsoft ODBC Driver 18 for SQL Server
- An internet connection for the weather API

## Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd india-weather-data-platform
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure SQL Server

Create a database named `WeatherDataEngineering`, then create the `dbo.WeatherObservations` table and its unique index using the project's SQL schema.

Update `src/db.py` with the SQL Server instance name available on your machine. The current development configuration uses Windows authentication and is specific to the original local environment.

### 5. Run the pipeline

From the project root:

```powershell
python -m src.pipeline
```

The pipeline extracts weather data, saves raw JSON files under `data/raw/`, and loads observations into SQL Server.

### 6. Run tests

```powershell
pytest -v
```

The tests use mocked components for selected failure scenarios. They do not replace a full integration test against a live SQL Server instance.

### 7. Run SQL analytics

Open the SQL scripts in SSMS, select the `WeatherDataEngineering` database, and execute the scripts.

## Scheduling

Windows Task Scheduler can launch the pipeline on a recurring schedule using the virtual environment's Python executable.

Scheduled collection depends on the computer being powered on and able to access the internet and SQL Server. Missed current-weather observations are not automatically recovered by this pipeline.

## Limitations and Future Improvements

- Current observations only; historical coverage depends on successful scheduled runs.
- No cloud deployment yet.
- No orchestration platform such as Airflow.
- No automated alerting or monitoring dashboard.
- SQL Server connection settings need to be configured for each environment.
- Test coverage is still developing, particularly for real database integration and idempotent loading.
- Further improvements could include stronger schema validation, retry policies, integration tests, cloud storage, and automated deployment.

## Data Source

Weather observations are retrieved from the [Open-Meteo API](https://open-meteo.com/).

## Project Goal

The goal is to demonstrate practical data engineering skills: API ingestion, raw-data persistence, relational loading, SQL analytics, data-quality checks, logging, testing, and local scheduling.
