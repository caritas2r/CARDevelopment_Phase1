"""
Utility script to inspect the database structure and contents
"""
import sqlite3
import os
from pathlib import Path

def inspect_database(db_path='data/car_database.db'):
    """
    Inspect the database to see what's inside
    
    Args:
        db_path: Path to the database file
    """
    abs_path = os.path.abspath(db_path)
    
    print("=" * 60)
    print("Database Inspection")
    print("=" * 60)
    print()
    print(f"Database Path: {abs_path}")
    print(f"Exists: {os.path.exists(db_path)}")
    print()
    
    if not os.path.exists(db_path):
        print("Database file does not exist yet.")
        print("It will be created when the backend starts for the first time.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"Number of tables: {len(tables)}")
        print()
        
        if tables:
            print("Tables found:")
            for table in tables:
                table_name = table[0]
                print(f"  - {table_name}")
                
                # Get table schema
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                print(f"    Columns ({len(columns)}):")
                for col in columns:
                    col_name, col_type = col[1], col[2]
                    nullable = "NULL" if col[3] == 0 else "NOT NULL"
                    default = f" DEFAULT {col[4]}" if col[4] else ""
                    print(f"      - {col_name} ({col_type}) {nullable}{default}")
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"    Rows: {count}")
                print()
        else:
            print("No tables found in database.")
            print("The database is empty (no schema defined yet).")
            print()
        
        # Get database file size
        file_size = os.path.getsize(db_path)
        print(f"Database file size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Error inspecting database: {e}")

if __name__ == '__main__':
    inspect_database()

