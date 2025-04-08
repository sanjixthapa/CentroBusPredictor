#fetchweather.py

import requests
from flask import jsonify
from .fetchbuses import fetch_realtime_data
from .DBconnector import get_db_session
from .models import WeatherData

WEATHER_API = "https://api.open-meteo.com/v1/forecast"


def get_weather(lat, lon):
    params = {
        'latitude': lat,
        'longitude': lon,
        "current": "temperature_2m,precipitation,wind_speed_10m",
        "timezone": "America/New_York"
    }
    response = requests.get(WEATHER_API, params=params)

    if response.status_code == 200:
        data = response.json()
        weather_data = data.get("current", {})

        # Save weather data to database
        save_weather_to_db(weather_data)

        return weather_data
    return {}


def save_weather_to_db(weather_data):
    """Save weather data to the database"""
    if not weather_data:
        return

    session = get_db_session()
    try:
        weather_entry = WeatherData(
            Temperature=weather_data.get("temperature_2m"),
            Precipitation=weather_data.get("precipitation"),
            WindSpeed=weather_data.get("wind_speed_10m")
        )
        session.add(weather_entry)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error saving weather data: {e}")
    finally:
        session.close()


def register_weather(app):
    @app.route('/routes/<route_id>/vehicles/weather', methods=['GET'])
    def vehicle_with_weather(route_id):
        buses = fetch_realtime_data(route=route_id)

        if isinstance(buses, dict) and "error" in buses:
            return jsonify(buses)

        result = []  # Initialize empty list

        for bus in buses:
            bus_data = {
                "bus_id": bus.get("bus_id"),
                "latitude": bus.get("latitude"),
                "longitude": bus.get("longitude"),
                "weather": None
            }

            if bus.get("latitude") and bus.get("longitude"):
                weather = get_weather(bus["latitude"], bus["longitude"])
                if weather:
                    bus_data["weather"] = {
                        "temperature": weather.get("temperature_2m"),
                        "precipitation": weather.get("precipitation"),
                        "wind_speed": weather.get("wind_speed_10m"),
                        "time": weather.get("time")
                    }

            result.append(bus_data)  # Append inside the loop

        return jsonify(result)