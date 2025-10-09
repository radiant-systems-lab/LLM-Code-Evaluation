# Regular Expressions and Text Processing
import re
import string
import unicodedata
import codecs
from collections import Counter, defaultdict
import difflib

class TextAnalyzer:
    """Text analysis and processing utilities"""
    
    def __init__(self):
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'url': r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b'
        }
    
    def extract_patterns(self, text, pattern_name):
        """Extract specific patterns from text"""
        if pattern_name in self.patterns:
            pattern = self.patterns[pattern_name]
            return re.findall(pattern, text, re.IGNORECASE)
        return []
    
    def clean_text(self, text):
        """Clean and normalize text"""
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep basic punctuation
        cleaned = re.sub(r'[^\w\s.,!?;:-]', '', cleaned)
        
        # Normalize unicode
        cleaned = unicodedata.normalize('NFKD', cleaned)
        
        return cleaned
    
    def extract_sentences(self, text):
        """Extract sentences using regex"""
        sentence_pattern = r'[.!?]+\s*'
        sentences = re.split(sentence_pattern, text)
        return [s.strip() for s in sentences if s.strip()]
    
    def extract_words(self, text):
        """Extract words and analyze frequency"""
        # Extract words (alphabetic characters only)
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                     'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        
        filtered_words = [word for word in words if word not in stop_words]
        
        return Counter(filtered_words)
    
    def find_and_replace(self, text, replacements):
        """Find and replace patterns"""
        result = text
        for pattern, replacement in replacements.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        return result
    
    def validate_formats(self, text_dict):
        """Validate various text formats"""
        results = {}
        
        for key, text in text_dict.items():
            if key == 'email':
                results[key] = bool(re.match(self.patterns['email'], text))
            elif key == 'phone':
                results[key] = bool(re.match(self.patterns['phone'], text))
            elif key == 'url':
                results[key] = bool(re.match(self.patterns['url'], text))
            elif key == 'password':
                # Password must have: 8+ chars, uppercase, lowercase, digit, special char
                pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
                results[key] = bool(re.match(pattern, text))
        
        return results

def advanced_regex_operations():
    """Advanced regex operations"""
    text = """
    Contact Information:
    John Doe: john.doe@email.com, phone: 555-123-4567
    Jane Smith: jane.smith@company.org, phone: (555) 987-6543
    Website: https://example.com
    IP Address: 192.168.1.1
    Credit Card: 1234-5678-9012-3456
    SSN: 123-45-6789
    """
    
    analyzer = TextAnalyzer()
    
    results = {}
    for pattern_name in analyzer.patterns:
        matches = analyzer.extract_patterns(text, pattern_name)
        results[pattern_name] = matches
    
    return results

def text_similarity_analysis():
    """Text similarity and diff analysis"""
    text1 = "The quick brown fox jumps over the lazy dog."
    text2 = "A quick brown fox jumped over a lazy dog."
    
    # Character-level similarity
    char_similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
    
    # Word-level similarity
    words1 = text1.lower().split()
    words2 = text2.lower().split()
    word_similarity = difflib.SequenceMatcher(None, words1, words2).ratio()
    
    # Get detailed diff
    diff = list(difflib.unified_diff(text1.split(), text2.split(), lineterm=''))
    
    return {
        'char_similarity': char_similarity,
        'word_similarity': word_similarity,
        'diff_lines': len(diff)
    }

def text_transformation():
    """Various text transformations"""
    text = "Hello World! This is a TEST of text transformations."
    
    transformations = {
        'uppercase': text.upper(),
        'lowercase': text.lower(),
        'title_case': text.title(),
        'swap_case': text.swapcase(),
        'reverse': text[::-1],
        'no_punctuation': text.translate(str.maketrans('', '', string.punctuation)),
        'only_alpha': ''.join(c for c in text if c.isalpha() or c.isspace()),
        'only_digits': ''.join(c for c in text if c.isdigit()),
        'rot13': codecs.encode(text, 'rot13')
    }
    
    return transformations

def complex_text_parsing():
    """Complex text parsing scenarios"""
    log_text = """
    2023-08-31 10:30:15 [INFO] User login successful: user_id=12345
    2023-08-31 10:31:22 [ERROR] Database connection failed: timeout=30s
    2023-08-31 10:32:45 [WARN] High memory usage detected: usage=85%
    2023-08-31 10:33:01 [INFO] User logout: user_id=12345, session_duration=2min
    """
    
    # Extract log entries
    log_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] (.+)'
    log_entries = re.findall(log_pattern, log_text)
    
    # Group by log level
    log_levels = defaultdict(list)
    for timestamp, level, message in log_entries:
        log_levels[level].append((timestamp, message))
    
    # Extract numeric values
    numeric_pattern = r'\b\d+(?:\.\d+)?\b'
    numbers = re.findall(numeric_pattern, log_text)
    
    return {
        'total_entries': len(log_entries),
        'log_levels': dict(log_levels),
        'extracted_numbers': numbers
    }

if __name__ == "__main__":
    print("Regular expression and text processing operations...")
    
    # Pattern extraction
    pattern_results = advanced_regex_operations()
    print(f"Pattern extraction results: {len(pattern_results)} patterns tested")
    
    # Text similarity
    similarity_results = text_similarity_analysis()
    print(f"Text similarity: {similarity_results['char_similarity']:.3f}")
    
    # Text transformations
    transform_results = text_transformation()
    print(f"Text transformations: {len(transform_results)} performed")
    
    # Complex parsing
    parsing_results = complex_text_parsing()
    print(f"Log parsing: {parsing_results['total_entries']} entries found")
    
    # Text validation
    analyzer = TextAnalyzer()
    validation_tests = {
        'email': 'user@example.com',
        'phone': '555-123-4567',
        'url': 'https://www.example.com',
        'password': 'SecurePass123!'
    }
    
    validation_results = analyzer.validate_formats(validation_tests)
    valid_count = sum(validation_results.values())
    print(f"Format validation: {valid_count}/{len(validation_results)} passed")
