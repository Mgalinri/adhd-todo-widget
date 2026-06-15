"""
ADHD-Friendly To-Do List Widget with Apple Music Integration
Main entry point for the application
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.utils.database import Database

def main():
    # Initialize database
    db_path = Path.home() / ".adhd_todo" / "tasks.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = Database(str(db_path))
    db.init_db()
    
    # Create and run application
    app = QApplication(sys.argv)
    window = MainWindow(db)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()