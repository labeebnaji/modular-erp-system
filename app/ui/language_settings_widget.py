"""
Language Settings Widget
Allows users to change application language and layout direction
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QRadioButton, QGroupBox, QMessageBox,
                               QButtonGroup, QFormLayout)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from app.i18n.translations import tr, set_language, get_language, _translator
from app.ui.styles import BUTTON_STYLE, GROUPBOX_STYLE


class LanguageSettingsWidget(QWidget):
    """Widget for language settings"""
    
    language_changed = Signal(str)  # Signal emitted when language changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_current_settings()
    
    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(tr('settings.language_settings'))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Language Selection Group
        language_group = QGroupBox(tr('settings.select_language'))
        language_group.setStyleSheet(GROUPBOX_STYLE)
        language_layout = QVBoxLayout()
        
        # Create button group for radio buttons
        self.language_button_group = QButtonGroup(self)
        
        # Arabic Radio Button
        self.arabic_radio = QRadioButton(tr('menu.arabic') + " (العربية)")
        self.arabic_radio.setLayoutDirection(Qt.RightToLeft)
        self.language_button_group.addButton(self.arabic_radio, 0)
        language_layout.addWidget(self.arabic_radio)
        
        # English Radio Button
        self.english_radio = QRadioButton(tr('menu.english') + " (English)")
        self.english_radio.setLayoutDirection(Qt.LeftToRight)
        self.language_button_group.addButton(self.english_radio, 1)
        language_layout.addWidget(self.english_radio)
        
        language_group.setLayout(language_layout)
        main_layout.addWidget(language_group)
        
        # Current Language Info
        info_group = QGroupBox(tr('settings.current_settings'))
        info_group.setStyleSheet(GROUPBOX_STYLE)
        info_layout = QFormLayout()
        
        self.current_language_label = QLabel()
        self.current_direction_label = QLabel()
        
        info_layout.addRow(tr('settings.current_language') + ":", self.current_language_label)
        info_layout.addRow(tr('settings.layout_direction') + ":", self.current_direction_label)
        
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.apply_button = QPushButton(tr('common.save'))
        self.apply_button.setStyleSheet(BUTTON_STYLE)
        self.apply_button.clicked.connect(self.apply_language)
        
        self.cancel_button = QPushButton(tr('common.cancel'))
        self.cancel_button.setStyleSheet(BUTTON_STYLE)
        self.cancel_button.clicked.connect(self.load_current_settings)
        
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Information Label
        info_text = QLabel(tr('settings.language_change_info'))
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #666; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        main_layout.addWidget(info_text)
        
        main_layout.addStretch()
    
    def load_current_settings(self):
        """Load and display current language settings"""
        current_lang = get_language()
        
        # Set radio button
        if current_lang == 'ar':
            self.arabic_radio.setChecked(True)
            self.current_language_label.setText("العربية (Arabic)")
            self.current_direction_label.setText("من اليمين إلى اليسار (RTL)")
        else:
            self.english_radio.setChecked(True)
            self.current_language_label.setText("English (الإنجليزية)")
            self.current_direction_label.setText("Left to Right (LTR)")
    
    def apply_language(self):
        """Apply the selected language"""
        if self.arabic_radio.isChecked():
            new_language = 'ar'
            language_name = "العربية"
            direction = "RTL"
        else:
            new_language = 'en'
            language_name = "English"
            direction = "LTR"
        
        current_lang = get_language()
        
        if new_language == current_lang:
            if current_lang == 'ar':
                QMessageBox.information(self, "معلومات", "اللغة الحالية هي العربية بالفعل.")
            else:
                QMessageBox.information(self, "Information", "Current language is already English.")
            return
        
        # Confirm change
        if current_lang == 'ar':
            reply = QMessageBox.question(
                self, 
                "تأكيد تغيير اللغة",
                f"هل تريد تغيير اللغة إلى {language_name}؟\n"
                f"سيتم تطبيق التغييرات فوراً.",
                QMessageBox.Yes | QMessageBox.No
            )
        else:
            reply = QMessageBox.question(
                self,
                "Confirm Language Change",
                f"Do you want to change language to {language_name}?\n"
                f"Changes will be applied immediately.",
                QMessageBox.Yes | QMessageBox.No
            )
        
        if reply == QMessageBox.Yes:
            # Save language
            set_language(new_language)
            
            # Emit signal to update main window
            self.language_changed.emit(new_language)
            
            # Update this widget's UI
            self.refresh_ui()
            
            # Update display
            self.load_current_settings()
            
            # Show success message
            if new_language == 'ar':
                QMessageBox.information(
                    self,
                    "نجح",
                    "تم تغيير اللغة بنجاح!\n\n"
                    "تم تطبيق التغييرات على الواجهة."
                )
            else:
                QMessageBox.information(
                    self,
                    "Success",
                    "Language changed successfully!\n\n"
                    "Changes have been applied to the interface."
                )
    
    def refresh_ui(self):
        """Refresh UI elements with new language"""
        # Update button texts
        self.apply_button.setText(tr('common.save'))
        self.cancel_button.setText(tr('common.cancel'))
        
        # Update radio button texts
        self.arabic_radio.setText(tr('menu.arabic') + " (العربية)")
        self.english_radio.setText(tr('menu.english') + " (English)")
        
        # Update group box titles
        for widget in self.findChildren(QGroupBox):
            if "select" in widget.title().lower() or "اختر" in widget.title():
                widget.setTitle(tr('settings.select_language'))
            elif "current" in widget.title().lower() or "الحالية" in widget.title():
                widget.setTitle(tr('settings.current_settings'))
    
    def get_selected_language(self):
        """Get the currently selected language"""
        if self.arabic_radio.isChecked():
            return 'ar'
        else:
            return 'en'
