import requests
import mysql.connector
from flask import jsonify, request


API_KEY = "PUZXP7CxWkPaWnvDWdacgiS4M"
base_URL = "https://bus-time.centro.org/bustime/api/v3/"

def fetch_route_data():
  endpoint = "getroutes"
  params = { "key": API_KEY,
            "format": "json"}
  
  response = requests.get(base_URL + endpoint, params=params)

  if response.status_code == 200:
    data = response.json()
    routes = data.get("bustime-response", {}).get("routes", [])

    struct_data = [
      {
        "route": route["rt"],
        "rtname": route["rtnm"]
      }
      for route in routes
    ]
    return struct_data
  else:
    return {"error": f"could not fetch any routes. status {response.status_code}"}
    
#def fetch_route_patterns():

def register_routedata(app):
  @app.route("/routes", methods=['GET'])
  def fetch_rtdata():
    result = fetch_route_data()
    return jsonify(result)
