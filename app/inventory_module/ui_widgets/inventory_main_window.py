"""
Labeeb ERP - Inventory Main Window
النافذة الرئيسية لوحدة المخزون
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QToolBar, QStatusBar, QLabel
)
from PySide6.QtCore import Qt, QSize, QDate
from PySide6.QtGui import QAction, QIcon

from app.ui.base_widget import TranslatableWidget
from app.i18n.translations import tr
from .stock_movements_widget import StockMovementsWidget
from .current_stock_widget import CurrentStockWidget
from .stock_transfer_widget import StockTransferWidget
from .stock_reports_widget import StockReportsWidget


class InventoryMainWindow(QMainWindow, TranslatableWidget):
    """النافذة الرئيسية لوحدة المخزون"""
    
    def __init__(self, backend, inventory_service, warehouse_service, 
                 unit_service, branch_service, parent=None):
        QMainWindow.__init__(self, parent)
        TranslatableWidget.__init__(self, parent)
        
        self.backend = backend
        self.inventory_service = inventory_service
        self.warehouse_service = warehouse_service
        self.unit_service = unit_service
        self.branch_service = branch_service
        
        self.setWindowTitle(tr('inventory.title'))
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 700)
        
        self.init_ui()
        self._create_toolbar()
        self._create_statusbar()
        self._apply_theme()
    
    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setMovable(True)
        
        self.stock_movements_widget = StockMovementsWidget(
            self.backend,
            self.inventory_service,
            self.warehouse_service,
            self.unit_service
        )
        
        self.current_stock_widget = CurrentStockWidget(
            self.backend,
            self.inventory_service,
            self.warehouse_service
        )
        
        self.stock_transfer_widget = StockTransferWidget(
            self.backend,
            self.inventory_service,
            self.warehouse_service
        )
        
        self.stock_reports_widget = StockReportsWidget(
            self.backend,
            self.inventory_service
        )
        
        self.tab_widget.addTab(self.current_stock_widget, tr('inventory.current_stock'))
        self.tab_widget.addTab(self.stock_movements_widget, tr('inventory.stock_movements'))
        self.tab_widget.addTab(self.stock_transfer_widget, tr('inventory.stock_transfer'))
        self.tab_widget.addTab(self.stock_reports_widget, tr('inventory.stock_reports'))
        
        self.main_layout.addWidget(self.tab_widget)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
    
    def _create_toolbar(self):
        self.toolbar = self.addToolBar(tr('common.toolbar'))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolbar.setIconSize(QSize(32, 32))
        
        new_action = QAction(QIcon(), tr('common.new'), self)
        new_action.triggered.connect(self._new_action)
        self.toolbar.addAction(new_action)
        
        save_action = QAction(QIcon(), tr('common.save'), self)
        save_action.triggered.connect(self._save_action)
        self.toolbar.addAction(save_action)
        
        self.toolbar.addSeparator()
        
        refresh_action = QAction(QIcon(), tr('common.refresh'), self)
        refresh_action.triggered.connect(self._refresh_action)
        self.toolbar.addAction(refresh_action)
    
    def _create_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.date_label = QLabel(QDate.currentDate().toString("dd/MM/yyyy"))
        self.status_bar.addPermanentWidget(self.date_label)
        
        self.status_bar.showMessage(tr('common.ready'), 3000)
    
    def _apply_theme(self):
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
        current_widget = self.tab_widget.widget(index)
        if hasattr(current_widget, 'refresh_data'):
            current_widget.refresh_data()
    
    def _new_action(self):
        current_page = self.tab_widget.currentWidget()
        if hasattr(current_page, 'new_document'):
            current_page.new_document()
    
    def _save_action(self):
        current_page = self.tab_widget.currentWidget()
        if hasattr(current_page, 'save_document'):
            current_page.save_document()
    
    def _refresh_action(self):
        current_page = self.tab_widget.currentWidget()
        if hasattr(current_page, 'refresh_data'):
            current_page.refresh_data()
    
    def refresh_translations(self):
        """تحديث الترجمات"""
        self.setWindowTitle(tr('inventory.title'))
        
        # Update tab titles
        self.tab_widget.setTabText(0, tr('inventory.current_stock'))
        self.tab_widget.setTabText(1, tr('inventory.stock_movements'))
        self.tab_widget.setTabText(2, tr('inventory.stock_transfer'))
        self.tab_widget.setTabText(3, tr('inventory.stock_reports'))
        
        # Update toolbar actions
        actions = self.toolbar.actions()
        if len(actions) >= 3:
            actions[0].setText(tr('common.new'))
            actions[1].setText(tr('common.save'))
            actions[2].setText(tr('common.refresh'))
        
        # Refresh child widgets
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if hasattr(widget, 'refresh_translations'):
                widget.refresh_translations()
