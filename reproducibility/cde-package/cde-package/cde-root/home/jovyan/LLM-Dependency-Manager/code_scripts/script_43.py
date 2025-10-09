# Advanced Python Features and Patterns
import asyncio
import functools
import itertools
import collections
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, TypeVar, Generic
import abc
from contextlib import contextmanager
import weakref
import inspect
from pathlib import Path

@dataclass
class PersonAdvanced:
    """Advanced dataclass with various features"""
    name: str
    age: int
    skills: List[str] = field(default_factory=list)
    metadata: Dict[str, Union[str, int]] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.age < 0:
            raise ValueError("Age cannot be negative")

class AdvancedPatterns:
    """Demonstration of advanced Python patterns"""
    
    def __init__(self):
        self.cache = {}
        self._observers = weakref.WeakSet()
    
    @functools.lru_cache(maxsize=128)
    def fibonacci(self, n):
        if n < 2:
            return n
        return self.fibonacci(n-1) + self.fibonacci(n-2)
    
    @property 
    def computed_value(self):
        return sum(range(100))
    
    @contextmanager
    def timer(self):
        import time
        start = time.time()
        yield
        print(f"Elapsed: {time.time() - start:.4f}s")

def decorator_factory(prefix="LOG"):
    """Advanced decorator with parameters"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            print(f"{prefix}: {func.__name__} called")
            return result
        return wrapper
    return decorator

async def async_operations():
    """Async/await patterns"""
    async def fetch_data(url):
        await asyncio.sleep(0.1)  # Simulate network delay
        return f"Data from {url}"
    
    # Concurrent execution
    tasks = [fetch_data(f"url{i}") for i in range(5)]
    results = await asyncio.gather(*tasks)
    return len(results)

T = TypeVar('T')

class GenericContainer(Generic[T]):
    """Generic class demonstration"""
    def __init__(self):
        self._items: List[T] = []
    
    def add(self, item: T) -> None:
        self._items.append(item)
    
    def get_all(self) -> List[T]:
        return self._items.copy()

def advanced_python_demo():
    """Demonstrate advanced Python features"""
    try:
        # Advanced data structures
        counter = collections.Counter("abcabc")
        deque = collections.deque(maxlen=5)
        for i in range(10):
            deque.append(i)
        
        # Advanced iterators
        combinations = list(itertools.combinations([1,2,3,4], 2))
        permutations = list(itertools.permutations([1,2,3], 2))
        
        # Function introspection
        sig = inspect.signature(advanced_python_demo)
        
        # Dataclass usage
        person = PersonAdvanced("Alice", 30, ["Python", "ML"])
        
        # Generic container
        container = GenericContainer[int]()
        container.add(42)
        
        # Pattern matching simulation (for older Python versions)
        value = 42
        if isinstance(value, int) and value > 0:
            result = "positive integer"
        else:
            result = "other"
        
        return {
            'counter_most_common': counter.most_common(1)[0] if counter else ('', 0),
            'deque_length': len(deque),
            'combinations_count': len(combinations),
            'permutations_count': len(permutations),
            'person_skills': len(person.skills),
            'container_items': len(container.get_all()),
            'pattern_match_result': result,
            'features_demonstrated': 8
        }
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    print("Advanced Python features and patterns...")
    result = advanced_python_demo()
    if 'error' not in result:
        print(f"Demo: {result['features_demonstrated']} features, {result['combinations_count']} combinations")
    
    # Run async demo
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        async_result = loop.run_until_complete(async_operations())
        print(f"Async: {async_result} tasks completed")
        loop.close()
    except:
        print("Async: Demo completed")