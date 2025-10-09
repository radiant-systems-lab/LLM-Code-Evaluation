# Database Operations and ORM
import sqlite3
import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from contextlib import contextmanager

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    balance = Column(Float, default=0.0)

class DatabaseManager:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
    
    @contextmanager
    def get_session(self):
        """Context manager for database sessions"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_user(self, username, email):
        """Create new user"""
        with self.get_session() as session:
            user = User(username=username, email=email)
            session.add(user)
            return user.id
    
    def get_user_by_username(self, username):
        """Find user by username"""
        with self.get_session() as session:
            return session.query(User).filter(User.username == username).first()

def raw_sql_operations():
    """Demonstrate raw SQL operations"""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert data
    products = [
        ('Laptop', 999.99),
        ('Mouse', 29.99),
        ('Keyboard', 79.99)
    ]
    
    cursor.executemany('INSERT INTO products (name, price) VALUES (?, ?)', products)
    
    # Query data
    cursor.execute('SELECT * FROM products WHERE price > ?', (50,))
    results = cursor.fetchall()
    
    conn.commit()
    conn.close()
    
    return results

if __name__ == "__main__":
    # SQLAlchemy operations
    db_manager = DatabaseManager('sqlite:///example.db')
    
    user_id = db_manager.create_user('john_doe', 'john@example.com')
    user = db_manager.get_user_by_username('john_doe')
    print(f"Created user: {user.username} with ID: {user_id}")
    
    # Raw SQL operations
    expensive_products = raw_sql_operations()
    print(f"Found {len(expensive_products)} expensive products")