#init.py
import datetime
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from .fetchbuses import register_routes, fetch_realtime_data
from .fetchroutes import register_routedata
from .fetchweather import register_weather
from .getstops import register_stops
from .prediction import register_predictions
from .DBconnector import init_db, get_db_session
from .models import Route, HistoricalBusData, RealTimeBusData

import atexit

def create_app():
    app = Flask(__name__)

    # Initialize database tables
    init_db()

    # Register API endpoints
    register_routes(app)
    register_routedata(app)
    register_weather(app)
    register_stops(app)
    register_predictions(app)

    # Set up the background scheduler
    scheduler = BackgroundScheduler()

    def scheduled_bus_fetch():
        session = get_db_session()
        try:
            # Safely get all route IDs as strings
            route_ids = [r.RouteID for r in session.query(Route).all()]
        except Exception as e:
            print(f"Error accessing routes for scheduled fetch: {e}")
            return
        finally:
            session.close()

        for route_id in route_ids:
            try:
                result = fetch_realtime_data(route=route_id)
                print(f"Fetched {len(result) if isinstance(result, list) else 0} buses for route {route_id}")
            except Exception as e:
                print(f"Error during scheduled fetch for route {route_id}: {e}")

    # Schedule the job to run every 2 minutesx
    scheduler.add_job(scheduled_bus_fetch, 'interval', minutes=1)
    scheduler.start()


    return app