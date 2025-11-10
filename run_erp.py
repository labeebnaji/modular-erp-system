"""
ERP System Launcher with Language Support
Applies saved language settings before starting the application
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Import language system first
from app.i18n.translations import get_language, _translator

def main():
    """Main application entry point"""
    
    # Create application
    app = QApplication(sys.argv)
    
    # Load saved language
    current_language = get_language()
    
    # Apply layout direction based on language
    if current_language == 'ar':
        app.setLayoutDirection(Qt.RightToLeft)
        print("✓ Language: Arabic (العربية)")
        print("✓ Direction: Right to Left (RTL)")
    else:
        app.setLayoutDirection(Qt.LeftToRight)
        print("✓ Language: English")
        print("✓ Direction: Left to Right (LTR)")
    
    # Set application properties
    app.setApplicationName("LabeebERP")
    app.setOrganizationName("LabeebERP")
    app.setApplicationVersion("1.0.0")
    
    # Import and show main window
    from main import MainWindow
    
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
