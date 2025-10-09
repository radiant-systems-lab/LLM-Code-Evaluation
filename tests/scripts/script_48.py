# Web Scraping and Data Mining
import requests
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import scrapy
from scrapy.crawler import CrawlerProcess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import numpy as np
from textblob import TextBlob
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud
import re
import json
import csv
from collections import Counter
import hashlib
import time
import random

def web_scraping_basics():
    """Basic web scraping techniques and data extraction"""
    try:
        # Simulate web scraping with mock data (to avoid actual network requests)
        mock_html_content = """
        <html>
        <head><title>Sample E-commerce Site</title></head>
        <body>
            <div class="header">
                <h1>Online Store</h1>
                <nav>
                    <ul>
                        <li><a href="/products">Products</a></li>
                        <li><a href="/about">About</a></li>
                        <li><a href="/contact">Contact</a></li>
                    </ul>
                </nav>
            </div>
            <div class="content">
                <div class="product" data-price="29.99">
                    <h2>Wireless Headphones</h2>
                    <p class="description">High-quality wireless headphones with noise cancellation</p>
                    <span class="price">$29.99</span>
                    <div class="reviews">
                        <div class="review">Great sound quality! - Rating: 5/5</div>
                        <div class="review">Comfortable to wear - Rating: 4/5</div>
                        <div class="review">Good value for money - Rating: 4/5</div>
                    </div>
                </div>
                <div class="product" data-price="49.99">
                    <h2>Bluetooth Speaker</h2>
                    <p class="description">Portable speaker with excellent bass response</p>
                    <span class="price">$49.99</span>
                    <div class="reviews">
                        <div class="review">Amazing bass! - Rating: 5/5</div>
                        <div class="review">Very portable - Rating: 4/5</div>
                    </div>
                </div>
                <div class="product" data-price="19.99">
                    <h2>USB Cable</h2>
                    <p class="description">Durable USB-C cable for fast charging</p>
                    <span class="price">$19.99</span>
                    <div class="reviews">
                        <div class="review">Works perfectly - Rating: 5/5</div>
                    </div>
                </div>
            </div>
            <footer>
                <p>Contact: info@store.com | Phone: (555) 123-4567</p>
            </footer>
        </body>
        </html>
        """
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(mock_html_content, 'html.parser')
        
        # Extract basic information
        title = soup.find('title').text if soup.find('title') else 'No title'
        
        # Extract navigation links
        nav_links = []
        nav_elements = soup.find_all('nav')
        for nav in nav_elements:
            links = nav.find_all('a')
            for link in links:
                nav_links.append({
                    'text': link.text,
                    'href': link.get('href', '')
                })
        
        # Extract product information
        products = []
        product_elements = soup.find_all('div', class_='product')
        
        for product in product_elements:
            product_data = {
                'name': product.find('h2').text if product.find('h2') else 'Unknown',
                'description': product.find('p', class_='description').text if product.find('p', class_='description') else '',
                'price': product.find('span', class_='price').text if product.find('span', class_='price') else '0',
                'data_price': float(product.get('data-price', 0)),
                'reviews': []
            }
            
            # Extract reviews
            review_elements = product.find_all('div', class_='review')
            for review in review_elements:
                review_text = review.text
                # Extract rating using regex
                rating_match = re.search(r'Rating: (\d+)/5', review_text)
                rating = int(rating_match.group(1)) if rating_match else 0
                
                product_data['reviews'].append({
                    'text': review_text,
                    'rating': rating
                })
            
            products.append(product_data)
        
        # Extract contact information using regex
        footer = soup.find('footer')
        contact_info = {}
        if footer:
            footer_text = footer.text
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', footer_text)
            phone_match = re.search(r'Phone: ([\\d\\s\\(\\)\\-]+)', footer_text)
            
            contact_info['email'] = email_match.group(1) if email_match else None
            contact_info['phone'] = phone_match.group(1) if phone_match else None
        
        # Calculate statistics
        total_products = len(products)
        average_price = np.mean([p['data_price'] for p in products])
        total_reviews = sum(len(p['reviews']) for p in products)
        average_rating = np.mean([r['rating'] for p in products for r in p['reviews']]) if total_reviews > 0 else 0
        
        # Text processing and analysis
        all_text = ' '.join([p['name'] + ' ' + p['description'] for p in products])
        word_count = len(all_text.split())
        
        # Find most common words
        words = re.findall(r'\\b\\w+\\b', all_text.lower())
        word_frequency = Counter(words)
        most_common_words = word_frequency.most_common(5)
        
        return {
            'page_title': title,
            'navigation_links': len(nav_links),
            'total_products': total_products,
            'total_reviews': total_reviews,
            'average_price': average_price,
            'average_rating': average_rating,
            'word_count': word_count,
            'most_common_words': most_common_words,
            'contact_email_found': contact_info.get('email') is not None,
            'contact_phone_found': contact_info.get('phone') is not None,
            'extraction_methods': 4
        }
        
    except Exception as e:
        return {'error': str(e)}

