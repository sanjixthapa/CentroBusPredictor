# train_model.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import numpy as np

# Load the training dataset
print("Loading training data...")
df = pd.read_csv("training_data.csv")

# Define features - we're using distance_to_stop directly from the dataset now
features = [
    'Latitude', 'Longitude', 'Speed',
    'Temperature', 'Precipitation', 'WindSpeed',
    'stop_lat', 'stop_lon', 'distance_to_stop'
]

# Additional features that might improve the model
if 'hour_of_day' in df.columns:
    features.append('hour_of_day')
if 'day_of_week' in df.columns:
    features.append('day_of_week')
if 'is_weekend' in df.columns:
    features.append('is_weekend')

target = 'ETA_seconds'

print(f"Original dataset size: {len(df)}")
df = df.dropna(subset=features + [target])
print(f"Dataset size after dropping NA: {len(df)}")

# Filter outliers if needed
# df = df[(df[target] > 0) & (df[target] < 3600)]  # Reasonable ETA range

# Prepare data for training
X = df[features]
y = df[target]

print(f"Features used for training: {features}")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training model...")
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1  # Use all CPU cores for faster training
)
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Model evaluation:")
print(f"Mean Absolute Error: {mae:.2f} seconds")
print(f"R² Score: {r2:.4f}")

# Feature importance
feature_importance = pd.DataFrame({
    'Feature': features,
    'Importance': model.feature_importances_
}).sort_values('Importance', ascending=False)

print("\nFeature importance:")
for i, row in feature_importance.iterrows():
    print(f"{row['Feature']}: {row['Importance']:.4f}")

# Save the model
print("Saving model to eta_predictor.pkl")
joblib.dump(model, "eta_predictor.pkl")
