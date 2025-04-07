from flask import Flask
from .fetchbuses import register_routes
from .fetchroutes import register_routedata
from .fetchweather import register_weather
from .DBconnector import init_db


# Initializes flask app and registers routes
def create_app():
    app = Flask(__name__)

    # Initialize database tables
    init_db()

    # Register API endpoints
    register_routes(app)
    register_routedata(app)
    register_weather(app)

    return app