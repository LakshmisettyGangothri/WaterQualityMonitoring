import pandas as pd
import os
from datetime import datetime

def initialize_data_files():
    """Initialize data files if they don't exist"""
    # Create data directory
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    # Initialize users.csv
    if not os.path.exists('data/users.csv'):
        users_df = pd.DataFrame({
            'user_id': pd.Series(dtype='str'),
            'username': pd.Series(dtype='str'),
            'email': pd.Series(dtype='str'),
            'password_hash': pd.Series(dtype='str'),
            'registration_date': pd.Series(dtype='str')
        })
        users_df.to_csv('data/users.csv', index=False)
    
    # Initialize predictions.csv
    if not os.path.exists('data/predictions.csv'):
        predictions_df = pd.DataFrame({
            'prediction_id': pd.Series(dtype='str'),
            'user_id': pd.Series(dtype='str'),
            'region': pd.Series(dtype='str'),
            'state': pd.Series(dtype='str'),
            'timestamp': pd.Series(dtype='str'),
            'potability': pd.Series(dtype='int'),
            'confidence': pd.Series(dtype='float'),
            'pH': pd.Series(dtype='float'),
            'Solids': pd.Series(dtype='float'),
            'Sulfate': pd.Series(dtype='float'),
            'Organic_carbon': pd.Series(dtype='float'),
            'Turbidity': pd.Series(dtype='float'),
            'Hardness': pd.Series(dtype='float'),
            'Chloramines': pd.Series(dtype='float'),
            'Conductivity': pd.Series(dtype='float'),
            'Trihalomethanes': pd.Series(dtype='float')
        })
        predictions_df.to_csv('data/predictions.csv', index=False)

def save_prediction(prediction_data):
    """Save a new prediction to the database"""
    try:
        # Load existing predictions
        predictions_df = pd.read_csv('data/predictions.csv')
        
        # Add prediction ID
        prediction_data['prediction_id'] = f"pred_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(predictions_df)}"
        
        # Create new prediction dataframe
        new_prediction_df = pd.DataFrame([prediction_data])
        
        # Concatenate and save
        if not predictions_df.empty:
            predictions_df = pd.concat([predictions_df, new_prediction_df], ignore_index=True)
        else:
            predictions_df = new_prediction_df
        predictions_df.to_csv('data/predictions.csv', index=False)
        
        return True
    except Exception as e:
        print(f"Error saving prediction: {e}")
        return False

def get_user_predictions(user_id):
    """Get all predictions for a specific user"""
    try:
        predictions_df = pd.read_csv('data/predictions.csv')
        user_predictions = predictions_df[predictions_df['user_id'] == user_id]
        if not user_predictions.empty:
            return user_predictions.sort_values('timestamp', ascending=False)
        else:
            return user_predictions
    except FileNotFoundError:
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading user predictions: {e}")
        return pd.DataFrame()

def get_all_users():
    """Get all users data"""
    try:
        users_df = pd.read_csv('data/users.csv')
        return users_df
    except FileNotFoundError:
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading users data: {e}")
        return pd.DataFrame()

def get_all_predictions():
    """Get all predictions data"""
    try:
        predictions_df = pd.read_csv('data/predictions.csv')
        return predictions_df
    except FileNotFoundError:
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading predictions data: {e}")
        return pd.DataFrame()

def export_data_csv(dataframe):
    """Export dataframe to CSV format for download"""
    return dataframe.to_csv(index=False)

def get_user_by_id(user_id):
    """Get user information by user ID"""
    try:
        users_df = pd.read_csv('data/users.csv')
        user_data = users_df[users_df['user_id'] == user_id]
        return user_data.iloc[0].to_dict() if not user_data.empty else None
    except:
        return None
