import joblib
from flask import request, jsonify
from geopy.distance import geodesic
from datetime import datetime
from centroapp.DBconnector import get_db_session
from centroapp.models import Stop

# Load the trained ETA model
model = joblib.load("eta_predictor.pkl")

# Feature list used during training (weather removed)
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
            route_id = request.args.get("route_id")
            stop_id = request.args.get("stop_id")
            date_str = request.args.get("date")   # Format: YYYY-MM-DD
            time_str = request.args.get("time")   # Format: HH:MM
            bus_lat = float(request.args.get("bus_lat"))
            bus_lon = float(request.args.get("bus_lon"))
            speed = float(request.args.get("speed"))

            # Parse datetime from input
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

            # Get stop location
            stop = session.query(Stop).filter_by(stop_id=stop_id).first()
            if not stop:
                return jsonify({"error": "Stop not found"}), 404

            stop_lat = stop.latitude
            stop_lon = stop.longitude

            # Compute distance between bus and stop
            distance = geodesic((bus_lat, bus_lon), (stop_lat, stop_lon)).meters

            # Temporal features
            hour = dt.hour
            weekday = dt.weekday()
            is_weekend = int(weekday >= 5)

            # Assemble feature vector
            feature_vec = [
                bus_lat, bus_lon, speed,
                stop_lat, stop_lon, distance,
                hour, weekday, is_weekend
            ]

            # Predict ETA
            eta_seconds = model.predict([feature_vec])[0]

            return jsonify({
                "route_id": route_id,
                "stop_id": stop_id,
                "ETA_seconds": round(float(eta_seconds), 2)
            })

        finally:
            session.close()
