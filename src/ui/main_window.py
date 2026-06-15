"""Main application window"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QStackedWidget,
    QListWidget, QListWidgetItem, QInputDialog, QMessageBox,
    QSpinBox, QTextEdit, QDialog, QFormLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from src.utils.database import Database
from src.utils.apple_music import AppleMusicPlayer
from src.ui.styles import get_stylesheet
from src.ui.widgets import CompactWidget, FullViewWidget

class MainWindow(QMainWindow):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.apple_music = AppleMusicPlayer()
        self.current_task_id = None
        self.time_elapsed = 0
        
        self.init_ui()
        self.setup_timers()
        self.load_tasks()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("ADHD To-Do Widget")
        self.setGeometry(100, 100, 400, 600)
        self.setStyleSheet(get_stylesheet())
        
        self.stacked = QStackedWidget()
        self.compact_view = CompactWidget(self)
        self.stacked.addWidget(self.compact_view)
        
        self.full_view = FullViewWidget(self)
        self.stacked.addWidget(self.full_view)
        
        self.setCentralWidget(self.stacked)
        self.stacked.setCurrentWidget(self.compact_view)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
    def setup_timers(self):
        """Setup timers for updates"""
        self.music_timer = QTimer()
        self.music_timer.timeout.connect(self.update_music_info)
        self.music_timer.start(2000)
        
        self.task_timer = QTimer()
        self.task_timer.timeout.connect(self.update_task_timer)
        
    def load_tasks(self):
        """Load tasks from database"""
        active_task = self.db.get_active_task()
        if active_task:
            self.display_task(active_task['id'])
        else:
            all_tasks = self.db.get_tasks()
            if all_tasks and not all_tasks[0]['is_completed']:
                self.db.set_active_task(all_tasks[0]['id'])
                self.display_task(all_tasks[0]['id'])
    
    def display_task(self, task_id: int):
        """Display a specific task"""
        self.current_task_id = task_id
        self.compact_view.update_task(task_id)
        self.full_view.update_task(task_id)
    
    def update_music_info(self):
        """Update music player info"""
        if self.apple_music.is_music_running():
            track_info = self.apple_music.get_current_track()
            self.compact_view.update_music(track_info)
            self.full_view.update_music(track_info)
    
    def update_task_timer(self):
        """Update task timer"""
        self.time_elapsed += 1
        if self.current_task_id:
            self.compact_view.update_timer(self.time_elapsed)
            self.full_view.update_timer(self.time_elapsed)
    
    def start_task_timer(self):
        """Start the task timer"""
        self.time_elapsed = 0
        self.task_timer.start(1000)
    
    def stop_task_timer(self):
        """Stop the task timer"""
        self.task_timer.stop()
    
    def complete_current_task(self):
        """Mark current task as complete"""
        if self.current_task_id:
            self.db.complete_task(self.current_task_id)
            self.stop_task_timer()
            
            all_tasks = self.db.get_tasks()
            for task in all_tasks:
                if not task['is_completed']:
                    self.display_task(task['id'])
                    return
            
            QMessageBox.information(self, "Great!", "All tasks completed! 🎉")
    
    def toggle_view(self):
        """Toggle between compact and full view"""
        if self.stacked.currentWidget() == self.compact_view:
            self.stacked.setCurrentWidget(self.full_view)
            self.setGeometry(50, 50, 600, 800)
        else:
            self.stacked.setCurrentWidget(self.compact_view)
            self.setGeometry(100, 100, 400, 600)
    
    def closeEvent(self, event):
        """Handle window close"""
        self.db.close()
        event.accept()


class AddTaskDialog(QDialog):
    """Dialog for adding a new task"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Add New Task")
        self.setGeometry(200, 200, 400, 300)
        self.init_ui()
        
    def init_ui(self):
        """Initialize dialog UI"""
        layout = QFormLayout()
        
        self.title_input = QTextEdit()
        self.title_input.setMaximumHeight(50)
        layout.addRow("Task Title:", self.title_input)
        
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(80)
        layout.addRow("Description:", self.desc_input)
        
        self.duration_input = QSpinBox()
        self.duration_input.setMinimum(5)
        self.duration_input.setMaximum(480)
        self.duration_input.setSingleStep(5)
        self.duration_input.setSuffix(" min")
        layout.addRow("Duration:", self.duration_input)
        
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("Add Task")
        cancel_btn = QPushButton("Cancel")
        
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)
        
        self.setLayout(layout)
    
    def get_task_data(self):
        """Get the task data from inputs"""
        title = self.title_input.toPlainText()
        description = self.desc_input.toPlainText()
        duration = self.duration_input.value()
        return title, description, duration