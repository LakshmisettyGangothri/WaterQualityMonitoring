import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def create_potability_pie_chart(predictions_df):
    """Create pie chart showing potability distribution"""
    if predictions_df.empty:
        return go.Figure()
    
    potability_counts = predictions_df['potability'].value_counts()
    labels = ['Not Drinkable', 'Drinkable']
    values = [potability_counts.get(0, 0), potability_counts.get(1, 0)]
    colors = ['#ff6b6b', '#51cf66']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.3,
        marker_colors=colors,
        textinfo='label+percent+value',
        textfont_size=12
    )])
    
    fig.update_layout(
        title="Water Potability Distribution",
        font=dict(size=14),
        height=400
    )
    
    return fig

def create_regional_bar_chart(predictions_df):
    """Create bar chart showing predictions by region"""
    if predictions_df.empty or 'region' not in predictions_df.columns:
        return go.Figure()
    
    regional_data = predictions_df.groupby('region').agg({
        'potability': ['count', 'sum']
    }).reset_index()
    
    regional_data.columns = ['region', 'total_predictions', 'drinkable_count']
    regional_data['not_drinkable'] = regional_data['total_predictions'] - regional_data['drinkable_count']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Drinkable',
        x=regional_data['region'],
        y=regional_data['drinkable_count'],
        marker_color='#51cf66'
    ))
    
    fig.add_trace(go.Bar(
        name='Not Drinkable',
        x=regional_data['region'],
        y=regional_data['not_drinkable'],
        marker_color='#ff6b6b'
    ))
    
    fig.update_layout(
        title="Water Quality Predictions by Region",
        xaxis_title="Region",
        yaxis_title="Number of Predictions",
        barmode='stack',
        height=400
    )
    
    return fig

def create_parameter_violation_chart(predictions_df):
    """Create chart showing parameter violations"""
    if predictions_df.empty:
        return go.Figure()
    
    # Define safe ranges
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
    
    violations = {}
    
    for param, (min_val, max_val) in safe_ranges.items():
        if param in predictions_df.columns:
            violation_count = len(predictions_df[
                (predictions_df[param] < min_val) | (predictions_df[param] > max_val)
            ])
            violations[param] = violation_count
    
    if violations:
        fig = go.Figure(data=[
            go.Bar(
                x=list(violations.keys()),
                y=list(violations.values()),
                marker_color='#ff8787',
                text=list(violations.values()),
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Parameter Violations Frequency",
            xaxis_title="Parameters",
            yaxis_title="Number of Violations",
            height=400
        )
    else:
        fig = go.Figure()
    
    return fig

def create_user_activity_chart(predictions_df):
    """Create chart showing user activity"""
    if predictions_df.empty:
        return go.Figure()
    
    user_activity = predictions_df.groupby('user_id').size().reset_index(name='prediction_count')
    user_activity = user_activity.sort_values('prediction_count', ascending=False).head(10)
    
    fig = go.Figure(data=[
        go.Bar(
            x=user_activity['user_id'],
            y=user_activity['prediction_count'],
            marker_color='#339af0',
            text=user_activity['prediction_count'],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Top 10 Most Active Users",
        xaxis_title="User ID",
        yaxis_title="Number of Predictions",
        height=400
    )
    
    return fig

def create_trends_over_time(predictions_df):
    """Create trends chart over time"""
    if predictions_df.empty:
        return go.Figure()
    
    # Convert timestamp to datetime
    predictions_df['timestamp_dt'] = pd.to_datetime(predictions_df['timestamp'])
    predictions_df['date'] = predictions_df['timestamp_dt'].dt.date
    
    # Group by date
    daily_stats = predictions_df.groupby('date').agg({
        'potability': ['count', 'sum'],
        'confidence': 'mean'
    }).reset_index()
    
    daily_stats.columns = ['date', 'total_predictions', 'drinkable_count', 'avg_confidence']
    daily_stats['not_drinkable'] = daily_stats['total_predictions'] - daily_stats['drinkable_count']
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Daily Predictions', 'Average Confidence'),
        vertical_spacing=0.1
    )
    
    # Add prediction trends
    fig.add_trace(
        go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['drinkable_count'],
            name='Drinkable',
            line=dict(color='#51cf66'),
            mode='lines+markers'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['not_drinkable'],
            name='Not Drinkable',
            line=dict(color='#ff6b6b'),
            mode='lines+markers'
        ),
        row=1, col=1
    )
    
    # Add confidence trend
    fig.add_trace(
        go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['avg_confidence'],
            name='Avg Confidence',
            line=dict(color='#339af0'),
            mode='lines+markers'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title="Prediction Trends Over Time",
        height=600,
        showlegend=True
    )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Count", row=1, col=1)
    fig.update_yaxes(title_text="Confidence (%)", row=2, col=1)
    
    return fig

def create_user_history_chart(user_predictions):
    """Create chart for individual user's prediction history"""
    if user_predictions.empty:
        return go.Figure()
    
    # Convert timestamp to datetime
    user_predictions['timestamp_dt'] = pd.to_datetime(user_predictions['timestamp'])
    
    # Create scatter plot with color coding for potability
    colors = ['#ff6b6b' if p == 0 else '#51cf66' for p in user_predictions['potability']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=user_predictions['timestamp_dt'],
        y=user_predictions['confidence'],
        mode='markers+lines',
        marker=dict(
            color=colors,
            size=10,
            line=dict(width=2, color='white')
        ),
        line=dict(color='gray', width=1),
        text=[f"{'Drinkable' if p == 1 else 'Not Drinkable'}<br>Confidence: {c:.1f}%<br>Region: {r}" 
              for p, c, r in zip(user_predictions['potability'], user_predictions['confidence'], user_predictions['region'])],
        hovertemplate='%{text}<extra></extra>',
        name='Predictions'
    ))
    
    fig.update_layout(
        title="Your Prediction History",
        xaxis_title="Date",
        yaxis_title="Confidence (%)",
        height=400,
        showlegend=False
    )
    
    return fig
