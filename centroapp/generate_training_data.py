#generate_training_data.py
import pandas as pd
from datetime import timedelta
from geopy.distance import geodesic
from DBconnector import get_db_session
from .models import HistoricalBusData, WeatherData, Stop

session = get_db_session()

#data from tables
bus_data = pd.read_sql(session.query(HistoricalBusData).statement, session.bind)
weather_data = pd.read_sql(session.query(WeatherData).statement, session.bind)
stops = pd.read_sql(session.query(Stop).statement, session.bind)

session.close()

#timestamps to datetime
bus_data['Timestamp'] = pd.to_datetime(bus_data['Timestamp'])
weather_data['Timestamp'] = pd.to_datetime(weather_data['Timestamp'])

#weather to each bus row
def get_nearest_weather(row):
    df = weather_data[(weather_data['BusID'] == row['BusID']) &
                      (weather_data['Timestamp'] - row['Timestamp']).abs() <= timedelta(minutes=5)]
    if not df.empty:
        return df.loc[df['Timestamp'].sub(row['Timestamp']).abs().idxmin()]
    return pd.Series()

weather_features = bus_data.apply(get_nearest_weather, axis=1)
combined_data = pd.concat([bus_data.reset_index(drop=True), weather_features.reset_index(drop=True)], axis=1)

#nearest stop for each bus row
def get_nearest_stop(row):
    route_stops = stops[stops['route_id'] == row['RouteID']]
    row_coord = (row['Latitude'], row['Longitude'])
    min_dist = float('inf')
    nearest = None
    for _, stop in route_stops.iterrows():
        stop_coord = (stop['latitude'], stop['longitude'])
        dist = geodesic(row_coord, stop_coord).meters
        if dist < min_dist:
            min_dist = dist
            nearest = stop
    return pd.Series({
        'stop_lat': nearest['latitude'],
        'stop_lon': nearest['longitude'],
        'stop_id': nearest['stop_id']
    }) if nearest is not None else pd.Series()

stop_features = bus_data.apply(get_nearest_stop, axis=1)
combined_data = pd.concat([combined_data, stop_features], axis=1)

# ETA to nearest stop
def calculate_eta(row):
    future_points = bus_data[(bus_data['BusID'] == row['BusID']) &
                              (bus_data['RouteID'] == row['RouteID']) &
                              (bus_data['Timestamp'] > row['Timestamp'])]

    for _, future in future_points.iterrows():
        if geodesic((future['Latitude'], future['Longitude']), (row['stop_lat'], row['stop_lon'])).meters < 50:
            return (future['Timestamp'] - row['Timestamp']).total_seconds()

    return None

combined_data['ETA_seconds'] = combined_data.apply(calculate_eta, axis=1)

#export
final_dataset = combined_data.dropna(subset=['ETA_seconds'])
final_dataset.to_csv("training_data.csv", index=False)

print("Training data saved to training_data.csv")
