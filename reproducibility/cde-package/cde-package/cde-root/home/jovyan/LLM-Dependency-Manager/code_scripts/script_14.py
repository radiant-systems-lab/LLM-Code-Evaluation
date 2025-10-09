# Testing Framework Examples
import unittest
import pytest
import doctest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

class Calculator:
    """Sample calculator class for testing
    
    >>> calc = Calculator()
    >>> calc.add(2, 3)
    5
    >>> calc.multiply(4, 5)
    20
    """
    
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
    
    def multiply(self, a, b):
        return a * b
    
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

class TestCalculator(unittest.TestCase):
    """Unit tests for Calculator class"""
    
    def setUp(self):
        self.calc = Calculator()
    
    def test_add(self):
        self.assertEqual(self.calc.add(2, 3), 5)
        self.assertEqual(self.calc.add(-1, 1), 0)
    
    def test_subtract(self):
        self.assertEqual(self.calc.subtract(5, 3), 2)
        self.assertEqual(self.calc.subtract(0, 5), -5)
    
    def test_multiply(self):
        self.assertEqual(self.calc.multiply(3, 4), 12)
        self.assertEqual(self.calc.multiply(-2, 3), -6)
    
    def test_divide(self):
        self.assertEqual(self.calc.divide(6, 2), 3.0)
        self.assertEqual(self.calc.divide(5, 4), 1.25)
    
    def test_divide_by_zero(self):
        with self.assertRaises(ValueError):
            self.calc.divide(5, 0)

# Pytest tests
def test_calculator_add():
    calc = Calculator()
    assert calc.add(2, 3) == 5
    assert calc.add(-1, 1) == 0

def test_calculator_with_fixture():
    calc = Calculator()
    result = calc.multiply(3, 4)
    assert result == 12

@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0),
    (10, -5, 5)
])
def test_calculator_add_parametrized(a, b, expected):
    calc = Calculator()
    assert calc.add(a, b) == expected

class FileManager:
    """File manager for testing with mocks"""
    
    def read_file(self, filepath):
        with open(filepath, 'r') as f:
            return f.read()
    
    def write_file(self, filepath, content):
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    
    def get_file_size(self, filepath):
        return os.path.getsize(filepath)

class TestFileManagerWithMocks(unittest.TestCase):
    """Test FileManager with mocks"""
    
    def setUp(self):
        self.file_manager = FileManager()
    
    @patch('builtins.open')
    def test_read_file_mock(self, mock_open):
        mock_open.return_value.__enter__.return_value.read.return_value = 'test content'
        
        result = self.file_manager.read_file('dummy_file.txt')
        
        self.assertEqual(result, 'test content')
        mock_open.assert_called_once_with('dummy_file.txt', 'r')
    
    @patch('os.path.getsize')
    def test_get_file_size_mock(self, mock_getsize):
        mock_getsize.return_value = 1024
        
        result = self.file_manager.get_file_size('dummy_file.txt')
        
        self.assertEqual(result, 1024)
        mock_getsize.assert_called_once_with('dummy_file.txt')
    
    def test_with_temporary_file(self):
        """Test with real temporary file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write('test content for file operations')
            temp_file_path = temp_file.name
        
        try:
            # Test reading
            content = self.file_manager.read_file(temp_file_path)
            self.assertEqual(content, 'test content for file operations')
            
            # Test file size
            size = self.file_manager.get_file_size(temp_file_path)
            self.assertGreater(size, 0)
            
        finally:
            os.unlink(temp_file_path)

class APIClient:
    """API client for testing"""
    
    def __init__(self, base_url):
        self.base_url = base_url
    
    def get_data(self, endpoint):
        # In real implementation, this would make HTTP request
        import requests
        response = requests.get(f"{self.base_url}/{endpoint}")
        return response.json()

class TestAPIClientWithMocks(unittest.TestCase):
    """Test API client with mocks"""
    
    @patch('requests.get')
    def test_get_data(self, mock_get):
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = {'key': 'value', 'status': 'success'}
        mock_get.return_value = mock_response
        
        # Test
        client = APIClient('https://api.example.com')
        result = client.get_data('users')
        
        # Assertions
        self.assertEqual(result['status'], 'success')
        mock_get.assert_called_once_with('https://api.example.com/users')

def run_doctests():
    """Run doctests"""
    doctest.testmod()

if __name__ == "__main__":
    print("Running tests...")
    
    # Run unittest tests
    print("\n=== Running unittest ===")
    unittest_suite = unittest.TestLoader().loadTestsFromTestCase(TestCalculator)
    unittest_runner = unittest.TextTestRunner(verbosity=1)
    unittest_result = unittest_runner.run(unittest_suite)
    
    print(f"\nUnittest results: {unittest_result.testsRun} tests run")
    print(f"Failures: {len(unittest_result.failures)}")
    print(f"Errors: {len(unittest_result.errors)}")
    
    # Run doctests
    print("\n=== Running doctests ===")
    run_doctests()
    
    print("\nTest execution completed.")
