#!/usr/bin/env python3
"""
Script 6: Data Visualization with Seaborn and Plotly
Tests advanced visualization libraries
"""

import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def create_visualizations():
    """Create various data visualizations"""
    print("Creating advanced data visualizations...")
    
    # Generate sample dataset
    np.random.seed(42)
    n_points = 500
    
    data = pd.DataFrame({
        'x': np.random.randn(n_points),
        'y': np.random.randn(n_points),
        'category': np.random.choice(['A', 'B', 'C', 'D'], n_points),
        'value': np.random.exponential(2, n_points),
        'time': pd.date_range('2023-01-01', periods=n_points, freq='H')
    })
    
    # Seaborn visualizations
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    sns.scatterplot(data=data, x='x', y='y', hue='category', size='value', alpha=0.6)
    plt.title('Seaborn Scatter Plot')
    
    plt.subplot(1, 3, 2)
    sns.boxplot(data=data, x='category', y='value')
    plt.title('Seaborn Box Plot')
    
    plt.subplot(1, 3, 3)
    sns.heatmap(data[['x', 'y', 'value']].corr(), annot=True, cmap='coolwarm')
    plt.title('Correlation Heatmap')
    
    plt.tight_layout()
    plt.savefig('seaborn_visualizations.png')
    print("Seaborn plots saved to seaborn_visualizations.png")
    
    # Plotly interactive visualizations
    fig1 = px.scatter_3d(data, x='x', y='y', z='value', color='category',
                         title='3D Scatter Plot', hover_data=['time'])
    fig1.write_html('plotly_3d_scatter.html')
    
    # Time series with Plotly
    time_data = data.groupby('time')['value'].mean().reset_index()
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=time_data['time'], y=time_data['value'],
                              mode='lines+markers', name='Average Value'))
    fig2.update_layout(title='Time Series Visualization',
                      xaxis_title='Time', yaxis_title='Value')
    fig2.write_html('plotly_timeseries.html')
    
    print("Plotly interactive plots saved as HTML files")
    
    # Statistical plots
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    sns.violinplot(data=data, x='category', y='value')
    plt.title('Violin Plot')
    
    plt.subplot(1, 2, 2)
    sns.jointplot(data=data, x='x', y='y', kind='hex')
    plt.suptitle('Hexbin Joint Plot')
    
    plt.tight_layout()
    plt.savefig('statistical_plots.png')
    
    return {
        'total_points': len(data),
        'categories': data['category'].nunique(),
        'visualizations_created': 8
    }

if __name__ == "__main__":
    results = create_visualizations()
    print(f"Visualization complete: {results}")