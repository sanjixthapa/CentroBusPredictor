#(possible)orm models for database 
class route:
    def __init__(self, route_id, route_name, route_start, route_end):
        self.route_id = route_id
        self.route_name = route_name
        self.route_start = route_start
        self.route_end = route_end

class bus: #realtime bus
    def __init__(self, bus_id, route_id, latitude, longitude, speed, timestmp):
        self.bus_id = bus_id
        self.route_id = route_id
        self.latitude = latitude
        self.longitude = longitude
        self.speed = speed
        self.timestmp = timestmp


        
          