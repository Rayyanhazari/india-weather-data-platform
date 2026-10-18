
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

CITIES = {
    "Hyderabad": (17.3850, 78.4867),
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Chennai": (13.0827, 80.2707),
    "Bengaluru": (12.9716, 77.5946),
    "Kolkata": (22.5726, 88.3639),
}

API_URL = "https://api.open-meteo.com/v1/forecast"
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"



def fetch_weather(city, latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,relative_humidity_2m,"
            "apparent_temperature,precipitation,"
            "weather_code,wind_speed_10m"
        ),
        "timezone": "Asia/Kolkata",
    }

    for attempt in range(3):
        try:
            response = requests.get(
                API_URL,
                params=params,
                timeout=30,
            )
            response.raise_for_status()

            return {
                "city": city,
                "latitude": latitude,
                "longitude": longitude,
                "fetched_at_utc": datetime.now(
                    timezone.utc
                ).isoformat(),
                "weather": response.json(),
            }

        except requests.RequestException:
            if attempt == 2:
                raise

            wait_seconds = 2 ** attempt
            print(
                f"{city}: request failed; retrying in "
                f"{wait_seconds}s..."
            )
            time.sleep(wait_seconds)


def validate_weather(record):
    required_fields = [
        "temperature_2m",
        "relative_humidity_2m",
        "apparent_temperature",
        "precipitation",
        "weather_code",
        "wind_speed_10m",
    ]

    weather = record.get("weather", {})
    current = weather.get("current", {})

    missing = [
        field for field in required_fields
        if current.get(field) is None
    ]

    if missing:
        raise ValueError(
            f"{record.get('city')}: missing fields {missing}"
        )

    if not isinstance(current["temperature_2m"], (int, float)):
        raise ValueError("Temperature must be numeric")

    if not 0 <= current["relative_humidity_2m"] <= 100:
        raise ValueError("Humidity must be between 0 and 100")

    if current["precipitation"] < 0:
        raise ValueError("Precipitation cannot be negative")

    if current["wind_speed_10m"] < 0:
        raise ValueError("Wind speed cannot be negative")

    return True


def collect_weather():
    records = []
    failed_cities = []

    for city, (latitude, longitude) in CITIES.items():
        try:
            record = fetch_weather(city, latitude, longitude)
            validate_weather(record)
            records.append(record)
        except (requests.RequestException, ValueError) as error:
            failed_cities.append(city)
            print(f"Failed to collect valid data for {city}: {error}")

    if not records:
        raise RuntimeError("No weather records were collected.")

    if failed_cities:
        raise RuntimeError(
            f"Extraction incomplete. Failed cities: {failed_cities}"
        )

    return records




def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    records = collect_weather()

    filename = (
        "weather_"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + ".json"
    )

    output_path = RAW_DIR / filename
    output_path.write_text(
        json.dumps(records, indent=2),
        encoding="utf-8",
    )

    print(f"\nSaved {len(records)} city records to {output_path}")



if __name__ == "__main__":
    main()
