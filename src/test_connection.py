import os
import pyodbc

SERVER = os.getenv("WEATHER_DB_SERVER")
DATABASE = os.getenv("WEATHER_DB_NAME", "WeatherDataEngineering")

if not SERVER:
    raise RuntimeError("WEATHER_DB_SERVER environment variable is not set.")

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

try:
    with pyodbc.connect(connection_string, timeout=10) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT @@SERVERNAME, DB_NAME()")
        server_name, database_name = cursor.fetchone()

        print("Connection successful!")
        print("Server:", server_name)
        print("Database:", database_name)

except pyodbc.Error as error:
    print("Connection failed:")
    print(error)
    raise