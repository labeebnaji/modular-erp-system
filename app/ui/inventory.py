from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from app.application.services import InventoryService
#from app.infrastructure.database import get_db # No longer needed
# Removed imports for sub-widgets as they are now directly managed by main.py
# from app.ui.item_widget import ItemWidget
# from app.ui.stock_movement_widget import StockMovementWidget

class InventoryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inventory_service = InventoryService()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Inventory Management")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # This InventoryWidget itself acts as a logical grouping for the sidebar menu.
        # Its sub-widgets (Items, Stock Movements) are now directly
        # managed and displayed by the QStackedWidget in main.py.
        # This widget will remain empty.

        main_layout.addStretch(1) # Ensure the layout expands if empty

        self.setLayout(main_layout)
