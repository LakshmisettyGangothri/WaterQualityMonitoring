import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

# Load the dataset
df = pd.read_csv("your_dataset.csv")  # Make sure this CSV exists in the project root
df.dropna(inplace=True)

# ✅ Recalculate Potability using logical conditions
def determine_potability(row):
    safe_conditions = 0
    if 6.5 <= row['pH'] <= 8.5: safe_conditions += 1
    if row['Solids'] <= 10000: safe_conditions += 1
    if row['Sulfate'] <= 400: safe_conditions += 1
    if row['Organic_carbon'] <= 20: safe_conditions += 1
    if row['Turbidity'] <= 5: safe_conditions += 1
    if row['Hardness'] <= 300: safe_conditions += 1
    if row['Chloramines'] <= 2.5: safe_conditions += 1
    if row['Conductivity'] <= 800: safe_conditions += 1
    if row['Trihalomethanes'] <= 100: safe_conditions += 1

    return int(safe_conditions >= 7)

df["Potability"] = df.apply(determine_potability, axis=1)

# Split into features and target
X = df.drop("Potability", axis=1)
y = df["Potability"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Model trained with accuracy: {accuracy:.2f}")

# Save the model
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/model.pkl")
print("✅ Model saved to models/model.pkl")
