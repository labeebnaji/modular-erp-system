from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from app.supplier_module.ui_widgets.supplier_widget import SupplierWidget
from app.application.services import ARAPService # Assuming ARAPService handles supplier operations

class SupplierMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Supplier Management")
        self.setGeometry(100, 100, 1000, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.arap_service = ARAPService() # Initialize ARAPService
        self.supplier_widget = SupplierWidget(self.arap_service)
        self.layout.addWidget(self.supplier_widget)

def main():
    app = QApplication([])
    window = SupplierMainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
