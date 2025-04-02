import requests
from flask import Flask, jsonify
from .fetchbuses import *
#from .fetchroutes import *

#API_KEY = "PUZXP7CxWkPaWnvDWdacgiS4M"
#BASE_BUS_API = "https://bus-time.centro.org/bustime/api/v3/"
WEATHER_API = "https://api.open-meteo.com/v1/forecast"


def get_weather(lat,lon):
    params = {
        'latitude': lat,
        'longitude': lon,
        "current": "temperature_2m,precipitation,wind_speed_10m",
        "timezone": "America/New_York"
    }
    response = requests.get(WEATHER_API, params=params)

    if response.status_code == 200:
        data = response.json()
        return data.get("current", {})
    return {}

def register_weather(app):
    @app.route('/routes/<route_id>/vehicles/weather', methods=['GET'])
    def vehicle_with_weather(route_id):
        buses = fetch_realtime_data(route=route_id) #import from fetchbuses
        
        result=[]

        for bus in buses:
            bus_data={
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

        result.append(bus_data)
        return jsonify(result)

   
