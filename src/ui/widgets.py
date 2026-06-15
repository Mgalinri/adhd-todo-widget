"""Reusable UI widgets"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QProgressBar, QListWidget, QListWidgetItem, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class CompactWidget(QWidget):
    """Compact widget view - minimal display for one task"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_task = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize compact widget UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        self.music_label = QLabel("🎵 Not playing")
        self.music_label.setFont(QFont("SF Pro Display", 10))
        self.music_label.setStyleSheet("color: #666; font-weight: bold;")
        layout.addWidget(self.music_label)
        
        self.task_title = QLabel("No task")
        self.task_title.setFont(QFont("SF Pro Display", 16, QFont.Weight.Bold))
        self.task_title.setWordWrap(True)
        layout.addWidget(self.task_title)
        
        self.timer_label = QLabel("0:00")
        self.timer_label.setFont(QFont("Courier", 28, QFont.Weight.Bold))
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("color: #007AFF;")
        layout.addWidget(self.timer_label)
        
        self.progress = QProgressBar()
        self.progress.setMaximumHeight(6)
        self.progress.setStyleSheet("QProgressBar { border: none; background-color: #E5E5EA; border-radius: 3px; } QProgressBar::chunk { background-color: #007AFF; border-radius: 3px; }")
        layout.addWidget(self.progress)
        
        self.subtasks_label = QLabel("Subtasks:")
        self.subtasks_label.setFont(QFont("SF Pro Display", 11, QFont.Weight.Bold))
        layout.addWidget(self.subtasks_label)
        
        self.subtasks_list = QListWidget()
        self.subtasks_list.setMaximumHeight(100)
        self.subtasks_list.setStyleSheet("QListWidget { border: 1px solid #E5E5EA; border-radius: 6px; padding: 4px; }")
        layout.addWidget(self.subtasks_list)
        
        button_layout = QHBoxLayout()
        self.play_btn = QPushButton("Start ▶")
        self.play_btn.clicked.connect(self.start_task)
        self.play_btn.setStyleSheet("QPushButton { background-color: #34C759; color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: bold; } QPushButton:hover { background-color: #30B050; }")
        button_layout.addWidget(self.play_btn)
        
        self.complete_btn = QPushButton("Complete ✓")
        self.complete_btn.clicked.connect(self.complete_task)
        self.complete_btn.setStyleSheet("QPushButton { background-color: #007AFF; color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: bold; } QPushButton:hover { background-color: #0051D5; }")
        button_layout.addWidget(self.complete_btn)
        
        layout.addLayout(button_layout)
        
        more_layout = QHBoxLayout()
        self.add_subtask_btn = QPushButton("+ Subtask")
        self.add_subtask_btn.clicked.connect(self.add_subtask)
        self.add_subtask_btn.setStyleSheet("background-color: #F2F2F7; border-radius: 6px;")
        more_layout.addWidget(self.add_subtask_btn)
        
        self.expand_btn = QPushButton("↗ Expand")
        self.expand_btn.clicked.connect(self.main_window.toggle_view)
        self.expand_btn.setStyleSheet("background-color: #F2F2F7; border-radius: 6px;")
        more_layout.addWidget(self.expand_btn)
        
        layout.addLayout(more_layout)
        layout.addStretch()
        self.setLayout(layout)
        self.setStyleSheet("QWidget { background-color: white; border-radius: 12px; }")
    
    def update_task(self, task_id: int):
        """Update the displayed task"""
        tasks = self.main_window.db.get_tasks()
        for t in tasks:
            if t['id'] == task_id:
                self.current_task = t
                self.task_title.setText(t['title'])
                self.main_window.db.set_active_task(task_id)
                
                subtasks = self.main_window.db.get_subtasks(task_id)
                self.subtasks_list.clear()
                for st in subtasks:
                    item = QListWidgetItem(st['title'])
                    item.setCheckState(Qt.CheckState.Checked if st['is_completed'] else Qt.CheckState.Unchecked)
                    self.subtasks_list.addItem(item)
                break
    
    def update_timer(self, seconds: int):
        """Update timer display"""
        minutes = seconds // 60
        secs = seconds % 60
        self.timer_label.setText(f"{minutes}:{secs:02d}")
        
        if self.current_task and self.current_task['duration']:
            total_seconds = self.current_task['duration'] * 60
            progress = min(int((seconds / total_seconds) * 100), 100)
            self.progress.setValue(progress)
    
    def update_music(self, track_info: dict):
        """Update music player display"""
        if track_info.get('is_playing'):
            text = f"🎵 {track_info.get('track', '')} - {track_info.get('artist', '')}"
        else:
            text = "🎵 Not playing"
        self.music_label.setText(text)
    
    def start_task(self):
        """Start the current task"""
        self.main_window.start_task_timer()
        self.play_btn.setText("Pause ⏸")
        self.play_btn.clicked.disconnect()
        self.play_btn.clicked.connect(self.pause_task)
    
    def pause_task(self):
        """Pause the current task"""
        self.main_window.stop_task_timer()
        self.play_btn.setText("Resume ▶")
    
    def complete_task(self):
        """Complete the current task"""
        self.main_window.complete_current_task()
    
    def add_subtask(self):
        """Add a subtask"""
        if not self.current_task:
            QMessageBox.warning(self, "No Task", "Please select a task first")
            return
        
        text, ok = QInputDialog.getText(self, "Add Subtask", "Subtask:")
        if ok and text:
            self.main_window.db.add_subtask(self.current_task['id'], text)
            self.update_task(self.current_task['id'])


