# Financial Analysis and Trading
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import yfinance as yf
from datetime import datetime, timedelta
import requests
import json

def stock_market_analysis():
    """Stock market data analysis and technical indicators"""
    try:
        # Simulate stock price data (normally would use yfinance)
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
        
        # Generate realistic stock price data
        n_days = len(dates)
        price_base = 100
        returns = np.random.normal(0.001, 0.02, n_days)  # Daily returns
        prices = [price_base]
        
        for i in range(1, n_days):
            price = prices[-1] * (1 + returns[i])
            prices.append(max(price, 1))  # Ensure price stays positive
        
        # Create DataFrame
        stock_data = pd.DataFrame({
            'Date': dates,
            'Open': [p * np.random.uniform(0.98, 1.02) for p in prices],
            'High': [p * np.random.uniform(1.00, 1.05) for p in prices],
            'Low': [p * np.random.uniform(0.95, 1.00) for p in prices],
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, n_days)
        })
        
        # Technical indicators
        def calculate_sma(prices, window):
            return prices.rolling(window=window).mean()
        
        def calculate_ema(prices, window):
            return prices.ewm(span=window).mean()
        
        def calculate_rsi(prices, window=14):
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        
        def calculate_bollinger_bands(prices, window=20, std_dev=2):
            sma = calculate_sma(prices, window)
            std = prices.rolling(window=window).std()
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            return upper_band, sma, lower_band
        
        def calculate_macd(prices, fast=12, slow=26, signal=9):
            ema_fast = calculate_ema(prices, fast)
            ema_slow = calculate_ema(prices, slow)
            macd_line = ema_fast - ema_slow
            signal_line = calculate_ema(macd_line, signal)
            histogram = macd_line - signal_line
            return macd_line, signal_line, histogram
        
        # Calculate indicators
        stock_data['SMA_20'] = calculate_sma(stock_data['Close'], 20)
        stock_data['SMA_50'] = calculate_sma(stock_data['Close'], 50)
        stock_data['EMA_20'] = calculate_ema(stock_data['Close'], 20)
        stock_data['RSI'] = calculate_rsi(stock_data['Close'])
        
        upper_bb, middle_bb, lower_bb = calculate_bollinger_bands(stock_data['Close'])
        stock_data['BB_Upper'] = upper_bb
        stock_data['BB_Middle'] = middle_bb
        stock_data['BB_Lower'] = lower_bb
        
        macd, signal, histogram = calculate_macd(stock_data['Close'])
        stock_data['MACD'] = macd
        stock_data['MACD_Signal'] = signal
        stock_data['MACD_Histogram'] = histogram
        
        # Trading signals
        def generate_signals(data):
            signals = []
            
            for i in range(len(data)):
                if i < 50:  # Need enough data for indicators
                    signals.append('hold')
                    continue
                
                # Simple moving average crossover
                if (data['SMA_20'].iloc[i] > data['SMA_50'].iloc[i] and 
                    data['SMA_20'].iloc[i-1] <= data['SMA_50'].iloc[i-1]):
                    signals.append('buy')
                elif (data['SMA_20'].iloc[i] < data['SMA_50'].iloc[i] and 
                      data['SMA_20'].iloc[i-1] >= data['SMA_50'].iloc[i-1]):
                    signals.append('sell')
                # RSI oversold/overbought
                elif data['RSI'].iloc[i] < 30:
                    signals.append('buy')
                elif data['RSI'].iloc[i] > 70:
                    signals.append('sell')
                else:
                    signals.append('hold')
            
            return signals
        
        stock_data['Signal'] = generate_signals(stock_data)
        
        # Performance metrics
        total_return = (stock_data['Close'].iloc[-1] / stock_data['Close'].iloc[0] - 1) * 100
        volatility = stock_data['Close'].pct_change().std() * np.sqrt(252) * 100
        max_price = stock_data['Close'].max()
        min_price = stock_data['Close'].min()
        
        # Signal distribution
        signal_counts = stock_data['Signal'].value_counts()
        
        return {
            'data_points': len(stock_data),
            'total_return_percent': total_return,
            'volatility_percent': volatility,
            'max_price': max_price,
            'min_price': min_price,
            'technical_indicators': 8,  # SMA, EMA, RSI, BB, MACD
            'buy_signals': signal_counts.get('buy', 0),
            'sell_signals': signal_counts.get('sell', 0),
            'hold_signals': signal_counts.get('hold', 0)
        }
        
    except Exception as e:
        return {'error': str(e)}

