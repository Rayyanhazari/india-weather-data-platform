
import json
import pytest
from datetime import datetime
from src import load


class FakeCursor:
    def __init__(self):
        self.calls = []
        self.rowcount = 1

    def execute(self, query, *params):
        self.calls.append((query, params))
        return self


class FakeConnection:
    def __init__(self):
        self.fake_cursor = FakeCursor()
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def cursor(self):
        return self.fake_cursor

    def commit(self):
        self.committed = True


def test_load_weather_executes_insert_and_commits(monkeypatch, tmp_path):
    # Arrange: create a temporary weather JSON file.
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()

    record = {
        "city": "Hyderabad",
        "latitude": 17.385,
        "longitude": 78.4867,
        "weather": {
            "current": {
                "time": "2026-10-18T13:00",
                "temperature_2m": 32.5,
                "apparent_temperature": 35.1,
                "relative_humidity_2m": 45,
                "precipitation": 0.0,
                "weather_code": 1,
                "wind_speed_10m": 12.0,
            }
        },
    }

    (raw_dir / "weather_test.json").write_text(
        json.dumps([record]),
        encoding="utf-8",
    )

    fake_connection = FakeConnection()

    monkeypatch.setattr(load, "RAW_DIR", raw_dir)
    monkeypatch.setattr(
        load,
        "get_connection",
        lambda: fake_connection,
    )

    # Act
    load.load_weather()

    # Assert
    assert len(fake_connection.fake_cursor.calls) == 1
    assert fake_connection.committed is True

    query, params = fake_connection.fake_cursor.calls[0]

    assert "IF NOT EXISTS" in query
    assert "INSERT INTO dbo.WeatherObservations" in query
    assert params[0] == "Hyderabad"
    assert isinstance(params[1], datetime)
    assert params[2] == "Hyderabad"
    assert params[3] == 17.385

def test_load_weather_fails_when_no_files_exist(monkeypatch, tmp_path):
    # Arrange: use an empty temporary directory.
    monkeypatch.setattr(load, "RAW_DIR", tmp_path)

    # Act & Assert
    with pytest.raises(
        FileNotFoundError,
        match="No weather JSON files found",
    ):
        load.load_weather()


def test_load_weather_fails_on_malformed_json(monkeypatch, tmp_path):
    # Arrange: create a corrupted JSON file.
    bad_file = tmp_path / "weather_broken.json"
    bad_file.write_text("{invalid json", encoding="utf-8")

    monkeypatch.setattr(load, "RAW_DIR", tmp_path)

    # Act & Assert
    with pytest.raises(json.JSONDecodeError):
        load.load_weather()


def test_load_weather_does_not_commit_when_database_fails(
    monkeypatch, tmp_path
):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()

    record = {
        "city": "Hyderabad",
        "latitude": 17.385,
        "longitude": 78.4867,
        "weather": {
            "current": {
                "time": "2026-10-18T13:00",
                "temperature_2m": 32.5,
                "apparent_temperature": 35.1,
                "relative_humidity_2m": 45,
                "precipitation": 0.0,
                "weather_code": 1,
                "wind_speed_10m": 12.0,
            }
        },
    }

    (raw_dir / "weather_test.json").write_text(
        json.dumps([record]),
        encoding="utf-8",
    )

    class FailingCursor:
        def execute(self, *args, **kwargs):
            raise RuntimeError("Simulated database failure")

    
    class FailingConnection:
        def __init__(self):
            self.committed = False
            self.rolled_back = False

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def cursor(self):
            return FailingCursor()

        def commit(self):
            self.committed = True

        def rollback(self):
            self.rolled_back = True


    fake_connection = FailingConnection()

    monkeypatch.setattr(load, "RAW_DIR", raw_dir)
    monkeypatch.setattr(
        load,
        "get_connection",
        lambda: fake_connection,
    )

    with pytest.raises(RuntimeError, match="Simulated database failure"):
        load.load_weather()

    assert fake_connection.committed is False
    assert fake_connection.rolled_back is True
