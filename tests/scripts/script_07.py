# Natural Language Processing
import nltk
import spacy
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from textblob import TextBlob
import re
from collections import Counter
from wordcloud import WordCloud

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except:
    pass

def nltk_processing(text):
    """NLTK text processing"""
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.sentiment import SentimentIntensityAnalyzer
    
    # Tokenization
    words = word_tokenize(text.lower())
    sentences = sent_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    
    # Sentiment analysis
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(text)
    
    return {
        'word_count': len(filtered_words),
        'sentence_count': len(sentences),
        'sentiment': sentiment,
        'top_words': Counter(filtered_words).most_common(5)
    }

def spacy_processing(text):
    """spaCy NLP processing"""
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        # Use blank model if language model not available
        nlp = spacy.blank("en")
    
    doc = nlp(text)
    
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    pos_tags = [(token.text, token.pos_) for token in doc]
    
    return {
        'entities': entities,
        'pos_tags': pos_tags[:10],  # First 10 for brevity
        'token_count': len(doc)
    }

def transformers_processing(text):
    """Transformers library processing"""
    try:
        # Sentiment analysis pipeline
        sentiment_pipeline = pipeline("sentiment-analysis", 
                                    model="distilbert-base-uncased-finetuned-sst-2-english")
        sentiment_result = sentiment_pipeline(text)
        
        # Text summarization (for longer texts)
        if len(text.split()) > 50:
            summarizer = pipeline("summarization", 
                                model="facebook/bart-large-cnn")
            summary = summarizer(text, max_length=100, min_length=30)
        else:
            summary = [{'summary_text': 'Text too short for summarization'}]
        
        return {
            'sentiment': sentiment_result,
            'summary': summary[0]['summary_text']
        }
    except Exception as e:
        return {'error': f"Transformers processing failed: {str(e)}"}

def textblob_processing(text):
    """TextBlob processing"""
    blob = TextBlob(text)
    
    # Sentiment analysis
    sentiment = blob.sentiment
    
    # Language detection
    try:
        language = blob.detect_language()
    except:
        language = 'unknown'
    
    # Noun phrase extraction
    noun_phrases = list(blob.noun_phrases)
    
    return {
        'sentiment_polarity': sentiment.polarity,
        'sentiment_subjectivity': sentiment.subjectivity,
        'language': language,
        'noun_phrases': noun_phrases[:5]
    }

def create_wordcloud(text):
    """Generate word cloud"""
    try:
        wordcloud = WordCloud(width=800, height=400, 
                            background_color='white').generate(text)
        wordcloud.to_file('/tmp/wordcloud.png')
        return True
    except Exception as e:
        print(f"WordCloud generation failed: {e}")
        return False

def regex_text_analysis(text):
    """Regex-based text analysis"""
    # Email extraction
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    
    # URL extraction
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    
    # Phone number extraction (US format)
    phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
    
    return {
        'emails': emails,
        'urls': urls,
        'phones': phones
    }

def main():
    sample_text = """
    Natural Language Processing (NLP) is a fascinating field of artificial intelligence. 
    It combines computational linguistics with machine learning and deep learning models. 
    Modern NLP applications include sentiment analysis, machine translation, and chatbots.
    Companies like Google and OpenAI have made significant breakthroughs in this area.
    Contact us at info@example.com or visit https://example.com for more information.
    You can also call us at 555-123-4567.
    """
    
    print("Running NLP analysis...")
    
    # NLTK processing
    nltk_results = nltk_processing(sample_text)
    print(f"NLTK: {nltk_results['word_count']} words, sentiment: {nltk_results['sentiment']['compound']:.2f}")
    
    # spaCy processing
    spacy_results = spacy_processing(sample_text)
    print(f"spaCy: {spacy_results['token_count']} tokens, {len(spacy_results['entities'])} entities")
    
    # Transformers processing
    transformers_results = transformers_processing(sample_text)
    if 'error' not in transformers_results:
        print(f"Transformers: Sentiment {transformers_results['sentiment'][0]['label']}")
    
    # TextBlob processing
    textblob_results = textblob_processing(sample_text)
    print(f"TextBlob: Polarity {textblob_results['sentiment_polarity']:.2f}")
    
    # Regex analysis
    regex_results = regex_text_analysis(sample_text)
    print(f"Regex: Found {len(regex_results['emails'])} emails, {len(regex_results['urls'])} URLs")
    
    # Word cloud generation
    wordcloud_created = create_wordcloud(sample_text)
    print(f"WordCloud: {'Created' if wordcloud_created else 'Failed'}")

if __name__ == "__main__":
    main()