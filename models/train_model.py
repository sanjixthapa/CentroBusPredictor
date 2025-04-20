#train_model.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

#load the training dataset
df = pd.read_csv("training_data.csv")

features = [
    'Latitude', 'Longitude', 'Speed',
    'Temperature', 'Precipitation', 'WindSpeed',
    'stop_lat', 'stop_lon'
]

target = 'ETA_seconds'

df = df.dropna(subset=features + [target])

from geopy.distance import geodesic
df['distance_to_stop'] = df.apply(
    lambda row: geodesic((row['Latitude'], row['Longitude']), (row['stop_lat'], row['stop_lon'])).meters,
    axis=1
)

features.append('distance_to_stop')

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Model trained — MAE: {mae:.2f} sec | R²: {r2:.2f}")

joblib.dump(model, "eta_predictor.pkl")
print("Model saved to eta_predictor.pkl")
