#!/usr/bin/env python3
"""
Script 9: Time Series Analysis
Tests time series analysis and forecasting dependencies
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
import pmdarima as pm
from prophet import Prophet
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def analyze_timeseries():
    """Time series analysis and forecasting"""
    print("Starting time series analysis...")
    
    # Generate synthetic time series data
    np.random.seed(42)
    dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
    
    # Create time series with trend and seasonality
    trend = np.linspace(100, 200, len(dates))
    seasonal = 10 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25)
    noise = np.random.normal(0, 5, len(dates))
    values = trend + seasonal + noise
    
    # Create DataFrame
    ts_data = pd.DataFrame({
        'ds': dates,
        'y': values
    })
    ts_data.set_index('ds', inplace=True)
    
    print(f"Time series data: {len(ts_data)} daily observations")
    
    # Stationarity test
    result = adfuller(ts_data['y'])
    print(f"ADF Statistic: {result[0]:.4f}")
    print(f"p-value: {result[1]:.4f}")
    
    # Seasonal decomposition
    decomposition = seasonal_decompose(ts_data['y'], model='additive', period=365)
    
    # Plot decomposition
    fig, axes = plt.subplots(4, 1, figsize=(12, 10))
    
    ts_data['y'].plot(ax=axes[0], title='Original Time Series')
    decomposition.trend.plot(ax=axes[1], title='Trend')
    decomposition.seasonal.plot(ax=axes[2], title='Seasonal')
    decomposition.resid.plot(ax=axes[3], title='Residual')
    
    plt.tight_layout()
    plt.savefig('timeseries_decomposition.png')
    print("Decomposition saved to timeseries_decomposition.png")
    
    # ARIMA modeling
    print("\nFitting ARIMA model...")
    train_size = int(len(ts_data) * 0.8)
    train, test = ts_data[:train_size], ts_data[train_size:]
    
    # Auto ARIMA
    auto_model = pm.auto_arima(train['y'], 
                               seasonal=True, 
                               m=12,
                               stepwise=True,
                               suppress_warnings=True,
                               max_p=3, max_q=3)
    
    print(f"Best ARIMA order: {auto_model.order}")
    
    # Forecast
    forecast_steps = len(test)
    forecast, conf_int = auto_model.predict(n_periods=forecast_steps, return_conf_int=True)
    
    # Prophet forecasting
    print("\nFitting Prophet model...")
    prophet_data = ts_data.reset_index()
    prophet_data.columns = ['ds', 'y']
    
    prophet_train = prophet_data[:train_size]
    
    model = Prophet(daily_seasonality=False, yearly_seasonality=True)
    model.fit(prophet_train)
    
    future = model.make_future_dataframe(periods=forecast_steps)
    prophet_forecast = model.predict(future)
    
    # Plot forecasts
    plt.figure(figsize=(14, 6))
    
    plt.subplot(1, 2, 1)
    plt.plot(train.index, train['y'], label='Train', color='blue')
    plt.plot(test.index, test['y'], label='Test', color='green')
    plt.plot(test.index, forecast, label='ARIMA Forecast', color='red')
    plt.fill_between(test.index, conf_int[:, 0], conf_int[:, 1], alpha=0.2, color='red')
    plt.title('ARIMA Forecast')
    plt.legend()
    plt.xticks(rotation=45)
    
    plt.subplot(1, 2, 2)
    plt.plot(prophet_data['ds'], prophet_data['y'], label='Actual', color='blue')
    plt.plot(prophet_forecast['ds'], prophet_forecast['yhat'], label='Prophet Forecast', color='orange')
    plt.fill_between(prophet_forecast['ds'], 
                    prophet_forecast['yhat_lower'], 
                    prophet_forecast['yhat_upper'], 
                    alpha=0.2, color='orange')
    plt.title('Prophet Forecast')
    plt.legend()
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig('timeseries_forecasts.png')
    print("Forecasts saved to timeseries_forecasts.png")
    
    # Calculate metrics
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    
    mae_arima = mean_absolute_error(test['y'], forecast)
    mse_arima = mean_squared_error(test['y'], forecast)
    
    return {
        'data_points': len(ts_data),
        'train_size': train_size,
        'test_size': len(test),
        'arima_order': str(auto_model.order),
        'mae_arima': round(mae_arima, 4),
        'mse_arima': round(mse_arima, 4)
    }

if __name__ == "__main__":
    results = analyze_timeseries()
    print(f"\nTime series analysis complete: {results}")