import pandas as pd
import hashlib
import uuid
from datetime import datetime
import os

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    """Authenticate user credentials"""
    try:
        users_df = pd.read_csv('data/users.csv')
        user_row = users_df[users_df['username'] == username]
        
        if not user_row.empty:
            stored_hash = user_row.iloc[0]['password_hash']
            input_hash = hash_password(password)
            
            if stored_hash == input_hash:
                return user_row.iloc[0].to_dict()
        
        return None
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

def register_user(username, email, password):
    """Register a new user"""
    try:
        # Check if users file exists
        if os.path.exists('data/users.csv'):
            users_df = pd.read_csv('data/users.csv')
            
            # Check if username already exists
            if username in users_df['username'].values:
                return False, "Username already exists"
            
            # Check if email already exists
            if email in users_df['email'].values:
                return False, "Email already registered"
        else:
            # Create empty dataframe if file doesn't exist
            users_df = pd.DataFrame({
                'user_id': pd.Series(dtype='str'),
                'username': pd.Series(dtype='str'),
                'email': pd.Series(dtype='str'),
                'password_hash': pd.Series(dtype='str'),
                'registration_date': pd.Series(dtype='str')
            })
        
        # Create new user
        new_user = {
            'user_id': str(uuid.uuid4()),
            'username': username,
            'email': email,
            'password_hash': hash_password(password),
            'registration_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Add to dataframe
        new_user_df = pd.DataFrame([new_user])
        users_df = pd.concat([users_df, new_user_df], ignore_index=True)
        
        # Save to file
        users_df.to_csv('data/users.csv', index=False)
        
        return True, "Registration successful!"
        
    except Exception as e:
        return False, f"Registration failed: {str(e)}"

def is_admin(username):
    """Check if user is admin"""
    return username == "Admin"
