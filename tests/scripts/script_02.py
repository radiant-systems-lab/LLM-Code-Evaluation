# Data Science Pipeline
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

def load_dataset(filepath):
    """Load and preprocess data"""
    df = pd.read_csv(filepath)
    return df.dropna()

def visualize_data(data):
    """Create visualization"""
    plt.figure(figsize=(10, 6))
    sns.heatmap(data.corr(), annot=True)
    plt.show()

def train_model(X, y):
    """Train ML model"""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    print(f"MSE: {mse}")
    return model

if __name__ == "__main__":
    # Simulated data
    data = np.random.randn(100, 5)
    df = pd.DataFrame(data, columns=['A', 'B', 'C', 'D', 'target'])
    
    X = df[['A', 'B', 'C', 'D']]
    y = df['target']
    
    model = train_model(X, y)
    print("Model trained successfully")