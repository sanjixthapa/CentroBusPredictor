import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# Load the training dataset
print("Loading training data...")
df = pd.read_csv("training_data.csv")

# Define feature columns (no weather features)
features = [
    'Latitude', 'Longitude', 'Speed',
    'stop_lat', 'stop_lon', 'distance_to_stop'
]

# Optional temporal features
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

# Prepare data for training
X = df[features]
y = df[target]

print(f"Features used for training: {features}")

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training model...")
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1  # Use all CPU cores
)
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\nModel evaluation:")
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

# Save model
print("Saving model to eta_predictor.pkl")
joblib.dump(model, "eta_predictor.pkl")
