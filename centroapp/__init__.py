from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from .fetchbuses import register_routes, fetch_realtime_data
from .fetchroutes import register_routedata
from .fetchweather import register_weather
from .getstops import register_stops
from .DBconnector import init_db, get_db_session
from .models import Route
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

    # Set up the background scheduler
    scheduler = BackgroundScheduler()

    def scheduled_bus_fetch():
        print("Fetching bus data for all routes...")
        session = get_db_session()
        try:
            all_routes = session.query(Route).all()
            for route in all_routes:
                route_name = route.Route
                route_id = route.RouteID
                print(f"Fetching data for route: {route_name}")
                result = fetch_realtime_data(route=route_id)
                print(result)
        except Exception as e:
            print(f"Error during scheduled fetch: {e}")
        finally:
            session.close()

    # Schedule the job to run every 2 minutes
    scheduler.add_job(scheduled_bus_fetch, 'interval', minutes=2)
    scheduler.start()

    # Ensure scheduler shuts down properly when app exits
    atexit.register(lambda: scheduler.shutdown())

    return app
