"""Database management for tasks and subtasks"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def init_db(self):
        """Initialize database with required tables"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Create tasks table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                duration INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                is_completed BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 0,
                order_index INTEGER DEFAULT 0
            )
        """)
        
        # Create subtasks table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS subtasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                is_completed BOOLEAN DEFAULT 0,
                order_index INTEGER DEFAULT 0,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
        """)
        
        self.conn.commit()
    
    def add_task(self, title: str, description: str = "", duration: int = 0) -> int:
        """Add a new task"""
        self.cursor.execute("""
            INSERT INTO tasks (title, description, duration)
            VALUES (?, ?, ?)
        """, (title, description, duration))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_tasks(self) -> List[Dict]:
        """Get all tasks"""
        self.cursor.execute("""
            SELECT id, title, description, duration, is_completed, is_active, created_at
            FROM tasks
            ORDER BY order_index ASC, created_at DESC
        """)
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
    
    def get_active_task(self) -> Optional[Dict]:
        """Get the currently active task"""
        self.cursor.execute("""
            SELECT id, title, description, duration, is_completed, is_active, created_at
            FROM tasks
            WHERE is_active = 1
            LIMIT 1
        """)
        row = self.cursor.fetchone()
        return self._row_to_dict(row) if row else None
    
    def set_active_task(self, task_id: int):
        """Set a task as active and deactivate others"""
        self.cursor.execute("UPDATE tasks SET is_active = 0")
        self.cursor.execute("UPDATE tasks SET is_active = 1 WHERE id = ?", (task_id,))
        self.conn.commit()
    
    def complete_task(self, task_id: int):
        """Mark a task as completed"""
        self.cursor.execute("""
            UPDATE tasks
            SET is_completed = 1, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (task_id,))
        self.conn.commit()
    
    def add_subtask(self, task_id: int, title: str) -> int:
        """Add a subtask to a task"""
        self.cursor.execute("""
            INSERT INTO subtasks (task_id, title)
            VALUES (?, ?)
        """, (task_id, title))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_subtasks(self, task_id: int) -> List[Dict]:
        """Get all subtasks for a task"""
        self.cursor.execute("""
            SELECT id, task_id, title, is_completed, order_index
            FROM subtasks
            WHERE task_id = ?
            ORDER BY order_index ASC
        """, (task_id,))
        return [self._subtask_row_to_dict(row) for row in self.cursor.fetchall()]
    
    def complete_subtask(self, subtask_id: int):
        """Mark a subtask as completed"""
        self.cursor.execute("""
            UPDATE subtasks
            SET is_completed = 1
            WHERE id = ?
        """, (subtask_id,))
        self.conn.commit()
    
    def delete_task(self, task_id: int):
        """Delete a task and its subtasks"""
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()
    
    def _row_to_dict(self, row) -> Dict:
        """Convert task row to dictionary"""
        if not row:
            return None
        return {
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'duration': row[3],
            'is_completed': row[4],
            'is_active': row[5],
            'created_at': row[6]
        }
    
    def _subtask_row_to_dict(self, row) -> Dict:
        """Convert subtask row to dictionary"""
        return {
            'id': row[0],
            'task_id': row[1],
            'title': row[2],
            'is_completed': row[3],
            'order_index': row[4]
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()