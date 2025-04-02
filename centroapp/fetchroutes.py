import requests
#import mysql.connector
from flask import jsonify, request


API_KEY = "PUZXP7CxWkPaWnvDWdacgiS4M"
base_URL = "https://bus-time.centro.org/bustime/api/v3/"

"""def get_db_connection():
  return mysql.connector.connect(
    host="pi.cs.oswego.edu",
    user="CSC380_25S_TeamA",
    password="csc380_25s",
    database="CSC380_25S_TeamA"
  )
"""
def fetch_route_data():
  endpoint = "getroutes"
  params = { "key": API_KEY,
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
    
#def fetch_route_patterns():

"""def store_routes_in_db(routes_data):
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = 
    INSERT INTO Routes (RouteID, RouteName)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE RouteName=VALUES(RouteName);
    

    for route in routes_data:
      cursor.execute(sql, (route["route"], route["rtname"]))

    conn.commit()
    cursor.close()
    conn.close()
"""

def register_routedata(app):
  @app.route("/routes", methods=['GET'])
  def fetch_rtdata():
    result = fetch_route_data()
    return jsonify(result)
