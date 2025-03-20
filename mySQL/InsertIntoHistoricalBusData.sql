INSERT INTO HistoricalBusData (BusID, RouteID, Latitude, Longitude, Speed, Timestamp)
SELECT BusID, RouteID, Latitude, Longitude, Speed, Timestamp
FROM RealTimeBusData
WHERE Timestamp < NOW() - INTERVAL 1 DAY;

DELETE FROM RealTimeBusData WHERE Timestamp < NOW() - INTERVAL 1 DAY;
