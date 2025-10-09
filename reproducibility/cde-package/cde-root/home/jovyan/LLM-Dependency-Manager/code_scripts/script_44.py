# Performance Profiling and Memory Management
import cProfile
import pstats
import tracemalloc
import gc
import sys
import time
import psutil
import memory_profiler
from line_profiler import LineProfiler
import objgraph
import weakref
from pympler import muppy, summary

def cpu_profiling():
    """CPU profiling and performance analysis"""
    try:
        # Function to profile
        def fibonacci_recursive(n):
            if n <= 1:
                return n
            return fibonacci_recursive(n-1) + fibonacci_recursive(n-2)
        
        def fibonacci_iterative(n):
            if n <= 1:
                return n
            a, b = 0, 1
            for _ in range(2, n + 1):
                a, b = b, a + b
            return b
        
        def matrix_multiplication(size=100):
            import numpy as np
            a = np.random.rand(size, size)
            b = np.random.rand(size, size)
            return np.dot(a, b)
        
        # Profile recursive fibonacci
        pr = cProfile.Profile()
        pr.enable()
        
        fib_results = []
        for i in range(30):
            fib_results.append(fibonacci_recursive(i))
        
        pr.disable()
        
        # Get profiling stats
        stats = pstats.Stats(pr)
        stats.sort_stats('cumulative')
        
        # Capture stats
        total_calls = stats.total_calls
        total_time = stats.total_tt
        
        # Profile iterative version for comparison
        start_time = time.time()
        fib_iter_results = [fibonacci_iterative(i) for i in range(30)]
        iter_time = time.time() - start_time
        
        # Profile matrix operations
        start_time = time.time()
        matrix_result = matrix_multiplication()
        matrix_time = time.time() - start_time
        
        # Line-by-line profiling simulation
        def slow_function():
            # Simulate different performance hotspots
            result = 0
            for i in range(100000):  # Hotspot 1
                result += i ** 2
            
            data = []
            for i in range(10000):  # Hotspot 2
                data.append(str(i) * 10)
            
            processed = []
            for item in data:  # Hotspot 3
                processed.append(item.upper())
            
            return len(processed)
        
        # Time the slow function
        start_time = time.time()
        slow_result = slow_function()
        slow_time = time.time() - start_time
        
        # System resource monitoring
        process = psutil.Process()
        cpu_percent = process.cpu_percent()
        memory_info = process.memory_info()
        
        return {
            'profiling_total_calls': total_calls,
            'profiling_total_time': total_time,
            'recursive_fib_last_result': fib_results[-1] if fib_results else 0,
            'iterative_fib_time': iter_time,
            'matrix_multiplication_time': matrix_time,
            'slow_function_time': slow_time,
            'slow_function_result': slow_result,
            'cpu_percent': cpu_percent,
            'memory_rss_mb': memory_info.rss / (1024 * 1024),
            'memory_vms_mb': memory_info.vms / (1024 * 1024)
        }
        
    except Exception as e:
        return {'error': str(e)}

