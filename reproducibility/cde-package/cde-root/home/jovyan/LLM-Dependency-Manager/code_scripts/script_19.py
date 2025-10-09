# Machine Learning and AI
import sklearn
from sklearn.datasets import make_classification, make_regression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import torch
import torch.nn as nn
import torch.optim as optim
import xgboost as xgb
import numpy as np

def sklearn_classification():
    """Scikit-learn classification example"""
    # Generate sample data
    X, y = make_classification(n_samples=1000, n_features=20, n_informative=10, 
                              n_redundant=5, n_classes=3, random_state=42)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train multiple models
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
        'LogisticRegression': LogisticRegression(random_state=42, max_iter=1000),
        'SVM': SVC(random_state=42)
    }
    
    results = {}
    for name, model in models.items():
        if name == 'SVM':
            model.fit(X_train_scaled, y_train)
            predictions = model.predict(X_test_scaled)
        else:
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)
        
        accuracy = accuracy_score(y_test, predictions)
        results[name] = accuracy
    
    return results

def sklearn_regression():
    """Scikit-learn regression example"""
    # Generate sample data
    X, y = make_regression(n_samples=1000, n_features=10, noise=0.1, random_state=42)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train models
    models = {
        'LinearRegression': LinearRegression(),
        'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
    }
    
    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        results[name] = mse
    
    return results

def tensorflow_neural_network():
    """TensorFlow/Keras neural network"""
    try:
        # Generate sample data
        X, y = make_classification(n_samples=1000, n_features=20, n_classes=2, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Normalize data
        X_train = X_train.astype('float32')
        X_test = X_test.astype('float32')
        X_train = (X_train - X_train.mean()) / X_train.std()
        X_test = (X_test - X_test.mean()) / X_test.std()
        
        # Build model
        model = keras.Sequential([
            layers.Dense(64, activation='relu', input_shape=(20,)),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(1, activation='sigmoid')
        ])
        
        # Compile model
        model.compile(optimizer='adam',
                     loss='binary_crossentropy',
                     metrics=['accuracy'])
        
        # Train model
        history = model.fit(X_train, y_train, epochs=10, batch_size=32, 
                           validation_split=0.2, verbose=0)
        
        # Evaluate model
        test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
        
        return {
            'test_accuracy': test_accuracy,
            'epochs_trained': len(history.history['loss']),
            'final_loss': history.history['loss'][-1]
        }
    except Exception as e:
        return {'error': str(e)}

def pytorch_neural_network():
    """PyTorch neural network"""
    try:
        # Generate sample data
        X, y = make_classification(n_samples=1000, n_features=10, n_classes=2, random_state=42)
        X = torch.FloatTensor(X)
        y = torch.FloatTensor(y)
        
        # Define neural network
        class SimpleNN(nn.Module):
            def __init__(self, input_size, hidden_size, output_size):
                super(SimpleNN, self).__init__()
                self.fc1 = nn.Linear(input_size, hidden_size)
                self.relu = nn.ReLU()
                self.fc2 = nn.Linear(hidden_size, output_size)
                self.sigmoid = nn.Sigmoid()
            
            def forward(self, x):
                x = self.fc1(x)
                x = self.relu(x)
                x = self.fc2(x)
                x = self.sigmoid(x)
                return x
        
        # Initialize model
        model = SimpleNN(10, 20, 1)
        criterion = nn.BCELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        
        # Training loop
        losses = []
        for epoch in range(100):
            optimizer.zero_grad()
            outputs = model(X)
            loss = criterion(outputs.squeeze(), y)
            loss.backward()
            optimizer.step()
            losses.append(loss.item())
        
        # Final accuracy
        with torch.no_grad():
            outputs = model(X)
            predicted = (outputs.squeeze() > 0.5).float()
            accuracy = (predicted == y).float().mean().item()
        
        return {
            'final_accuracy': accuracy,
            'epochs_trained': 100,
            'final_loss': losses[-1]
        }
    except Exception as e:
        return {'error': str(e)}

def xgboost_example():
    """XGBoost example"""
    try:
        # Generate sample data
        X, y = make_classification(n_samples=1000, n_features=15, n_classes=2, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Create DMatrix for XGBoost
        dtrain = xgb.DMatrix(X_train, label=y_train)
        dtest = xgb.DMatrix(X_test, label=y_test)
        
        # Set parameters
        params = {
            'objective': 'binary:logistic',
            'eval_metric': 'logloss',
            'max_depth': 6,
            'learning_rate': 0.1,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'seed': 42
        }
        
        # Train model
        model = xgb.train(params, dtrain, num_boost_round=100, 
                         evals=[(dtest, 'test')], verbose_eval=False)
        
        # Make predictions
        predictions = model.predict(dtest)
        predicted_labels = (predictions > 0.5).astype(int)
        accuracy = accuracy_score(y_test, predicted_labels)
        
        return {
            'accuracy': accuracy,
            'num_boost_rounds': 100,
            'feature_importance': len(model.get_score())
        }
    except Exception as e:
        return {'error': str(e)}

def cross_validation_example():
    """Cross-validation example"""
    # Generate sample data
    X, y = make_classification(n_samples=500, n_features=10, n_classes=2, random_state=42)
    
    # Models to compare
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=50, random_state=42),
        'LogisticRegression': LogisticRegression(random_state=42, max_iter=1000),
    }
    
    cv_results = {}
    for name, model in models.items():
        scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
        cv_results[name] = {
            'mean_accuracy': scores.mean(),
            'std_accuracy': scores.std(),
            'scores': scores.tolist()
        }
    
    return cv_results

