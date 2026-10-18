
import json
import logging
from pathlib import Path
from datetime import datetime
from src.db import get_connection

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"


LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(
            LOG_DIR / "pipeline.log",
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)



def load_weather():
    logger.info("Weather data loading started")
    files = sorted(RAW_DIR.glob("weather_*.json"))

    if not files:
        raise FileNotFoundError("No weather JSON files found.")

    inserted = 0
    skipped = 0

    
    with get_connection() as connection:
        cursor = connection.cursor()

        try:
            for file_path in files:
                records = json.loads(
                    file_path.read_text(encoding="utf-8")
                )

                for record in records:
                    current = record["weather"]["current"]
                    city = record["city"]

                    observation_time = datetime.fromisoformat(
                        current["time"]
                    )

                    values = (
                        city,
                        record["latitude"],
                        record["longitude"],
                        observation_time,
                        current["temperature_2m"],
                        current["apparent_temperature"],
                        current["relative_humidity_2m"],
                        current["precipitation"],
                        current["weather_code"],
                        current["wind_speed_10m"],
                    )

                    cursor.execute(
                        """
                        IF NOT EXISTS (
                            SELECT 1
                            FROM dbo.WeatherObservations
                            WHERE City = ?
                              AND ObservationTime = ?
                        )
                        BEGIN
                            INSERT INTO dbo.WeatherObservations (
                                City, Latitude, Longitude,
                                ObservationTime, TemperatureC,
                                FeelsLikeC, HumidityPercent,
                                PrecipitationMM, WeatherCode,
                                WindSpeedKmh
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        END
                        """,
                        city,
                        observation_time,
                        *values,
                    )

                    if cursor.rowcount == 1:
                        inserted += 1
                    else:
                        skipped += 1

            connection.commit()

        except Exception:
            connection.rollback()
            logger.exception(
                "Weather load failed; transaction rolled back"
            )
            raise

        logger.info(
            "Loading completed | inserted=%s | skipped=%s",
            inserted,
            skipped,
        )


    print(f"Inserted records: {inserted}")
    print(f"Skipped existing records: {skipped}")
    print(f"Log file: {LOG_DIR / 'pipeline.log'}")


if __name__ == "__main__":
    load_weather()
