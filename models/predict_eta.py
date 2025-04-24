# predict_eta.py
import joblib
import pandas as pd
import numpy as np
from flask import request, jsonify
from geopy.distance import geodesic
from datetime import datetime, timedelta
from sqlalchemy import func
from centroapp.DBconnector import get_db_session
from centroapp.models import Stop, HistoricalBusData

model = joblib.load("eta_predictor.pkl")

features = [
    'Latitude', 'Longitude', 'Speed',
    'stop_lat', 'stop_lon', 'distance_to_stop',
    'hour_sin', 'hour_cos', 'weekday_sin', 'weekday_cos',
    'is_weekend'
]

def register_eta_prediction(app):
    @app.route("/predict_eta", methods=["GET"])
    def predict_eta():
        session = get_db_session()
        try:
            route_id = request.args.get("route_id")
            stop_id = request.args.get("stop_id")
            date_str = request.args.get("date")
            time_str = request.args.get("time")

            if not all([route_id, stop_id, date_str, time_str]):
                return jsonify({"error": "Missing required parameters"}), 400

            target_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            hour, weekday = target_dt.hour, target_dt.weekday()
            is_weekend = 1 if weekday >= 5 else 0
            mysql_weekday = weekday + 1

            stop = session.query(Stop).filter_by(route_id=route_id, stop_id=stop_id).first()
            if not stop:
                return jsonify({"error": "Stop not found for this route"}), 404

            stop_lat, stop_lon = float(stop.latitude), float(stop.longitude)

            historical_buses = []
            for window_size in range(1, 4):
                hour_start = max(0, hour - window_size)
                hour_end = min(23, hour + window_size)
                historical_buses = session.query(
                    HistoricalBusData.Latitude,
                    HistoricalBusData.Longitude,
                    HistoricalBusData.Speed
                ).filter(
                    HistoricalBusData.RouteID == route_id,
                    HistoricalBusData.Speed > 0,
                    HistoricalBusData.Speed < 100,
                    func.hour(HistoricalBusData.Timestamp).between(hour_start, hour_end),
                    func.dayofweek(HistoricalBusData.Timestamp) == mysql_weekday
                ).order_by(func.rand()).limit(10).all()
                if historical_buses:
                    break

            if not historical_buses:
                return jsonify({"error": "Not enough historical data"}), 404

            def trimmed_avg(values, trim=0.1):
                values = sorted(values)
                k = int(len(values) * trim)
                trimmed = values[k:len(values)-k] if len(values) > 2 * k else values
                return sum(trimmed) / len(trimmed) if trimmed else sum(values) / len(values)

            avg_lat = trimmed_avg([float(b.Latitude) for b in historical_buses])
            avg_lon = trimmed_avg([float(b.Longitude) for b in historical_buses])
            avg_speed = trimmed_avg([float(b.Speed) for b in historical_buses])
            distance = geodesic((avg_lat, avg_lon), (stop_lat, stop_lon)).meters

            input_data = pd.DataFrame([{
                'Latitude': avg_lat,
                'Longitude': avg_lon,
                'Speed': avg_speed,
                'stop_lat': stop_lat,
                'stop_lon': stop_lon,
                'distance_to_stop': distance,
                'hour_sin': np.sin(2 * np.pi * hour / 24),
                'hour_cos': np.cos(2 * np.pi * hour / 24),
                'weekday_sin': np.sin(2 * np.pi * weekday / 7),
                'weekday_cos': np.cos(2 * np.pi * weekday / 7),
                'is_weekend': is_weekend
            }])

            eta_seconds = float(model.predict(input_data[features])[0])
            buffer_seconds = max(30, min(300, abs(eta_seconds * 0.1)))
            earliest = (target_dt + timedelta(seconds=eta_seconds - buffer_seconds)).strftime("%H:%M")
            latest = (target_dt + timedelta(seconds=eta_seconds + buffer_seconds)).strftime("%H:%M")
            return jsonify({
                "route_id": route_id,
                "stop_id": stop_id,
                "requested_time": target_dt.strftime("%Y-%m-%d %H:%M"),
                "predicted_arrival_window": f"{earliest} to {latest}"
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            session.close()
