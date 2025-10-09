#!/usr/bin/env python3
"""
Example Script 3: Machine Learning with Scikit-learn
This script demonstrates basic machine learning operations.
"""

from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import numpy as np

def train_model():
    """Train a simple classification model"""
    
    print("Generating synthetic dataset...")
    # Generate synthetic dataset
    X, y = make_classification(
        n_samples=1000,
        n_features=20,
        n_informative=10,
        n_redundant=10,
        n_clusters_per_class=1,
        random_state=42
    )
    
    print(f"Dataset created: {X.shape[0]} samples, {X.shape[1]} features")
    
    # Split the dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    # Train Random Forest model
    print("\nTraining Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Evaluate model
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nModel Accuracy: {accuracy:.4f}")
    
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Feature importance
    feature_importance = model.feature_importances_
    top_features = np.argsort(feature_importance)[-5:][::-1]
    
    print("\nTop 5 Most Important Features:")
    for i, feature_idx in enumerate(top_features):
        print(f"  Feature {feature_idx}: {feature_importance[feature_idx]:.4f}")
    
    # Save model
    joblib.dump(model, 'trained_model.pkl')
    print("\nModel saved as 'trained_model.pkl'")
    
    # Save results summary
    results = {
        "accuracy": float(accuracy),
        "dataset_size": X.shape[0],
        "features": X.shape[1],
        "test_samples": len(y_test)
    }
    
    import json
    with open('model_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Results saved to 'model_results.json'")

if __name__ == "__main__":
    train_model()