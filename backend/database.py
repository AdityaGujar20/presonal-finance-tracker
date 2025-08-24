import sqlite3
import pandas as pd
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path="finance_tracker.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_transaction(self, date, category, amount, transaction_type, description=""):
        """Add a new transaction to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO transactions (date, category, amount, type, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (date, category, amount, transaction_type, description))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return False
    
    def get_all_transactions(self):
        """Retrieve all transactions from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query('''
                SELECT id, date, category, amount, type, description, created_at
                FROM transactions
                ORDER BY date DESC, created_at DESC
            ''', conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error retrieving transactions: {e}")
            return pd.DataFrame()
    
    def get_transactions_by_category(self, category):
        """Get transactions filtered by category"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query('''
                SELECT * FROM transactions 
                WHERE category = ?
                ORDER BY date DESC
            ''', conn, params=(category,))
            conn.close()
            return df
        except Exception as e:
            print(f"Error retrieving transactions by category: {e}")
            return pd.DataFrame()
    
    def get_transactions_by_date_range(self, start_date, end_date):
        """Get transactions within a date range"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query('''
                SELECT * FROM transactions 
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC
            ''', conn, params=(start_date, end_date))
            conn.close()
            return df
        except Exception as e:
            print(f"Error retrieving transactions by date range: {e}")
            return pd.DataFrame()
    
    def delete_transaction(self, transaction_id):
        """Delete a transaction by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting transaction: {e}")
            return False
    
    def get_monthly_summary(self):
        """Get monthly income and expense summary"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query('''
                SELECT 
                    strftime('%Y-%m', date) as month,
                    type,
                    SUM(amount) as total_amount
                FROM transactions
                GROUP BY strftime('%Y-%m', date), type
                ORDER BY month DESC
            ''', conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error retrieving monthly summary: {e}")
            return pd.DataFrame()
    
    def get_category_summary(self):
        """Get spending summary by category"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query('''
                SELECT 
                    category,
                    type,
                    COUNT(*) as transaction_count,
                    SUM(amount) as total_amount,
                    AVG(amount) as avg_amount
                FROM transactions
                GROUP BY category, type
                ORDER BY total_amount DESC
            ''', conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error retrieving category summary: {e}")
            return pd.DataFrame()