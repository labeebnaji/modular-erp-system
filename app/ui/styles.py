"""
Unified Styling for ERP System
This module contains all the styling constants used across the application
"""

# Button Styles
BUTTON_STYLE = """
    QPushButton {
        background-color: #ADD8E6;
        border: 1px solid #87CEEB;
        border-radius: 5px;
        padding: 5px;
        min-height: 25px;
    }
    QPushButton:hover {
        background-color: #87CEEB;
    }
    QPushButton:pressed {
        background-color: #6A9FBC;
    }
    QPushButton:disabled {
        background-color: #D3D3D3;
        color: #808080;
    }
"""

# Table Styles
TABLE_STYLE = """
    QTableWidget, QTableView {
        alternate-background-color: #F0F8FF;
        background-color: #FFFFFF;
        selection-background-color: #ADD8E6;
        gridline-color: #E0E0E0;
    }
    QHeaderView::section {
        background-color: #87CEEB;
        color: white;
        padding: 4px;
        border: 1px solid #6A9FBC;
        font-weight: bold;
    }
"""

# Group Box Styles
GROUPBOX_STYLE = """
    QGroupBox {
        border: 2px solid #87CEEB;
        border-radius: 5px;
        margin-top: 10px;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
    }
"""

# Input Field Styles
INPUT_STYLE = """
    QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QComboBox {
        border: 1px solid #87CEEB;
        border-radius: 3px;
        padding: 3px;
        background-color: white;
    }
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QComboBox:focus {
        border: 2px solid #6A9FBC;
    }
"""

# Label Styles
LABEL_STYLE = """
    QLabel {
        color: #333333;
    }
"""

# Main Window Style
MAIN_WINDOW_STYLE = """
    QMainWindow {
        background-color: #F5F5F5;
    }
"""

# Sidebar Style (for POS and Main Window)
SIDEBAR_STYLE = """
    QListWidget {
        background-color: #FFFFFF;
        border: 1px solid #87CEEB;
        border-radius: 5px;
    }
    QListWidget::item {
        padding: 8px;
        border-bottom: 1px solid #E0E0E0;
    }
    QListWidget::item:selected {
        background-color: #ADD8E6;
        color: white;
    }
    QListWidget::item:hover {
        background-color: #F0F8FF;
    }
"""

# Tab Widget Style
TAB_STYLE = """
    QTabWidget::pane {
        border: 1px solid #87CEEB;
        border-radius: 5px;
    }
    QTabBar::tab {
        background-color: #E0E0E0;
        border: 1px solid #87CEEB;
        padding: 8px 15px;
        margin-right: 2px;
    }
    QTabBar::tab:selected {
        background-color: #87CEEB;
        color: white;
    }
    QTabBar::tab:hover {
        background-color: #ADD8E6;
    }
"""

# Status Bar Style
STATUSBAR_STYLE = """
    QStatusBar {
        background-color: #87CEEB;
        color: white;
        border-top: 1px solid #6A9FBC;
    }
"""

# Toolbar Style
TOOLBAR_STYLE = """
    QToolBar {
        background-color: #F0F8FF;
        border: 1px solid #87CEEB;
        spacing: 3px;
    }
    QToolButton {
        background-color: #ADD8E6;
        border: 1px solid #87CEEB;
        border-radius: 3px;
        padding: 5px;
    }
    QToolButton:hover {
        background-color: #87CEEB;
    }
"""

# Message Box Style
MESSAGEBOX_STYLE = """
    QMessageBox {
        background-color: #FFFFFF;
    }
    QMessageBox QPushButton {
        background-color: #ADD8E6;
        border: 1px solid #87CEEB;
        border-radius: 5px;
        padding: 5px 15px;
        min-width: 80px;
    }
    QMessageBox QPushButton:hover {
        background-color: #87CEEB;
    }
"""

# Color Palette
COLORS = {
    'primary': '#87CEEB',        # Sky Blue
    'primary_light': '#ADD8E6',  # Light Blue
    'primary_dark': '#6A9FBC',   # Dark Blue
    'background': '#F5F5F5',     # Light Gray
    'background_alt': '#F0F8FF', # Alice Blue
    'white': '#FFFFFF',
    'text': '#333333',
    'text_light': '#808080',
    'border': '#E0E0E0',
    'success': '#90EE90',        # Light Green
    'warning': '#FFD700',        # Gold
    'error': '#FF6B6B',          # Light Red
}

def apply_button_style(button):
    """Apply button style to a QPushButton"""
    button.setStyleSheet(BUTTON_STYLE)

def apply_table_style(table):
    """Apply table style to a QTableWidget or QTableView"""
    table.setStyleSheet(TABLE_STYLE)
    table.setAlternatingRowColors(True)

def apply_groupbox_style(groupbox):
    """Apply groupbox style to a QGroupBox"""
    groupbox.setStyleSheet(GROUPBOX_STYLE)

def apply_input_style(widget):
    """Apply input style to input widgets"""
    widget.setStyleSheet(INPUT_STYLE)

def apply_all_styles(widget):
    """Apply all styles to a widget and its children"""
    from PySide6.QtWidgets import QPushButton, QTableWidget, QTableView, QGroupBox, QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QComboBox
    
    # Apply to buttons
    for button in widget.findChildren(QPushButton):
        apply_button_style(button)
    
    # Apply to tables
    for table in widget.findChildren(QTableWidget):
        apply_table_style(table)
    for table in widget.findChildren(QTableView):
        apply_table_style(table)
    
    # Apply to group boxes
    for groupbox in widget.findChildren(QGroupBox):
        apply_groupbox_style(groupbox)
    
    # Apply to input fields
    for input_widget in widget.findChildren(QLineEdit):
        apply_input_style(input_widget)
    for input_widget in widget.findChildren(QSpinBox):
        apply_input_style(input_widget)
    for input_widget in widget.findChildren(QDoubleSpinBox):
        apply_input_style(input_widget)
    for input_widget in widget.findChildren(QDateEdit):
        apply_input_style(input_widget)
    for input_widget in widget.findChildren(QComboBox):
        apply_input_style(input_widget)