def memory_profiling():
    """Memory profiling and leak detection"""
    try:
        # Start memory tracing
        tracemalloc.start()
        
        # Memory-intensive operations
        def create_large_lists():
            data = []
            for i in range(1000):
                sublist = [j for j in range(1000)]
                data.append(sublist)
            return data
        
        def create_objects():
            class TestObject:
                def __init__(self, data):
                    self.data = data
                    self.references = []
            
            objects = []
            for i in range(10000):
                obj = TestObject(f"data_{i}")
                objects.append(obj)
            
            # Create circular references
            for i in range(len(objects) - 1):
                objects[i].references.append(objects[i + 1])
                objects[i + 1].references.append(objects[i])
            
            return objects
        
        # Baseline memory
        snapshot1 = tracemalloc.take_snapshot()
        
        # Create memory load
        large_data = create_large_lists()
        objects = create_objects()
        
        # Take snapshot after allocation
        snapshot2 = tracemalloc.take_snapshot()
        
        # Calculate memory difference
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        
        # Memory statistics
        current_memory, peak_memory = tracemalloc.get_traced_memory()
        
        # Garbage collection
        gc_before = len(gc.get_objects())
        collected = gc.collect()
        gc_after = len(gc.get_objects())
        
        # Object counting with objgraph simulation
        def count_objects_by_type():
            obj_count = {}
            for obj in gc.get_objects():
                obj_type = type(obj).__name__
                obj_count[obj_type] = obj_count.get(obj_type, 0) + 1
            return obj_count
        
        object_counts = count_objects_by_type()
        top_object_types = sorted(object_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Memory leak detection
        def detect_memory_leaks():
            # Create and delete objects multiple times
            for cycle in range(3):
                temp_objects = []
                for i in range(1000):
                    temp_objects.append([i] * 100)
                del temp_objects
                gc.collect()
        
        # Memory before leak test
        mem_before_leak = psutil.Process().memory_info().rss
        detect_memory_leaks()
        mem_after_leak = psutil.Process().memory_info().rss
        
        # Weak references example
        class TrackedObject:
            def __init__(self, name):
                self.name = name
        
        # Create objects with weak references
        strong_refs = []
        weak_refs = []
        
        for i in range(100):
            obj = TrackedObject(f"obj_{i}")
            strong_refs.append(obj)
            weak_refs.append(weakref.ref(obj))
        
        # Check weak reference validity
        valid_weak_refs = sum(1 for ref in weak_refs if ref() is not None)
        
        # Clean up and check again
        del strong_refs
        gc.collect()
        valid_weak_refs_after = sum(1 for ref in weak_refs if ref() is not None)
        
        # Stop memory tracing
        tracemalloc.stop()
        
        return {
            'current_memory_mb': current_memory / (1024 * 1024),
            'peak_memory_mb': peak_memory / (1024 * 1024),
            'gc_objects_before': gc_before,
            'gc_objects_collected': collected,
            'gc_objects_after': gc_after,
            'top_object_types': top_object_types,
            'memory_stats_count': len(top_stats),
            'memory_leak_diff_bytes': mem_after_leak - mem_before_leak,
            'weak_refs_before_cleanup': valid_weak_refs,
            'weak_refs_after_cleanup': valid_weak_refs_after,
            'large_data_size': len(large_data),
            'objects_created': len(objects) if 'objects' in locals() else 0
        }
        
    except Exception as e:
        return {'error': str(e)}

def performance_optimization():
    """Performance optimization techniques"""
    try:
        import numpy as np
        from collections import defaultdict
        
        # Optimization technique 1: List comprehensions vs loops
        def list_comp_test(n=100000):
            # Using list comprehension
            start = time.time()
            squares_comp = [i**2 for i in range(n)]
            comp_time = time.time() - start
            
            # Using traditional loop
            start = time.time()
            squares_loop = []
            for i in range(n):
                squares_loop.append(i**2)
            loop_time = time.time() - start
            
            return comp_time, loop_time, len(squares_comp)
        
        comp_time, loop_time, list_size = list_comp_test()
        
        # Optimization technique 2: Dictionary defaultdict vs regular dict
        def dict_comparison_test(n=10000):
            # Regular dictionary with key checking
            start = time.time()
            regular_dict = {}
            for i in range(n):
                key = i % 100
                if key in regular_dict:
                    regular_dict[key] += 1
                else:
                    regular_dict[key] = 1
            regular_time = time.time() - start
            
            # Using defaultdict
            start = time.time()
            default_dict = defaultdict(int)
            for i in range(n):
                key = i % 100
                default_dict[key] += 1
            default_time = time.time() - start
            
            return regular_time, default_time, len(regular_dict)
        
        regular_dict_time, default_dict_time, dict_size = dict_comparison_test()
        
        # Optimization technique 3: NumPy vs pure Python
        def numpy_vs_python(size=1000000):
            data = list(range(size))
            
            # Pure Python
            start = time.time()
            python_sum = sum(x**2 for x in data)
            python_time = time.time() - start
            
            # NumPy
            np_data = np.array(data)
            start = time.time()
            numpy_sum = np.sum(np_data**2)
            numpy_time = time.time() - start
            
            return python_time, numpy_time, python_sum, int(numpy_sum)
        
        python_time, numpy_time, python_sum, numpy_sum = numpy_vs_python()
        
        # Optimization technique 4: String concatenation methods
        def string_concat_test(n=10000):
            # Using + operator
            start = time.time()
            result1 = ""
            for i in range(n):
                result1 += str(i)
            plus_time = time.time() - start
            
            # Using join
            start = time.time()
            parts = [str(i) for i in range(n)]
            result2 = "".join(parts)
            join_time = time.time() - start
            
            return plus_time, join_time, len(result1), len(result2)
        
        plus_time, join_time, len1, len2 = string_concat_test()
        
        # Optimization technique 5: Set operations vs list operations
        def set_vs_list_test(n=10000):
            data1 = list(range(n))
            data2 = list(range(n//2, n + n//2))
            
            # List intersection
            start = time.time()
            intersection_list = [x for x in data1 if x in data2]
            list_time = time.time() - start
            
            # Set intersection
            start = time.time()
            set1, set2 = set(data1), set(data2)
            intersection_set = list(set1 & set2)
            set_time = time.time() - start
            
            return list_time, set_time, len(intersection_list), len(intersection_set)
        
        list_int_time, set_int_time, list_int_len, set_int_len = set_vs_list_test()
        
        # Calculate optimization ratios
        comp_speedup = loop_time / comp_time if comp_time > 0 else 1
        dict_speedup = regular_dict_time / default_dict_time if default_dict_time > 0 else 1
        numpy_speedup = python_time / numpy_time if numpy_time > 0 else 1
        string_speedup = plus_time / join_time if join_time > 0 else 1
        set_speedup = list_int_time / set_int_time if set_int_time > 0 else 1
        
        return {
            'list_comprehension_speedup': comp_speedup,
            'defaultdict_speedup': dict_speedup,
            'numpy_speedup': numpy_speedup,
            'string_join_speedup': string_speedup,
            'set_operation_speedup': set_speedup,
            'optimization_techniques': 5,
            'average_speedup': (comp_speedup + dict_speedup + numpy_speedup + string_speedup + set_speedup) / 5,
            'results_match': (python_sum == numpy_sum and len1 == len2 and list_int_len == set_int_len)
        }
        
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    print("Performance profiling and memory management...")
    
    # CPU profiling
    cpu_result = cpu_profiling()
    if 'error' not in cpu_result:
        print(f"CPU Profiling: {cpu_result['profiling_total_calls']} calls, {cpu_result['profiling_total_time']:.4f}s total")
    
    # Memory profiling
    memory_result = memory_profiling()
    if 'error' not in memory_result:
        print(f"Memory: Peak {memory_result['peak_memory_mb']:.2f}MB, {memory_result['gc_objects_collected']} objects collected")
    
    # Performance optimization
    perf_result = performance_optimization()
    if 'error' not in perf_result:
        print(f"Optimization: Avg speedup {perf_result['average_speedup']:.2f}x, NumPy {perf_result['numpy_speedup']:.1f}x faster")