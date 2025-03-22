import requests
from flask import Flask, jsonify, request


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

  
    
def fetch_route_patterns():
