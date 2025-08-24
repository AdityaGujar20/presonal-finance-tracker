#!/usr/bin/env python3
"""
Backup and Restore utilities for Personal Finance Tracker
Helps you backup your local data and restore it if needed
"""

import sqlite3
import pandas as pd
import json
import os
from datetime import datetime
import shutil

class BackupManager:
    def __init__(self, db_path="finance_tracker.db"):
        self.db_path = db_path
        self.backup_dir = "backups"
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self):
        """Create a complete backup of your financial data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # 1. Copy the entire database file
            db_backup_path = f"{self.backup_dir}/finance_tracker_backup_{timestamp}.db"
            shutil.copy2(self.db_path, db_backup_path)
            
            # 2. Export to CSV for human-readable backup
            csv_backup_path = f"{self.backup_dir}/transactions_backup_{timestamp}.csv"
            self.export_to_csv(csv_backup_path)
            
            # 3. Export to JSON for easy import
            json_backup_path = f"{self.backup_dir}/transactions_backup_{timestamp}.json"
            self.export_to_json(json_backup_path)
            
            print(f"✅ Backup created successfully!")
            print(f"📁 Database backup: {db_backup_path}")
            print(f"📊 CSV backup: {csv_backup_path}")
            print(f"📄 JSON backup: {json_backup_path}")
            
            return {
                "database": db_backup_path,
                "csv": csv_backup_path,
                "json": json_backup_path
            }
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None
    
    def export_to_csv(self, output_path):
        """Export all transactions to CSV"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query('''
                SELECT id, date, category, amount, type, description, created_at
                FROM transactions
                ORDER BY date DESC
            ''', conn)
            conn.close()
            
            df.to_csv(output_path, index=False)
            print(f"📊 CSV export completed: {output_path}")
            
        except Exception as e:
            print(f"❌ CSV export failed: {e}")
    
    def export_to_json(self, output_path):
        """Export all transactions to JSON"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query('''
                SELECT id, date, category, amount, type, description, created_at
                FROM transactions
                ORDER BY date DESC
            ''', conn)
            conn.close()
            
            # Convert to JSON
            transactions = df.to_dict('records')
            
            backup_data = {
                "export_date": datetime.now().isoformat(),
                "total_transactions": len(transactions),
                "transactions": transactions
            }
            
            with open(output_path, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            print(f"📄 JSON export completed: {output_path}")
            
        except Exception as e:
            print(f"❌ JSON export failed: {e}")
    
    def restore_from_backup(self, backup_path):
        """Restore database from backup file"""
        try:
            if backup_path.endswith('.db'):
                # Restore from database backup
                shutil.copy2(backup_path, self.db_path)
                print(f"✅ Database restored from: {backup_path}")
                
            elif backup_path.endswith('.json'):
                # Restore from JSON backup
                self.restore_from_json(backup_path)
                
            elif backup_path.endswith('.csv'):
                # Restore from CSV backup
                self.restore_from_csv(backup_path)
                
            else:
                print(f"❌ Unsupported backup format: {backup_path}")
                
        except Exception as e:
            print(f"❌ Restore failed: {e}")
    
    def restore_from_json(self, json_path):
        """Restore transactions from JSON backup"""
        try:
            with open(json_path, 'r') as f:
                backup_data = json.load(f)
            
            transactions = backup_data['transactions']
            
            # Clear existing data (optional - ask user)
            response = input("⚠️  This will replace all existing data. Continue? (y/N): ")
            if response.lower() != 'y':
                print("❌ Restore cancelled")
                return
            
            # Recreate database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Drop and recreate table
            cursor.execute('DROP TABLE IF EXISTS transactions')
            cursor.execute('''
                CREATE TABLE transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    type TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert transactions
            for transaction in transactions:
                cursor.execute('''
                    INSERT INTO transactions (date, category, amount, type, description, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    transaction['date'],
                    transaction['category'],
                    transaction['amount'],
                    transaction['type'],
                    transaction.get('description', ''),
                    transaction.get('created_at', datetime.now().isoformat())
                ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Restored {len(transactions)} transactions from JSON backup")
            
        except Exception as e:
            print(f"❌ JSON restore failed: {e}")
    
    def list_backups(self):
        """List all available backups"""
        try:
            backups = []
            for file in os.listdir(self.backup_dir):
                if file.startswith('finance_tracker_backup_') or file.startswith('transactions_backup_'):
                    file_path = os.path.join(self.backup_dir, file)
                    file_size = os.path.getsize(file_path)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    backups.append({
                        'file': file,
                        'path': file_path,
                        'size': f"{file_size / 1024:.1f} KB",
                        'created': file_time.strftime("%Y-%m-%d %H:%M:%S")
                    })
            
            if backups:
                print("\n📁 Available Backups:")
                print("-" * 80)
                for backup in sorted(backups, key=lambda x: x['created'], reverse=True):
                    print(f"📄 {backup['file']}")
                    print(f"   Size: {backup['size']} | Created: {backup['created']}")
                    print(f"   Path: {backup['path']}")
                    print()
            else:
                print("📁 No backups found. Create one with create_backup()")
                
        except Exception as e:
            print(f"❌ Error listing backups: {e}")

def main():
    """Interactive backup/restore utility"""
    backup_manager = BackupManager()
    
    print("💾 Personal Finance Tracker - Backup Manager")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Create backup")
        print("2. List backups")
        print("3. Restore from backup")
        print("4. Export to CSV")
        print("5. Export to JSON")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            backup_manager.create_backup()
            
        elif choice == '2':
            backup_manager.list_backups()
            
        elif choice == '3':
            backup_manager.list_backups()
            backup_path = input("\nEnter backup file path: ").strip()
            if os.path.exists(backup_path):
                backup_manager.restore_from_backup(backup_path)
            else:
                print("❌ Backup file not found")
                
        elif choice == '4':
            output_path = f"transactions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            backup_manager.export_to_csv(output_path)
            
        elif choice == '5':
            output_path = f"transactions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_manager.export_to_json(output_path)
            
        elif choice == '6':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()