def portfolio_optimization():
    """Portfolio optimization and risk management"""
    try:
        # Simulate portfolio of 10 stocks
        np.random.seed(42)
        n_assets = 10
        n_days = 252  # One trading year
        
        # Generate random returns for each asset
        mean_returns = np.random.uniform(0.05, 0.15, n_assets)  # 5% to 15% annual return
        volatilities = np.random.uniform(0.10, 0.30, n_assets)   # 10% to 30% volatility
        
        # Generate correlation matrix
        correlation_matrix = np.random.uniform(-0.5, 0.8, (n_assets, n_assets))
        correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
        np.fill_diagonal(correlation_matrix, 1.0)
        
        # Ensure positive semidefinite
        eigenvals, eigenvecs = np.linalg.eigh(correlation_matrix)
        eigenvals[eigenvals < 0] = 0.01
        correlation_matrix = eigenvecs @ np.diag(eigenvals) @ eigenvecs.T
        
        # Create covariance matrix
        cov_matrix = np.outer(volatilities, volatilities) * correlation_matrix
        
        # Portfolio optimization using mean-variance optimization
        def portfolio_performance(weights, mean_returns, cov_matrix):
            returns = np.sum(mean_returns * weights)
            std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            return returns, std
        
        def negative_sharpe(weights, mean_returns, cov_matrix, risk_free_rate=0.02):
            returns, std = portfolio_performance(weights, mean_returns, cov_matrix)
            sharpe = (returns - risk_free_rate) / std
            return -sharpe
        
        # Optimization constraints
        from scipy.optimize import minimize
        
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_weights = np.array([1/n_assets] * n_assets)
        
        # Optimize for maximum Sharpe ratio
        opt_result = minimize(negative_sharpe, initial_weights, 
                            args=(mean_returns, cov_matrix),
                            method='SLSQP', bounds=bounds, constraints=constraints)
        
        optimal_weights = opt_result.x
        opt_return, opt_volatility = portfolio_performance(optimal_weights, mean_returns, cov_matrix)
        opt_sharpe = (opt_return - 0.02) / opt_volatility
        
        # Risk metrics
        def calculate_var(returns, confidence_level=0.05):
            """Calculate Value at Risk"""
            return np.percentile(returns, confidence_level * 100)
        
        def calculate_cvar(returns, confidence_level=0.05):
            """Calculate Conditional Value at Risk"""
            var = calculate_var(returns, confidence_level)
            return returns[returns <= var].mean()
        
        # Simulate portfolio returns
        portfolio_returns = np.random.multivariate_normal(
            mean_returns / 252, cov_matrix / 252, n_days
        )
        weighted_returns = np.sum(portfolio_returns * optimal_weights, axis=1)
        
        var_5 = calculate_var(weighted_returns, 0.05)
        cvar_5 = calculate_cvar(weighted_returns, 0.05)
        
        # Efficient frontier calculation (simplified)
        def efficient_frontier(mean_returns, cov_matrix, n_portfolios=100):
            results = []
            target_returns = np.linspace(mean_returns.min(), mean_returns.max(), n_portfolios)
            
            for target in target_returns:
                # Constraint: target return
                constraints = [
                    {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                    {'type': 'eq', 'fun': lambda x, target=target: np.sum(x * mean_returns) - target}
                ]
                
                # Minimize portfolio variance
                result = minimize(lambda x: np.dot(x.T, np.dot(cov_matrix, x)),
                                initial_weights, method='SLSQP',
                                bounds=bounds, constraints=constraints)
                
                if result.success:
                    weights = result.x
                    ret, vol = portfolio_performance(weights, mean_returns, cov_matrix)
                    results.append({'return': ret, 'volatility': vol, 'weights': weights})
            
            return results
        
        efficient_portfolios = efficient_frontier(mean_returns, cov_matrix, 20)
        
        # Asset allocation analysis
        asset_allocation = {
            'large_cap': np.sum(optimal_weights[:4]),
            'mid_cap': np.sum(optimal_weights[4:7]),
            'small_cap': np.sum(optimal_weights[7:])
        }
        
        # Rebalancing simulation
        def rebalancing_analysis(initial_weights, target_weights, threshold=0.05):
            current_weights = initial_weights.copy()
            rebalance_events = 0
            
            # Simulate weight drift over time
            for day in range(n_days):
                # Random weight changes
                weight_changes = np.random.normal(0, 0.01, n_assets)
                current_weights *= (1 + weight_changes)
                current_weights /= current_weights.sum()  # Normalize
                
                # Check if rebalancing is needed
                max_deviation = np.max(np.abs(current_weights - target_weights))
                if max_deviation > threshold:
                    current_weights = target_weights.copy()
                    rebalance_events += 1
            
            return rebalance_events
        
        rebalance_count = rebalancing_analysis(initial_weights, optimal_weights)
        
        return {
            'assets_in_portfolio': n_assets,
            'optimization_successful': opt_result.success,
            'optimal_return': opt_return,
            'optimal_volatility': opt_volatility,
            'optimal_sharpe_ratio': opt_sharpe,
            'var_5_percent': var_5,
            'cvar_5_percent': cvar_5,
            'efficient_portfolios': len(efficient_portfolios),
            'rebalancing_events': rebalance_count,
            'max_weight': np.max(optimal_weights),
            'diversification_ratio': 1 / np.sum(optimal_weights ** 2)
        }
        
    except Exception as e:
        return {'error': str(e)}

def cryptocurrency_analysis():
    """Cryptocurrency market analysis"""
    try:
        # Simulate cryptocurrency data
        cryptos = ['BTC', 'ETH', 'ADA', 'DOT', 'LINK', 'UNI', 'MATIC', 'AVAX']
        
        # Simulate price data for each crypto
        crypto_data = {}
        np.random.seed(42)
        
        for crypto in cryptos:
            # Generate more volatile returns for crypto
            returns = np.random.normal(0.002, 0.05, 365)  # Higher volatility
            prices = [1000 * (1 + np.random.uniform(-0.5, 2))]  # Starting prices
            
            for ret in returns:
                price = prices[-1] * (1 + ret)
                prices.append(max(price, 1))
            
            crypto_data[crypto] = {
                'prices': prices[1:],  # Remove initial price
                'volume': np.random.randint(1000000, 100000000, 365),
                'market_cap': [p * np.random.randint(10000000, 100000000) for p in prices[1:]]
            }
        
        # Market analysis
        def analyze_crypto_market(data):
            analysis = {}
            
            for crypto, info in data.items():
                prices = np.array(info['prices'])
                returns = np.diff(prices) / prices[:-1]
                
                analysis[crypto] = {
                    'total_return': (prices[-1] / prices[0] - 1) * 100,
                    'volatility': np.std(returns) * np.sqrt(365) * 100,
                    'max_price': np.max(prices),
                    'min_price': np.min(prices),
                    'avg_volume': np.mean(info['volume']),
                    'current_market_cap': info['market_cap'][-1]
                }
            
            return analysis
        
        market_analysis = analyze_crypto_market(crypto_data)
        
        # Correlation analysis
        price_matrix = np.array([data['prices'] for data in crypto_data.values()]).T
        returns_matrix = np.diff(price_matrix, axis=0) / price_matrix[:-1]
        correlation_matrix = np.corrcoef(returns_matrix.T)
        
        # DeFi metrics simulation
        defi_protocols = {
            'Uniswap': {'tvl': 5000000000, 'volume_24h': 1000000000},
            'Aave': {'tvl': 8000000000, 'volume_24h': 500000000},
            'Compound': {'tvl': 3000000000, 'volume_24h': 300000000},
            'MakerDAO': {'tvl': 6000000000, 'volume_24h': 200000000}
        }
        
        total_defi_tvl = sum(protocol['tvl'] for protocol in defi_protocols.values())
        
        # Yield farming simulation
        def simulate_yield_farming(initial_investment=10000, apy=0.15, days=365):
            daily_rate = apy / 365
            final_value = initial_investment * (1 + daily_rate) ** days
            return final_value - initial_investment
        
        yield_profit = simulate_yield_farming()
        
        # NFT market simulation
        nft_collections = {
            'CryptoPunks': {'floor_price': 50, 'volume': 500},
            'BAYC': {'floor_price': 30, 'volume': 800},
            'Azuki': {'floor_price': 15, 'volume': 300},
            'CloneX': {'floor_price': 10, 'volume': 200}
        }
        
        total_nft_volume = sum(col['volume'] for col in nft_collections.values())
        
        # Market dominance calculation
        total_market_cap = sum(analysis['current_market_cap'] for analysis in market_analysis.values())
        btc_dominance = market_analysis['BTC']['current_market_cap'] / total_market_cap * 100
        
        # Sentiment analysis (simulated)
        sentiment_indicators = {
            'fear_greed_index': np.random.randint(10, 90),
            'social_sentiment': np.random.choice(['bullish', 'bearish', 'neutral']),
            'whale_activity': np.random.choice(['high', 'medium', 'low']),
            'institutional_interest': np.random.uniform(0.1, 0.8)
        }
        
        return {
            'cryptocurrencies_analyzed': len(cryptos),
            'total_market_cap': total_market_cap,
            'btc_dominance': btc_dominance,
            'highest_return_crypto': max(market_analysis.keys(), 
                                       key=lambda x: market_analysis[x]['total_return']),
            'most_volatile_crypto': max(market_analysis.keys(), 
                                      key=lambda x: market_analysis[x]['volatility']),
            'average_correlation': np.mean(correlation_matrix[np.triu_indices_from(correlation_matrix, k=1)]),
            'defi_protocols': len(defi_protocols),
            'total_defi_tvl': total_defi_tvl,
            'yield_farming_profit': yield_profit,
            'nft_collections': len(nft_collections),
            'total_nft_volume': total_nft_volume,
            'fear_greed_index': sentiment_indicators['fear_greed_index']
        }
        
    except Exception as e:
        return {'error': str(e)}

def algorithmic_trading():
    """Algorithmic trading strategies"""
    try:
        # Simulate market data
        np.random.seed(42)
        n_days = 1000
        prices = [100]
        
        # Generate price series with trends and volatility
        for i in range(n_days - 1):
            trend = 0.0005 * (1 + 0.1 * np.sin(i / 50))  # Cyclical trend
            noise = np.random.normal(0, 0.02)
            price_change = trend + noise
            new_price = prices[-1] * (1 + price_change)
            prices.append(max(new_price, 1))
        
        prices = np.array(prices)
        
        # Strategy 1: Mean Reversion
        def mean_reversion_strategy(prices, window=20, threshold=2):
            sma = pd.Series(prices).rolling(window).mean().values
            std = pd.Series(prices).rolling(window).std().values
            
            positions = np.zeros(len(prices))
            
            for i in range(window, len(prices)):
                z_score = (prices[i] - sma[i]) / std[i]
                
                if z_score < -threshold:  # Price below mean - buy
                    positions[i] = 1
                elif z_score > threshold:  # Price above mean - sell
                    positions[i] = -1
                else:
                    positions[i] = 0
            
            return positions
        
        # Strategy 2: Momentum
        def momentum_strategy(prices, short_window=10, long_window=30):
            short_ma = pd.Series(prices).rolling(short_window).mean().values
            long_ma = pd.Series(prices).rolling(long_window).mean().values
            
            positions = np.zeros(len(prices))
            
            for i in range(long_window, len(prices)):
                if short_ma[i] > long_ma[i] and short_ma[i-1] <= long_ma[i-1]:
                    positions[i] = 1  # Buy signal
                elif short_ma[i] < long_ma[i] and short_ma[i-1] >= long_ma[i-1]:
                    positions[i] = -1  # Sell signal
                else:
                    positions[i] = positions[i-1]  # Hold position
            
            return positions
        
        # Strategy 3: Pairs Trading
        def pairs_trading_strategy(prices1, prices2, window=30, threshold=2):
            # Calculate spread
            spread = prices1 - prices2
            spread_mean = pd.Series(spread).rolling(window).mean().values
            spread_std = pd.Series(spread).rolling(window).std().values
            
            positions = np.zeros(len(prices1))
            
            for i in range(window, len(prices1)):
                if spread_std[i] > 0:
                    z_score = (spread[i] - spread_mean[i]) / spread_std[i]
                    
                    if z_score > threshold:  # Spread too high - sell pair
                        positions[i] = -1
                    elif z_score < -threshold:  # Spread too low - buy pair
                        positions[i] = 1
                    else:
                        positions[i] = 0
            
            return positions
        
        # Execute strategies
        mr_positions = mean_reversion_strategy(prices)
        momentum_positions = momentum_strategy(prices)
        
        # Generate second price series for pairs trading
        prices2 = prices * (1 + np.random.normal(0, 0.01, len(prices)))
        pairs_positions = pairs_trading_strategy(prices, prices2)
        
        # Calculate returns for each strategy
        def calculate_strategy_returns(prices, positions, transaction_cost=0.001):
            returns = np.diff(prices) / prices[:-1]
            strategy_returns = positions[1:] * returns - np.abs(np.diff(positions)) * transaction_cost
            
            cumulative_return = np.prod(1 + strategy_returns) - 1
            sharpe_ratio = np.mean(strategy_returns) / np.std(strategy_returns) * np.sqrt(252) if np.std(strategy_returns) > 0 else 0
            max_drawdown = self.calculate_max_drawdown(np.cumprod(1 + strategy_returns))
            
            return {
                'total_return': cumulative_return * 100,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown * 100,
                'win_rate': np.mean(strategy_returns > 0) * 100
            }
        
        # Helper function for max drawdown
        def calculate_max_drawdown(cumulative_returns):
            peak = np.maximum.accumulate(cumulative_returns)
            drawdown = (cumulative_returns - peak) / peak
            return np.min(drawdown)
        
        # Fixed version without self reference
        def calculate_strategy_returns_fixed(prices, positions, transaction_cost=0.001):
            returns = np.diff(prices) / prices[:-1]
            strategy_returns = positions[1:] * returns - np.abs(np.diff(positions)) * transaction_cost
            
            cumulative_return = np.prod(1 + strategy_returns) - 1
            sharpe_ratio = np.mean(strategy_returns) / np.std(strategy_returns) * np.sqrt(252) if np.std(strategy_returns) > 0 else 0
            
            # Calculate max drawdown
            cumulative_curve = np.cumprod(1 + strategy_returns)
            peak = np.maximum.accumulate(cumulative_curve)
            drawdown = (cumulative_curve - peak) / peak
            max_drawdown = np.min(drawdown)
            
            return {
                'total_return': cumulative_return * 100,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown * 100,
                'win_rate': np.mean(strategy_returns > 0) * 100
            }
        
        mr_performance = calculate_strategy_returns_fixed(prices, mr_positions)
        momentum_performance = calculate_strategy_returns_fixed(prices, momentum_positions)
        pairs_performance = calculate_strategy_returns_fixed(prices, pairs_positions)
        
        # Risk management metrics
        def risk_metrics(positions, prices):
            # Position sizing
            avg_position_size = np.mean(np.abs(positions[positions != 0]))
            
            # Number of trades
            trades = np.sum(np.abs(np.diff(positions)) > 0)
            
            # Time in market
            time_in_market = np.mean(positions != 0) * 100
            
            return {
                'average_position_size': avg_position_size,
                'total_trades': trades,
                'time_in_market_percent': time_in_market
            }
        
        mr_risk = risk_metrics(mr_positions, prices)
        momentum_risk = risk_metrics(momentum_positions, prices)
        pairs_risk = risk_metrics(pairs_positions, prices)
        
        # Portfolio of strategies
        combined_positions = (mr_positions + momentum_positions + pairs_positions) / 3
        combined_performance = calculate_strategy_returns_fixed(prices, combined_positions)
        
        return {
            'trading_days': n_days,
            'strategies_tested': 3,
            'mean_reversion_return': mr_performance['total_return'],
            'momentum_return': momentum_performance['total_return'],
            'pairs_trading_return': pairs_performance['total_return'],
            'combined_strategy_return': combined_performance['total_return'],
            'best_strategy_sharpe': max(mr_performance['sharpe_ratio'], 
                                      momentum_performance['sharpe_ratio'],
                                      pairs_performance['sharpe_ratio']),
            'total_trades_executed': mr_risk['total_trades'] + momentum_risk['total_trades'] + pairs_risk['total_trades'],
            'average_time_in_market': (mr_risk['time_in_market_percent'] + 
                                     momentum_risk['time_in_market_percent'] + 
                                     pairs_risk['time_in_market_percent']) / 3
        }
        
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    print("Financial analysis and trading operations...")
    
    # Stock market analysis
    stock_result = stock_market_analysis()
    if 'error' not in stock_result:
        print(f"Stock Analysis: {stock_result['total_return_percent']:.2f}% return, {stock_result['buy_signals']} buy signals")
    
    # Portfolio optimization
    portfolio_result = portfolio_optimization()
    if 'error' not in portfolio_result:
        print(f"Portfolio: {portfolio_result['optimal_sharpe_ratio']:.3f} Sharpe ratio, {portfolio_result['rebalancing_events']} rebalances")
    
    # Cryptocurrency analysis
    crypto_result = cryptocurrency_analysis()
    if 'error' not in crypto_result:
        print(f"Crypto: {crypto_result['btc_dominance']:.1f}% BTC dominance, ${crypto_result['total_defi_tvl']/1e9:.1f}B DeFi TVL")
    
    # Algorithmic trading
    algo_result = algorithmic_trading()
    if 'error' not in algo_result:
        print(f"Algo Trading: {algo_result['combined_strategy_return']:.2f}% return, {algo_result['total_trades_executed']} trades")