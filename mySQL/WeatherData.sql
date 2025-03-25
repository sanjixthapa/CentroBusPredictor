CREATE TABLE WeatherData (
    WeatherID INT PRIMARY KEY AUTO_INCREMENT,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,  -- When data was fetched
    Temperature DECIMAL(5,2),
    Precipitation DECIMAL(5,2),
    WindSpeed DECIMAL(5,2),
    Visibility DECIMAL(5,2),
);
