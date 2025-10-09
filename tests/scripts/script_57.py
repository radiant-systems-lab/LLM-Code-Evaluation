#!/usr/bin/env python3
"""
Script 7: Web Framework with Flask
Tests web framework and API dependencies
"""

from flask import Flask, jsonify, request, render_template_string
import sqlite3
import json
import hashlib
from datetime import datetime
import pandas as pd

# Initialize Flask app
app = Flask(__name__)

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>API Dashboard</title>
</head>
<body>
    <h1>Flask API Dashboard</h1>
    <h2>API Endpoints:</h2>
    <ul>
        <li>/api/data - GET data</li>
        <li>/api/stats - GET statistics</li>
        <li>/api/hash - POST to hash text</li>
    </ul>
    <p>Total requests: {{ request_count }}</p>
    <p>Server time: {{ server_time }}</p>
</body>
</html>
"""

class DataService:
    """Service for data operations"""
    
    def __init__(self):
        self.request_count = 0
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE metrics (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                value REAL,
                category TEXT
            )
        ''')
        
        # Insert sample data
        import random
        for i in range(100):
            cursor.execute(
                "INSERT INTO metrics (timestamp, value, category) VALUES (?, ?, ?)",
                (datetime.now().isoformat(), random.random() * 100, 
                 random.choice(['A', 'B', 'C']))
            )
        conn.commit()
        conn.close()
        print("Database initialized with 100 records")
    
    def get_data(self):
        """Retrieve data from database"""
        conn = sqlite3.connect(':memory:')
        df = pd.read_sql_query("SELECT * FROM metrics LIMIT 10", conn)
        conn.close()
        return df.to_dict(orient='records')
    
    def get_stats(self):
        """Calculate statistics"""
        self.request_count += 1
        return {
            'total_requests': self.request_count,
            'timestamp': datetime.now().isoformat(),
            'status': 'operational'
        }

# Initialize service
service = DataService()

@app.route('/')
def home():
    """Home route"""
    return render_template_string(
        HTML_TEMPLATE,
        request_count=service.request_count,
        server_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

@app.route('/api/data', methods=['GET'])
def get_data():
    """API endpoint for data"""
    data = service.get_data()
    return jsonify(data)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """API endpoint for statistics"""
    stats = service.get_stats()
    return jsonify(stats)

@app.route('/api/hash', methods=['POST'])
def hash_text():
    """API endpoint to hash text"""
    data = request.get_json()
    text = data.get('text', '')
    hashed = hashlib.sha256(text.encode()).hexdigest()
    return jsonify({
        'original': text,
        'hash': hashed,
        'algorithm': 'sha256'
    })

def run_test_server():
    """Run Flask in test mode"""
    print("Starting Flask test server...")
    
    # Simulate requests
    with app.test_client() as client:
        # Test home page
        response = client.get('/')
        print(f"Home page status: {response.status_code}")
        
        # Test API endpoints
        response = client.get('/api/data')
        print(f"Data API status: {response.status_code}")
        
        response = client.get('/api/stats')
        stats = json.loads(response.data)
        print(f"Stats API: {stats}")
        
        response = client.post('/api/hash', 
                             json={'text': 'Hello Flask!'})
        hash_result = json.loads(response.data)
        print(f"Hash API: {hash_result['hash'][:16]}...")
    
    print("Flask test complete")
    return True

if __name__ == "__main__":
    # Run in test mode instead of starting actual server
    success = run_test_server()
    print(f"Test completed: {success}")