#fetchroutes.py

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

def fetch_routes_from_db(): #getting routes from db now
    session = get_db_session()
    try:
        query = session.query(Route)
        routes = query.all()
        return [
            {
                "route": rt.RouteID,
                "rtname": rt.Route
                
            } for rt in routes
        ]
    except Exception as e:
        session.rollback()
        print(f"could not get routes from db {e}")
    finally:
        session.close()
        
def register_routedata(app):
    @app.route("/routes/db", methods=['GET'])
    def fetch_rtdata():
        result = fetch_routes_from_db()
        # Store routes in database
        #if isinstance(result, list):
        #    store_routes_in_db(result)
        return jsonify(result)