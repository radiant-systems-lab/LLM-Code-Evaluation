#!/usr/bin/env python3
"""
Script 10: Database Operations with SQLAlchemy
Tests database ORM and connection dependencies
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import sqlite3

# Create base class for models
Base = declarative_base()

class Customer(Base):
    """Customer model"""
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationship
    orders = relationship("Order", back_populates="customer")

class Product(Base):
    """Product model"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    price = Column(Float)
    stock = Column(Integer)

class Order(Base):
    """Order model"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    total_amount = Column(Float)
    order_date = Column(DateTime, default=datetime.now)
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    product = relationship("Product")

def perform_database_operations():
    """Perform various database operations"""
    print("Starting database operations with SQLAlchemy...")
    
    # Create in-memory SQLite database
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("Database schema created successfully")
    
    # Insert sample data
    customers = []
    for i in range(50):
        customer = Customer(
            name=f"Customer_{i}",
            email=f"customer{i}@example.com"
        )
        customers.append(customer)
        session.add(customer)
    
    products = []
    product_names = ['Laptop', 'Phone', 'Tablet', 'Headphones', 'Monitor']
    for i, name in enumerate(product_names):
        product = Product(
            name=name,
            price=np.random.uniform(100, 2000),
            stock=np.random.randint(10, 100)
        )
        products.append(product)
        session.add(product)
    
    session.commit()
    print(f"Inserted {len(customers)} customers and {len(products)} products")
    
    # Create orders
    np.random.seed(42)
    for i in range(100):
        order = Order(
            customer_id=np.random.randint(1, len(customers) + 1),
            product_id=np.random.randint(1, len(products) + 1),
            quantity=np.random.randint(1, 5),
            total_amount=np.random.uniform(100, 5000),
            order_date=datetime.now() - timedelta(days=np.random.randint(0, 365))
        )
        session.add(order)
    
    session.commit()
    print("Created 100 orders")
    
    # Query operations
    # 1. Count total customers
    customer_count = session.query(Customer).count()
    print(f"Total customers: {customer_count}")
    
    # 2. Top customers by order count
    from sqlalchemy import func
    top_customers = session.query(
        Customer.name,
        func.count(Order.id).label('order_count')
    ).join(Order).group_by(Customer.id).order_by(func.count(Order.id).desc()).limit(5).all()
    
    print("\nTop 5 customers by order count:")
    for name, count in top_customers:
        print(f"  {name}: {count} orders")
    
    # 3. Product inventory status
    inventory = session.query(Product).all()
    low_stock = [p for p in inventory if p.stock < 20]
    print(f"\nProducts with low stock (<20): {len(low_stock)}")
    
    # 4. Revenue analysis using pandas
    orders_query = """
        SELECT o.*, c.name as customer_name, p.name as product_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        JOIN products p ON o.product_id = p.id
    """
    
    # Execute raw SQL and load into pandas
    df_orders = pd.read_sql_query(orders_query, engine)
    
    # Revenue by month
    df_orders['order_date'] = pd.to_datetime(df_orders['order_date'])
    df_orders['month'] = df_orders['order_date'].dt.to_period('M')
    monthly_revenue = df_orders.groupby('month')['total_amount'].sum()
    
    print(f"\nMonthly revenue analysis: {len(monthly_revenue)} months")
    print(f"Total revenue: ${df_orders['total_amount'].sum():.2f}")
    print(f"Average order value: ${df_orders['total_amount'].mean():.2f}")
    
    # 5. Complex aggregation
    product_stats = session.query(
        Product.name,
        func.count(Order.id).label('total_orders'),
        func.sum(Order.quantity).label('total_quantity'),
        func.avg(Order.total_amount).label('avg_amount')
    ).join(Order).group_by(Product.id).all()
    
    print("\nProduct performance:")
    for stats in product_stats:
        print(f"  {stats.name}: {stats.total_orders} orders, {stats.total_quantity} units")
    
    # Export to JSON
    results = {
        'customers': customer_count,
        'products': len(products),
        'orders': 100,
        'total_revenue': float(df_orders['total_amount'].sum()),
        'low_stock_products': len(low_stock)
    }
    
    with open('database_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nResults exported to database_results.json")
    
    # Clean up
    session.close()
    
    return results

if __name__ == "__main__":
    results = perform_database_operations()
    print(f"\nDatabase operations complete: {results}")