import os
import sys
import requests
import numpy as np
from flask import Flask
from datetime import datetime

def calculate_stats(data):
    """Calculate basic statistics"""
    return np.mean(data), np.std(data)

def make_request(url):
    """Make HTTP request"""
    response = requests.get(url)
    return response.json()

def create_app():
    """Create Flask app"""
    app = Flask(__name__)
    return app

if __name__ == "__main__":
    print(f"Current time: {datetime.now()}")
    data = [1, 2, 3, 4, 5]
    mean, std = calculate_stats(data)
    print(f"Mean: {mean}, Std: {std}")