def advanced_data_mining():
    """Advanced data mining and pattern recognition"""
    try:
        # Generate synthetic web data for mining
        np.random.seed(42)
        
        # Simulate user behavior data
        users = []
        for i in range(1000):
            user = {
                'user_id': f'user_{i:04d}',
                'age': np.random.randint(18, 65),
                'gender': np.random.choice(['M', 'F']),
                'location': np.random.choice(['New York', 'California', 'Texas', 'Florida', 'Illinois']),
                'pages_visited': np.random.randint(1, 50),
                'time_on_site': np.random.exponential(300),  # seconds
                'purchases': np.random.randint(0, 10),
                'purchase_amount': np.random.exponential(50) if np.random.random() > 0.3 else 0,
                'device_type': np.random.choice(['mobile', 'desktop', 'tablet'], p=[0.6, 0.3, 0.1]),
                'session_count': np.random.randint(1, 20)
            }
            users.append(user)
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(users)
        
        # Data mining tasks
        
        # 1. Customer Segmentation
        def customer_segmentation(df):
            # Simple segmentation based on behavior
            segments = {}
            
            # High-value customers
            high_value = df[(df['purchase_amount'] > df['purchase_amount'].quantile(0.8)) & 
                           (df['purchases'] > df['purchases'].quantile(0.7))]
            
            # Frequent browsers (low purchase)
            browsers = df[(df['pages_visited'] > df['pages_visited'].quantile(0.8)) & 
                         (df['purchases'] <= 1)]
            
            # Mobile users
            mobile_users = df[df['device_type'] == 'mobile']
            
            # New users
            new_users = df[df['session_count'] <= 2]
            
            segments['high_value'] = len(high_value)
            segments['browsers'] = len(browsers)
            segments['mobile_users'] = len(mobile_users)
            segments['new_users'] = len(new_users)
            
            return segments
        
        segments = customer_segmentation(df)
        
        # 2. Association Rule Mining (Market Basket Analysis simulation)
        def market_basket_analysis():
            # Simulate product purchase data
            products = ['laptop', 'mouse', 'keyboard', 'monitor', 'headphones', 
                       'speakers', 'webcam', 'cable', 'charger', 'bag']
            
            transactions = []
            for _ in range(500):
                # Each transaction has 1-5 products
                transaction_size = np.random.randint(1, 6)
                transaction = np.random.choice(products, transaction_size, replace=False)
                transactions.append(list(transaction))
            
            # Calculate support for individual items
            item_counts = Counter()
            for transaction in transactions:
                for item in transaction:
                    item_counts[item] += 1
            
            # Calculate support for pairs (simplified association rules)
            pair_counts = Counter()
            for transaction in transactions:
                if len(transaction) >= 2:
                    for i in range(len(transaction)):
                        for j in range(i + 1, len(transaction)):
                            pair = tuple(sorted([transaction[i], transaction[j]]))
                            pair_counts[pair] += 1
            
            # Find rules with confidence > 0.5
            strong_rules = []
            total_transactions = len(transactions)
            
            for pair, count in pair_counts.items():
                if count >= 10:  # Minimum support threshold
                    item1, item2 = pair
                    # Calculate confidence: P(item2|item1)
                    confidence = count / item_counts[item1]
                    if confidence > 0.5:
                        strong_rules.append({
                            'rule': f'{item1} -> {item2}',
                            'support': count / total_transactions,
                            'confidence': confidence
                        })
            
            return len(transactions), len(strong_rules), strong_rules[:3]  # Top 3 rules
        
        total_transactions, num_strong_rules, top_rules = market_basket_analysis()
        
        # 3. Anomaly Detection
        def detect_anomalies(df):
            # Simple statistical anomaly detection
            anomalies = {}
            
            # Z-score based anomaly detection
            def z_score_anomalies(series, threshold=3):
                z_scores = np.abs((series - series.mean()) / series.std())
                return np.sum(z_scores > threshold)
            
            # Detect anomalies in different metrics
            anomalies['time_on_site'] = z_score_anomalies(df['time_on_site'])
            anomalies['pages_visited'] = z_score_anomalies(df['pages_visited'])
            anomalies['purchase_amount'] = z_score_anomalies(df[df['purchase_amount'] > 0]['purchase_amount'])
            
            # Behavioral anomalies
            # Users with high page visits but zero purchases
            high_browse_no_purchase = len(df[(df['pages_visited'] > df['pages_visited'].quantile(0.9)) & 
                                           (df['purchases'] == 0)])
            
            # Users with high purchase amounts but low page visits
            high_purchase_low_browse = len(df[(df['purchase_amount'] > df['purchase_amount'].quantile(0.9)) & 
                                            (df['pages_visited'] < df['pages_visited'].quantile(0.2))])
            
            anomalies['high_browse_no_purchase'] = high_browse_no_purchase
            anomalies['high_purchase_low_browse'] = high_purchase_low_browse
            
            return anomalies
        
        anomalies = detect_anomalies(df)
        
        # 4. Trend Analysis
        def trend_analysis(df):
            # Simulate time-series data for trend analysis
            dates = pd.date_range('2023-01-01', periods=365, freq='D')
            
            # Generate synthetic metrics with trends
            base_traffic = 1000
            seasonal_component = 200 * np.sin(2 * np.pi * np.arange(365) / 365)  # Annual seasonality
            trend_component = 2 * np.arange(365)  # Linear growth
            noise = np.random.normal(0, 50, 365)
            
            daily_visits = base_traffic + seasonal_component + trend_component + noise
            daily_visits = np.maximum(daily_visits, 0)  # Ensure non-negative
            
            # Calculate moving averages
            ma_7 = pd.Series(daily_visits).rolling(window=7).mean().iloc[-1]
            ma_30 = pd.Series(daily_visits).rolling(window=30).mean().iloc[-1]
            
            # Calculate growth rate
            first_month_avg = np.mean(daily_visits[:30])
            last_month_avg = np.mean(daily_visits[-30:])
            growth_rate = (last_month_avg - first_month_avg) / first_month_avg * 100
            
            # Detect trend direction
            recent_trend = np.polyfit(range(30), daily_visits[-30:], 1)[0]  # Slope of last 30 days
            
            return {
                'total_days_analyzed': len(daily_visits),
                'average_daily_visits': np.mean(daily_visits),
                'max_daily_visits': np.max(daily_visits),
                'min_daily_visits': np.min(daily_visits),
                'moving_avg_7_days': ma_7,
                'moving_avg_30_days': ma_30,
                'yearly_growth_rate': growth_rate,
                'recent_trend_slope': recent_trend,
                'trend_direction': 'up' if recent_trend > 0 else 'down'
            }
        
        trend_results = trend_analysis(df)
        
        # 5. Text Mining and Sentiment Analysis
        def text_sentiment_analysis():
            # Simulate user reviews/comments
            sample_reviews = [
                "Great product, very satisfied with the purchase!",
                "Poor quality, not worth the money",
                "Amazing service, will buy again",
                "Terrible experience, slow shipping",
                "Excellent quality and fast delivery",
                "Product broke after one week",
                "Outstanding customer support",
                "Overpriced for what you get",
                "Perfect for my needs",
                "Disappointing, expected better"
            ] * 10  # Simulate 100 reviews
            
            # Add some variation
            reviews = []
            sentiments = ['positive', 'negative', 'neutral']
            
            for _ in range(200):
                base_review = np.random.choice(sample_reviews)
                sentiment = np.random.choice(sentiments, p=[0.5, 0.3, 0.2])
                
                # Modify review based on sentiment
                if sentiment == 'positive':
                    modifiers = [' - highly recommend!', ' Amazing!', ' Perfect!']
                elif sentiment == 'negative':
                    modifiers = [' - very disappointed', ' Terrible!', ' Waste of money!']
                else:
                    modifiers = [' - okay product', ' - average quality', ' - decent']
                
                modifier = np.random.choice(modifiers)
                reviews.append(base_review + modifier)
            
            # Sentiment analysis using TextBlob
            sentiments = []
            polarities = []
            
            for review in reviews[:50]:  # Analyze subset for performance
                try:
                    blob = TextBlob(review)
                    polarity = blob.sentiment.polarity
                    polarities.append(polarity)
                    
                    if polarity > 0.1:
                        sentiments.append('positive')
                    elif polarity < -0.1:
                        sentiments.append('negative')
                    else:
                        sentiments.append('neutral')
                except:
                    sentiments.append('neutral')
                    polarities.append(0)
            
            sentiment_counts = Counter(sentiments)
            avg_polarity = np.mean(polarities)
            
            return {
                'total_reviews_analyzed': len(sentiments),
                'positive_reviews': sentiment_counts.get('positive', 0),
                'negative_reviews': sentiment_counts.get('negative', 0),
                'neutral_reviews': sentiment_counts.get('neutral', 0),
                'average_sentiment_polarity': avg_polarity,
                'sentiment_score': 'positive' if avg_polarity > 0.1 else 'negative' if avg_polarity < -0.1 else 'neutral'
            }
        
        sentiment_results = text_sentiment_analysis()
        
        return {
            'total_users_analyzed': len(df),
            'customer_segments': segments,
            'market_basket_transactions': total_transactions,
            'association_rules_found': num_strong_rules,
            'top_association_rules': top_rules,
            'anomalies_detected': anomalies,
            'trend_analysis': trend_results,
            'sentiment_analysis': sentiment_results,
            'data_mining_techniques': 5,
            'analysis_completeness': 'comprehensive'
        }
        
    except Exception as e:
        return {'error': str(e)}