class FullViewWidget(QWidget):
    """Full view widget - detailed display"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_task = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize full view UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        header_layout = QHBoxLayout()
        self.music_label = QLabel("🎵 Not playing")
        self.music_label.setFont(QFont("SF Pro Display", 11))
        header_layout.addWidget(self.music_label)
        header_layout.addStretch()
        
        collapse_btn = QPushButton("↙ Collapse")
        collapse_btn.clicked.connect(self.main_window.toggle_view)
        header_layout.addWidget(collapse_btn)
        layout.addLayout(header_layout)
        
        self.task_title = QLabel("No task")
        self.task_title.setFont(QFont("SF Pro Display", 22, QFont.Weight.Bold))
        self.task_title.setWordWrap(True)
        layout.addWidget(self.task_title)
        
        timer_layout = QHBoxLayout()
        self.timer_label = QLabel("0:00")
        self.timer_label.setFont(QFont("Courier", 32, QFont.Weight.Bold))
        timer_layout.addWidget(self.timer_label)
        timer_layout.addSpacing(20)
        
        self.progress = QProgressBar()
        self.progress.setMaximumHeight(8)
        timer_layout.addWidget(self.progress)
        layout.addLayout(timer_layout)
        
        self.task_desc = QLabel()
        self.task_desc.setFont(QFont("SF Pro Display", 11))
        self.task_desc.setWordWrap(True)
        self.task_desc.setStyleSheet("color: #666;")
        layout.addWidget(self.task_desc)
        
        layout.addSpacing(12)
        self.subtasks_title = QLabel("Subtasks:")
        self.subtasks_title.setFont(QFont("SF Pro Display", 14, QFont.Weight.Bold))
        layout.addWidget(self.subtasks_title)
        
        self.subtasks_list = QListWidget()
        self.subtasks_list.setStyleSheet("QListWidget { border: 1px solid #E5E5EA; border-radius: 8px; padding: 8px; }")
        layout.addWidget(self.subtasks_list)
        
        action_layout = QHBoxLayout()
        start_btn = QPushButton("▶ Start")
        start_btn.clicked.connect(self.main_window.start_task_timer)
        start_btn.setStyleSheet("QPushButton { background-color: #34C759; color: white; border-radius: 8px; padding: 10px 20px; font-weight: bold; }")
        action_layout.addWidget(start_btn)
        
        complete_btn = QPushButton("✓ Complete")
        complete_btn.clicked.connect(self.main_window.complete_current_task)
        complete_btn.setStyleSheet("QPushButton { background-color: #007AFF; color: white; border-radius: 8px; padding: 10px 20px; font-weight: bold; }")
        action_layout.addWidget(complete_btn)
        layout.addLayout(action_layout)
        
        self.setLayout(layout)
    
    def update_task(self, task_id: int):
        """Update the displayed task"""
        tasks = self.main_window.db.get_tasks()
        for t in tasks:
            if t['id'] == task_id:
                self.current_task = t
                self.task_title.setText(t['title'])
                self.task_desc.setText(t['description'] or "")
                
                subtasks = self.main_window.db.get_subtasks(task_id)
                self.subtasks_list.clear()
                for st in subtasks:
                    item = QListWidgetItem(st['title'])
                    item.setCheckState(Qt.CheckState.Checked if st['is_completed'] else Qt.CheckState.Unchecked)
                    self.subtasks_list.addItem(item)
                break
    
    def update_timer(self, seconds: int):
        """Update timer display"""
        minutes = seconds // 60
        secs = seconds % 60
        self.timer_label.setText(f"{minutes}:{secs:02d}")
        
        if self.current_task and self.current_task['duration']:
            total_seconds = self.current_task['duration'] * 60
            progress = min(int((seconds / total_seconds) * 100), 100)
            self.progress.setValue(progress)
    
    def update_music(self, track_info: dict):
        """Update music player display"""
        if track_info.get('is_playing'):
            text = f"🎵 {track_info.get('track', '')} - {track_info.get('artist', '')}"
        else:
            text = "🎵 Not playing"
        self.music_label.setText(text)