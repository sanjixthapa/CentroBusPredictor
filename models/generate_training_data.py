import pandas as pd
import math
from datetime import datetime
from centroapp.DBconnector import get_db_session
from centroapp.models import HistoricalBusData, WeatherData, Stop


def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in meters"""
    R = 6371  # km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    return R * 2 * math.asin(math.sqrt(a)) * 1000  # meters


def generate_training_data():
    session = get_db_session()
    training_rows = []

    try:
        # Load all data at once
        bus_data = session.query(HistoricalBusData).all()
        weather_data = pd.read_sql(session.query(WeatherData).statement, session.bind)
        stops_data = session.query(Stop).all()

        # Convert weather data timestamps for faster lookups
        weather_data['Timestamp'] = pd.to_datetime(weather_data['Timestamp'])

        # Map stops by route for faster lookup
        stops_by_route = {}
        for stop in stops_data:
            if stop.route_id not in stops_by_route:
                stops_by_route[stop.route_id] = []
            stops_by_route[stop.route_id].append(stop)

        print(f"Processing {len(bus_data)} bus records...")
        processed = 0

        # Process each bus record
        for bus in bus_data:
            processed += 1
            if processed % 1000 == 0:
                print(f"Processed {processed}/{len(bus_data)} records...")

            # Skip records with missing data
            if not bus.RouteID or not bus.Latitude or not bus.Longitude or not bus.Speed:
                continue

            # Find stops for this route
            stops = stops_by_route.get(bus.RouteID, [])
            if not stops:
                continue

            # Find nearest stop
            try:
                bus_lat = float(bus.Latitude)
                bus_lon = float(bus.Longitude)
            except (ValueError, TypeError):
                continue

            try:
                nearest_stop = min(
                    stops,
                    key=lambda stop: haversine(bus_lat, bus_lon, stop.latitude, stop.longitude)
                )

                distance = haversine(bus_lat, bus_lon, nearest_stop.latitude, nearest_stop.longitude)
            except (ValueError, TypeError):
                continue

            # Calculate basic ETA (distance/speed)
            try:
                speed = float(bus.Speed)
                if speed <= 0:
                    continue
                eta_seconds = distance / (speed * 0.277778)  # Convert km/h to m/s
            except (ValueError, TypeError, ZeroDivisionError):
                continue

            # Find closest weather record (within 5 minutes)
            bus_timestamp = bus.Timestamp
            if not bus_timestamp:
                continue

            # Handle weather data safely
            temperature = precipitation = wind_speed = None
            try:
                # Filter weather data for this bus
                filtered_weather = weather_data[weather_data['BusID'] == bus.BusID]

                if not filtered_weather.empty:
                    # Calculate time differences
                    bus_dt = pd.to_datetime(bus_timestamp)
                    time_diffs = abs((filtered_weather['Timestamp'] - bus_dt).dt.total_seconds())

                    # Find closest within 5 minutes (300 seconds)
                    close_weather = filtered_weather[time_diffs < 300]

                    if not close_weather.empty:
                        # Find the closest weather record by time
                        idx = time_diffs[close_weather.index].idxmin()
                        closest_weather = filtered_weather.loc[idx]

                        temperature = closest_weather['Temperature']
                        precipitation = closest_weather['Precipitation']
                        wind_speed = closest_weather['WindSpeed']
            except Exception as e:
                # Just continue without weather data if there's an error
                print(f"Weather data error at record {processed}: {e}")

            # Create row with all features
            if eta_seconds < 3600:  # Only include ETAs less than 1 hour
                row = {
                    'BusID': bus.BusID,
                    'RouteID': bus.RouteID,
                    'Latitude': bus_lat,
                    'Longitude': bus_lon,
                    'Speed': speed,
                    'stop_id': nearest_stop.stop_id,
                    'stop_lat': nearest_stop.latitude,
                    'stop_lon': nearest_stop.longitude,
                    'distance_to_stop': distance,
                    'Temperature': temperature,
                    'Precipitation': precipitation,
                    'WindSpeed': wind_speed,
                    'hour_of_day': bus_timestamp.hour,
                    'day_of_week': bus_timestamp.weekday(),
                    'is_weekend': 1 if bus_timestamp.weekday() >= 5 else 0,
                    'ETA_seconds': round(eta_seconds, 2)
                }
                training_rows.append(row)

        # Save to CSV
        df = pd.DataFrame(training_rows)
        df.to_csv("training_data.csv", index=False)
        print(f"Saved {len(df)} training rows to training_data.csv")
        print(f"   Features included: {', '.join(df.columns)}")

    finally:
        session.close()


if __name__ == "__main__":
    generate_training_data()