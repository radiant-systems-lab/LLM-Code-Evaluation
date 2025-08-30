#!/usr/bin/env python3
"""
Example Script 2: Web Scraping and Text Processing
This script demonstrates web requests and natural language processing.
"""

import requests
from bs4 import BeautifulSoup
import nltk
from collections import Counter
import json

def fetch_and_analyze_text():
    """Fetch web content and analyze text"""
    
    # Sample URLs for demonstration
    urls = [
        "https://httpbin.org/json",  # Returns sample JSON
        "https://jsonplaceholder.typicode.com/posts/1"  # Sample API
    ]
    
    all_text = []
    
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            if 'json' in response.headers.get('content-type', ''):
                # Handle JSON content
                data = response.json()
                text_content = str(data)
            else:
                # Handle HTML content
                soup = BeautifulSoup(response.text, 'html.parser')
                text_content = soup.get_text()
            
            all_text.append(text_content)
            print(f"Successfully fetched content from: {url}")
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            continue
    
    # Combine all text
    combined_text = " ".join(all_text)
    
    # Basic text analysis
    words = combined_text.lower().split()
    word_freq = Counter(words)
    
    print("\nText Analysis Results:")
    print(f"Total words: {len(words)}")
    print(f"Unique words: {len(word_freq)}")
    print("\nTop 10 most common words:")
    for word, count in word_freq.most_common(10):
        print(f"  {word}: {count}")
    
    # Save results
    results = {
        "total_words": len(words),
        "unique_words": len(word_freq),
        "top_words": dict(word_freq.most_common(10))
    }
    
    with open('text_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to 'text_analysis_results.json'")

if __name__ == "__main__":
    fetch_and_analyze_text()