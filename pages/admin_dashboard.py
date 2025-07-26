import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.data_handler import get_all_users, get_all_predictions, export_data_csv
from utils.visualizations import (
    create_potability_pie_chart, 
    create_regional_bar_chart,
    create_parameter_violation_chart,
    create_user_activity_chart,
    create_trends_over_time
)

def show_admin_dashboard():
    """Display admin dashboard with analytics and user management"""
    
    # Header with logout button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🔧 Admin Dashboard")
        st.subheader("Water Quality System Analytics & Management")
    with col2:
        if st.button("Logout", type="secondary"):
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.is_admin = False
            st.rerun()
    
    st.markdown("---")
    
    # Load data
    users_df = get_all_users()
    predictions_df = get_all_predictions()
    
    # Create tabs for different admin functions
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics Overview", "👥 User Management", "📈 Detailed Analytics", "📁 Data Export"])
    
    with tab1:
        show_analytics_overview(users_df, predictions_df)
    
    with tab2:
        show_user_management(users_df, predictions_df)
    
    with tab3:
        show_detailed_analytics(predictions_df)
    
    with tab4:
        show_data_export(users_df, predictions_df)

def show_analytics_overview(users_df, predictions_df):
    """Show high-level analytics overview"""
    
    st.subheader("📊 System Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_users = len(users_df) if not users_df.empty else 0
    total_predictions = len(predictions_df) if not predictions_df.empty else 0
    drinkable_count = len(predictions_df[predictions_df['potability'] == 1]) if not predictions_df.empty else 0
    avg_confidence = predictions_df['confidence'].mean() if not predictions_df.empty else 0
    
    with col1:
        st.metric("Total Users", total_users)
    with col2:
        st.metric("Total Predictions", total_predictions)
    with col3:
        st.metric("Drinkable Samples", f"{drinkable_count}/{total_predictions}" if total_predictions > 0 else "0/0")
    with col4:
        st.metric("Avg Confidence", f"{avg_confidence:.1f}%" if avg_confidence > 0 else "0%")
    
    if not predictions_df.empty:
        # Visualization row 1
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Water Potability Distribution")
            pie_chart = create_potability_pie_chart(predictions_df)
            st.plotly_chart(pie_chart, use_container_width=True)
        
        with col2:
            st.subheader("Predictions by Region")
            bar_chart = create_regional_bar_chart(predictions_df)
            st.plotly_chart(bar_chart, use_container_width=True)
        
        # Visualization row 2
        st.subheader("Parameter Violations Analysis")
        violation_chart = create_parameter_violation_chart(predictions_df)
        st.plotly_chart(violation_chart, use_container_width=True)
        
    else:
        st.info("📝 No prediction data available yet.")

def show_user_management(users_df, predictions_df):
    """Show user management interface"""
    
    st.subheader("👥 User Management")
    
    if not users_df.empty:
        # User statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("User Statistics")
            if not predictions_df.empty:
                # Calculate user activity
                user_activity = predictions_df.groupby('user_id').agg({
                    'potability': 'count',
                    'timestamp': 'max'
                }).rename(columns={'potability': 'total_predictions', 'timestamp': 'last_activity'})
                
                # Merge with user data
                user_summary = users_df.merge(user_activity, left_on='user_id', right_index=True, how='left')
                user_summary['total_predictions'] = user_summary['total_predictions'].fillna(0).astype(int)
                user_summary['last_activity'] = user_summary['last_activity'].fillna('Never')
                
                st.dataframe(user_summary[['username', 'email', 'registration_date', 'total_predictions', 'last_activity']], 
                           use_container_width=True)
            else:
                st.dataframe(users_df[['username', 'email', 'registration_date']], use_container_width=True)
        
        with col2:
            st.subheader("User Activity Chart")
            if not predictions_df.empty:
                activity_chart = create_user_activity_chart(predictions_df)
                st.plotly_chart(activity_chart, use_container_width=True)
            else:
                st.info("No user activity data to display")
        
        # Individual user details
        st.subheader("Individual User Details")
        selected_user = st.selectbox("Select User", users_df['username'].tolist())
        
        if selected_user:
            user_info = users_df[users_df['username'] == selected_user].iloc[0]
            user_id = user_info['user_id']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**User Information:**")
                st.write(f"Username: {user_info['username']}")
                st.write(f"Email: {user_info['email']}")
                st.write(f"Registration Date: {user_info['registration_date']}")
            
            with col2:
                if not predictions_df.empty:
                    user_predictions = predictions_df[predictions_df['user_id'] == user_id]
                    if not user_predictions.empty:
                        st.write("**Activity Summary:**")
                        st.write(f"Total Predictions: {len(user_predictions)}")
                        st.write(f"Drinkable Results: {len(user_predictions[user_predictions['potability'] == 1])}")
                        st.write(f"Last Activity: {user_predictions['timestamp'].max()}")
                    else:
                        st.write("**Activity Summary:**")
                        st.write("No predictions made yet")
                else:
                    st.write("**Activity Summary:**")
                    st.write("No predictions made yet")
            
            # User prediction history
            if not predictions_df.empty:
                user_predictions = predictions_df[predictions_df['user_id'] == user_id]
                if not user_predictions.empty:
                    st.subheader(f"Prediction History for {selected_user}")
                    display_columns = ['timestamp', 'region', 'state', 'potability', 'confidence', 'pH', 'Solids', 'Chloramines']
                    display_df = user_predictions[display_columns].copy()
                    display_df['potability'] = display_df['potability'].map({1: '✅ Drinkable', 0: '❌ Not Drinkable'})
                    display_df['confidence'] = display_df['confidence'].apply(lambda x: f"{x:.1f}%")
                    st.dataframe(display_df.sort_values('timestamp', ascending=False), use_container_width=True)
    
    else:
        st.info("📝 No users registered yet.")

def show_detailed_analytics(predictions_df):
    """Show detailed analytics and trends"""
    
    st.subheader("📈 Detailed Analytics")
    
    if not predictions_df.empty:
        # Time-based analytics
        st.subheader("Trends Over Time")
        trends_chart = create_trends_over_time(predictions_df)
        st.plotly_chart(trends_chart, use_container_width=True)
        
        # Parameter statistics
        st.subheader("Parameter Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Average Parameter Values (All Samples)**")
            param_columns = ['pH', 'Solids', 'Sulfate', 'Organic_carbon', 'Turbidity', 'Hardness', 'Chloramines', 'Conductivity', 'Trihalomethanes']
            avg_params = predictions_df[param_columns].mean()
            for param, value in avg_params.items():
                st.write(f"{param}: {value:.2f}")
        
        with col2:
            st.write("**Average Parameter Values by Potability**")
            drinkable_avg = predictions_df[predictions_df['potability'] == 1][param_columns].mean()
            not_drinkable_avg = predictions_df[predictions_df['potability'] == 0][param_columns].mean()
            
            comparison_df = pd.DataFrame({
                'Drinkable': drinkable_avg,
                'Not Drinkable': not_drinkable_avg
            })
            st.dataframe(comparison_df)
        
        # Regional analysis
        st.subheader("Regional Analysis")
        if 'region' in predictions_df.columns and 'state' in predictions_df.columns:
            regional_stats = predictions_df.groupby(['state', 'region']).agg({
                'potability': ['count', 'mean'],
                'confidence': 'mean'
            }).round(2)
            
            regional_stats.columns = ['Total_Samples', 'Potability_Rate', 'Avg_Confidence']
            st.dataframe(regional_stats, use_container_width=True)
        
        # Recent activity
        st.subheader("Recent Activity (Last 7 Days)")
        recent_date = datetime.now() - timedelta(days=7)
        predictions_df['timestamp_dt'] = pd.to_datetime(predictions_df['timestamp'])
        recent_predictions = predictions_df[predictions_df['timestamp_dt'] >= recent_date]
        
        if not recent_predictions.empty:
            st.write(f"Total predictions in last 7 days: {len(recent_predictions)}")
            st.write(f"Drinkable samples: {len(recent_predictions[recent_predictions['potability'] == 1])}")
            st.write(f"Most active regions: {recent_predictions['region'].value_counts().head(3).to_dict()}")
        else:
            st.write("No recent activity in the last 7 days.")
    
    else:
        st.info("📝 No prediction data available for detailed analytics.")

def show_data_export(users_df, predictions_df):
    """Show data export functionality"""
    
    st.subheader("📁 Data Export")
    st.write("Export system data for external analysis or backup purposes.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Available Data:**")
        st.write(f"- Users: {len(users_df)} records")
        st.write(f"- Predictions: {len(predictions_df)} records")
    
    with col2:
        st.write("**Export Options:**")
        
        if st.button("📊 Export Users Data", type="secondary"):
            if not users_df.empty:
                csv_data = export_data_csv(users_df)
                st.download_button(
                    label="Download Users CSV",
                    data=csv_data,
                    file_name=f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.error("No user data to export")
        
        if st.button("🔬 Export Predictions Data", type="secondary"):
            if not predictions_df.empty:
                csv_data = export_data_csv(predictions_df)
                st.download_button(
                    label="Download Predictions CSV",
                    data=csv_data,
                    file_name=f"predictions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.error("No prediction data to export")
    
    # Data summary
    if not predictions_df.empty or not users_df.empty:
        st.subheader("Data Summary")
        
        if not predictions_df.empty:
            st.write("**Prediction Data Sample:**")
            st.dataframe(predictions_df.head(), use_container_width=True)
        
        if not users_df.empty:
            st.write("**User Data Sample:**")
            # Don't show password hashes
            display_users = users_df.drop('password_hash', axis=1) if 'password_hash' in users_df.columns else users_df
            st.dataframe(display_users.head(), use_container_width=True)
