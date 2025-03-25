CREATE TABLE Routes (
    RouteID INT PRIMARY KEY AUTO_INCREMENT,
    RouteName VARCHAR(100) NOT NULL,
    StartLocation VARCHAR(100),
    EndLocation VARCHAR(100)
);
#