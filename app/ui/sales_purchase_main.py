"""
Labeeb ERP - Sales & Purchase Management Module
وحدة إدارة المبيعات والمشتريات
"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
                               QToolBar, QMessageBox)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon

from app.ui.sales_invoices_page import SalesInvoicesPage
from app.ui.purchase_invoices_page import PurchaseInvoicesPage
from app.ui.sales_orders_page import SalesOrdersPage
from app.ui.purchase_orders_page import PurchaseOrdersPage
from app.ui.base_widget import TranslatableWidget
from app.i18n.translations import tr


class SalesPurchaseMainWindow(TranslatableWidget, QMainWindow):
    """نافذة إدارة المبيعات والمشتريات الرئيسية"""
    
    def __init__(self, sales_purchase_service, inventory_service, arap_service, 
                 unit_service, payment_method_service, branch_service, 
                 company_service, currency_service, parent=None):
        super().__init__(parent)
        
        # Services
        self.sales_purchase_service = sales_purchase_service
        self.inventory_service = inventory_service
        self.arap_service = arap_service
        self.unit_service = unit_service
        self.payment_method_service = payment_method_service
        self.branch_service = branch_service
        self.company_service = company_service
        self.currency_service = currency_service
        
        self.setWindowTitle(tr('windows.sales_purchase'))
        self.setGeometry(100, 100, 1400, 900)
        
        self.init_ui()
        self._create_toolbar()
        
    def init_ui(self):
        """تهيئة الواجهة"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Tab Widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setMovable(True)
        
        # Create Pages
        self.sales_invoices_page = SalesInvoicesPage(
            self.sales_purchase_service,
            self.inventory_service,
            self.arap_service,
            self.unit_service,
            self.payment_method_service,
            self.branch_service,
            self.company_service,
            self.currency_service
        )
        
        self.purchase_invoices_page = PurchaseInvoicesPage(
            self.sales_purchase_service,
            self.inventory_service,
            self.arap_service,
            self.unit_service,
            self.payment_method_service,
            self.branch_service,
            self.company_service,
            self.currency_service
        )
        
        self.sales_orders_page = SalesOrdersPage(
            self.sales_purchase_service,
            self.arap_service,
            self.branch_service,
            self.company_service
        )
        
        self.purchase_orders_page = PurchaseOrdersPage(
            self.sales_purchase_service,
            self.arap_service,
            self.branch_service,
            self.company_service
        )
        
        # Add Tabs
        self.tab_widget.addTab(self.sales_invoices_page, tr('sales.sales_invoices'))
        self.tab_widget.addTab(self.purchase_invoices_page, tr('sales.purchase_invoices'))
        self.tab_widget.addTab(self.sales_orders_page, tr('sales.sales_orders'))
        self.tab_widget.addTab(self.purchase_orders_page, tr('sales.purchase_orders'))
        
        self.main_layout.addWidget(self.tab_widget)
    
    def _create_toolbar(self):
        """إنشاء شريط الأدوات"""
        self.toolbar = self.addToolBar(tr('common.toolbar'))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolbar.setIconSize(QSize(32, 32))
        
        # New Action
        new_action = QAction(QIcon(), tr('common.new'), self)
        new_action.triggered.connect(self._new_action)
        self.toolbar.addAction(new_action)
        
        # Save Action
        save_action = QAction(QIcon(), tr('common.save'), self)
        save_action.triggered.connect(self._save_action)
        self.toolbar.addAction(save_action)
        
        # Delete Action
        delete_action = QAction(QIcon(), tr('common.delete'), self)
        delete_action.triggered.connect(self._delete_action)
        self.toolbar.addAction(delete_action)
        
        self.toolbar.addSeparator()
        
        # Refresh Action
        refresh_action = QAction(QIcon(), tr('common.refresh'), self)
        refresh_action.triggered.connect(self._refresh_action)
        self.toolbar.addAction(refresh_action)
    
    def _new_action(self):
        """إنشاء جديد"""
        current_page = self.tab_widget.currentWidget()
        if hasattr(current_page, 'new_document'):
            current_page.new_document()
    
    def _save_action(self):
        """حفظ"""
        current_page = self.tab_widget.currentWidget()
        if hasattr(current_page, 'save_document'):
            current_page.save_document()
    
    def _delete_action(self):
        """حذف"""
        current_page = self.tab_widget.currentWidget()
        if hasattr(current_page, 'delete_document'):
            current_page.delete_document()
    
    def _refresh_action(self):
        """تحديث"""
        current_page = self.tab_widget.currentWidget()
        if hasattr(current_page, 'refresh_data'):
            current_page.refresh_data()
    
    def refresh_translations(self):
        """تحديث الترجمات"""
        super().refresh_translations()
        self.setWindowTitle(tr('windows.sales_purchase'))
        
        # Update tab titles
        self.tab_widget.setTabText(0, tr('sales.sales_invoices'))
        self.tab_widget.setTabText(1, tr('sales.purchase_invoices'))
        self.tab_widget.setTabText(2, tr('sales.sales_orders'))
        self.tab_widget.setTabText(3, tr('sales.purchase_orders'))
