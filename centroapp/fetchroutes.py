import requests
from flask import jsonify, request
from .DBconnector import get_db_session
from .models import Route

API_KEY = "PUZXP7CxWkPaWnvDWdacgiS4M"
base_URL = "https://bus-time.centro.org/bustime/api/v3/"


def fetch_route_data():
    endpoint = "getroutes"
    params = {"key": API_KEY,
              "format": "json"}

    response = requests.get(base_URL + endpoint, params=params)

    if response.status_code == 200:
        data = response.json()
        routes = data.get("bustime-response", {}).get("routes", [])

        route_data = [
            {
                "route": route["rt"],
                "rtname": route["rtnm"]
            }
            for route in routes
        ]
        return route_data
    else:
        return {"error": f"could not fetch any routes. status {response.status_code}"}


def store_routes_in_db(routes_data):
    session = get_db_session()
    try:
        for route in routes_data:
            # Use route["route"] (e.g., "OSW10") as the RouteID
            # Use route["rtname"] (e.g., "SUNY Oswego Blue Route") as the Route
            existing = session.query(Route).filter_by(RouteID=route["route"]).first()
            if not existing:
                new_route = Route(RouteID=route["route"], Route=route["rtname"])
                session.add(new_route)
            elif existing.Route != route["rtname"]:
                # Update route name if it changed
                existing.Route = route["rtname"]
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error storing routes: {e}")
    finally:
        session.close()


def register_routedata(app):
    @app.route("/routes", methods=['GET'])
    def fetch_rtdata():
        result = fetch_route_data()
        # Store routes in database
        if isinstance(result, list):
            store_routes_in_db(result)
        return jsonify(result)