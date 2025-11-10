"""
Labeeb ERP - Purchase Orders Page
صفحة أوامر الشراء
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from app.ui.base_widget import TranslatableWidget
from app.i18n.translations import tr


class PurchaseOrdersPage(TranslatableWidget):
    """صفحة أوامر الشراء - قيد التطوير"""
    
    def __init__(self, sales_purchase_service, arap_service, branch_service,
                 company_service, parent=None):
        super().__init__(parent)
        
        self.sales_purchase_service = sales_purchase_service
        self.arap_service = arap_service
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        label = QLabel(tr('sales.purchase_orders') + " - " + tr('common.coming_soon'))
        label.setStyleSheet("font-size: 24px; color: #666; padding: 50px;")
        label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(label)
    
    def new_document(self):
        pass
    
    def save_document(self):
        pass
    
    def delete_document(self):
        pass
    
    def refresh_data(self):
        pass
