# Database Management and Data Warehousing
import sqlite3
import psycopg2
import pymongo
import redis
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import hashlib
from collections import defaultdict
import pickle

# SQLAlchemy models
Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    total_spent = Column(Float, default=0.0)
    
    orders = relationship("Order", back_populates="customer")

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100))
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)
    
    order_items = relationship("OrderItem", back_populates="product")

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    order_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), default='pending')
    
    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

def relational_database_operations():
    """Relational database operations with SQLAlchemy and SQLite"""
    try:
        # Create in-memory SQLite database
        engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Generate sample data
        np.random.seed(42)
        
        # Create customers
        customer_names = ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson', 'Emma Brown', 
                         'Frank Miller', 'Grace Lee', 'Henry Garcia', 'Ivy Martinez', 'Jack Anderson']
        
        customers = []
        for i, name in enumerate(customer_names):
            customer = Customer(
                name=name,
                email=f"{name.lower().replace(' ', '.')}@email.com",
                registration_date=datetime.utcnow() - timedelta(days=np.random.randint(30, 365)),
                total_spent=np.random.uniform(100, 5000)
            )
            customers.append(customer)
            session.add(customer)
        
        # Create products
        product_data = [
            ('Laptop', 'Electronics', 999.99),
            ('Mouse', 'Electronics', 25.99),
            ('Keyboard', 'Electronics', 79.99),
            ('Monitor', 'Electronics', 299.99),
            ('Desk Chair', 'Furniture', 199.99),
            ('Coffee Mug', 'Home', 12.99),
            ('Notebook', 'Office', 5.99),
            ('Pen Set', 'Office', 15.99),
            ('Phone Case', 'Electronics', 19.99),
            ('Water Bottle', 'Home', 24.99)
        ]
        
        products = []
        for name, category, price in product_data:
            product = Product(
                name=name,
                category=category,
                price=price,
                stock_quantity=np.random.randint(10, 100)
            )
            products.append(product)
            session.add(product)
        
        session.commit()
        
        # Create orders
        orders_created = 0
        total_order_items = 0
        
        for customer in customers:
            num_orders = np.random.randint(1, 5)
            
            for _ in range(num_orders):
                order = Order(
                    customer_id=customer.id,
                    order_date=datetime.utcnow() - timedelta(days=np.random.randint(1, 90)),
                    total_amount=0,
                    status=np.random.choice(['pending', 'completed', 'cancelled'], p=[0.2, 0.7, 0.1])
                )
                session.add(order)
                session.flush()  # To get order ID
                
                # Add order items
                num_items = np.random.randint(1, 4)
                order_total = 0
                
                selected_products = np.random.choice(products, num_items, replace=False)
                
                for product in selected_products:
                    quantity = np.random.randint(1, 3)
                    item_price = product.price * quantity
                    order_total += item_price
                    
                    order_item = OrderItem(
                        order_id=order.id,
                        product_id=product.id,
                        quantity=quantity,
                        price=item_price
                    )
                    session.add(order_item)
                    total_order_items += 1
                
                order.total_amount = order_total
                orders_created += 1
        
        session.commit()
        
        # Perform complex queries
        
        # 1. Customer analysis
        customer_stats = session.query(Customer).count()
        avg_customer_spent = session.query(Customer).all()
        avg_spent = np.mean([c.total_spent for c in avg_customer_spent])
        
        # 2. Product analysis
        product_stats = session.query(Product).count()
        products_by_category = defaultdict(int)
        for product in session.query(Product).all():
            products_by_category[product.category] += 1
        
        # 3. Order analysis
        completed_orders = session.query(Order).filter(Order.status == 'completed').count()
        total_orders = session.query(Order).count()
        completion_rate = completed_orders / total_orders if total_orders > 0 else 0
        
        # 4. Revenue analysis
        completed_order_objects = session.query(Order).filter(Order.status == 'completed').all()
        total_revenue = sum(order.total_amount for order in completed_order_objects)
        avg_order_value = total_revenue / completed_orders if completed_orders > 0 else 0
        
        # 5. Join queries - Top customers by order count
        from sqlalchemy import func
        top_customers = session.query(
            Customer.name,
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('total_spent')
        ).join(Order).group_by(Customer.id).order_by(
            func.count(Order.id).desc()
        ).limit(3).all()
        
        # 6. Product popularity
        popular_products = session.query(
            Product.name,
            func.sum(OrderItem.quantity).label('total_sold'),
            func.sum(OrderItem.price).label('total_revenue')
        ).join(OrderItem).group_by(Product.id).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(3).all()
        
        session.close()
        
        return {
            'customers_created': customer_stats,
            'products_created': product_stats,
            'orders_created': orders_created,
            'order_items_created': total_order_items,
            'average_customer_spent': avg_spent,
            'products_by_category': dict(products_by_category),
            'order_completion_rate': completion_rate,
            'total_revenue': total_revenue,
            'average_order_value': avg_order_value,
            'top_customers': len(top_customers),
            'popular_products_analyzed': len(popular_products),
            'database_operations': 6,
            'query_complexity': 'high'
        }
        
    except Exception as e:
        return {'error': str(e)}

