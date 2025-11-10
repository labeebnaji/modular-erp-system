from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton
from app.customer_module.ui_widgets.customer_widget import CustomerWidget
from app.application.services import ARAPService # Assuming ARAPService handles customer operations

class CustomerMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Customer Management")
        self.setGeometry(100, 100, 1000, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.arap_service = ARAPService() # Initialize ARAPService
        self.customer_widget = CustomerWidget(self.arap_service)
        self.layout.addWidget(self.customer_widget)

def main():
    app = QApplication([])
    window = CustomerMainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
