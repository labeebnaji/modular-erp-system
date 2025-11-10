from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from app.application.services import ARAPService
#from app.infrastructure.database import get_db # No longer needed
# Removed imports for sub-widgets as they are now directly managed by main.py
# from app.ui.customer_widget import CustomerWidget
# from app.ui.vendor_widget import VendorWidget
# from app.ui.invoice_widget import InvoiceWidget
# from app.ui.payment_widget import PaymentWidget

class ARAPWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.arap_service = ARAPService()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Accounts Receivable / Accounts Payable")
        # self.setGeometry(100, 100, 1200, 800) # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # This ARAPWidget itself acts as a logical grouping for the sidebar menu.
        # Its sub-widgets (Customers, Vendors, Invoices, Payments) are now directly
        # managed and displayed by the QStackedWidget in main.py.
        # This widget will remain empty.

        main_layout.addStretch(1) # Ensure the layout expands if empty

        self.setLayout(main_layout)
