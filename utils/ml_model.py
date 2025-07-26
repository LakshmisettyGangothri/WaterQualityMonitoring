import pandas as pd
import joblib
import os

# Load the trained model
def load_model():
    return joblib.load("models/model.pkl")

# Make a prediction and return confidence
def make_prediction(model, input_data):
    df = pd.DataFrame([input_data])
    prediction = model.predict(df)[0]
    confidence = max(model.predict_proba(df)[0]) * 100
    return prediction, confidence

# Analyze parameters for safety
def get_parameter_analysis(sample_data):
    safe_ranges = {
        'pH': (6.5, 8.5),
        'Solids': (0, 10000),
        'Sulfate': (0, 400),
        'Organic_carbon': (0, 20),
        'Turbidity': (0, 5),
        'Hardness': (0, 300),
        'Chloramines': (0, 2.5),
        'Conductivity': (0, 800),
        'Trihalomethanes': (0, 100)
    }

    analysis = []
    for param, value in sample_data.items():
        if param in safe_ranges:
            min_val, max_val = safe_ranges[param]
            status = "Safe ✅" if min_val <= value <= max_val else "Unsafe ⚠️"
            analysis.append({
                'Parameter': param,
                'Value': value,
                'Safe Range': f"{min_val}-{max_val}",
                'Status': status
            })

    return pd.DataFrame(analysis)

# Generate suggestions if parameters are unsafe
def generate_precautions(sample_data):
    suggestions = []
    if sample_data['pH'] < 6.5 or sample_data['pH'] > 8.5:
        suggestions.append("Maintain pH between 6.5 and 8.5.")
    if sample_data['Turbidity'] > 5:
        suggestions.append("Reduce turbidity using filtration methods.")
    if sample_data['Chloramines'] > 2.5:
        suggestions.append("Check for excess chlorination.")
    if sample_data['Sulfate'] > 400:
        suggestions.append("High sulfate levels can cause taste issues.")
    return suggestions
