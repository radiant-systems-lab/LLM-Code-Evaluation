#!/usr/bin/env python3
"""
Script 5: Deep Learning with TensorFlow/Keras
Tests deep learning framework dependencies
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

def build_neural_network():
    """Build and train a simple neural network"""
    print("Building deep learning model with TensorFlow/Keras...")
    
    # Generate synthetic dataset
    np.random.seed(42)
    n_samples = 1000
    n_features = 20
    
    X = np.random.randn(n_samples, n_features)
    y = (X[:, 0] + X[:, 1] * 2 - X[:, 2] * 0.5 + np.random.randn(n_samples) * 0.1 > 0).astype(int)
    
    # Split and scale data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Build model
    model = models.Sequential([
        layers.Dense(64, activation='relu', input_shape=(n_features,)),
        layers.Dropout(0.3),
        layers.Dense(32, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(16, activation='relu'),
        layers.Dense(1, activation='sigmoid')
    ])
    
    # Compile model
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    print(f"Model architecture: {model.summary()}")
    
    # Train model
    history = model.fit(
        X_train_scaled, y_train,
        epochs=10,
        batch_size=32,
        validation_split=0.2,
        verbose=1
    )
    
    # Evaluate
    test_loss, test_accuracy = model.evaluate(X_test_scaled, y_test, verbose=0)
    print(f"Test accuracy: {test_accuracy:.4f}")
    
    # Save model
    model.save('neural_network_model.h5')
    print("Model saved to neural_network_model.h5")
    
    return {
        'model_params': model.count_params(),
        'test_accuracy': test_accuracy,
        'training_epochs': len(history.history['loss'])
    }

if __name__ == "__main__":
    tf.random.set_seed(42)
    results = build_neural_network()
    print(f"Training complete: {results}")