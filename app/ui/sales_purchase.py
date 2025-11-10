from PySide6.QtWidgets import QWidget
#from PySide6.QtWidgets import QTabWidget
#from app.ui.sales_order_widget import SalesOrderWidget
#from app.ui.purchase_order_widget import PurchaseOrderWidget
from app.application.services import SalesPurchaseService
#from app.infrastructure.database import get_db

class SalesPurchaseWidget(QWidget):
    def __init__(self, sales_purchase_service, parent=None):
        super().__init__(parent)
        self.sales_purchase_service = sales_purchase_service
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Sales & Purchase Management")
        # Removed fixed geometry

        # Previously, this contained a QTabWidget and its sub-widgets.
        # Now, sub-widgets are directly managed by main.py's QStackedWidget.
        pass
