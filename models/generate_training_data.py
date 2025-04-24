# generate_training_data.py
import pandas as pd
import numpy as np
from datetime import datetime
from geopy.distance import geodesic
from scipy.spatial import KDTree
from centroapp.DBconnector import get_db_session
from centroapp.models import HistoricalBusData, Stop

def generate_training_data():
    session = get_db_session()
    training_rows = []

    try:
        bus_data = session.query(HistoricalBusData).all()
        stops_data = session.query(Stop).all()

        # Build Stops DataFrame
        stops_df = pd.DataFrame([{
            'route_id': stop.route_id,
            'stop_id': stop.stop_id,
            'stop_lat': stop.latitude,
            'stop_lon': stop.longitude
        } for stop in stops_data])

        # Build a KDTree for each route
        route_stop_trees = {}
        for route_id, group in stops_df.groupby('route_id'):
            coords = group[['stop_lat', 'stop_lon']].values
            if len(coords) > 0:
                tree = KDTree(coords)
                route_stop_trees[route_id] = (tree, group)

        print(f"Built KDTree for {len(route_stop_trees)} routes.")

        for i, bus in enumerate(bus_data):
            if i % 1000 == 0:
                print(f"Processing record {i}/{len(bus_data)}...")

            if not all([bus.RouteID, bus.Latitude, bus.Longitude, bus.Speed]):
                continue

            tree_info = route_stop_trees.get(bus.RouteID)
            if not tree_info:
                continue

            bus_lat = float(bus.Latitude)
            bus_lon = float(bus.Longitude)
            speed = float(bus.Speed)
            if speed <= 0:
                continue

            tree, group = tree_info
            dist, idx = tree.query([bus_lat, bus_lon])
            nearest_stop = group.iloc[idx]

            distance = geodesic((bus_lat, bus_lon), (nearest_stop['stop_lat'], nearest_stop['stop_lon'])).meters
            eta_seconds = distance / (speed * 0.277778)  # Convert km/h to m/s

            if not bus.Timestamp or eta_seconds > 3600:
                continue

            timestamp = bus.Timestamp
            training_rows.append({
                'BusID': bus.BusID,
                'RouteID': bus.RouteID,
                'Latitude': bus_lat,
                'Longitude': bus_lon,
                'Speed': speed,
                'stop_id': nearest_stop['stop_id'],
                'stop_lat': nearest_stop['stop_lat'],
                'stop_lon': nearest_stop['stop_lon'],
                'distance_to_stop': distance,
                'hour_of_day': timestamp.hour,
                'day_of_week': timestamp.weekday(),
                'is_weekend': 1 if timestamp.weekday() >= 5 else 0,
                'ETA_seconds': round(eta_seconds, 2)
            })

        df = pd.DataFrame(training_rows)
        df.to_csv("training_data.csv", index=False)
        print(f"\n✅ Generated {len(df)} training rows.")

    finally:
        session.close()

if __name__ == "__main__":
    generate_training_data()
