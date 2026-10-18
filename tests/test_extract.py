
import pytest

from src import extract


def test_partial_failure_stops_collection(monkeypatch):
    calls = []

    def fake_fetch(city, latitude, longitude):
        calls.append(city)

        if city == "Delhi":
            raise extract.requests.HTTPError("503 Service Unavailable")

        return {
            "city": city,
            "latitude": latitude,
            "longitude": longitude,
            "weather": {"current": {}},
        }

    monkeypatch.setattr(extract, "fetch_weather", fake_fetch)
    monkeypatch.setattr(extract, "validate_weather", lambda record: True)

    with pytest.raises(RuntimeError, match="Extraction incomplete"):
        extract.collect_weather()

    assert len(calls) == len(extract.CITIES)
    