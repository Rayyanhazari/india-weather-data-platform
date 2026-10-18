
import os

import pyodbc


SERVER = os.getenv("WEATHER_DB_SERVER")
DATABASE = os.getenv(
    "WEATHER_DB_NAME",
    "WeatherDataEngineering",
)

if not SERVER:
    raise RuntimeError(
        "WEATHER_DB_SERVER environment variable is not set."
    )

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)


def get_connection():
    return pyodbc.connect(CONNECTION_STRING, timeout=10)
