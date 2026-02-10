#!/usr/bin/env python3
"""
Week 3 - Task 2: SQLite Database
Stores file states and events
"""

import sqlite3
from datetime import datetime

class FileDatabase:
    def __init__(self, db_path='file_tracking.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()
        
        # Files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filepath TEXT UNIQUE,
                hash TEXT,
                size INTEGER,
                entropy REAL,
                created_at TIMESTAMP,
                modified_at TIMESTAMP
            )
        ''')
        
        # Events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filepath TEXT,
                event_type TEXT,
                timestamp TIMESTAMP,
                hash_before TEXT,
                hash_after TEXT,
                entropy_before REAL,
                entropy_after REAL
            )
        ''')
        
        self.conn.commit()
    
    def add_file(self, filepath, hash_val, size, entropy):
        """Add or update file record"""
        cursor = self.conn.cursor()
        now = datetime.now()
        
        cursor.execute('''
            INSERT OR REPLACE INTO files 
            (filepath, hash, size, entropy, created_at, modified_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (filepath, hash_val, size, entropy, now, now))
        
        self.conn.commit()
    
    def log_event(self, filepath, event_type, hash_before=None, hash_after=None, 
                  entropy_before=None, entropy_after=None):
        """Log file event"""
        cursor = self.conn.cursor()
        now = datetime.now()
        
        cursor.execute('''
            INSERT INTO file_events 
            (filepath, event_type, timestamp, hash_before, hash_after, 
             entropy_before, entropy_after)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (filepath, event_type, now, hash_before, hash_after, 
              entropy_before, entropy_after))
        
        self.conn.commit()
    
    def get_file(self, filepath):
        """Get file record"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM files WHERE filepath = ?', (filepath,))
        return cursor.fetchone()
    
    def get_events(self, filepath=None, limit=100):
        """Get recent events"""
        cursor = self.conn.cursor()
        
        if filepath:
            cursor.execute('''
                SELECT * FROM file_events 
                WHERE filepath = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (filepath, limit))
        else:
            cursor.execute('''
                SELECT * FROM file_events 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        return cursor.fetchall()
    
    def close(self):
        """Close database connection"""
        self.conn.close()

if __name__ == "__main__":
    # Test database
    db = FileDatabase('test.db')
    
    # Add test file
    db.add_file('/test/file.txt', 'abc123', 1024, 5.2)
    
    # Log test event
    db.log_event('/test/file.txt', 'CREATE', hash_after='abc123', entropy_after=5.2)
    
    # Query
    print("File:", db.get_file('/test/file.txt'))
    print("Events:", db.get_events())
    
    db.close()
    print("Database test complete!")
