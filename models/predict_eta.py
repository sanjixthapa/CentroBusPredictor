import joblib
import pandas as pd
from flask import request, jsonify
from geopy.distance import geodesic
from datetime import datetime, timedelta
from sqlalchemy import func
from centroapp.DBconnector import get_db_session
from centroapp.models import Route, Stop, RealTimeBusData, HistoricalBusData

# Load the trained model
model = joblib.load("eta_predictor.pkl")

# Feature list exactly matching the training script
features = [
    'Latitude', 'Longitude', 'Speed',
    'stop_lat', 'stop_lon', 'distance_to_stop',
    'hour_of_day', 'day_of_week', 'is_weekend'
]

def register_eta_prediction(app):
    @app.route("/predict_eta_future", methods=["GET"])
    def predict_eta_future():
        session = get_db_session()

        try:
            # Parse input
            route_id = request.args.get("route_id")
            stop_id = request.args.get("stop_id")
            date_str = request.args.get("date")
            time_str = request.args.get("time")

            if not all([route_id, stop_id, date_str, time_str]):
                return jsonify({"error": "Missing required parameters"}), 400

            # Parse datetime
            try:
                target_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            except ValueError:
                return jsonify({"error": "Invalid date or time format"}), 400

            hour = target_dt.hour
            weekday = target_dt.weekday()
            is_weekend = 1 if weekday >= 5 else 0
            mysql_weekday = weekday + 1

            # Get stop info
            stop = session.query(Stop).filter_by(route_id=route_id, stop_id=stop_id).first()
            if not stop:
                return jsonify({"error": "Stop not found for this route"}), 404

            stop_lat, stop_lon = float(stop.latitude), float(stop.longitude)

            # Try fetching historical data — expand time window if needed
            historical_buses = []
            for window_size in range(1, 4):  # Try ±1, ±2, ±3 hours
                hour_start = max(0, hour - window_size)
                hour_end = min(23, hour + window_size)

                historical_buses = session.query(
                    HistoricalBusData.Latitude,
                    HistoricalBusData.Longitude,
                    HistoricalBusData.Speed
                ).filter(
                    HistoricalBusData.RouteID == route_id,
                    HistoricalBusData.Speed > 0,
                    HistoricalBusData.Speed < 100,  # skip implausible values
                    func.hour(HistoricalBusData.Timestamp).between(hour_start, hour_end),
                    func.dayofweek(HistoricalBusData.Timestamp) == mysql_weekday
                ).order_by(func.rand()).limit(10).all()

                if historical_buses:
                    break

            if not historical_buses:
                return jsonify({"error": "Not enough historical data"}), 404

            # Compute trimmed average (to avoid outliers)
            def trimmed_avg(values, trim_percent=0.1):
                sorted_vals = sorted(values)
                k = int(len(sorted_vals) * trim_percent)
                trimmed = sorted_vals[k: len(sorted_vals) - k]
                return sum(trimmed) / len(trimmed) if trimmed else sum(sorted_vals) / len(sorted_vals)

            latitudes = [float(b.Latitude) for b in historical_buses]
            longitudes = [float(b.Longitude) for b in historical_buses]
            speeds = [float(b.Speed) for b in historical_buses]

            avg_lat = trimmed_avg(latitudes)
            avg_lon = trimmed_avg(longitudes)
            avg_speed = trimmed_avg(speeds)

            distance = geodesic((avg_lat, avg_lon), (stop_lat, stop_lon)).meters

            input_data = pd.DataFrame([{
                'Latitude': avg_lat,
                'Longitude': avg_lon,
                'Speed': avg_speed,
                'stop_lat': stop_lat,
                'stop_lon': stop_lon,
                'distance_to_stop': distance,
                'hour_of_day': hour,
                'day_of_week': weekday,
                'is_weekend': is_weekend
            }])

            # Ensure all features are present
            if not all(col in input_data.columns for col in features):
                return jsonify({"error": f"Missing required features in model input"}), 500

            eta_seconds = model.predict(input_data[features])[0]
            # Round ETA to nearest 30 seconds
            buffer_seconds = max(30, min(300, abs(eta_seconds * 0.1)))  # 10% buffer, capped at 5 mins

            # Create a time window
            earliest = (target_dt + timedelta(seconds=eta_seconds - buffer_seconds)).strftime("%H:%M")
            latest = (target_dt + timedelta(seconds=eta_seconds + buffer_seconds)).strftime("%H:%M")
            arrival_window = f"{earliest} to {latest}"

            return jsonify({
                "route_id": route_id,
                "stop_id": stop_id,
                "requested_time": target_dt.strftime("%Y-%m-%d %H:%M"),
                "predicted_arrival_window": arrival_window
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            session.close()
