# predict_eta.py (final version with live + ML fallback)
import os
import joblib
import pandas as pd
import numpy as np
import requests
from flask import request, jsonify
from geopy.distance import geodesic
from datetime import datetime, timedelta
from sqlalchemy import func
from centroapp.DBconnector import get_db_session
from centroapp.models import Stop, HistoricalBusData

# Load trained model
model_path = os.path.join(os.path.dirname(__file__), "../models/eta_predictor.pkl")
model = joblib.load(model_path)

# Feature list for model
features = [
    'Latitude', 'Longitude', 'Speed',
    'stop_lat', 'stop_lon', 'distance_to_stop',
    'hour_sin', 'hour_cos', 'weekday_sin', 'weekday_cos',
    'is_weekend'
]

# Fetch Centro live predictions
API_KEY = "PUZXP7CxWkPaWnvDWdacgiS4M"
BASE_URL = "https://bus-time.centro.org/bustime/api/v3/"

def fetch_predictions(stop_ids, route_ids=None, top=1):
    params = {
        "key": API_KEY,
        "stpid": ",".join(stop_ids),
        "format": "json",
        "top": top
    }
    if route_ids:
        params["rt"] = ",".join(route_ids)

    response = requests.get(BASE_URL + "getpredictions", params=params)
    if response.status_code != 200:
        return []

    data = response.json()
    return data.get("bustime-response", {}).get("prd", [])

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

            now = datetime.now()

            stop = session.query(Stop).filter_by(route_id=route_id, stop_id=stop_id).first()
            if not stop:
                return jsonify({"error": "Stop not found for this route"}), 404

            stop_lat, stop_lon = float(stop.latitude), float(stop.longitude)

            # Check if request is close enough for live predictions (within 1 hour)
            if abs((target_dt - now).total_seconds()) < 3600:
                centro_predictions = fetch_predictions([stop_id], [route_id])

                if centro_predictions:
                    nearest_prediction = min(centro_predictions, key=lambda p: p.get('countdown', float('inf')))
                    countdown_min = nearest_prediction.get('countdown')
                    if countdown_min is not None:
                        arrival_time = now + timedelta(minutes=countdown_min)
                        window_early = (arrival_time - timedelta(minutes=1)).strftime("%H:%M")
                        window_late = (arrival_time + timedelta(minutes=1)).strftime("%H:%M")

                        return jsonify({
                            "route_id": route_id,
                            "stop_id": stop_id,
                            "requested_time": target_dt.strftime("%Y-%m-%d %H:%M"),
                            "predicted_arrival_window": f"{window_early} to {window_late}",
                            "source": "live centro prediction"
                        })

            # Fall back to historical ML model
            historical_buses = []
            mysql_weekday = weekday + 1
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
                "predicted_arrival_window": f"{earliest} to {latest}",
                "source": "historical model prediction"
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            session.close()
