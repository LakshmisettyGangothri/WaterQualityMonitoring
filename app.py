import streamlit as st
import pandas as pd
import hashlib
from utils.auth import authenticate_user, register_user, is_admin
from utils.data_handler import initialize_data_files

# Initialize data files
initialize_data_files()

# Set page configuration
st.set_page_config(
    page_title="Water Quality Prediction System",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    """Main application logic"""
    
    # If user is authenticated, show appropriate dashboard
    if st.session_state.authenticated:
        if st.session_state.is_admin:
            # Import and run admin dashboard
            from pages.admin_dashboard import show_admin_dashboard
            show_admin_dashboard()
        else:
            # Import and run user dashboard
            from pages.user_dashboard import show_user_dashboard
            show_user_dashboard()
    else:
        # Show login/registration page
        show_login_page()

def show_login_page():
    """Display login and registration interface"""
    
    st.title("💧 Water Quality Prediction System")
    st.markdown("---")
    
    # Create tabs for login and registration
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                if username and password:
                    # Check for admin credentials
                    if username == "Admin" and password == "Admin":
                        st.session_state.authenticated = True
                        st.session_state.user_id = "admin"
                        st.session_state.username = "Admin"
                        st.session_state.is_admin = True
                        st.success("Admin login successful!")
                        st.rerun()
                    else:
                        # Regular user authentication
                        user_data = authenticate_user(username, password)
                        if user_data is not None:
                            st.session_state.authenticated = True
                            st.session_state.user_id = user_data['user_id']
                            st.session_state.username = username
                            st.session_state.is_admin = False
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                else:
                    st.error("Please enter both username and password")
    
    with tab2:
        st.subheader("Register")
        
        # Initialize registration form values in session state
        if 'registration_success' not in st.session_state:
            st.session_state.registration_success = False
        
        with st.form("register_form", clear_on_submit=True):
            reg_username = st.text_input("Choose Username", key="reg_username")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Choose Password", type="password", key="reg_password")
            reg_confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")
            register_button = st.form_submit_button("Register")
            
            if register_button:
                if reg_username and reg_email and reg_password and reg_confirm_password:
                    if reg_password == reg_confirm_password:
                        if len(reg_password) >= 6:
                            success, message = register_user(reg_username, reg_email, reg_password)
                            if success:
                                st.success(message)
                                st.success("You can now login with your credentials!")
                                st.session_state.registration_success = True
                                # Clear form data by rerunning
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.error("Password must be at least 6 characters long")
                    else:
                        st.error("Passwords do not match")
                else:
                    st.error("Please fill in all fields")

if __name__ == "__main__":
    main()

st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)