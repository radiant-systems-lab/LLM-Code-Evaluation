# Data Visualization and Plotting
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import numpy as np
import pandas as pd
from bokeh.plotting import figure, save, output_file
from bokeh.models import HoverTool

def matplotlib_visualizations():
    """Create various matplotlib plots"""
    # Generate sample data
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    y3 = np.sin(x) * np.exp(-x/5)
    
    # Create subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    
    # Line plot
    ax1.plot(x, y1, 'b-', label='sin(x)')
    ax1.plot(x, y2, 'r--', label='cos(x)')
    ax1.set_title('Trigonometric Functions')
    ax1.legend()
    ax1.grid(True)
    
    # Scatter plot
    np.random.seed(42)
    x_scatter = np.random.randn(100)
    y_scatter = 2 * x_scatter + np.random.randn(100)
    ax2.scatter(x_scatter, y_scatter, alpha=0.6)
    ax2.set_title('Scatter Plot')
    ax2.set_xlabel('X values')
    ax2.set_ylabel('Y values')
    
    # Histogram
    data = np.random.normal(0, 1, 1000)
    ax3.hist(data, bins=30, alpha=0.7, color='green')
    ax3.set_title('Normal Distribution')
    ax3.set_xlabel('Value')
    ax3.set_ylabel('Frequency')
    
    # Bar plot
    categories = ['A', 'B', 'C', 'D', 'E']
    values = [23, 45, 56, 78, 32]
    ax4.bar(categories, values, color=['red', 'green', 'blue', 'orange', 'purple'])
    ax4.set_title('Bar Chart')
    ax4.set_xlabel('Categories')
    ax4.set_ylabel('Values')
    
    plt.tight_layout()
    plt.savefig('/tmp/matplotlib_plots.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return {'plots_created': 4, 'data_points': len(x)}

def seaborn_visualizations():
    """Create seaborn statistical plots"""
    # Generate sample dataset
    np.random.seed(42)
    n_samples = 200
    data = pd.DataFrame({
        'x': np.random.randn(n_samples),
        'y': np.random.randn(n_samples),
        'category': np.random.choice(['A', 'B', 'C'], n_samples),
        'value': np.random.randint(1, 100, n_samples)
    })
    
    # Set style
    sns.set_style("whitegrid")
    
    # Create multiple plots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Scatter plot with categories
    sns.scatterplot(data=data, x='x', y='y', hue='category', ax=axes[0, 0])
    axes[0, 0].set_title('Seaborn Scatter Plot')
    
    # Box plot
    sns.boxplot(data=data, x='category', y='value', ax=axes[0, 1])
    axes[0, 1].set_title('Box Plot by Category')
    
    # Violin plot
    sns.violinplot(data=data, x='category', y='value', ax=axes[1, 0])
    axes[1, 0].set_title('Violin Plot')
    
    # Correlation heatmap
    corr_data = data[['x', 'y', 'value']].corr()
    sns.heatmap(corr_data, annot=True, ax=axes[1, 1])
    axes[1, 1].set_title('Correlation Heatmap')
    
    plt.tight_layout()
    plt.savefig('/tmp/seaborn_plots.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return {'samples': n_samples, 'categories': len(data['category'].unique())}

def plotly_interactive_plots():
    """Create interactive plotly visualizations"""
    # Generate sample data
    np.random.seed(42)
    n_points = 100
    
    # Create subplot figure
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('3D Scatter', 'Time Series', 'Heatmap', 'Bar Chart'),
        specs=[[{"type": "scatter3d"}, {"type": "scatter"}],
               [{"type": "heatmap"}, {"type": "bar"}]]
    )
    
    # 3D Scatter plot
    x = np.random.randn(n_points)
    y = np.random.randn(n_points)
    z = x + y + np.random.randn(n_points) * 0.5
    
    fig.add_trace(
        go.Scatter3d(x=x, y=y, z=z, mode='markers',
                    marker=dict(size=5, color=z, colorscale='Viridis')),
        row=1, col=1
    )
    
    # Time series
    dates = pd.date_range('2024-01-01', periods=50)
    values = np.cumsum(np.random.randn(50))
    
    fig.add_trace(
        go.Scatter(x=dates, y=values, mode='lines+markers'),
        row=1, col=2
    )
    
    # Heatmap
    heatmap_data = np.random.randn(10, 10)
    fig.add_trace(
        go.Heatmap(z=heatmap_data, colorscale='RdBu'),
        row=2, col=1
    )
    
    # Bar chart
    categories = ['Category A', 'Category B', 'Category C', 'Category D']
    values = [20, 35, 30, 25]
    
    fig.add_trace(
        go.Bar(x=categories, y=values),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False, title_text="Interactive Plotly Dashboard")
    fig.write_html('/tmp/plotly_plots.html')
    
    return {'interactive_plots': 4, 'data_points': n_points}

def bokeh_visualization():
    """Create bokeh interactive plot"""
    # Generate sample data
    n = 100
    x = np.random.random(n) * 100
    y = np.random.random(n) * 100
    colors = np.random.choice(['red', 'green', 'blue', 'orange', 'purple'], n)
    sizes = np.random.randint(10, 30, n)
    
    # Create figure
    p = figure(title="Bokeh Scatter Plot", width=600, height=400,
               tools="pan,wheel_zoom,box_zoom,reset,save")
    
    # Add circle renderer
    p.circle(x, y, size=sizes, color=colors, alpha=0.6)
    
    # Add hover tool
    hover = HoverTool(tooltips=[("(X,Y)", "($x, $y)")])
    p.add_tools(hover)
    
    # Save to file
    output_file('/tmp/bokeh_plot.html')
    save(p)
    
    return {'bokeh_points': n, 'unique_colors': len(set(colors))}

def advanced_matplotlib_features():
    """Advanced matplotlib features"""
    fig = plt.figure(figsize=(15, 10))
    
    # 3D plot
    ax1 = fig.add_subplot(221, projection='3d')
    x = np.random.randn(100)
    y = np.random.randn(100)
    z = x**2 + y**2 + np.random.randn(100) * 0.1
    ax1.scatter(x, y, z, c=z, cmap='viridis')
    ax1.set_title('3D Scatter Plot')
    
    # Polar plot
    ax2 = fig.add_subplot(222, projection='polar')
    theta = np.linspace(0, 2*np.pi, 100)
    r = 1 + 0.3 * np.sin(5*theta)
    ax2.plot(theta, r)
    ax2.set_title('Polar Plot')
    
    # Contour plot
    ax3 = fig.add_subplot(223)
    x = np.linspace(-3, 3, 100)
    y = np.linspace(-3, 3, 100)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    contour = ax3.contourf(X, Y, Z, levels=20, cmap='coolwarm')
    plt.colorbar(contour, ax=ax3)
    ax3.set_title('Contour Plot')
    
    # Multiple y-axes
    ax4 = fig.add_subplot(224)
    x = np.linspace(0, 10, 50)
    y1 = np.sin(x)
    y2 = np.exp(x/10)
    
    ax4.plot(x, y1, 'b-', label='sin(x)')
    ax4.set_ylabel('sin(x)', color='b')
    ax4.tick_params(axis='y', labelcolor='b')
    
    ax4_twin = ax4.twinx()
    ax4_twin.plot(x, y2, 'r-', label='exp(x/10)')
    ax4_twin.set_ylabel('exp(x/10)', color='r')
    ax4_twin.tick_params(axis='y', labelcolor='r')
    ax4.set_title('Dual Y-Axis Plot')
    
    plt.tight_layout()
    plt.savefig('/tmp/advanced_plots.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return {'advanced_plots': 4, 'plot_types': ['3d', 'polar', 'contour', 'dual_axis']}

if __name__ == "__main__":
    print("Data visualization operations...")
    
    matplotlib_result = matplotlib_visualizations()
    print(f"Matplotlib: Created {matplotlib_result['plots_created']} plots")
    
    seaborn_result = seaborn_visualizations()
    print(f"Seaborn: Analyzed {seaborn_result['samples']} samples")
    
    plotly_result = plotly_interactive_plots()
    print(f"Plotly: Created {plotly_result['interactive_plots']} interactive plots")
    
    bokeh_result = bokeh_visualization()
    print(f"Bokeh: Created plot with {bokeh_result['bokeh_points']} points")
    
    advanced_result = advanced_matplotlib_features()
    print(f"Advanced plots: {len(advanced_result['plot_types'])} different types created")