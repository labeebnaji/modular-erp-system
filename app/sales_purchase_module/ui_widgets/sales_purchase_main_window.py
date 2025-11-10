"""
Labeeb ERP - Sales & Purchase Main Window
النافذة الرئيسية لوحدة المبيعات والمشتريات
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QToolBar, QMessageBox, QStatusBar, QLabel
)
from PySide6.QtCore import Qt, QSize, QDate
from PySide6.QtGui import QAction, QIcon
import datetime

from app.ui.base_widget import TranslatableWidget
from app.i18n.translations import tr
from .sales_invoices_widget import SalesInvoicesWidget
from .purchase_invoices_widget import PurchaseInvoicesWidget
from .sales_orders_widget import SalesOrdersWidget
from .purchase_orders_widget import PurchaseOrdersWidget


class SalesPurchaseMainWindow(QMainWindow):
    """النافذة الرئيسية لوحدة المبيعات والمشتريات"""
    
    def __init__(self, backend, arap_service, inventory_service, unit_service,
                 payment_method_service, branch_service, company_service,
                 currency_service, warehouse_service, parent=None):
        print("[SalesPurchaseMainWindow] Starting __init__...")
        super().__init__(parent)
        print("[SalesPurchaseMainWindow] super().__init__ completed")
        
        # Services
        self.backend = backend
        self.arap_service = arap_service
        self.inventory_service = inventory_service
        self.unit_service = unit_service
        self.payment_method_service = payment_method_service
        self.branch_service = branch_service
        self.company_service = company_service
        self.currency_service = currency_service
        self.warehouse_service = warehouse_service
        print("[SalesPurchaseMainWindow] Services assigned")
        
        print("[SalesPurchaseMainWindow] Setting window title...")
        self.setWindowTitle("Sales & Purchase Management")
        
        print("[SalesPurchaseMainWindow] Setting geometry...")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 700)
        print("[SalesPurchaseMainWindow] Window properties set")
        
        print("[SalesPurchaseMainWindow] Calling init_ui...")
        self.init_ui()
        print("[SalesPurchaseMainWindow] init_ui completed")
        
        print("[SalesPurchaseMainWindow] Creating toolbar...")
        self._create_toolbar()
        print("[SalesPurchaseMainWindow] Toolbar created")
        
        print("[SalesPurchaseMainWindow] Creating statusbar...")
        self._create_statusbar()
        print("[SalesPurchaseMainWindow] Statusbar created")
        
        print("[SalesPurchaseMainWindow] Applying theme...")
        self._apply_theme()
        print("[SalesPurchaseMainWindow] __init__ completed successfully")
    
    def init_ui(self):
        """تهيئة الواجهة"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        
        # Tab Widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setMovable(True)
        
        # Create Pages
        self.sales_invoices_widget = SalesInvoicesWidget(
            self.backend,
            self.arap_service,
            self.inventory_service,
            self.unit_service,
            self.payment_method_service,
            self.branch_service,
            self.company_service,
            self.currency_service,
            self.warehouse_service
        )
        
        self.purchase_invoices_widget = PurchaseInvoicesWidget(
            self.backend,
            self.arap_service,
            self.inventory_service,
            self.unit_service,
            self.payment_method_service,
            self.branch_service,
            self.company_service,
            self.currency_service,
            self.warehouse_service
        )
        
        self.sales_orders_widget = SalesOrdersWidget(
            self.backend,
            self.arap_service,
            self.branch_service,
            self.company_service
        )
        
        self.purchase_orders_widget = PurchaseOrdersWidget(
            self.backend,
            self.arap_service,
            self.branch_service,
            self.company_service
        )
        
        # Add Tabs
        self.tab_widget.addTab(self.sales_invoices_widget, tr('sales.sales_invoices'))
        self.tab_widget.addTab(self.purchase_invoices_widget, tr('sales.purchase_invoices'))
        self.tab_widget.addTab(self.sales_orders_widget, tr('sales.sales_orders'))
        self.tab_widget.addTab(self.purchase_orders_widget, tr('sales.purchase_orders'))
        
        self.main_layout.addWidget(self.tab_widget)
        
        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
    
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
        
        # Print Action
        print_action = QAction(QIcon(), tr('common.print'), self)
        print_action.triggered.connect(self._print_action)
        self.toolbar.addAction(print_action)
        
        self.toolbar.addSeparator()
        
        # Refresh Action
        refresh_action = QAction(QIcon(), tr('common.refresh'), self)
        refresh_action.triggered.connect(self._refresh_action)
        self.toolbar.addAction(refresh_action)
        
        self.toolbar.addSeparator()
        
        # Navigation Actions
        first_action = QAction(QIcon(), tr('common.first'), self)
        first_action.triggered.connect(self._first_action)
        self.toolbar.addAction(first_action)
        
        previous_action = QAction(QIcon(), tr('common.previous'), self)
        previous_action.triggered.connect(self._previous_action)
        self.toolbar.addAction(previous_action)
        
        next_action = QAction(QIcon(), tr('common.next'), self)
        next_action.triggered.connect(self._next_action)
        self.toolbar.addAction(next_action)
        
        last_action = QAction(QIcon(), tr('common.last'), self)
        last_action.triggered.connect(self._last_action)
        self.toolbar.addAction(last_action)
    
    def _create_statusbar(self):
        """إنشاء شريط الحالة"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Date label
        self.date_label = QLabel(QDate.currentDate().toString("dd/MM/yyyy"))
        self.status_bar.addPermanentWidget(self.date_label)
        
        self.status_bar.showMessage(tr('common.ready'), 3000)
    
    def _apply_theme(self):
        """تطبيق التصميم"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                background-color: white;
            }
            QTabBar::tab {
                background: #e0e0e0;
                border: 1px solid #ccc;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
            }
            QToolBar {
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                spacing: 5px;
                padding: 5px;
            }
            QStatusBar {
                background-color: #f0f0f0;
                border-top: 1px solid #ddd;
            }
        """)
    
    def _on_tab_changed(self, index):
        """عند تغيير التبويب"""
        current_widget = self.tab_widget.widget(index)
        if hasattr(current_widget, 'refresh_data'):
            current_widget.refresh_data()
    
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
    
    def _print_action(self):
        """طباعة"""
        current_page = self.tab_widget.currentWidget()
        if hasattr(current_page, 'print_document'):
            current_page.print_document()
    
    def _refresh_action(self):
        """تحديث"""
        current_page = self.tab_widget.currentWidget()
        if hasattr(current_page, 'refresh_data'):
            current_page.refresh_data()
    
    def _first_action(self):
        """الأول"""
        current_page = self.tab_widget.currentWidget()
        if hasattr(current_page, 'first_document'):
            current_page.first_document()
    
    def _previous_action(self):
        """السابق"""
        current_page = self.tab_widget.currentWidget()
        if hasattr(current_page, 'previous_document'):
            current_page.previous_document()
    
    def _next_action(self):
        """التالي"""
        current_page = self.tab_widget.currentWidget()
        if hasattr(current_page, 'next_document'):
            current_page.next_document()
    
    def _last_action(self):
        """الأخير"""
        current_page = self.tab_widget.currentWidget()
        if hasattr(current_page, 'last_document'):
            current_page.last_document()
    
    def refresh_translations(self):
        """تحديث الترجمات"""
        super().refresh_translations()
        self.setWindowTitle(tr('windows.sales_purchase'))
        
        # Update tab titles
        self.tab_widget.setTabText(0, tr('sales.sales_invoices'))
        self.tab_widget.setTabText(1, tr('sales.purchase_invoices'))
        self.tab_widget.setTabText(2, tr('sales.sales_orders'))
        self.tab_widget.setTabText(3, tr('sales.purchase_orders'))
