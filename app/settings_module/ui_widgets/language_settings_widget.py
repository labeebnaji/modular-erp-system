from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox
from PySide6.QtCore import Qt, QSettings, QCoreApplication
from PySide6.QtGui import QMouseEvent # Import QMouseEvent
import sys

class LanguageSettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("ERP_System", "POS_App") # Use same settings as main.py
        self.init_ui()
        self.load_current_language()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        form_layout = QHBoxLayout()
        self.language_label = QLabel(self.tr("Select Language:"))
        self.language_combo = QComboBox()
        self.language_combo.addItem(self.tr("العربية"), "ar")
        self.language_combo.addItem(self.tr("English"), "en")
        
        self.apply_button = QPushButton(self.tr("Apply Language"))
        self.apply_button.clicked.connect(self.apply_language)
        
        form_layout.addWidget(self.language_label)
        form_layout.addWidget(self.language_combo)
        form_layout.addWidget(self.apply_button)
        form_layout.addStretch(1) # Push elements to the left

        main_layout.addLayout(form_layout)
        main_layout.addStretch(1)
        self.setLayout(main_layout)

    def load_current_language(self):
        current_lang = self.settings.value("language", "ar", type=str)
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)

    def apply_language(self):
        selected_lang_code = self.language_combo.currentData()
        self.settings.setValue("language", selected_lang_code)
        QMessageBox.information(self, self.tr("Language Change"), self.tr("اللغة ستتغير بعد إعادة تشغيل التطبيق.")) # Inform user to restart
        # In a more advanced scenario, you might attempt to dynamically reload UI, but restarting is simpler for now.
        # For immediate visual change without restart, we'd need to re-instantiate many widgets which is complex.
        
    def tr(self, text, disambiguation=None, n=-1):
        return QCoreApplication.translate("LanguageSettingsWidget", text, disambiguation, n)
