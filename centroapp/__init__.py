from flask import Flask
from .fetchbuses import register_routes
#initializes flask app and registers routes
def create_app():
    app = Flask(__name__)
    
    register_routes(app)
    return app