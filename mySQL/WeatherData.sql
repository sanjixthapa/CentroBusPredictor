CREATE TABLE WeatherData (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    RouteID varchar(100) NOT NULL,
    BusID int NOT NULL,
    Timestamp datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Temperature decimal(5,2) DEFAULT NULL,
    Precipitation decimal(5,2) DEFAULT NULL,
    WindSpeed decimal(5,2) DEFAULT NULL,
    FOREIGN KEY (RouteID) REFERENCES Routes(RouteID),
    FOREIGN KEY (BusID) REFERENCES RealTimeBusData(BusID)
);
