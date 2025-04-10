from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Route(Base):
    __tablename__ = 'Routes'

    RouteID = Column(String(100), primary_key=True)
    Route = Column(String(45))

    # Relationships
    real_time_buses = relationship("RealTimeBusData", back_populates="route")
    historical_buses = relationship("HistoricalBusData", back_populates="route")

    def __repr__(self):
        return f"<Route(RouteID={self.RouteID}, Route='{self.Route}')>"


class RealTimeBusData(Base):
    __tablename__ = 'RealTimeBusData'

    BusID = Column(Integer, primary_key=True, autoincrement=True)
    RouteID = Column(Integer, ForeignKey('Routes.RouteID'))
    Latitude = Column(Float(precision=9, decimal_return_scale=6))
    Longitude = Column(Float(precision=9, decimal_return_scale=6))
    Speed = Column(Float(precision=5, decimal_return_scale=2))
    Timestamp = Column(DateTime, default=func.now())

    # Relationship
    route = relationship("Route", back_populates="real_time_buses")

    def __repr__(self):
        return f"<RealTimeBusData(BusID={self.BusID}, RouteID={self.RouteID}, Lat={self.Latitude}, Lon={self.Longitude})>"


class HistoricalBusData(Base):
    __tablename__ = 'HistoricalBusData'

    RecordID = Column(Integer, primary_key=True, autoincrement=True)
    BusID = Column(Integer, ForeignKey('RealTimeBusData.BusID'))
    RouteID = Column(Integer, ForeignKey('Routes.RouteID'))
    Latitude = Column(Float(precision=9, decimal_return_scale=6))
    Longitude = Column(Float(precision=9, decimal_return_scale=6))
    Speed = Column(Float(precision=5, decimal_return_scale=2))
    Timestamp = Column(DateTime)

    # Relationship
    route = relationship("Route", back_populates="historical_buses")

    def __repr__(self):
        return f"<HistoricalBusData(RecordID={self.RecordID}, BusID={self.BusID}, RouteID={self.RouteID})>"


class WeatherData(Base):
    __tablename__ = 'WeatherData'

    WeatherID = Column(Integer, primary_key=True, autoincrement=True)
    Timestamp = Column(DateTime, default=func.now())
    Temperature = Column(Float(precision=5, decimal_return_scale=2))
    Precipitation = Column(Float(precision=5, decimal_return_scale=2))
    WindSpeed = Column(Float(precision=5, decimal_return_scale=2))

    def __repr__(self):
        return f"<WeatherData(WeatherID={self.WeatherID}, Temp={self.Temperature}, Precip={self.Precipitation})>"
    
class Stop(Base):
    __tablename__ = 'Stops'
    stop_id = Column(String(20), primary_key=True)
    route_id = Column(String(10))
    stop_name = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    direction = Column(String(50))
    
    def __repr__(self):
        return f"<Stop(stop_id={self.stop_id}, route_id={self.route_id})>"