def web_automation():
    """Web automation and crawling simulation"""
    try:
        # Simulate web automation tasks without actual browser automation
        
        # 1. Simulate form automation
        def simulate_form_automation():
            forms_processed = 0
            form_types = ['login', 'registration', 'contact', 'survey', 'checkout']
            
            automation_results = []
            
            for form_type in form_types:
                # Simulate form filling
                fields_filled = np.random.randint(3, 10)
                success_rate = np.random.uniform(0.85, 0.98)
                processing_time = np.random.uniform(1, 5)  # seconds
                
                automation_results.append({
                    'form_type': form_type,
                    'fields_filled': fields_filled,
                    'success_rate': success_rate,
                    'avg_processing_time': processing_time
                })
                
                forms_processed += 1
            
            return forms_processed, automation_results
        
        forms_count, form_results = simulate_form_automation()
        
        # 2. Simulate web crawling
        def simulate_web_crawling():
            # Simulate crawling a website structure
            pages_crawled = []
            base_urls = ['/', '/products', '/about', '/contact', '/blog', '/news']
            
            crawl_stats = {
                'pages_discovered': 0,
                'pages_crawled': 0,
                'total_links': 0,
                'unique_domains': 0,
                'crawl_depth': 3,
                'robots_txt_respected': True
            }
            
            # Simulate crawling each base URL
            for base_url in base_urls:
                # Generate sub-pages for each base URL
                sub_pages = np.random.randint(5, 20)
                
                for i in range(sub_pages):
                    page_url = f"{base_url}/page_{i}"
                    
                    # Simulate page analysis
                    page_data = {
                        'url': page_url,
                        'status_code': np.random.choice([200, 404, 301, 500], p=[0.85, 0.1, 0.04, 0.01]),
                        'content_length': np.random.randint(1000, 50000),
                        'load_time': np.random.uniform(0.5, 3.0),
                        'outbound_links': np.random.randint(5, 30),
                        'internal_links': np.random.randint(10, 50),
                        'images_count': np.random.randint(0, 20),
                        'title_length': np.random.randint(20, 80),
                        'meta_description_present': np.random.choice([True, False], p=[0.8, 0.2])
                    }
                    
                    pages_crawled.append(page_data)
                    
                    if page_data['status_code'] == 200:
                        crawl_stats['pages_crawled'] += 1
                        crawl_stats['total_links'] += page_data['outbound_links'] + page_data['internal_links']
                    
                    crawl_stats['pages_discovered'] += 1
            
            # Calculate crawling metrics
            successful_pages = [p for p in pages_crawled if p['status_code'] == 200]
            avg_load_time = np.mean([p['load_time'] for p in successful_pages]) if successful_pages else 0
            avg_content_length = np.mean([p['content_length'] for p in successful_pages]) if successful_pages else 0
            
            crawl_stats['avg_load_time'] = avg_load_time
            crawl_stats['avg_content_length'] = avg_content_length
            crawl_stats['crawl_success_rate'] = len(successful_pages) / len(pages_crawled) if pages_crawled else 0
            
            return crawl_stats
        
        crawl_results = simulate_web_crawling()
        
        # 3. Simulate data extraction patterns
        def simulate_data_extraction():
            extraction_patterns = [
                'product_prices',
                'contact_information',
                'social_media_links',
                'images_and_media',
                'structured_data',
                'user_reviews',
                'navigation_menus',
                'metadata'
            ]
            
            extraction_results = {}
            
            for pattern in extraction_patterns:
                # Simulate extraction success and data quality
                items_extracted = np.random.randint(50, 500)
                extraction_accuracy = np.random.uniform(0.75, 0.95)
                processing_speed = np.random.uniform(10, 100)  # items per second
                
                extraction_results[pattern] = {
                    'items_extracted': items_extracted,
                    'accuracy': extraction_accuracy,
                    'processing_speed': processing_speed,
                    'data_quality_score': extraction_accuracy * np.random.uniform(0.9, 1.0)
                }
            
            total_items = sum(result['items_extracted'] for result in extraction_results.values())
            avg_accuracy = np.mean([result['accuracy'] for result in extraction_results.values()])
            
            return extraction_results, total_items, avg_accuracy
        
        extraction_results, total_extracted, avg_extraction_accuracy = simulate_data_extraction()
        
        # 4. Simulate rate limiting and throttling
        def simulate_rate_limiting():
            # Simulate requests with rate limiting
            total_requests = 1000
            rate_limit_per_minute = 60
            
            successful_requests = 0
            throttled_requests = 0
            failed_requests = 0
            
            # Simulate request patterns
            for minute in range(20):  # 20 minutes simulation
                requests_this_minute = np.random.poisson(rate_limit_per_minute * 1.2)  # Slightly above limit
                
                if requests_this_minute <= rate_limit_per_minute:
                    successful_requests += requests_this_minute
                else:
                    successful_requests += rate_limit_per_minute
                    excess = requests_this_minute - rate_limit_per_minute
                    
                    # Some excess requests are throttled (delayed), others fail
                    throttled_this_minute = int(excess * 0.7)
                    failed_this_minute = excess - throttled_this_minute
                    
                    throttled_requests += throttled_this_minute
                    failed_requests += failed_this_minute
            
            return {
                'total_requests_attempted': successful_requests + throttled_requests + failed_requests,
                'successful_requests': successful_requests,
                'throttled_requests': throttled_requests,
                'failed_requests': failed_requests,
                'success_rate': successful_requests / (successful_requests + throttled_requests + failed_requests),
                'rate_limit_per_minute': rate_limit_per_minute
            }
        
        rate_limit_results = simulate_rate_limiting()
        
        return {
            'forms_automated': forms_count,
            'form_automation_success': np.mean([r['success_rate'] for r in form_results]),
            'web_crawling_results': crawl_results,
            'data_extraction_patterns': len(extraction_results),
            'total_items_extracted': total_extracted,
            'extraction_accuracy': avg_extraction_accuracy,
            'rate_limiting_results': rate_limit_results,
            'automation_capabilities': 4,
            'overall_automation_success': True
        }
        
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    print("Web scraping and data mining...")
    
    # Web scraping
    scraping_result = web_scraping_basics()
    if 'error' not in scraping_result:
        print(f"Scraping: {scraping_result['total_products']} products, avg rating {scraping_result['average_rating']:.2f}")
    
    # Data mining
    mining_result = advanced_data_mining()
    if 'error' not in mining_result:
        print(f"Mining: {mining_result['total_users_analyzed']} users, {mining_result['association_rules_found']} association rules")
    
    # Web automation
    automation_result = web_automation()
    if 'error' not in automation_result:
        print(f"Automation: {automation_result['forms_automated']} forms, {automation_result['total_items_extracted']} items extracted")