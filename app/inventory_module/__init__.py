"""
Labeeb ERP - Inventory Module
وحدة إدارة المخزون المتكاملة
"""

from .inventory_backend import InventoryBackend
from .ui_widgets.inventory_main_window import InventoryMainWindow

__all__ = ['InventoryBackend', 'InventoryMainWindow']
