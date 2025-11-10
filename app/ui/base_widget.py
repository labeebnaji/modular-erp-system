"""
Base Widget with Translation Support
All widgets should inherit from this to support dynamic language switching
"""

from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QGroupBox, QTableWidget
from PySide6.QtCore import Qt
from app.i18n.translations import tr, get_language


class TranslatableWidget(QWidget):
    """Base widget with translation support"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._translation_keys = {}  # Store translation keys for dynamic update
    
    def refresh_translations(self):
        """Refresh all translatable elements - override in subclasses"""
        # Update layout direction for this widget and all children
        current_lang = get_language()
        if current_lang == 'ar':
            self.setLayoutDirection(Qt.RightToLeft)
            # Apply to all child widgets
            for child in self.findChildren(QWidget):
                child.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)
            # Apply to all child widgets
            for child in self.findChildren(QWidget):
                child.setLayoutDirection(Qt.LeftToRight)
        
        # Update all stored translation keys
        self._update_translations()
    
    def _update_translations(self):
        """Update all widgets with stored translation keys"""
        # Update buttons
        for button in self.findChildren(QPushButton):
            if hasattr(button, '_translation_key'):
                button.setText(tr(button._translation_key))
        
        # Update labels
        for label in self.findChildren(QLabel):
            if hasattr(label, '_translation_key'):
                label.setText(tr(label._translation_key))
        
        # Update group boxes
        for groupbox in self.findChildren(QGroupBox):
            if hasattr(groupbox, '_translation_key'):
                groupbox.setTitle(tr(groupbox._translation_key))
        
        # Update table headers
        for table in self.findChildren(QTableWidget):
            if hasattr(table, '_header_keys'):
                headers = [tr(key) for key in table._header_keys]
                table.setHorizontalHeaderLabels(headers)
    
    def set_translatable_text(self, widget, translation_key):
        """Set text with translation key for dynamic updates"""
        widget._translation_key = translation_key
        widget.setText(tr(translation_key))
    
    def set_translatable_title(self, widget, translation_key):
        """Set title with translation key for dynamic updates"""
        widget._translation_key = translation_key
        widget.setTitle(tr(translation_key))
    
    def set_translatable_headers(self, table, header_keys):
        """Set table headers with translation keys"""
        table._header_keys = header_keys
        headers = [tr(key) for key in header_keys]
        table.setHorizontalHeaderLabels(headers)


def create_translatable_button(text_key, parent=None):
    """Create a button with translation support"""
    button = QPushButton(parent)
    button._translation_key = text_key
    button.setText(tr(text_key))
    return button


def create_translatable_label(text_key, parent=None):
    """Create a label with translation support"""
    label = QLabel(parent)
    label._translation_key = text_key
    label.setText(tr(text_key))
    return label


def create_translatable_groupbox(title_key, parent=None):
    """Create a group box with translation support"""
    groupbox = QGroupBox(parent)
    groupbox._translation_key = title_key
    groupbox.setTitle(tr(title_key))
    return groupbox
