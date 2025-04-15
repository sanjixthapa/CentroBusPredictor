# predictions.py

import requests
from flask import jsonify, request

API_KEY = "PUZXP7CxWkPaWnvDWdacgiS4M"
BASE_URL = "https://bus-time.centro.org/bustime/api/v3/"

# Fetch predictions from the BusTime API
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


# Flask route to expose predictions
def register_predictions(app):
    @app.route("/predictions", methods=["GET"])
    def get_predictions():
        stop_ids = request.args.getlist("stop_id")
        route_ids = request.args.getlist("route")
        top = request.args.get("top", default=1, type=int)

        if not stop_ids:
            return jsonify({"error": "Missing stop_id parameter"}), 400

        predictions = fetch_predictions(stop_ids, route_ids, top)

        # optionally store in DB
        # store_predictions(predictions)

        return jsonify([
            {
                "route": p.get("rt"),
                "destination": p.get("des"),
                "stop_name": p.get("stpnm"),
                "stop_id": p.get("stpid"),
                "vehicle_id": p.get("vid"),
                "predicted_time": p.get("prdtm"),
                "countdown": int(p.get("prdctdn", 0)),
                "delay": p.get("dly", False),

            } for p in predictions
        ])
