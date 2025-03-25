import requests
#from app.DBconnector import get_db_connection
from flask import jsonify, request

API_KEY = "PUZXP7CxWkPaWnvDWdacgiS4M"
base_URL = "https://bus-time.centro.org/bustime/api/v3/"

def fetch_realtime_data(route=None, bus_id=None):
    endpoint = "getvehicles"#centro api endpt
    params = { "key": API_KEY,
              "format": "json"}
    if route and not bus_id:
        params["rt"] = route #rt filter param
    elif bus_id and not route:
        params["vid"] = bus_id #vid param  
        
    response = requests.get(base_URL + endpoint, params=params)
    
    if response.status_code == 200: #OK
        data = response.json() #response data from /getvehicles
        buses = data.get("bustime-response", {}).get("vehicle",[])  
        
        structured_data = [
            {
               "bus_id": bus["vid"],
                "route": bus["rt"],
                "latitude": bus["lat"],
                "longitude": bus["lon"],
                "speed": bus["spd"],
                "timestamp": bus["tmstmp"] 
            }
            for bus in buses
        ]
        if structured_data == []:
            return {"error": "No buses found"}
        return structured_data
    else:
        return {"error": f"failed to fetch data. Status: {response.status_code}"}
#only fetches data cant store it in db yet
def register_routes(app):
    @app.route("/buses", methods=['GET'])
    def fetch_data():
        route = request.args.get("route")
        bus_id = request.args.get("bus_id")
        result = fetch_realtime_data(route, bus_id)
        return jsonify(result)