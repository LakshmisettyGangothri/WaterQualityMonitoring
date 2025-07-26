import pandas as pd
import joblib
import os

# Load the trained model from file
def load_model(path="models/model.pkl"):
    """Load the trained model from disk"""
    return joblib.load(path)

# Make prediction and return (label, confidence)
def make_prediction(model, sample_dict):
    """Make prediction and return (label, confidence)"""
    import numpy as np
    import pandas as pd

    # Convert input dict to DataFrame
    X = pd.DataFrame([sample_dict])
    prediction_proba = model.predict_proba(X)[0]
    prediction = int(prediction_proba[1] >= 0.5)
    confidence = float(prediction_proba[prediction]) * 100
    return prediction, confidence

# Analyze individual parameters for safety
def get_parameter_analysis(sample_data):
    """Returns a dataframe showing which parameters are safe/unsafe"""
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
                'Safe Range': f"{min_val} - {max_val}",
                'Status': status
            })

    return pd.DataFrame(analysis)

# Generate safety suggestions if parameters are outside safe range
def generate_precautions(sample_data):
    """Returns a list of recommended actions based on unsafe values"""
    suggestions = []
    if sample_data['pH'] < 6.5 or sample_data['pH'] > 8.5:
        suggestions.append("💡 Maintain pH between 6.5 and 8.5.")
    if sample_data['Turbidity'] > 5:
        suggestions.append("💡 Reduce turbidity using filtration methods.")
    if sample_data['Chloramines'] > 2.5:
        suggestions.append("💡 Check for excess chlorination.")
    if sample_data['Sulfate'] > 400:
        suggestions.append("💡 High sulfate levels can cause taste issues.")
    if sample_data['Hardness'] > 300:
        suggestions.append("💡 Soften hard water using ion exchange or RO.")
    if sample_data['Conductivity'] > 800:
        suggestions.append("💡 Check for excessive ion concentration.")
    return suggestions
