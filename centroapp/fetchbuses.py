import requests
from datetime import datetime
from flask import jsonify, request
from .DBconnector import get_db_session
from .models import RealTimeBusData, Route

API_KEY = "PUZXP7CxWkPaWnvDWdacgiS4M"
base_URL = "https://bus-time.centro.org/bustime/api/v3/"


def fetch_all_routes():
    """Fetch all available routes from the Centro API"""
    endpoint = "getroutes"  # Centro API endpoint for routes
    params = {"key": API_KEY, "format": "json"}

    response = requests.get(base_URL + endpoint, params=params)

    if response.status_code == 200:
        data = response.json()
        routes = data.get("bustime-response", {}).get("routes", [])

        if not routes:
            return {"error": "No routes found"}

        route_data = []
        session = get_db_session()

        try:
            for route in routes:
                route_id = route.get("rt")
                route_name = route.get("rtnm")

                # Save or update route in database
                existing_route = session.query(Route).filter_by(RouteID=route_id).first()
                if existing_route:
                    # Update route name if it exists
                    existing_route.Route = route_name
                else:
                    # Create new route
                    new_route = Route(RouteID=route_id, Route=route_name)
                    session.add(new_route)

                route_data.append({
                    "route_id": route_id,
                    "route_name": route_name
                })

            session.commit()
            return route_data
        except Exception as e:
            session.rollback()
            return {"error": f"Failed to save routes to database: {str(e)}"}
        finally:
            session.close()
    else:
        return {"error": f"Failed to fetch routes. Status: {response.status_code}"}


def fetch_realtime_data(route=None, bus_id=None):
    """Fetch real-time bus data, optionally filtered by route or bus ID"""
    endpoint = "getvehicles"  # centro api endpt
    params = {"key": API_KEY, "format": "json"}

    if route and not bus_id:
        params["rt"] = route  # rt filter param
    elif bus_id and not route:
        params["vid"] = bus_id  # vid param

    response = requests.get(base_URL + endpoint, params=params)

    if response.status_code == 200:  # OK
        data = response.json()  # response data from /getvehicles
        buses = data.get("bustime-response", {}).get("vehicle", [])

        if not buses:
            return {"error": "No buses found"}

        bus_data = [
            {
                "bus_id": bus["vid"],
                "route": bus["rt"],  # This is the route ID (e.g. "OSW10")
                "latitude": float(bus["lat"]),
                "longitude": float(bus["lon"]),
                "speed": float(bus["spd"]),
                "timestamp": bus["tmstmp"]
            }
            for bus in buses
        ]

        # Store in database
        save_bus_data_to_db(bus_data)

        return bus_data
    else:
        return {"error": f"Failed to fetch data. Status: {response.status_code}"}


def fetch_all_buses():
    """Fetch buses for all available routes"""
    # First get all routes
    routes = fetch_all_routes()

    # Check if we got an error
    if routes and "error" in routes:
        return routes

    all_buses = []
    route_ids = [route["route_id"] for route in routes]

    for route_id in route_ids:
        route_buses = fetch_realtime_data(route=route_id)
        if route_buses and not isinstance(route_buses, dict) or "error" not in route_buses:
            all_buses.extend(route_buses)

    return all_buses


def save_bus_data_to_db(bus_data_list):
    """Save the bus data to the database"""
    session = get_db_session()
    try:
        for bus_data in bus_data_list:
            # Convert timestamp format from API to datetime
            timestamp = datetime.strptime(bus_data["timestamp"], "%Y%m%d %H:%M")

            # Get or create route - bus_data["route"] is the route ID
            route_obj = session.query(Route).filter_by(RouteID=bus_data["route"]).first()
            if not route_obj:
                # If route doesn't exist, create with ID as both RouteID and Route (temporary)
                route_obj = Route(RouteID=bus_data["route"], Route=bus_data["route"])
                session.add(route_obj)
                session.flush()

            # Create real-time bus data entry
            bus_entry = RealTimeBusData(
                BusID=int(bus_data["bus_id"]),
                RouteID=route_obj.RouteID,  # This is the route ID
                Latitude=bus_data["latitude"],
                Longitude=bus_data["longitude"],
                Speed=bus_data["speed"],
                Timestamp=timestamp
            )

            # Upsert - delete old entry if exists and insert new one
            existing = session.query(RealTimeBusData).filter_by(BusID=int(bus_data["bus_id"])).first()
            if existing:
                session.delete(existing)

            session.add(bus_entry)

        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error saving bus data: {e}")
    finally:
        session.close()


def register_routes(app):
    @app.route("/routes", methods=['GET'])
    def get_routes():
        """Get all available routes"""
        routes = fetch_all_routes()
        return jsonify(routes)

    @app.route("/buses", methods=['GET'])
    def fetch_data():
        route = request.args.get("route")
        bus_id = request.args.get("bus_id")

        # If no specific route or bus is requested, fetch all buses from all routes
        if not route and not bus_id:
            result = fetch_all_buses()
        else:
            result = fetch_realtime_data(route, bus_id)

        return jsonify(result)

    @app.route("/buses/db", methods=['GET'])
    def get_buses_from_db():
        """Get buses from database instead of API"""
        session = get_db_session()
        try:
            route = request.args.get("route")

            query = session.query(RealTimeBusData)
            if route:
                # Filter by route ID
                query = query.filter_by(RouteID=route)

            buses = query.all()

            result = [
                {
                    "bus_id": bus.BusID,
                    "route_id": bus.RouteID,  # Route ID (e.g., "OSW10")
                    "route_name": bus.route.Route if bus.route else None,  # Route name (e.g., "SUNY Oswego Blue Route")
                    "latitude": float(bus.Latitude) if bus.Latitude else None,
                    "longitude": float(bus.Longitude) if bus.Longitude else None,
                    "speed": float(bus.Speed) if bus.Speed else None,
                    "timestamp": bus.Timestamp.strftime("%Y-%m-%d %H:%M:%S") if bus.Timestamp else None
                }
                for bus in buses
            ]

            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)})
        finally:
            session.close()