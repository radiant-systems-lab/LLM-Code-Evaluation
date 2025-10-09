# Async Programming and Concurrency
import asyncio
import aiohttp
import concurrent.futures
import threading
import time
from queue import Queue
import uvloop

async def fetch_url_async(session, url):
    """Async HTTP request"""
    try:
        async with session.get(url) as response:
            return await response.text()
    except aiohttp.ClientError as e:
        print(f"Error fetching {url}: {e}")
        return None

async def fetch_multiple_urls(urls):
    """Fetch multiple URLs concurrently"""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url_async(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

def cpu_intensive_task(n):
    """CPU-intensive task for threading example"""
    result = sum(i * i for i in range(n))
    return result

def threaded_execution(tasks):
    """Execute tasks using ThreadPoolExecutor"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_task = {executor.submit(cpu_intensive_task, task): task for task in tasks}
        results = []
        
        for future in concurrent.futures.as_completed(future_to_task):
            task = future_to_task[future]
            try:
                result = future.result()
                results.append((task, result))
            except Exception as exc:
                print(f'Task {task} generated an exception: {exc}')
        
        return results

class ProducerConsumerExample:
    def __init__(self):
        self.queue = Queue()
        self.results = []
    
    def producer(self, items):
        """Producer thread"""
        for item in items:
            time.sleep(0.1)  # Simulate work
            self.queue.put(item)
            print(f"Produced: {item}")
        
        # Signal completion
        self.queue.put(None)
    
    def consumer(self):
        """Consumer thread"""
        while True:
            item = self.queue.get()
            if item is None:
                break
            
            # Process item
            processed = item * 2
            self.results.append(processed)
            print(f"Consumed: {item} -> {processed}")
            self.queue.task_done()

async def async_main():
    """Main async function"""
    print("Starting async operations...")
    
    # Test URLs
    urls = [
        'https://httpbin.org/delay/1',
        'https://httpbin.org/delay/2',
        'https://httpbin.org/json'
    ]
    
    start_time = time.time()
    results = await fetch_multiple_urls(urls)
    end_time = time.time()
    
    print(f"Fetched {len([r for r in results if r and not isinstance(r, Exception)])} URLs")
    print(f"Async execution time: {end_time - start_time:.2f} seconds")

def main():
    """Main synchronous function"""
    # Threading example
    print("Testing threading...")
    tasks = [100000, 200000, 300000, 400000]
    start_time = time.time()
    thread_results = threaded_execution(tasks)
    end_time = time.time()
    print(f"Threading execution time: {end_time - start_time:.2f} seconds")
    
    # Producer-Consumer example
    print("Testing producer-consumer...")
    pc_example = ProducerConsumerExample()
    items = list(range(1, 11))
    
    producer_thread = threading.Thread(target=pc_example.producer, args=(items,))
    consumer_thread = threading.Thread(target=pc_example.consumer)
    
    producer_thread.start()
    consumer_thread.start()
    
    producer_thread.join()
    consumer_thread.join()
    
    print(f"Processed {len(pc_example.results)} items")
    
    # Run async code
    try:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except:
        pass  # uvloop not available
    
    asyncio.run(async_main())

if __name__ == "__main__":
    main()