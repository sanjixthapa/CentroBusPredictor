# CentroBusPredictor
CSC 380 Team A Project

Centro (https://www.centro.org/) is the public bus system operating in Central New York State.
They provide service to Syracuse, Oswego, and other surrounding cities. Busses that operate on the various routes carry tracking devices, and this data can be connected through the Centro API using an appropriate key.
Objective
The objective of this project is to design and implement a bus prediction system based on data collected from buses running along the various routes. The data would be stored on a local database (e.g., MySQL running on pi.cs.oswego.edu) and then could be analyzed and searched by an external application. It would give users the ability to determine the accuracy of the schedules.
Key Features & Challenges
The application should have the following features:
• Poll the Centro API periodically for specific routes, while respecting the data limits imposed when using the API key
• Determine an appropriate schema for the data
• Consider adding additional data, like temperature, precipitation, etc.
• A web interface that permits searching and filtering of routes, dates, etc.
Challenges to overcome.
• Working with structured data, JSON, MySQL
• Data analysis
• Web interface design
