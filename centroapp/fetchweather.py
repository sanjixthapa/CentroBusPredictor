#fetchweather.py

import requests
from datetime import datetime
from flask import jsonify
from .fetchbuses import fetch_realtime_data
from .DBconnector import get_db_session
from .models import WeatherData, HistoricalBusData
from sqlalchemy import desc

WEATHER_API = "https://api.open-meteo.com/v1/forecast"


def get_weather(lat, lon,bus_id=None, route_id=None):
    params = {
        'latitude': lat,
        'longitude': lon,
        "current": "temperature_2m,precipitation,wind_speed_10m",
        "timezone": "America/New_York"
    }
    response = requests.get(WEATHER_API, params=params)

    if response.status_code == 200:
        data = response.json()
        weather_data = {
            "temperature_2m": data.get("current", {}).get("temperature_2m", 0),
            "precipitation": data.get("current", {}).get("precipitation", 0),
            "wind_speed_10m": data.get("current", {}).get("wind_speed_10m", 0),
            "time": data.get("current", {}).get("time"),
            "bus_id": bus_id,
            "route_id": route_id
        }
        saved_entry = save_weather_to_db(weather_data)
        if saved_entry:
            weather_data['weather_id'] = saved_entry.ID
            print(f"Successfully saved weather data with ID: {saved_entry.ID}")
        else:
            print("Failed to save weather data to database")
        return weather_data
    return {}

def save_weather_to_db(weather_data):
    """Save weather data to the database"""
    if not weather_data:
        return None

    session = get_db_session()
    try:

        print(
            f"Attempting to save weather for BusID: {weather_data.get('bus_id')}, RouteID: {weather_data.get('route_id')}")

        weather_entry = WeatherData(
            RouteID=weather_data.get("route_id"),
            BusID=weather_data.get("bus_id"),
            Temperature=float(weather_data.get("temperature_2m", 0)),
            Precipitation=float(weather_data.get("precipitation", 0)),
            WindSpeed=float(weather_data.get("wind_speed_10m", 0)),
            Timestamp=datetime.now()  # Using current time as timestamp
        )

        session.add(weather_entry)
        session.commit()
        session.refresh(weather_entry)
        return weather_entry
    except Exception as e:
        session.rollback()
        print(f"Error saving weather data: {e}")
        return None
    finally:
        session.close()

#fallback
def get_latest_buses_from_db(route_id):
    session = get_db_session()
    try:
        subquery = (
            session.query(
                HistoricalBusData.BusID,
                HistoricalBusData.Latitude,
                HistoricalBusData.Longitude,
                HistoricalBusData.Timestamp
            )
            .filter(HistoricalBusData.RouteID == route_id)
            .order_by(desc(HistoricalBusData.Timestamp))
            .limit(1)  # Customize how many recent entries you want
            .all()
        )

        return [
            {
                "bus_id": bus.BusID,
                "latitude": bus.Latitude,
                "longitude": bus.Longitude,
                "timestamp": bus.Timestamp.strftime("%Y-%m-%d %H:%M")
            }
            for bus in subquery
        ]
    except Exception as e:
        print(f"[ERROR] Failed DB fallback: {e}")
        return []
    finally:
        session.close()


def register_weather(app):
    @app.route('/routes/<route_id>/vehicles/weather', methods=['GET'])
    def vehicle_with_weather(route_id):
        buses = fetch_realtime_data(route=route_id)

        if isinstance(buses, dict) and "error" in buses:
            print(f"no running buses for {route_id}, fallback to db")
            buses = get_latest_buses_from_db(route_id)
        
        result = []  # Initialize empty list
        for bus in buses:
            bus_data = {
                "bus_id": bus.get("bus_id"),
                "route_id": route_id,
                "latitude": bus.get("latitude"),
                "longitude": bus.get("longitude"),
                "weather": None
            }

            if bus.get("latitude") and bus.get("longitude"):
                weather = get_weather(
                        lat=bus["latitude"],
                        lon=bus["longitude"],
                        bus_id=bus.get("bus_id"),  # Now passing bus_id
                        route_id = route_id  # Now passing route_id
                )

                if weather:

                    bus_data["weather"] = {
                            "temperature": weather.get("temperature_2m"),
                            "precipitation": weather.get("precipitation"),
                            "wind_speed": weather.get("wind_speed_10m"),
                            "time": weather.get("time"),
                            "weather_id": weather.get("weather_id")
                            
                        }

            result.append(bus_data)  # Append inside the loop
        return jsonify(result)