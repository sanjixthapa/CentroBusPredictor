import pandas as pd
from datetime import datetime
from geopy.distance import geodesic
from centroapp.DBconnector import get_db_session
from centroapp.models import HistoricalBusData, Stop


def generate_training_data():
    session = get_db_session()
    training_rows = []

    try:
        bus_data = session.query(HistoricalBusData).all()
        stops_data = session.query(Stop).all()

        # Map stops by route
        stops_by_route = {}
        for stop in stops_data:
            if stop.route_id not in stops_by_route:
                stops_by_route[stop.route_id] = []
            stops_by_route[stop.route_id].append(stop)

        print(f"Processing {len(bus_data)} bus records...")
        processed = 0

        for bus in bus_data:
            processed += 1
            if processed % 1000 == 0:
                print(f"Processed {processed}/{len(bus_data)} records...")

            if not bus.RouteID or not bus.Latitude or not bus.Longitude or not bus.Speed:
                continue

            stops = stops_by_route.get(bus.RouteID, [])
            if not stops:
                continue

            try:
                bus_lat = float(bus.Latitude)
                bus_lon = float(bus.Longitude)
                speed = float(bus.Speed)
                if speed <= 0:
                    continue
            except (ValueError, TypeError):
                continue

            try:
                nearest_stop = min(
                    stops,
                    key=lambda stop: geodesic((bus_lat, bus_lon), (stop.latitude, stop.longitude)).meters
                )
                distance = geodesic((bus_lat, bus_lon), (nearest_stop.latitude, nearest_stop.longitude)).meters
                eta_seconds = distance / (speed * 0.277778)  # Convert km/h to m/s
            except Exception:
                continue

            bus_timestamp = bus.Timestamp
            if not bus_timestamp or eta_seconds > 3600:
                continue

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
                'hour_of_day': bus_timestamp.hour,
                'day_of_week': bus_timestamp.weekday(),
                'is_weekend': 1 if bus_timestamp.weekday() >= 5 else 0,
                'ETA_seconds': round(eta_seconds, 2)
            }

            training_rows.append(row)

        df = pd.DataFrame(training_rows)
        df.to_csv("training_data.csv", index=False)
        print(f"Saved {len(df)} training rows to training_data.csv")
        print(f"   Features: {', '.join(df.columns)}")

    finally:
        session.close()


if __name__ == "__main__":
    generate_training_data()
