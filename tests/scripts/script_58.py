#!/usr/bin/env python3
"""
Script 8: Natural Language Processing
Tests NLP libraries and text processing dependencies
"""

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
import spacy
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter

def analyze_text():
    """Comprehensive text analysis pipeline"""
    print("Starting NLP analysis pipeline...")
    
    # Sample text
    text = """
    Natural language processing (NLP) is a subfield of linguistics, computer science, 
    and artificial intelligence concerned with the interactions between computers and 
    human language. The goal is to program computers to process and analyze large 
    amounts of natural language data. Challenges in NLP frequently involve speech 
    recognition, natural language understanding, and natural language generation.
    Machine learning approaches have been particularly successful in recent years.
    Deep learning models like transformers have revolutionized the field.
    """
    
    # Download required NLTK data (will fail if not installed)
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet', quiet=True)
    
    # NLTK processing
    sentences = sent_tokenize(text)
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_words = [w for w in words if w.isalnum() and w not in stop_words]
    
    print(f"NLTK Analysis: {len(sentences)} sentences, {len(words)} words")
    
    # Stemming and Lemmatization
    stemmer = PorterStemmer()
    lemmatizer = WordNetLemmatizer()
    
    stemmed = [stemmer.stem(word) for word in filtered_words]
    lemmatized = [lemmatizer.lemmatize(word) for word in filtered_words]
    
    # TextBlob sentiment analysis
    blob = TextBlob(text)
    sentiment = blob.sentiment
    print(f"Sentiment: Polarity={sentiment.polarity:.3f}, Subjectivity={sentiment.subjectivity:.3f}")
    
    # Word frequency analysis
    word_freq = Counter(filtered_words)
    top_words = word_freq.most_common(10)
    
    # Create DataFrame for analysis
    df = pd.DataFrame(top_words, columns=['Word', 'Frequency'])
    print("\nTop 10 words:")
    print(df)
    
    # Generate word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(filtered_words))
    
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud')
    
    # Plot word frequencies
    plt.subplot(1, 2, 2)
    plt.bar(df['Word'][:10], df['Frequency'][:10])
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.title('Top 10 Word Frequencies')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig('nlp_analysis.png')
    print("NLP visualizations saved to nlp_analysis.png")
    
    # Try spacy (will fail if not installed with model)
    try:
        # Load spacy model
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        
        # Extract entities
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        print(f"\nSpacy entities found: {len(entities)}")
        
    except Exception as e:
        print(f"Spacy processing skipped: {e}")
        entities = []
    
    return {
        'sentences': len(sentences),
        'words': len(words),
        'unique_words': len(set(filtered_words)),
        'sentiment_polarity': sentiment.polarity,
        'entities_found': len(entities)
    }

if __name__ == "__main__":
    results = analyze_text()
    print(f"\nNLP Analysis complete: {results}")