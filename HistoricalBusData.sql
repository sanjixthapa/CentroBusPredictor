CREATE TABLE HistoricalBusData (
    RecordID INT PRIMARY KEY AUTO_INCREMENT,
    BusID INT,
    RouteID INT,
    Latitude DECIMAL(9,6),
    Longitude DECIMAL(9,6),
    Speed DECIMAL(5,2),
    Timestamp DATETIME,
    FOREIGN KEY (BusID) REFERENCES RealTimeBusData(BusID),
    FOREIGN KEY (RouteID) REFERENCES Routes(RouteID)
);
