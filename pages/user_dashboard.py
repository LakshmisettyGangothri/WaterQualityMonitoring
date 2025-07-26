import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from utils.ml_model import load_model, make_prediction, generate_precautions, get_parameter_analysis
from utils.data_handler import save_prediction, get_user_predictions
from utils.visualizations import create_user_history_chart

def show_user_dashboard():
    """Display user dashboard with water quality prediction interface"""
    
    # Header with logout button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"Welcome, {st.session_state.username}!")
        st.subheader("💧 Water Quality Prediction Dashboard")
    with col2:
        if st.button("Logout", type="secondary"):
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.is_admin = False
            st.rerun()
    
    st.markdown("---")
    
    # Create tabs for prediction and history
    tab1, tab2 = st.tabs(["🔬 Water Quality Test", "📊 My Prediction History"])
    
    with tab1:
        show_prediction_interface()
    
    with tab2:
        show_user_history()

def show_prediction_interface():
    """Show water quality prediction form and results"""
    
    st.subheader("Enter Water Sample Parameters")
    st.write("Please enter the water quality parameters for analysis:")
    
    # Create form for water parameters
    with st.form("water_quality_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            region = st.text_input("Region", placeholder="e.g., North District")
            state = st.text_input("State", placeholder="e.g., California")
            ph = st.number_input("pH Level", min_value=0.0, max_value=14.0, value=7.0, step=0.1)
            solids = st.number_input("Total Dissolved Solids (ppm)", min_value=0.0, value=1000.0, step=10.0)
            sulphates = st.number_input("Sulphates (mg/L)", min_value=0.0, value=200.0, step=1.0)
        
        with col2:
            organic_carbon = st.number_input("Organic Carbon (ppm)", min_value=0.0, value=10.0, step=0.1)
            turbidity = st.number_input("Turbidity (NTU)", min_value=0.0, value=4.0, step=0.1)
            hardness = st.number_input("Hardness (mg/L)", min_value=0.0, value=200.0, step=1.0)
            chloramines = st.number_input("Chloramines (ppm)", min_value=0.0, value=2.0, step=0.1)
            conductivity = st.number_input("Conductivity (μS/cm)", min_value=0.0, value=400.0, step=1.0)
            trihalomethanes = st.number_input("Trihalomethanes (μg/L)", min_value=0.0, value=50.0, step=0.1)
        
        submit_button = st.form_submit_button("🔍 Analyze Water Quality", type="primary")
        
        if submit_button:
            if region and state:
                # Prepare data for prediction
                sample_data = {
                    'pH': ph,
                    'Solids': solids,
                    'Sulfate': sulphates,
                    'Organic_carbon': organic_carbon,
                    'Turbidity': turbidity,
                    'Hardness': hardness,
                    'Chloramines': chloramines,
                    'Conductivity': conductivity,
                    'Trihalomethanes': trihalomethanes
                }
                
                # Make prediction
                try:
                    model = load_model()
                    prediction, confidence = make_prediction(model, sample_data)
                    
                    # Save prediction to database
                    prediction_data = {
                        'user_id': st.session_state.user_id,
                        'region': region,
                        'state': state,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'potability': prediction,
                        'confidence': confidence,
                        **sample_data
                    }
                    save_prediction(prediction_data)
                    
                    # Display results
                    show_prediction_results(sample_data, prediction, confidence, region, state)
                    
                except Exception as e:
                    st.error(f"Error making prediction: {str(e)}")
            else:
                st.error("Please enter both region and state information")

def show_prediction_results(sample_data, prediction, confidence, region, state):
    """Display prediction results with analysis and suggestions"""
    
    st.markdown("---")
    st.subheader("🔬 Analysis Results")
    
    # Main result
    if prediction == 1:
        st.success(f"✅ **The water is DRINKABLE** (Confidence: {confidence:.1f}%)")
        result_color = "green"
    else:
        st.error(f"❌ **The water is NOT DRINKABLE** (Confidence: {confidence:.1f}%)")
        result_color = "red"
    
    # Parameter analysis
    st.subheader("📊 Parameter-wise Analysis")
    analysis_df = get_parameter_analysis(sample_data)
    
    # Color code the status column
    def highlight_status(val):
        if "Safe" in val:
            return 'background-color: lightgreen'
        else:
            return 'background-color: lightcoral'
    
    styled_df = analysis_df.style.map(highlight_status, subset=['Status'])
    st.dataframe(styled_df, use_container_width=True)
    
    # Precautionary suggestions
    st.subheader("🛡️ Precautionary Suggestions")
    suggestions = generate_precautions(sample_data)
    
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            st.write(f"{i}. {suggestion}")
    else:
        st.write("✅ All parameters are within safe ranges. No specific precautions needed.")
    
    # Additional information
    with st.expander("ℹ️ Additional Information"):
        st.write(f"**Sample Location:** {region}, {state}")
        st.write(f"**Analysis Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.write("**Note:** This prediction is based on machine learning analysis. For critical decisions, please consult with water quality experts.")

def show_user_history():
    """Display user's prediction history"""
    
    st.subheader("📊 Your Prediction History")
    
    # Get user predictions
    user_predictions = get_user_predictions(st.session_state.user_id)
    
    if not user_predictions.empty:
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        total_tests = len(user_predictions)
        drinkable_count = len(user_predictions[user_predictions['potability'] == 1])
        avg_confidence = user_predictions['confidence'].mean()
        latest_test = user_predictions['timestamp'].max()
        
        with col1:
            st.metric("Total Tests", total_tests)
        with col2:
            st.metric("Drinkable Samples", f"{drinkable_count}/{total_tests}")
        with col3:
            st.metric("Avg Confidence", f"{avg_confidence:.1f}%")
        with col4:
            if not user_predictions.empty and 'timestamp' in user_predictions.columns:
                latest_test_str = str(latest_test).split()[0] if pd.notna(latest_test) and str(latest_test) != 'nan' else "N/A"
            else:
                latest_test_str = "N/A"
            st.metric("Latest Test", latest_test_str)
        
        # History chart
        if len(user_predictions) > 1:
            st.subheader("Prediction Trends")
            chart = create_user_history_chart(user_predictions)
            st.plotly_chart(chart, use_container_width=True)
        
        # Recent predictions table
        st.subheader("Recent Predictions")
        display_columns = ['timestamp', 'region', 'state', 'potability', 'confidence', 'pH', 'Solids', 'Chloramines']
        display_df = user_predictions[display_columns].copy()
        # Create a copy and properly handle data types
        display_df = display_df.copy()
        display_df['potability'] = display_df['potability'].astype(int).map({1: '✅ Drinkable', 0: '❌ Not Drinkable'})
        display_df['confidence'] = display_df['confidence'].astype(float).apply(lambda x: f"{x:.1f}%")
        
        sorted_df = display_df.sort_values('timestamp', ascending=False)
        st.dataframe(sorted_df, use_container_width=True)
        
    else:
        st.info("📝 No predictions yet. Start by testing a water sample!")
        st.write("Use the 'Water Quality Test' tab to analyze your first water sample.")