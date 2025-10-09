#!/usr/bin/env python3
"""
Example Script 1: Data Analysis with Pandas and NumPy
This script demonstrates common data science operations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def analyze_data():
    """Analyze sample dataset"""
    # Create sample data
    data = {
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'age': [25, 30, 35, 28, 32],
        'salary': [50000, 60000, 70000, 55000, 65000],
        'department': ['Engineering', 'Marketing', 'Engineering', 'Sales', 'Marketing']
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    print("Dataset Overview:")
    print(df.head())
    print(f"\nDataset shape: {df.shape}")
    print(f"Average salary: ${df['salary'].mean():.2f}")
    
    # Group by department
    dept_stats = df.groupby('department')['salary'].agg(['mean', 'count'])
    print("\nSalary by Department:")
    print(dept_stats)
    
    # Simple visualization
    plt.figure(figsize=(10, 6))
    plt.subplot(1, 2, 1)
    df['department'].value_counts().plot(kind='bar')
    plt.title('Employees by Department')
    plt.xticks(rotation=45)
    
    plt.subplot(1, 2, 2)
    plt.scatter(df['age'], df['salary'])
    plt.xlabel('Age')
    plt.ylabel('Salary')
    plt.title('Age vs Salary')
    
    plt.tight_layout()
    plt.savefig('analysis_results.png')
    print("\nVisualization saved as 'analysis_results.png'")

if __name__ == "__main__":
    analyze_data()