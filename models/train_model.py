
# train_model.py
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

print("Loading training data...")
df = pd.read_csv("training_data.csv")

required = [
    'Latitude', 'Longitude', 'Speed',
    'stop_lat', 'stop_lon', 'distance_to_stop',
    'hour_of_day', 'day_of_week', 'is_weekend',
    'ETA_seconds'
]
df.dropna(subset=required, inplace=True)

# Time encodings
df['hour_sin'] = np.sin(2 * np.pi * df['hour_of_day'] / 24)
df['hour_cos'] = np.cos(2 * np.pi * df['hour_of_day'] / 24)
df['weekday_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
df['weekday_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)

features = [
    'Latitude', 'Longitude', 'Speed',
    'stop_lat', 'stop_lon', 'distance_to_stop',
    'hour_sin', 'hour_cos', 'weekday_sin', 'weekday_cos',
    'is_weekend'
]
target = 'ETA_seconds'

X = df[features]
y = df[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\nModel evaluation:")
print(f"MAE: {mae:.2f} seconds")
print(f"R² Score: {r2:.4f}")

joblib.dump(model, "eta_predictor.pkl")
