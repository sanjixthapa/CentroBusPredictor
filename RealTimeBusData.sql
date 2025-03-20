CREATE TABLE RealTimeBusData (
    BusID INT PRIMARY KEY AUTO_INCREMENT,
    RouteID INT,
    Latitude DECIMAL(9,6),
    Longitude DECIMAL(9,6),
    Speed DECIMAL(5,2),  -- Optional: Track speed for better predictions
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (RouteID) REFERENCES Routes(RouteID)
);
