"""
Inventory Module UI Widgets
"""

from .inventory_main_window import InventoryMainWindow
from .stock_movements_widget import StockMovementsWidget
from .current_stock_widget import CurrentStockWidget
from .stock_transfer_widget import StockTransferWidget
from .stock_reports_widget import StockReportsWidget

__all__ = [
    'InventoryMainWindow',
    'StockMovementsWidget',
    'CurrentStockWidget',
    'StockTransferWidget',
    'StockReportsWidget'
]
