CREATE TABLE WeatherData (
    WeatherID INT PRIMARY KEY AUTO_INCREMENT,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    Temperature DECIMAL(5,2),
    Precipitation DECIMAL(5,2),
    WindSpeed DECIMAL(5,2),
);