def nosql_document_operations():
    """NoSQL document database operations simulation"""
    try:
        # Simulate MongoDB operations with in-memory data structures
        
        # Mock MongoDB collections
        users_collection = []
        posts_collection = []
        comments_collection = []
        
        # Generate user documents
        np.random.seed(42)
        
        for i in range(50):
            user_doc = {
                '_id': f'user_{i:03d}',
                'username': f'user{i}',
                'email': f'user{i}@example.com',
                'profile': {
                    'firstName': f'FirstName{i}',
                    'lastName': f'LastName{i}',
                    'age': np.random.randint(18, 65),
                    'location': np.random.choice(['New York', 'California', 'Texas', 'Florida']),
                    'interests': np.random.choice(['tech', 'sports', 'music', 'travel', 'food'], 
                                                size=np.random.randint(1, 4), replace=False).tolist()
                },
                'settings': {
                    'notifications': np.random.choice([True, False]),
                    'privacy': np.random.choice(['public', 'private', 'friends']),
                    'theme': np.random.choice(['light', 'dark'])
                },
                'joinDate': datetime.utcnow() - timedelta(days=np.random.randint(30, 730)),
                'lastLogin': datetime.utcnow() - timedelta(days=np.random.randint(0, 30)),
                'followerCount': np.random.randint(0, 1000),
                'followingCount': np.random.randint(0, 500)
            }
            users_collection.append(user_doc)
        
        # Generate post documents
        for i in range(200):
            author = np.random.choice(users_collection)
            post_doc = {
                '_id': f'post_{i:03d}',
                'authorId': author['_id'],
                'title': f'Post Title {i}',
                'content': f'This is the content of post {i}. It contains various topics and ideas.',
                'tags': np.random.choice(['technology', 'lifestyle', 'business', 'entertainment', 'science'], 
                                       size=np.random.randint(1, 3), replace=False).tolist(),
                'category': np.random.choice(['blog', 'news', 'tutorial', 'opinion']),
                'publishDate': datetime.utcnow() - timedelta(days=np.random.randint(0, 365)),
                'likes': np.random.randint(0, 500),
                'shares': np.random.randint(0, 100),
                'viewCount': np.random.randint(10, 2000),
                'status': np.random.choice(['published', 'draft', 'archived'], p=[0.8, 0.15, 0.05]),
                'metadata': {
                    'readTime': np.random.randint(2, 15),
                    'difficulty': np.random.choice(['beginner', 'intermediate', 'advanced']),
                    'featured': np.random.choice([True, False], p=[0.1, 0.9])
                }
            }
            posts_collection.append(post_doc)
        
        # Generate comment documents
        for i in range(500):
            post = np.random.choice([p for p in posts_collection if p['status'] == 'published'])
            commenter = np.random.choice(users_collection)
            
            comment_doc = {
                '_id': f'comment_{i:03d}',
                'postId': post['_id'],
                'authorId': commenter['_id'],
                'content': f'This is comment {i} on the post.',
                'timestamp': datetime.utcnow() - timedelta(days=np.random.randint(0, 30)),
                'likes': np.random.randint(0, 50),
                'replies': [],
                'flagged': np.random.choice([True, False], p=[0.05, 0.95])
            }
            
            # Add some replies
            if np.random.random() < 0.3:  # 30% chance of having replies
                num_replies = np.random.randint(1, 4)
                for j in range(num_replies):
                    replier = np.random.choice(users_collection)
                    reply = {
                        '_id': f'reply_{i}_{j}',
                        'authorId': replier['_id'],
                        'content': f'Reply {j} to comment {i}',
                        'timestamp': comment_doc['timestamp'] + timedelta(minutes=np.random.randint(5, 120)),
                        'likes': np.random.randint(0, 20)
                    }
                    comment_doc['replies'].append(reply)
            
            comments_collection.append(comment_doc)
        
        # Perform NoSQL-style queries and aggregations
        
        # 1. User analytics
        active_users = len([u for u in users_collection 
                           if (datetime.utcnow() - u['lastLogin']).days <= 7])
        
        users_by_location = defaultdict(int)
        for user in users_collection:
            users_by_location[user['profile']['location']] += 1
        
        avg_follower_count = np.mean([u['followerCount'] for u in users_collection])
        
        # 2. Content analytics
        published_posts = [p for p in posts_collection if p['status'] == 'published']
        total_views = sum(p['viewCount'] for p in published_posts)
        avg_engagement = np.mean([p['likes'] + p['shares'] for p in published_posts])
        
        posts_by_category = defaultdict(int)
        for post in published_posts:
            posts_by_category[post['category']] += 1
        
        # 3. Tag analysis
        tag_frequency = defaultdict(int)
        for post in published_posts:
            for tag in post['tags']:
                tag_frequency[tag] += 1
        
        most_popular_tags = sorted(tag_frequency.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # 4. Comment analytics
        total_comments = len(comments_collection)
        comments_with_replies = len([c for c in comments_collection if c['replies']])
        avg_comment_likes = np.mean([c['likes'] for c in comments_collection])
        
        # 5. User engagement patterns
        user_post_counts = defaultdict(int)
        for post in published_posts:
            user_post_counts[post['authorId']] += 1
        
        most_active_users = sorted(user_post_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # 6. Temporal analysis
        recent_posts = len([p for p in published_posts 
                           if (datetime.utcnow() - p['publishDate']).days <= 30])
        
        # 7. Advanced aggregation - User content performance
        user_performance = {}
        for user in users_collection[:5]:  # Top 5 users analysis
            user_posts = [p for p in published_posts if p['authorId'] == user['_id']]
            if user_posts:
                total_views = sum(p['viewCount'] for p in user_posts)
                total_engagement = sum(p['likes'] + p['shares'] for p in user_posts)
                user_performance[user['username']] = {
                    'posts': len(user_posts),
                    'total_views': total_views,
                    'total_engagement': total_engagement,
                    'avg_engagement_per_post': total_engagement / len(user_posts)
                }
        
        return {
            'total_users': len(users_collection),
            'total_posts': len(posts_collection),
            'total_comments': total_comments,
            'active_users_last_week': active_users,
            'users_by_location': dict(users_by_location),
            'published_posts': len(published_posts),
            'total_content_views': total_views,
            'average_engagement': avg_engagement,
            'posts_by_category': dict(posts_by_category),
            'top_tags': most_popular_tags,
            'comments_with_replies': comments_with_replies,
            'most_active_users_count': len(most_active_users),
            'recent_posts_month': recent_posts,
            'user_performance_analyzed': len(user_performance),
            'document_operations': 7,
            'aggregation_complexity': 'high'
        }
        
    except Exception as e:
        return {'error': str(e)}

def data_warehousing():
    """Data warehousing and ETL operations"""
    try:
        # Simulate ETL (Extract, Transform, Load) process
        
        # 1. EXTRACT - Simulate data from multiple sources
        
        # Source 1: Sales data
        sales_data = []
        for i in range(1000):
            sale = {
                'sale_id': i + 1,
                'date': datetime.utcnow() - timedelta(days=np.random.randint(0, 365)),
                'product_id': np.random.randint(1, 50),
                'customer_id': np.random.randint(1, 200),
                'quantity': np.random.randint(1, 10),
                'unit_price': np.round(np.random.uniform(10, 500), 2),
                'total_amount': 0,  # Will be calculated
                'sales_rep_id': np.random.randint(1, 20),
                'region': np.random.choice(['North', 'South', 'East', 'West'])
            }
            sale['total_amount'] = sale['quantity'] * sale['unit_price']
            sales_data.append(sale)
        
        # Source 2: Customer data
        customer_data = []
        for i in range(200):
            customer = {
                'customer_id': i + 1,
                'name': f'Customer {i+1}',
                'email': f'customer{i+1}@example.com',
                'registration_date': datetime.utcnow() - timedelta(days=np.random.randint(30, 1000)),
                'age_group': np.random.choice(['18-25', '26-35', '36-45', '46-55', '55+']),
                'city': np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
                'segment': np.random.choice(['Premium', 'Standard', 'Basic']),
                'lifetime_value': np.round(np.random.uniform(100, 10000), 2)
            }
            customer_data.append(customer)
        
        # Source 3: Product data
        product_data = []
        categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports']
        for i in range(50):
            product = {
                'product_id': i + 1,
                'name': f'Product {i+1}',
                'category': np.random.choice(categories),
                'cost': np.round(np.random.uniform(5, 200), 2),
                'margin': np.round(np.random.uniform(0.2, 0.6), 2),
                'supplier_id': np.random.randint(1, 10),
                'launch_date': datetime.utcnow() - timedelta(days=np.random.randint(30, 800))
            }
            product_data.append(product)
        
        # 2. TRANSFORM - Data cleaning and transformation
        
        # Convert to DataFrames for easier processing
        sales_df = pd.DataFrame(sales_data)
        customer_df = pd.DataFrame(customer_data)
        product_df = pd.DataFrame(product_data)
        
        # Data quality checks and cleaning
        data_quality_issues = {
            'duplicate_sales': sales_df.duplicated().sum(),
            'missing_customer_emails': customer_df['email'].isnull().sum(),
            'negative_quantities': (sales_df['quantity'] < 0).sum(),
            'zero_prices': (sales_df['unit_price'] == 0).sum()
        }
        
        # Clean data
        sales_df = sales_df.drop_duplicates()
        sales_df = sales_df[sales_df['quantity'] > 0]
        sales_df = sales_df[sales_df['unit_price'] > 0]
        
        # Transform data - Create date dimensions
        sales_df['year'] = sales_df['date'].dt.year
        sales_df['month'] = sales_df['date'].dt.month
        sales_df['quarter'] = sales_df['date'].dt.quarter
        sales_df['day_of_week'] = sales_df['date'].dt.dayofweek
        sales_df['week_of_year'] = sales_df['date'].dt.isocalendar().week
        
        # Create fact table (Sales Fact)
        fact_sales = sales_df.merge(customer_df, on='customer_id', how='left')
        fact_sales = fact_sales.merge(product_df, on='product_id', how='left')
        
        # Calculate derived metrics
        fact_sales['profit'] = fact_sales['total_amount'] - (fact_sales['quantity'] * fact_sales['cost'])
        fact_sales['profit_margin'] = fact_sales['profit'] / fact_sales['total_amount']
        
        # 3. Create dimension tables
        
        # Date dimension
        date_range = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
        date_dimension = pd.DataFrame({
            'date': date_range,
            'year': date_range.year,
            'month': date_range.month,
            'quarter': date_range.quarter,
            'day_of_week': date_range.dayofweek,
            'month_name': date_range.strftime('%B'),
            'is_weekend': date_range.dayofweek >= 5
        })
        
        # Customer dimension (enhanced)
        customer_dimension = customer_df.copy()
        customer_dimension['customer_tier'] = pd.cut(customer_dimension['lifetime_value'], 
                                                    bins=[0, 500, 2000, 5000, float('inf')], 
                                                    labels=['Bronze', 'Silver', 'Gold', 'Platinum'])
        
        # Product dimension (enhanced)
        product_dimension = product_df.copy()
        product_dimension['price_category'] = pd.cut(product_dimension['cost'], 
                                                   bins=[0, 25, 100, 300, float('inf')], 
                                                   labels=['Budget', 'Standard', 'Premium', 'Luxury'])
        
        # 4. LOAD - Aggregate and analyze data (simulating loading to warehouse)
        
        # Sales aggregations by different dimensions
        monthly_sales = fact_sales.groupby(['year', 'month']).agg({
            'total_amount': 'sum',
            'profit': 'sum',
            'quantity': 'sum',
            'sale_id': 'count'
        }).reset_index()
        
        category_performance = fact_sales.groupby('category').agg({
            'total_amount': 'sum',
            'profit': 'sum',
            'quantity': 'sum',
            'profit_margin': 'mean'
        }).reset_index()
        
        customer_analytics = fact_sales.groupby('customer_id').agg({
            'total_amount': 'sum',
            'sale_id': 'count',
            'profit': 'sum'
        }).reset_index()
        customer_analytics['avg_order_value'] = customer_analytics['total_amount'] / customer_analytics['sale_id']
        
        regional_performance = fact_sales.groupby('region').agg({
            'total_amount': 'sum',
            'profit': 'sum',
            'customer_id': 'nunique'
        }).reset_index()
        
        # Advanced analytics
        # Cohort analysis simulation
        customer_cohorts = defaultdict(list)
        for customer in customer_df.itertuples():
            cohort_month = customer.registration_date.strftime('%Y-%m')
            customer_cohorts[cohort_month].append(customer.customer_id)
        
        # RFM analysis (Recency, Frequency, Monetary)
        current_date = datetime.utcnow()
        rfm_analysis = fact_sales.groupby('customer_id').agg({
            'date': lambda x: (current_date - x.max()).days,  # Recency
            'sale_id': 'count',  # Frequency
            'total_amount': 'sum'  # Monetary
        }).reset_index()
        rfm_analysis.columns = ['customer_id', 'recency', 'frequency', 'monetary']
        
        # Score customers (1-5 scale)
        rfm_analysis['R_score'] = pd.qcut(rfm_analysis['recency'].rank(method='first'), 5, 
                                         labels=[5, 4, 3, 2, 1])  # Lower recency = higher score
        rfm_analysis['F_score'] = pd.qcut(rfm_analysis['frequency'], 5, labels=[1, 2, 3, 4, 5])
        rfm_analysis['M_score'] = pd.qcut(rfm_analysis['monetary'], 5, labels=[1, 2, 3, 4, 5])
        
        # Calculate warehouse storage and performance metrics
        fact_table_rows = len(fact_sales)
        dimension_table_rows = len(date_dimension) + len(customer_dimension) + len(product_dimension)
        
        # Simulate query performance metrics
        query_performance = {
            'avg_query_time_ms': np.random.uniform(50, 500),
            'cache_hit_rate': np.random.uniform(0.7, 0.95),
            'index_efficiency': np.random.uniform(0.8, 0.98),
            'storage_compression_ratio': np.random.uniform(0.3, 0.7)
        }
        
        return {
            'source_systems': 3,
            'total_sales_records': len(sales_data),
            'total_customers': len(customer_data),
            'total_products': len(product_data),
            'data_quality_issues_found': sum(data_quality_issues.values()),
            'fact_table_rows': fact_table_rows,
            'dimension_table_rows': dimension_table_rows,
            'monthly_aggregations': len(monthly_sales),
            'category_analysis': len(category_performance),
            'customer_segments': len(rfm_analysis),
            'cohort_months': len(customer_cohorts),
            'regional_analysis': len(regional_performance),
            'total_revenue': fact_sales['total_amount'].sum(),
            'total_profit': fact_sales['profit'].sum(),
            'average_profit_margin': fact_sales['profit_margin'].mean(),
            'query_performance': query_performance,
            'etl_processes': 3,
            'warehouse_complexity': 'enterprise'
        }
        
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    print("Database management and data warehousing...")
    
    # Relational database operations
    relational_result = relational_database_operations()
    if 'error' not in relational_result:
        print(f"Relational DB: {relational_result['customers_created']} customers, ${relational_result['total_revenue']:.2f} revenue")
    
    # NoSQL document operations
    nosql_result = nosql_document_operations()
    if 'error' not in nosql_result:
        print(f"NoSQL: {nosql_result['total_users']} users, {nosql_result['published_posts']} published posts")
    
    # Data warehousing
    warehouse_result = data_warehousing()
    if 'error' not in warehouse_result:
        print(f"Data Warehouse: {warehouse_result['fact_table_rows']} fact rows, {warehouse_result['etl_processes']} ETL processes")