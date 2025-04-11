#getstops.py

import requests
from flask import jsonify, request
from .DBconnector import get_db_session
from .models import Stop

API_KEY = "PUZXP7CxWkPaWnvDWdacgiS4M"
base_URL = "https://bus-time.centro.org/bustime/api/v3/"

def fetch_directions(route_id):
    params = {
        "key": API_KEY,
        "rt": route_id,
        "format": "json"
    }
    
    response = requests.get(base_URL + "getdirections", params=params)
    if response.status_code != 200:
        return []
    
    data = response.json()
    directions = data.get("bustime-response", {}).get("directions", [])
    
    return [dir["id"] for dir in directions]
    
def fetch_and_store_stops(route_id, dir):
    #fetch stops from api given rt and dir param
    params = {
        "key": API_KEY,
        "rt": route_id,
        "dir": dir,
        "format": "json"
    }
    response = requests.get(base_URL + "getstops", params=params)
    if response.status_code != 200:
        return {"error": f"Failed to fetch stops: {response.status_code}"}
    
    data = response.json()
    stops = data.get("bustime-response", {}).get("stops", [])
    
    session = get_db_session()
    
    try:
        for stop in stops:
            stop_id = stop["stpid"]
            #check if stop exists in database
            #if not add to db
            existing_stop = session.query(Stop).filter_by(stop_id=stop_id).first()
            
            if not existing_stop:
                new_stop = Stop(
                    stop_id=stop_id,
                    route_id=route_id,
                    stop_name=stop.get("stpnm"),
                    latitude=stop.get("lat"),
                    longitude=stop.get("lon"),
                    direction=dir
                )
                session.add(new_stop)
        session.commit()
    except Exception as e:
        session.rollback()
        print("error storing stops for rtid", e)
    finally:
        session.close()
    
    return stops

def register_stops(app):
    @app.route("/stops", methods=["GET"])
    def get_stops():
        route = request.args.get("route")
        direction = request.args.get("dir")
        
        #must have params
        if not route or not direction:
            return jsonify({"error":  "missing route or dir parameter"})
        
        rt_directions = fetch_directions(route)
        if direction not in rt_directions:
            return jsonify({"error": "invalid directions"})
        #returns stops based on route, direction
        stops = fetch_and_store_stops(route, direction)
        return jsonify(stops)