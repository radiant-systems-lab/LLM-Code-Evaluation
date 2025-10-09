# Database Management and ORM
import sqlite3
import psycopg2
import pymongo
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import StaticPool
import redis
from datetime import datetime, timedelta
import json

# SQLAlchemy ORM setup
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    posts = relationship("Post", back_populates="author")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(String(1000))
    author_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    author = relationship("User", back_populates="posts")
    
    def __repr__(self):
        return f"<Post(title='{self.title}', author='{self.author.username if self.author else None}')>"

def sqlite_operations():
    """SQLite database operations"""
    try:
        # Create in-memory database
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE employees (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT,
                salary REAL,
                hire_date DATE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE departments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                budget REAL
            )
        ''')
        
        # Insert sample data
        departments = [
            ('Engineering', 1000000),
            ('Marketing', 500000),
            ('Sales', 750000),
            ('HR', 300000)
        ]
        
        cursor.executemany('INSERT INTO departments (name, budget) VALUES (?, ?)', departments)
        
        employees = [
            ('Alice Johnson', 'Engineering', 85000, '2020-01-15'),
            ('Bob Smith', 'Engineering', 75000, '2019-03-20'),
            ('Carol Davis', 'Marketing', 65000, '2021-05-10'),
            ('David Wilson', 'Sales', 60000, '2020-08-05'),
            ('Eve Brown', 'Sales', 70000, '2019-11-12'),
            ('Frank Miller', 'HR', 55000, '2021-02-28')
        ]
        
        cursor.executemany('INSERT INTO employees (name, department, salary, hire_date) VALUES (?, ?, ?, ?)', employees)
        
        # Query operations
        # 1. Get all employees with salary > 70000
        cursor.execute('SELECT * FROM employees WHERE salary > 70000')
        high_earners = cursor.fetchall()
        
        # 2. Department-wise employee count
        cursor.execute('''
            SELECT department, COUNT(*) as emp_count, AVG(salary) as avg_salary
            FROM employees 
            GROUP BY department
        ''')
        dept_stats = cursor.fetchall()
        
        # 3. Join with departments table
        cursor.execute('''
            SELECT e.name, e.salary, d.budget
            FROM employees e
            JOIN departments d ON e.department = d.name
            WHERE e.salary > 60000
        ''')
        join_results = cursor.fetchall()
        
        # Transaction example
        try:
            cursor.execute('BEGIN TRANSACTION')
            cursor.execute('UPDATE employees SET salary = salary * 1.1 WHERE department = ?', ('Engineering',))
            cursor.execute('INSERT INTO employees (name, department, salary, hire_date) VALUES (?, ?, ?, ?)', 
                         ('Grace Lee', 'Engineering', 80000, '2024-01-01'))
            cursor.execute('COMMIT')
            transaction_success = True
        except Exception as e:
            cursor.execute('ROLLBACK')
            transaction_success = False
        
        conn.close()
        
        return {
            'database_type': 'SQLite',
            'tables_created': 2,
            'employees_inserted': len(employees),
            'departments_inserted': len(departments),
            'high_earners': len(high_earners),
            'department_stats': len(dept_stats),
            'join_results': len(join_results),
            'transaction_successful': transaction_success
        }
        
    except Exception as e:
        return {'error': str(e)}

def postgresql_simulation():
    """PostgreSQL operations simulation"""
    try:
        # Simulate PostgreSQL connection and operations
        # In real scenario: conn = psycopg2.connect(host="localhost", database="testdb", user="user", password="password")
        
        # Simulate complex queries and operations
        simulated_operations = {
            'create_database': {'status': 'success', 'database': 'analytics_db'},
            'create_tables': {
                'customers': {'columns': 8, 'indexes': 3},
                'orders': {'columns': 10, 'indexes': 4},
                'products': {'columns': 12, 'indexes': 5},
                'order_items': {'columns': 6, 'indexes': 3}
            },
            'data_insertion': {
                'customers': 10000,
                'orders': 50000,
                'products': 1000,
                'order_items': 125000
            },
            'complex_queries': [
                {
                    'name': 'monthly_sales_report',
                    'type': 'aggregation',
                    'execution_time_ms': 245,
                    'rows_processed': 50000,
                    'result_rows': 12
                },
                {
                    'name': 'customer_segmentation',
                    'type': 'window_function',
                    'execution_time_ms': 890,
                    'rows_processed': 10000,
                    'result_rows': 10000
                },
                {
                    'name': 'product_recommendations',
                    'type': 'common_table_expression',
                    'execution_time_ms': 1200,
                    'rows_processed': 125000,
                    'result_rows': 50
                }
            ],
            'stored_procedures': [
                {'name': 'calculate_loyalty_points', 'parameters': 3},
                {'name': 'update_inventory', 'parameters': 2},
                {'name': 'generate_monthly_report', 'parameters': 1}
            ],
            'triggers': [
                {'name': 'audit_customer_changes', 'table': 'customers'},
                {'name': 'update_order_total', 'table': 'orders'},
                {'name': 'inventory_check', 'table': 'order_items'}
            ]
        }
        
        # Simulate performance metrics
        performance_metrics = {
            'connection_pool_size': 20,
            'active_connections': 8,
            'average_query_time_ms': 150,
            'cache_hit_ratio': 0.85,
            'index_usage_ratio': 0.92,
            'database_size_gb': 2.5
        }
        
        return {
            'database_type': 'PostgreSQL',
            'tables': len(simulated_operations['create_tables']),
            'total_records': sum(simulated_operations['data_insertion'].values()),
            'complex_queries': len(simulated_operations['complex_queries']),
            'stored_procedures': len(simulated_operations['stored_procedures']),
            'triggers': len(simulated_operations['triggers']),
            'performance': performance_metrics,
            'simulation': True
        }
        
    except Exception as e:
        return {'error': str(e)}

def mongodb_operations():
    """MongoDB operations simulation"""
    try:
        # Simulate MongoDB operations
        # In real scenario: client = pymongo.MongoClient('mongodb://localhost:27017/')
        
        # Simulate document-based operations
        collections = {
            'users': {
                'documents': 5000,
                'indexes': ['email', 'username', 'created_at'],
                'average_document_size_kb': 2.1
            },
            'products': {
                'documents': 1000,
                'indexes': ['category', 'price', 'tags'],
                'average_document_size_kb': 5.3
            },
            'orders': {
                'documents': 15000,
                'indexes': ['user_id', 'created_at', 'status'],
                'average_document_size_kb': 3.8
            },
            'reviews': {
                'documents': 25000,
                'indexes': ['product_id', 'rating', 'created_at'],
                'average_document_size_kb': 1.2
            }
        }
        
        # Simulate aggregation pipelines
        aggregation_pipelines = [
            {
                'name': 'sales_by_category',
                'stages': ['$match', '$group', '$sort', '$limit'],
                'execution_time_ms': 320,
                'documents_processed': 15000
            },
            {
                'name': 'user_engagement_metrics',
                'stages': ['$lookup', '$unwind', '$group', '$project'],
                'execution_time_ms': 580,
                'documents_processed': 30000
            },
            {
                'name': 'product_ratings_summary',
                'stages': ['$match', '$group', '$addFields', '$sort'],
                'execution_time_ms': 190,
                'documents_processed': 25000
            }
        ]
        
        # Simulate text search operations
        text_search_results = {
            'search_queries': 1250,
            'average_response_time_ms': 45,
            'text_indexes': 3,
            'search_accuracy': 0.89
        }
        
        # Simulate geospatial operations
        geospatial_operations = {
            'location_based_queries': 450,
            'geospatial_indexes': ['2dsphere', '2d'],
            'average_radius_search_time_ms': 25,
            'proximity_searches': 180
        }
        
        # Simulate sharding information
        sharding_info = {
            'sharded_collections': ['orders', 'reviews'],
            'shard_count': 3,
            'chunk_count': 24,
            'balancer_enabled': True
        }
        
        return {
            'database_type': 'MongoDB',
            'collections': len(collections),
            'total_documents': sum(col['documents'] for col in collections.values()),
            'total_indexes': sum(len(col['indexes']) for col in collections.values()),
            'aggregation_pipelines': len(aggregation_pipelines),
            'text_search_queries': text_search_results['search_queries'],
            'geospatial_operations': geospatial_operations['location_based_queries'],
            'sharded_collections': len(sharding_info['sharded_collections']),
            'simulation': True
        }
        
    except Exception as e:
        return {'error': str(e)}

def sqlalchemy_orm_operations():
    """SQLAlchemy ORM operations"""
    try:
        # Create in-memory SQLite database
        engine = create_engine('sqlite:///:memory:', 
                             connect_args={'check_same_thread': False},
                             poolclass=StaticPool)
        
        # Create all tables
        Base.metadata.create_all(engine)
        
        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Create sample users
        users_data = [
            User(username='alice', email='alice@example.com'),
            User(username='bob', email='bob@example.com'),
            User(username='carol', email='carol@example.com'),
            User(username='dave', email='dave@example.com'),
            User(username='eve', email='eve@example.com')
        ]
        
        session.add_all(users_data)
        session.commit()
        
        # Create sample posts
        posts_data = [
            Post(title='Introduction to Python', content='Python is a great language...', author_id=1),
            Post(title='Database Design', content='Good database design is crucial...', author_id=1),
            Post(title='Web Development', content='Modern web development involves...', author_id=2),
            Post(title='Machine Learning', content='ML algorithms can help...', author_id=3),
            Post(title='Data Analysis', content='Data analysis reveals insights...', author_id=2),
            Post(title='Software Engineering', content='Best practices in software...', author_id=4),
            Post(title='System Design', content='Scalable system design...', author_id=5),
            Post(title='API Development', content='RESTful APIs are important...', author_id=3)
        ]
        
        session.add_all(posts_data)
        session.commit()
        
        # Query operations
        # 1. Get all users
        all_users = session.query(User).all()
        
        # 2. Get user with posts
        user_with_posts = session.query(User).filter(User.username == 'alice').first()
        alice_posts = user_with_posts.posts if user_with_posts else []
        
        # 3. Join query
        posts_with_authors = session.query(Post, User).join(User).all()
        
        # 4. Aggregate query
        post_count_by_user = session.query(User.username, 
                                         session.query(Post).filter(Post.author_id == User.id).count().label('post_count')).all()
        
        # 5. Filter and order
        recent_posts = session.query(Post).order_by(Post.created_at.desc()).limit(3).all()
        
        # 6. Update operation
        user_to_update = session.query(User).filter(User.username == 'bob').first()
        if user_to_update:
            user_to_update.email = 'bob.updated@example.com'
            session.commit()
        
        # 7. Delete operation
        post_to_delete = session.query(Post).filter(Post.title.like('%System%')).first()
        if post_to_delete:
            session.delete(post_to_delete)
            session.commit()
        
        # Raw SQL query
        result = session.execute(text('SELECT COUNT(*) as total_posts FROM posts')).fetchone()
        total_posts_raw = result[0] if result else 0
        
        session.close()
        
        return {
            'orm_framework': 'SQLAlchemy',
            'users_created': len(users_data),
            'posts_created': len(posts_data),
            'total_users': len(all_users),
            'alice_posts': len(alice_posts),
            'posts_with_authors': len(posts_with_authors),
            'recent_posts': len(recent_posts),
            'total_posts_raw': total_posts_raw,
            'operations': ['create', 'read', 'update', 'delete', 'join', 'aggregate']
        }
        
    except Exception as e:
        return {'error': str(e)}

def redis_caching():
    """Redis caching operations simulation"""
    try:
        # Simulate Redis operations
        # In real scenario: r = redis.Redis(host='localhost', port=6379, db=0)
        
        class MockRedis:
            def __init__(self):
                self.data = {}
                self.expires = {}
            
            def set(self, key, value, ex=None):
                self.data[key] = value
                if ex:
                    self.expires[key] = datetime.utcnow() + timedelta(seconds=ex)
                return True
            
            def get(self, key):
                if key in self.expires and datetime.utcnow() > self.expires[key]:
                    del self.data[key]
                    del self.expires[key]
                    return None
                return self.data.get(key)
            
            def delete(self, key):
                if key in self.data:
                    del self.data[key]
                if key in self.expires:
                    del self.expires[key]
                return True
            
            def exists(self, key):
                return key in self.data
            
            def keys(self, pattern='*'):
                if pattern == '*':
                    return list(self.data.keys())
                return [k for k in self.data.keys() if pattern.replace('*', '') in k]
            
            def hset(self, name, key, value):
                if name not in self.data:
                    self.data[name] = {}
                self.data[name][key] = value
                return True
            
            def hget(self, name, key):
                return self.data.get(name, {}).get(key)
            
            def hgetall(self, name):
                return self.data.get(name, {})
            
            def sadd(self, name, *values):
                if name not in self.data:
                    self.data[name] = set()
                for value in values:
                    self.data[name].add(value)
                return len(values)
            
            def smembers(self, name):
                return self.data.get(name, set())
            
            def incr(self, name):
                current = int(self.data.get(name, 0))
                self.data[name] = str(current + 1)
                return current + 1
        
        r = MockRedis()
        
        # Basic string operations
        cache_operations = []
        
        # Set and get operations
        r.set('user:1000', json.dumps({'name': 'Alice', 'email': 'alice@example.com'}))
        r.set('user:1001', json.dumps({'name': 'Bob', 'email': 'bob@example.com'}))
        r.set('session:abc123', 'user_id:1000', ex=3600)  # 1 hour expiry
        cache_operations.append('string_operations')
        
        # Hash operations (user profiles)
        r.hset('profile:1000', 'name', 'Alice Johnson')
        r.hset('profile:1000', 'age', '28')
        r.hset('profile:1000', 'city', 'New York')
        user_profile = r.hgetall('profile:1000')
        cache_operations.append('hash_operations')
        
        # Set operations (user interests)
        r.sadd('interests:1000', 'python', 'data-science', 'machine-learning')
        r.sadd('interests:1001', 'javascript', 'react', 'node.js')
        alice_interests = r.smembers('interests:1000')
        cache_operations.append('set_operations')
        
        # Counter operations (page views)
        for _ in range(50):
            r.incr('pageviews:homepage')
        for _ in range(30):
            r.incr('pageviews:about')
        homepage_views = r.get('pageviews:homepage')
        cache_operations.append('counter_operations')
        
        # Caching patterns simulation
        cache_patterns = {
            'read_through': {
                'cache_hits': 850,
                'cache_misses': 150,
                'hit_ratio': 0.85
            },
            'write_behind': {
                'queued_writes': 25,
                'batch_size': 100,
                'flush_interval_seconds': 30
            },
            'cache_aside': {
                'manual_cache_updates': 200,
                'cache_invalidations': 45,
                'stale_data_incidents': 3
            }
        }
        
        # Performance metrics
        performance_metrics = {
            'average_get_latency_ms': 0.15,
            'average_set_latency_ms': 0.18,
            'memory_usage_mb': 128.5,
            'operations_per_second': 12000,
            'connection_pool_size': 20
        }
        
        return {
            'cache_system': 'Redis',
            'operations_performed': len(cache_operations),
            'data_types_used': ['string', 'hash', 'set', 'counter'],
            'cache_patterns': len(cache_patterns),
            'user_profiles_cached': len([k for k in r.keys() if 'profile:' in k]),
            'page_view_counters': int(homepage_views) + int(r.get('pageviews:about') or 0),
            'alice_interests_count': len(alice_interests),
            'performance_metrics': performance_metrics,
            'simulation': True
        }
        
    except Exception as e:
        return {'error': str(e)}

def database_performance_tuning():
    """Database performance optimization simulation"""
    # Simulate performance analysis
    performance_analysis = {
        'slow_queries': [
            {
                'query': 'SELECT * FROM orders WHERE created_at > ? AND status = ?',
                'execution_time_ms': 2500,
                'rows_examined': 500000,
                'rows_returned': 1200,
                'optimization': 'Add composite index on (created_at, status)'
            },
            {
                'query': 'SELECT u.name, COUNT(o.id) FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id',
                'execution_time_ms': 1800,
                'rows_examined': 100000,
                'rows_returned': 5000,
                'optimization': 'Add index on orders.user_id, consider materialized view'
            }
        ],
        'index_recommendations': [
            {
                'table': 'orders',
                'columns': ['created_at', 'status'],
                'type': 'composite',
                'estimated_improvement': '75%'
            },
            {
                'table': 'products',
                'columns': ['category_id'],
                'type': 'single',
                'estimated_improvement': '45%'
            },
            {
                'table': 'users',
                'columns': ['email'],
                'type': 'unique',
                'estimated_improvement': '90%'
            }
        ],
        'table_statistics': {
            'users': {'rows': 50000, 'size_mb': 25.6, 'indexes': 3},
            'orders': {'rows': 250000, 'size_mb': 180.3, 'indexes': 5},
            'products': {'rows': 10000, 'size_mb': 45.2, 'indexes': 4},
            'order_items': {'rows': 500000, 'size_mb': 95.8, 'indexes': 3}
        },
        'query_patterns': {
            'select_queries': 85.5,  # percentage
            'insert_queries': 8.2,
            'update_queries': 4.8,
            'delete_queries': 1.5
        }
    }
    
    # Optimization strategies
    optimization_strategies = [
        {
            'strategy': 'Index Optimization',
            'actions': ['Create composite indexes', 'Remove unused indexes', 'Optimize index key order'],
            'estimated_performance_gain': 40
        },
        {
            'strategy': 'Query Optimization',
            'actions': ['Rewrite N+1 queries', 'Use EXPLAIN for query plans', 'Optimize JOIN operations'],
            'estimated_performance_gain': 60
        },
        {
            'strategy': 'Schema Design',
            'actions': ['Normalize hot tables', 'Denormalize read-heavy tables', 'Partition large tables'],
            'estimated_performance_gain': 30
        },
        {
            'strategy': 'Caching Strategy',
            'actions': ['Implement query result caching', 'Use application-level caching', 'Database connection pooling'],
            'estimated_performance_gain': 50
        }
    ]
    
    # Connection pool configuration
    connection_pool_config = {
        'max_connections': 100,
        'initial_connections': 10,
        'connection_timeout_seconds': 30,
        'idle_timeout_seconds': 600,
        'pool_usage_percentage': 65.2
    }
    
    return {
        'slow_queries_identified': len(performance_analysis['slow_queries']),
        'index_recommendations': len(performance_analysis['index_recommendations']),
        'tables_analyzed': len(performance_analysis['table_statistics']),
        'optimization_strategies': len(optimization_strategies),
        'total_database_size_mb': sum(table['size_mb'] for table in performance_analysis['table_statistics'].values()),
        'connection_pool_utilization': connection_pool_config['pool_usage_percentage'],
        'estimated_max_improvement': max(strategy['estimated_performance_gain'] for strategy in optimization_strategies)
    }

if __name__ == "__main__":
    print("Database management and ORM operations...")
    
    # SQLite operations
    sqlite_result = sqlite_operations()
    if 'error' not in sqlite_result:
        print(f"SQLite: {sqlite_result['employees_inserted']} employees, {sqlite_result['high_earners']} high earners")
    
    # PostgreSQL simulation
    postgresql_result = postgresql_simulation()
    if 'error' not in postgresql_result:
        print(f"PostgreSQL: {postgresql_result['tables']} tables, {postgresql_result['total_records']} records, {postgresql_result['complex_queries']} complex queries")
    
    # MongoDB simulation
    mongodb_result = mongodb_operations()
    if 'error' not in mongodb_result:
        print(f"MongoDB: {mongodb_result['collections']} collections, {mongodb_result['total_documents']} documents, {mongodb_result['aggregation_pipelines']} pipelines")
    
    # SQLAlchemy ORM
    sqlalchemy_result = sqlalchemy_orm_operations()
    if 'error' not in sqlalchemy_result:
        print(f"SQLAlchemy: {sqlalchemy_result['users_created']} users, {sqlalchemy_result['posts_created']} posts, {len(sqlalchemy_result['operations'])} operations")
    
    # Redis caching
    redis_result = redis_caching()
    if 'error' not in redis_result:
        print(f"Redis: {redis_result['operations_performed']} operations, {len(redis_result['data_types_used'])} data types, {redis_result['page_view_counters']} page views")
    
    # Performance tuning
    performance_result = database_performance_tuning()
    print(f"Performance: {performance_result['slow_queries_identified']} slow queries, {performance_result['estimated_max_improvement']}% max improvement possible")