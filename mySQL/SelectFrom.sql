SELECT h.RouteID, h.Latitude, h.Longitude, h.Timestamp, w.Temperature, w.Precipitation
FROM HistoricalBusData h
JOIN WeatherData w
ON DATE(h.Timestamp) = DATE(w.Timestamp)
ORDER BY h.Timestamp DESC;
