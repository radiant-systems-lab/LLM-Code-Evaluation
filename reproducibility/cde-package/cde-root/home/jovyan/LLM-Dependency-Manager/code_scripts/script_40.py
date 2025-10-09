# Time Series Analysis and Forecasting
import numpy as np
import pandas as pd
from scipy import stats
from scipy.fft import fft, fftfreq
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

def time_series_decomposition():
    """Time series decomposition and trend analysis"""
    try:
        # Generate synthetic time series data
        np.random.seed(42)
        n_points = 1000
        time_index = pd.date_range('2020-01-01', periods=n_points, freq='D')
        
        # Components
        trend = np.linspace(100, 200, n_points)  # Linear trend
        seasonal = 10 * np.sin(2 * np.pi * np.arange(n_points) / 365.25)  # Annual seasonality
        weekly = 5 * np.sin(2 * np.pi * np.arange(n_points) / 7)  # Weekly seasonality
        noise = np.random.normal(0, 5, n_points)  # Random noise
        
        # Combine components
        ts_data = trend + seasonal + weekly + noise
        
        # Create time series DataFrame
        ts_df = pd.DataFrame({
            'date': time_index,
            'value': ts_data,
            'trend': trend,
            'seasonal': seasonal + weekly,
            'noise': noise
        })
        ts_df.set_index('date', inplace=True)
        
        # Classical decomposition
        def classical_decomposition(series, period=365):
            # Moving average for trend
            trend_ma = series.rolling(window=period, center=True).mean()
            
            # Detrended series
            detrended = series - trend_ma
            
            # Seasonal component (average for each period)
            seasonal_avg = detrended.groupby(detrended.index.dayofyear).mean()
            seasonal_comp = detrended.copy()
            
            for i in range(len(seasonal_comp)):
                day_of_year = seasonal_comp.index[i].dayofyear
                if day_of_year in seasonal_avg.index:
                    seasonal_comp.iloc[i] = seasonal_avg[day_of_year]
                else:
                    seasonal_comp.iloc[i] = 0
            
            # Remainder
            remainder = series - trend_ma - seasonal_comp
            
            return trend_ma, seasonal_comp, remainder
        
        trend_est, seasonal_est, remainder_est = classical_decomposition(ts_df['value'])
        
        # STL decomposition (simplified)
        def stl_decomposition(series, seasonal_length=365):
            # Simplified STL using rolling statistics
            # Seasonal component
            seasonal = series.copy()
            for i in range(len(seasonal)):
                day_of_year = seasonal.index[i].dayofyear
                same_days = series[series.index.dayofyear == day_of_year]
                seasonal.iloc[i] = same_days.median()
            
            # Trend component (LOESS approximation using rolling median)
            trend = (series - seasonal).rolling(window=30, center=True).median()
            
            # Remainder
            remainder = series - trend - seasonal
            
            return trend, seasonal, remainder
        
        stl_trend, stl_seasonal, stl_remainder = stl_decomposition(ts_df['value'])
        
        # Decomposition quality metrics
        def decomposition_quality(original, trend, seasonal, remainder):
            # Remove NaN values for comparison
            mask = ~(pd.isna(trend) | pd.isna(seasonal) | pd.isna(remainder))
            
            if mask.sum() == 0:
                return 0, 0, 0
            
            original_clean = original[mask]
            reconstructed = (trend + seasonal + remainder)[mask]
            
            mse = mean_squared_error(original_clean, reconstructed)
            
            # Variance explained by each component
            trend_var = np.var(trend[mask]) / np.var(original_clean) if np.var(original_clean) > 0 else 0
            seasonal_var = np.var(seasonal[mask]) / np.var(original_clean) if np.var(original_clean) > 0 else 0
            
            return mse, trend_var, seasonal_var
        
        classical_mse, classical_trend_var, classical_seasonal_var = decomposition_quality(
            ts_df['value'], trend_est, seasonal_est, remainder_est
        )
        
        stl_mse, stl_trend_var, stl_seasonal_var = decomposition_quality(
            ts_df['value'], stl_trend, stl_seasonal, stl_remainder
        )
        
        # Seasonality detection
        def detect_seasonality(series, max_period=365):
            # Autocorrelation function
            autocorr = [series.autocorr(lag=lag) for lag in range(1, min(max_period + 1, len(series) // 2))]
            
            # Find peaks in autocorrelation
            peaks = []
            for i in range(1, len(autocorr) - 1):
                if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1] and autocorr[i] > 0.3:
                    peaks.append((i + 1, autocorr[i]))
            
            # Sort by correlation strength
            peaks.sort(key=lambda x: x[1], reverse=True)
            
            return peaks[:5]  # Top 5 seasonal patterns
        
        seasonal_patterns = detect_seasonality(ts_df['value'])
        
        # Trend analysis
        def analyze_trend(series):
            # Linear trend
            x = np.arange(len(series))
            mask = ~pd.isna(series)
            
            if mask.sum() < 2:
                return 0, 0, 'no_trend'
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x[mask], series[mask])
            
            # Trend classification
            if p_value < 0.05:
                if slope > 0:
                    trend_type = 'increasing'
                else:
                    trend_type = 'decreasing'
            else:
                trend_type = 'no_trend'
            
            return slope, r_value**2, trend_type
        
        trend_slope, trend_r2, trend_type = analyze_trend(ts_df['value'])
        
        return {
            'time_series_length': len(ts_df),
            'decomposition_methods': 2,
            'classical_mse': classical_mse,
            'stl_mse': stl_mse,
            'trend_variance_explained': classical_trend_var,
            'seasonal_variance_explained': classical_seasonal_var,
            'seasonal_patterns_detected': len(seasonal_patterns),
            'strongest_seasonal_period': seasonal_patterns[0][0] if seasonal_patterns else None,
            'strongest_seasonal_correlation': seasonal_patterns[0][1] if seasonal_patterns else 0,
            'trend_slope': trend_slope,
            'trend_r_squared': trend_r2,
            'trend_type': trend_type
        }
        
    except Exception as e:
        return {'error': str(e)}

def arima_modeling():
    """ARIMA and related time series models"""
    try:
        # Generate ARIMA-like data
        np.random.seed(42)
        n = 500
        
        # AR(2) process: X_t = 0.5*X_{t-1} + 0.3*X_{t-2} + ε_t
        ar_coeffs = [0.5, 0.3]
        ar_data = [0, 0]  # Initial values
        
        for t in range(2, n):
            noise = np.random.normal(0, 1)
            value = ar_coeffs[0] * ar_data[t-1] + ar_coeffs[1] * ar_data[t-2] + noise
            ar_data.append(value)
        
        ar_series = pd.Series(ar_data)
        
        # MA(2) process: X_t = ε_t + 0.4*ε_{t-1} + 0.2*ε_{t-2}
        ma_coeffs = [0.4, 0.2]
        noise_series = np.random.normal(0, 1, n)
        ma_data = []
        
        for t in range(n):
            value = noise_series[t]
            if t >= 1:
                value += ma_coeffs[0] * noise_series[t-1]
            if t >= 2:
                value += ma_coeffs[1] * noise_series[t-2]
            ma_data.append(value)
        
        ma_series = pd.Series(ma_data)
        
        # ARIMA(1,1,1) process
        # First create AR(1) process, then difference, then apply MA
        raw_data = [0]
        for t in range(1, n):
            noise = np.random.normal(0, 1)
            value = 0.7 * raw_data[t-1] + noise
            raw_data.append(value)
        
        # Integrate to make I(1)
        integrated_data = np.cumsum(raw_data)
        arima_series = pd.Series(integrated_data)
        
        # Stationarity tests
        def adf_test(series):
            # Simplified Augmented Dickey-Fuller test
            # Using differencing approach
            diff_series = series.diff().dropna()
            
            # Test if mean is significantly different from zero
            t_stat, p_value = stats.ttest_1samp(diff_series, 0)
            
            # Simplified interpretation
            is_stationary = abs(t_stat) > 2.0  # Rough threshold
            
            return {
                'statistic': t_stat,
                'p_value': p_value,
                'is_stationary': is_stationary
            }
        
        ar_adf = adf_test(ar_series)
        ma_adf = adf_test(ma_series)
        arima_adf = adf_test(arima_series)
        
        # Model identification
        def calculate_acf_pacf(series, max_lags=20):
            # Autocorrelation Function
            acf = [series.autocorr(lag=lag) for lag in range(max_lags + 1)]
            
            # Partial Autocorrelation Function (simplified)
            pacf = [1.0]  # PACF at lag 0 is always 1
            
            for k in range(1, max_lags + 1):
                # Use Yule-Walker equations (simplified)
                if k == 1:
                    pacf.append(acf[1])
                else:
                    # Approximate PACF using linear regression
                    y = series[k:].values
                    X = np.column_stack([series[i:-(k-i)].values for i in range(k)])
                    
                    if len(y) > k and X.shape[0] > 0:
                        try:
                            reg = LinearRegression().fit(X, y)
                            pacf.append(reg.coef_[-1])  # Last coefficient
                        except:
                            pacf.append(0)
                    else:
                        pacf.append(0)
            
            return acf, pacf
        
        ar_acf, ar_pacf = calculate_acf_pacf(ar_series)
        ma_acf, ma_pacf = calculate_acf_pacf(ma_series)
        
        # Model parameter estimation (Method of Moments)
        def estimate_ar_parameters(series, order):
            acf_values = [series.autocorr(lag=lag) for lag in range(order + 1)]
            
            if order == 1:
                return [acf_values[1]] if len(acf_values) > 1 else [0]
            elif order == 2:
                # Yule-Walker equations for AR(2)
                if len(acf_values) >= 3:
                    r1, r2 = acf_values[1], acf_values[2]
                    phi1 = r1 * (1 - r2) / (1 - r1**2) if (1 - r1**2) != 0 else 0
                    phi2 = (r2 - r1**2) / (1 - r1**2) if (1 - r1**2) != 0 else 0
                    return [phi1, phi2]
                else:
                    return [0, 0]
            else:
                return [0] * order
        
        ar_params_est = estimate_ar_parameters(ar_series, 2)
        
        # Model diagnostics
        def ljung_box_test(residuals, lags=10):
            # Simplified Ljung-Box test for serial correlation
            n = len(residuals)
            acf_residuals = []
            
            for lag in range(1, lags + 1):
                if lag < len(residuals):
                    correlation = np.corrcoef(residuals[:-lag], residuals[lag:])[0, 1]
                    if not np.isnan(correlation):
                        acf_residuals.append(correlation**2)
                    else:
                        acf_residuals.append(0)
            
            # Q statistic (simplified)
            Q = n * (n + 2) * sum([(acf / (n - k)) for k, acf in enumerate(acf_residuals, 1)])
            
            # Degrees of freedom (simplified)
            df = len(acf_residuals)
            p_value = 1 - stats.chi2.cdf(Q, df) if df > 0 else 1
            
            return Q, p_value
        
        # Forecast evaluation
        def evaluate_forecast(actual, predicted):
            mse = mean_squared_error(actual, predicted)
            mae = mean_absolute_error(actual, predicted)
            rmse = np.sqrt(mse)
            
            # MAPE (Mean Absolute Percentage Error)
            mape = np.mean(np.abs((actual - predicted) / actual)) * 100
            
            return {
                'mse': mse,
                'mae': mae,
                'rmse': rmse,
                'mape': mape
            }
        
        # Simple forecasting
        def simple_forecast(series, method='naive', steps=10):
            if method == 'naive':
                # Naive forecast (last value)
                forecast = [series.iloc[-1]] * steps
            elif method == 'drift':
                # Drift method
                slope = (series.iloc[-1] - series.iloc[0]) / (len(series) - 1)
                forecast = [series.iloc[-1] + slope * i for i in range(1, steps + 1)]
            elif method == 'ses':
                # Simple Exponential Smoothing
                alpha = 0.3
                last_smooth = series.iloc[0]
                for value in series[1:]:
                    last_smooth = alpha * value + (1 - alpha) * last_smooth
                forecast = [last_smooth] * steps
            else:
                forecast = [0] * steps
            
            return forecast
        
        # Generate forecasts
        train_size = int(0.8 * len(ar_series))
        train_data = ar_series[:train_size]
        test_data = ar_series[train_size:]
        
        naive_forecast = simple_forecast(train_data, 'naive', len(test_data))
        drift_forecast = simple_forecast(train_data, 'drift', len(test_data))
        ses_forecast = simple_forecast(train_data, 'ses', len(test_data))
        
        # Evaluate forecasts
        naive_metrics = evaluate_forecast(test_data, naive_forecast)
        drift_metrics = evaluate_forecast(test_data, drift_forecast)
        ses_metrics = evaluate_forecast(test_data, ses_forecast)
        
        return {
            'time_series_models': 3,  # AR, MA, ARIMA
            'ar_series_length': len(ar_series),
            'ar_stationary': ar_adf['is_stationary'],
            'ma_stationary': ma_adf['is_stationary'],
            'arima_stationary': arima_adf['is_stationary'],
            'ar_estimated_params': ar_params_est,
            'forecast_methods': 3,
            'naive_rmse': naive_metrics['rmse'],
            'drift_rmse': drift_metrics['rmse'],
            'ses_rmse': ses_metrics['rmse'],
            'best_forecast_method': min(
                [('naive', naive_metrics['rmse']), 
                 ('drift', drift_metrics['rmse']), 
                 ('ses', ses_metrics['rmse'])], 
                key=lambda x: x[1]
            )[0]
        }
        
    except Exception as e:
        return {'error': str(e)}

def spectral_analysis():
    """Frequency domain analysis and spectral methods"""
    try:
        # Generate signal with multiple frequencies
        np.random.seed(42)
        n_samples = 1000
        sampling_rate = 100  # Hz
        time = np.linspace(0, n_samples/sampling_rate, n_samples, endpoint=False)
        
        # Multi-frequency signal
        signal = (
            2 * np.sin(2 * np.pi * 5 * time) +     # 5 Hz component
            1.5 * np.sin(2 * np.pi * 15 * time) +   # 15 Hz component
            1 * np.sin(2 * np.pi * 25 * time) +     # 25 Hz component
            0.5 * np.random.randn(n_samples)         # Noise
        )
        
        # FFT analysis
        fft_values = fft(signal)
        fft_freq = fftfreq(n_samples, 1/sampling_rate)
        
        # Power spectral density
        power_spectrum = np.abs(fft_values)**2 / n_samples
        
        # Find peaks in spectrum
        def find_spectral_peaks(frequencies, power, threshold=0.1):
            # Only consider positive frequencies
            pos_mask = frequencies > 0
            pos_freq = frequencies[pos_mask]
            pos_power = power[pos_mask]
            
            peaks = []
            max_power = np.max(pos_power)
            
            for i in range(1, len(pos_power) - 1):
                if (pos_power[i] > pos_power[i-1] and 
                    pos_power[i] > pos_power[i+1] and 
                    pos_power[i] > threshold * max_power):
                    peaks.append((pos_freq[i], pos_power[i]))
            
            # Sort by power
            peaks.sort(key=lambda x: x[1], reverse=True)
            return peaks
        
        spectral_peaks = find_spectral_peaks(fft_freq, power_spectrum)
        
        # Periodogram
        def periodogram(signal, sampling_rate):
            N = len(signal)
            frequencies = np.fft.fftfreq(N, 1/sampling_rate)
            fft_signal = np.fft.fft(signal)
            
            # One-sided periodogram
            pos_mask = frequencies >= 0
            periodogram_values = (np.abs(fft_signal[pos_mask])**2 / (N * sampling_rate))
            
            # Double the values (except DC and Nyquist)
            periodogram_values[1:-1] *= 2
            
            return frequencies[pos_mask], periodogram_values
        
        period_freq, period_power = periodogram(signal, sampling_rate)
        
        # Spectral density estimation (Welch's method simulation)
        def welch_method(signal, nperseg=256, noverlap=128):
            # Simplified Welch's method
            n = len(signal)
            segments = []
            
            for i in range(0, n - nperseg + 1, nperseg - noverlap):
                segment = signal[i:i + nperseg]
                if len(segment) == nperseg:
                    # Apply Hanning window
                    windowed = segment * np.hanning(nperseg)
                    segments.append(windowed)
            
            if not segments:
                return np.array([0]), np.array([0])
            
            # Average periodograms
            freq = np.fft.fftfreq(nperseg, 1/sampling_rate)[:nperseg//2]
            psd_avg = np.zeros(len(freq))
            
            for segment in segments:
                fft_seg = np.fft.fft(segment)
                psd = np.abs(fft_seg[:nperseg//2])**2
                psd_avg += psd
            
            psd_avg /= len(segments)
            
            return freq, psd_avg
        
        welch_freq, welch_psd = welch_method(signal)
        
        # Coherence analysis (between signal and delayed version)
        def coherence_analysis(x, y, nperseg=256):
            # Cross-spectral density
            segments_x = []
            segments_y = []
            
            for i in range(0, len(x) - nperseg + 1, nperseg//2):
                seg_x = x[i:i + nperseg]
                seg_y = y[i:i + nperseg]
                
                if len(seg_x) == nperseg and len(seg_y) == nperseg:
                    segments_x.append(seg_x * np.hanning(nperseg))
                    segments_y.append(seg_y * np.hanning(nperseg))
            
            if not segments_x:
                return np.array([0]), np.array([0])
            
            freq = np.fft.fftfreq(nperseg, 1/sampling_rate)[:nperseg//2]
            Pxy = np.zeros(len(freq), dtype=complex)
            Pxx = np.zeros(len(freq))
            Pyy = np.zeros(len(freq))
            
            for seg_x, seg_y in zip(segments_x, segments_y):
                fft_x = np.fft.fft(seg_x)[:nperseg//2]
                fft_y = np.fft.fft(seg_y)[:nperseg//2]
                
                Pxy += fft_x * np.conj(fft_y)
                Pxx += np.abs(fft_x)**2
                Pyy += np.abs(fft_y)**2
            
            Pxy /= len(segments_x)
            Pxx /= len(segments_x)
            Pyy /= len(segments_x)
            
            # Coherence
            coherence = np.abs(Pxy)**2 / (Pxx * Pyy + 1e-12)  # Add small value to avoid division by zero
            
            return freq, coherence
        
        # Delayed version of signal
        delay = 10
        delayed_signal = np.roll(signal, delay)
        coherence_freq, coherence_values = coherence_analysis(signal, delayed_signal)
        
        # Spectogram (time-frequency analysis)
        def spectrogram(signal, nperseg=128, noverlap=64):
            n = len(signal)
            step = nperseg - noverlap
            n_windows = (n - nperseg) // step + 1
            
            freq = np.fft.fftfreq(nperseg, 1/sampling_rate)[:nperseg//2]
            time_windows = np.arange(n_windows) * step / sampling_rate
            
            spec = np.zeros((len(freq), n_windows))
            
            for i in range(n_windows):
                start = i * step
                end = start + nperseg
                
                if end <= n:
                    segment = signal[start:end] * np.hanning(nperseg)
                    fft_seg = np.fft.fft(segment)[:nperseg//2]
                    spec[:, i] = np.abs(fft_seg)**2
            
            return time_windows, freq, spec
        
        spec_time, spec_freq, spectrogram_data = spectrogram(signal)
        
        # Filter design and application
        def butter_lowpass_filter(signal, cutoff_freq, sampling_rate, order=4):
            # Simplified Butterworth filter (using FFT approach)
            fft_signal = np.fft.fft(signal)
            freq = np.fft.fftfreq(len(signal), 1/sampling_rate)
            
            # Create filter response
            normalized_freq = np.abs(freq) / (sampling_rate / 2)
            normalized_cutoff = cutoff_freq / (sampling_rate / 2)
            
            # Butterworth filter response
            filter_response = 1 / np.sqrt(1 + (normalized_freq / normalized_cutoff)**(2 * order))
            
            # Apply filter
            filtered_fft = fft_signal * filter_response
            filtered_signal = np.real(np.fft.ifft(filtered_fft))
            
            return filtered_signal
        
        # Apply low-pass filter
        filtered_signal = butter_lowpass_filter(signal, cutoff_freq=20, sampling_rate=sampling_rate)
        
        return {
            'signal_length': len(signal),
            'sampling_rate': sampling_rate,
            'spectral_peaks_detected': len(spectral_peaks),
            'dominant_frequency': spectral_peaks[0][0] if spectral_peaks else 0,
            'dominant_power': spectral_peaks[0][1] if spectral_peaks else 0,
            'frequency_resolution': sampling_rate / n_samples,
            'nyquist_frequency': sampling_rate / 2,
            'welch_segments': len(welch_psd),
            'max_coherence': np.max(coherence_values) if len(coherence_values) > 0 else 0,
            'spectrogram_time_windows': len(spec_time),
            'spectrogram_freq_bins': len(spec_freq),
            'filter_applied': True,
            'signal_energy_original': np.sum(signal**2),
            'signal_energy_filtered': np.sum(filtered_signal**2)
        }
        
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    print("Time series analysis and forecasting operations...")
    
    # Time series decomposition
    decomposition_result = time_series_decomposition()
    if 'error' not in decomposition_result:
        print(f"Decomposition: {decomposition_result['seasonal_patterns_detected']} seasonal patterns, trend {decomposition_result['trend_type']}")
    
    # ARIMA modeling
    arima_result = arima_modeling()
    if 'error' not in arima_result:
        print(f"ARIMA: Best forecast method {arima_result['best_forecast_method']}, RMSE {arima_result[arima_result['best_forecast_method'] + '_rmse']:.3f}")
    
    # Spectral analysis
    spectral_result = spectral_analysis()
    if 'error' not in spectral_result:
        print(f"Spectral: {spectral_result['spectral_peaks_detected']} peaks, dominant freq {spectral_result['dominant_frequency']:.1f} Hz")