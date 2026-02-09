#!/usr/bin/env python3
"""
Script 395: Text Processing and NLP
Natural language processing operations
"""

from collections import Counter\nimport gensim\nimport keras\nimport lightgbm\nimport matplotlib.pyplot as plt\nimport numpy as np\nimport os\nimport pandas as pd\nimport plotly\nimport re\nimport torch\nimport transformers

def load_text_data():
    """Load sample text data"""
    texts = [
        "Natural language processing is fascinating.",
        "Machine learning models require training data.",
        "Python is great for data science.",
        "Text analysis reveals patterns in documents.",
        "Sentiment analysis detects emotions in text."
    ] * 20
    return texts

def preprocess_text(texts):
    """Preprocess text data"""
    processed = []
    for text in texts:
        # Lowercase
        text = text.lower()
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        # Tokenize
        tokens = text.split()
        processed.append(tokens)
    return processed

def analyze_text(texts):
    """Analyze text features"""
    analysis = {
        'total_texts': len(texts),
        'avg_length': np.mean([len(text) for text in texts]),
        'unique_words': len(set(' '.join(texts).split())),
        'word_frequencies': Counter(' '.join(texts).split()).most_common(10)
    }
    return analysis

def vectorize_text(texts):
    """Convert text to numerical vectors"""
    from sklearn.feature_extraction.text import TfidfVectorizer
    vectorizer = TfidfVectorizer(max_features=100)
    vectors = vectorizer.fit_transform(texts)
    return vectors, vectorizer

if __name__ == "__main__":
    print("Text processing operations...")
    texts = load_text_data()
    preprocessed = preprocess_text(texts)
    analysis = analyze_text(texts)
    vectors, vectorizer = vectorize_text(texts)
    print(f"Analyzed {analysis['total_texts']} texts, {analysis['unique_words']} unique words")
    print(f"Vectorized to shape: {vectors.shape}")