def feature_engineering_example():
    """Feature engineering and preprocessing"""
    # Create sample dataset with mixed data types
    np.random.seed(42)
    n_samples = 1000
    
    # Numerical features
    numerical_features = np.random.randn(n_samples, 3)
    
    # Categorical features
    categories = ['A', 'B', 'C', 'D']
    categorical_feature = np.random.choice(categories, n_samples)
    
    # Label encoding
    label_encoder = LabelEncoder()
    categorical_encoded = label_encoder.fit_transform(categorical_feature)
    
    # Combine features
    X = np.column_stack([numerical_features, categorical_encoded])
    y = (X[:, 0] + X[:, 1] > 0).astype(int)  # Simple target
    
    # Feature scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train model with processed features
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    scores = cross_val_score(model, X_scaled, y, cv=3, scoring='accuracy')
    
    return {
        'samples': n_samples,
        'features': X.shape[1],
        'categories': len(categories),
        'cv_accuracy': scores.mean()
    }

if __name__ == "__main__":
    print("Machine learning operations...")
    
    # Scikit-learn classification
    classification_results = sklearn_classification()
    print(f"Classification accuracies: {classification_results}")
    
    # Scikit-learn regression
    regression_results = sklearn_regression()
    print(f"Regression MSE scores: {regression_results}")
    
    # TensorFlow/Keras
    tf_results = tensorflow_neural_network()
    if 'error' not in tf_results:
        print(f"TensorFlow accuracy: {tf_results['test_accuracy']:.4f}")
    
    # PyTorch
    pytorch_results = pytorch_neural_network()
    if 'error' not in pytorch_results:
        print(f"PyTorch accuracy: {pytorch_results['final_accuracy']:.4f}")
    
    # XGBoost
    xgb_results = xgboost_example()
    if 'error' not in xgb_results:
        print(f"XGBoost accuracy: {xgb_results['accuracy']:.4f}")
    
    # Cross-validation
    cv_results = cross_validation_example()
    print(f"Cross-validation completed for {len(cv_results)} models")
    
    # Feature engineering
    fe_results = feature_engineering_example()
    print(f"Feature engineering: {fe_results['features']} features, {fe_results['cv_accuracy']:.4f} accuracy")