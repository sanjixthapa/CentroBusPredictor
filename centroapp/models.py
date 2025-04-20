#models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Route(Base):
    __tablename__ = 'Routes'

    RouteID = Column(String(100), primary_key=True)
    Route = Column(String(100), nullable=False)

    # Relationships
    real_time_buses = relationship("RealTimeBusData", back_populates="route")
    historical_buses = relationship("HistoricalBusData", back_populates="route")
    stops = relationship("Stop", back_populates="route")

    def __repr__(self):
        return f"<Route(RouteID='{self.RouteID}', Route='{self.Route}')>"


class RealTimeBusData(Base):
    __tablename__ = 'RealTimeBusData'

    ID = Column(Integer, primary_key=True, autoincrement=True)
    BusID = Column(Integer)
    RouteID = Column(String(100), ForeignKey('Routes.RouteID', ondelete='CASCADE', onupdate='CASCADE'))
    Latitude = Column(DECIMAL(9, 6))
    Longitude = Column(DECIMAL(9, 6))
    Speed = Column(DECIMAL(5, 2))
    Timestamp = Column(DateTime, default=func.now())

    # Relationship
    route = relationship("Route", back_populates="real_time_buses")

    def __repr__(self):
        return f"<RealTimeBusData(BusID={self.BusID}, RouteID='{self.RouteID}', Lat={self.Latitude}, Lon={self.Longitude})>"


class HistoricalBusData(Base):
    __tablename__ = 'HistoricalBusData'

    ID = Column(Integer, primary_key=True, autoincrement=True)
    BusID = Column(Integer, index=True)
    RouteID = Column(String(100), ForeignKey('Routes.RouteID', ondelete='SET NULL', onupdate='CASCADE'), index=True)
    Latitude = Column(DECIMAL(9, 6))
    Longitude = Column(DECIMAL(9, 6))
    Speed = Column(DECIMAL(5, 2))
    Timestamp = Column(DateTime)

    # Relationship
    route = relationship("Route", back_populates="historical_buses")

    def __repr__(self):
        return f"<HistoricalBusData(ID={self.ID}, BusID={self.BusID}, RouteID='{self.RouteID}')>"


class WeatherData(Base):
    __tablename__ = 'WeatherData'

    ID = Column(Integer, primary_key=True, autoincrement=True)
    RouteID = Column(String(100), ForeignKey('Routes.RouteID'))
    BusID = Column(Integer, ForeignKey('RealTimeBusData.BusID'))
    Timestamp = Column(DateTime, default=func.now())
    Temperature = Column(Float(precision=5, decimal_return_scale=2))
    Precipitation = Column(Float(precision=5, decimal_return_scale=2))
    WindSpeed = Column(Float(precision=5, decimal_return_scale=2))
    # Relationships
    route = relationship("Route")
    bus = relationship("RealTimeBusData", foreign_keys=[BusID])


    def __repr__(self):
        return (f"<WeatherData(ID={self.ID}, RouteID={self.RouteID}, BusID={self.BusID},"
                f"Timestamp={self.Timestamp}, Temperature={self.Temperature}, "
                f"Precipitation={self.Precipitation}, WindSpeed={self.WindSpeed})>")


class Stop(Base):
    __tablename__ = 'Stops'

    id = Column(Integer, primary_key=True, autoincrement=True)
    stop_id = Column(String(20))
    route_id = Column(String(10), ForeignKey('Routes.RouteID', ondelete='SET NULL', onupdate='CASCADE'), index=True)
    stop_name = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    direction = Column(String(50))
    

    # Relationship
    route = relationship("Route", back_populates="stops")

    def __repr__(self):
        return f"<Stop(stop_id='{self.stop_id}', route_id='{self.route_id}', stop_name='{self.stop_name}')>"