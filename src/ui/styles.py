"""Application stylesheets and themes"""

def get_stylesheet():
    """Return the main application stylesheet"""
    return """
    QMainWindow { background-color: #FFFFFF; }
    QWidget { background-color: #FFFFFF; color: #000000; }
    QPushButton { background-color: #F2F2F7; border: none; border-radius: 6px; padding: 8px 12px; color: #000000; font-weight: bold; }
    QPushButton:hover { background-color: #E5E5EA; }
    QLabel { color: #000000; }
    QProgressBar { border: none; border-radius: 4px; background-color: #E5E5EA; height: 6px; }
    QProgressBar::chunk { background-color: #007AFF; border-radius: 4px; }
    QListWidget { border: 1px solid #E5E5EA; border-radius: 6px; background-color: #FFFFFF; }
    QListWidget::item { padding: 6px; border-radius: 4px; }
    QListWidget::item:selected { background-color: #E5E5EA; }
    QListWidget::item:hover { background-color: #F2F2F7; }
    QTextEdit { border: 1px solid #E5E5EA; border-radius: 6px; padding: 8px; background-color: #FFFFFF; }
    """
