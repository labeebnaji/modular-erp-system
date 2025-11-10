"""
Complete Inventory Management Widget
Includes stock movements, current stock view, and inventory reports
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                               QTableWidget, QTableWidgetItem, QPushButton, QLabel,
                               QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox,
                               QMessageBox, QGroupBox, QFormLayout, QHeaderView, QTextEdit)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
from decimal import Decimal
from datetime import datetime

from app.application.services import InventoryService, WarehouseService, CompanyService, BranchService, UnitService
from app.ui.styles import BUTTON_STYLE, TABLE_STYLE, GROUPBOX_STYLE
from app.i18n.translations import tr


class StockMovementWidget(QWidget):
    """Widget for managing stock movements"""
    
    def __init__(self, inventory_service, warehouse_service, unit_service, parent=None):
        super().__init__(parent)
        self.inventory_service = inventory_service
        self.warehouse_service = warehouse_service
        self.unit_service = unit_service
        self.init_ui()
        self.load_stock_movements()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Form for adding stock movement
        form_group = QGroupBox(tr('inventory.stock_movements'))
        form_group.setStyleSheet(GROUPBOX_STYLE)
        form_layout = QFormLayout()
        
        # Item selection
        self.item_combo = QComboBox()
        self.load_items()
        form_layout.addRow(QLabel(tr('common.name') + ":"), self.item_combo)
        
        # Movement type
        self.movement_type_combo = QComboBox()
        self.movement_type_combo.addItem(tr('inventory.stock_in'), 0)
        self.movement_type_combo.addItem(tr('inventory.stock_out'), 1)
        self.movement_type_combo.addItem(tr('inventory.transfer'), 2)
        self.movement_type_combo.addItem(tr('inventory.adjustment'), 3)
        form_layout.addRow(QLabel(tr('common.type') + ":"), self.movement_type_combo)
        
        # Quantity
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setRange(0.01, 999999.99)
        self.quantity_input.setDecimals(2)
        form_layout.addRow(QLabel(tr('common.quantity') + ":"), self.quantity_input)
        
        # Cost
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0.00, 999999.99)
        self.cost_input.setDecimals(2)
        form_layout.addRow(QLabel(tr('common.price') + ":"), self.cost_input)
        
        # Date
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form_layout.addRow(QLabel(tr('common.date') + ":"), self.date_input)
        
        # Reference number
        self.ref_no_input = QLineEdit()
        self.ref_no_input.setPlaceholderText(tr('common.code'))
        form_layout.addRow(QLabel(tr('common.code') + ":"), self.ref_no_input)
        
        # Notes
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText(tr('common.description'))
        form_layout.addRow(QLabel(tr('common.description') + ":"), self.notes_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton(tr('common.add'))
        self.add_button.setStyleSheet(BUTTON_STYLE)
        self.add_button.clicked.connect(self.add_stock_movement)
        
        self.clear_button = QPushButton(tr('common.clear'))
        self.clear_button.setStyleSheet(BUTTON_STYLE)
        self.clear_button.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.clear_button)
        form_layout.addRow(button_layout)
        
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        # Table for stock movements
        self.movements_table = QTableWidget()
        self.movements_table.setColumnCount(8)
        self.movements_table.setHorizontalHeaderLabels([
            "ID", tr('common.name'), tr('common.type'), 
            tr('common.quantity'), tr('common.price'), 
            tr('common.date'), tr('common.code'), tr('common.description')
        ])
        self.movements_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.movements_table.setStyleSheet(TABLE_STYLE)
        self.movements_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.movements_table)
    
    def load_items(self):
        """Load all items into combo box"""
        self.item_combo.clear()
        items = self.inventory_service.get_all_items()
        for item in items:
            self.item_combo.addItem(f"{item.name_ar} ({item.code})", item.id)
    
    def load_stock_movements(self):
        """Load all stock movements"""
        self.movements_table.setRowCount(0)
        movements = self.inventory_service.get_all_stock_movements()
        
        movement_types = {
            0: tr('inventory.stock_in'),
            1: tr('inventory.stock_out'),
            2: tr('inventory.transfer'),
            3: tr('inventory.adjustment')
        }
        
        self.movements_table.setRowCount(len(movements))
        for row, movement in enumerate(movements):
            item = self.inventory_service.get_item_by_id(movement.item_id)
            item_name = item.name_ar if item else "Unknown"
            
            self.movements_table.setItem(row, 0, QTableWidgetItem(str(movement.id)))
            self.movements_table.setItem(row, 1, QTableWidgetItem(item_name))
            self.movements_table.setItem(row, 2, QTableWidgetItem(movement_types.get(movement.movement_type, "Unknown")))
            self.movements_table.setItem(row, 3, QTableWidgetItem(f"{movement.quantity:.2f}"))
            self.movements_table.setItem(row, 4, QTableWidgetItem(f"{movement.cost:.2f}"))
            self.movements_table.setItem(row, 5, QTableWidgetItem(str(movement.movement_date)))
            self.movements_table.setItem(row, 6, QTableWidgetItem(movement.ref_no or ""))
            self.movements_table.setItem(row, 7, QTableWidgetItem(movement.memo or ""))
    
    def add_stock_movement(self):
        """Add new stock movement"""
        item_id = self.item_combo.currentData()
        movement_type = self.movement_type_combo.currentData()
        quantity = Decimal(str(self.quantity_input.value()))
        cost = Decimal(str(self.cost_input.value()))
        movement_date = self.date_input.date().toPython()
        ref_no = self.ref_no_input.text()
        memo = self.notes_input.text()
        
        if not item_id:
            QMessageBox.warning(self, tr('common.warning'), tr('messages.required_field'))
            return
        
        try:
            self.inventory_service.create_stock_movement(
                company_id=1,  # Default
                branch_id=1,   # Default
                item_id=item_id,
                movement_type=movement_type,
                quantity=quantity,
                cost=cost,
                movement_date=movement_date,
                ref_no=ref_no,
                memo=memo,
                created_by=1  # Default
            )
            QMessageBox.information(self, tr('common.success'), tr('messages.save_success'))
            self.clear_form()
            self.load_stock_movements()
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"{tr('common.error')}: {str(e)}")
    
    def clear_form(self):
        """Clear all form fields"""
        self.item_combo.setCurrentIndex(0)
        self.movement_type_combo.setCurrentIndex(0)
        self.quantity_input.setValue(0.0)
        self.cost_input.setValue(0.0)
        self.date_input.setDate(QDate.currentDate())
        self.ref_no_input.clear()
        self.notes_input.clear()


class CurrentStockWidget(QWidget):
    """Widget for viewing current stock levels"""
    
    def __init__(self, inventory_service, parent=None):
        super().__init__(parent)
        self.inventory_service = inventory_service
        self.init_ui()
        self.load_current_stock()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Search and filter
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr('common.search'))
        self.search_input.textChanged.connect(self.filter_stock)
        
        self.refresh_button = QPushButton(tr('common.refresh'))
        self.refresh_button.setStyleSheet(BUTTON_STYLE)
        self.refresh_button.clicked.connect(self.load_current_stock)
        
        filter_layout.addWidget(QLabel(tr('common.search') + ":"))
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(self.refresh_button)
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)
        
        # Stock table
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(7)
        self.stock_table.setHorizontalHeaderLabels([
            "ID", tr('common.code'), tr('common.name'), 
            tr('common.quantity'), tr('inventory.reorder_level'),
            tr('common.status'), tr('common.price')
        ])
        self.stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stock_table.setStyleSheet(TABLE_STYLE)
        self.stock_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.stock_table)
    
    def load_current_stock(self):
        """Load current stock levels for all items"""
        self.stock_table.setRowCount(0)
        items = self.inventory_service.get_all_items()
        
        self.stock_table.setRowCount(len(items))
        for row, item in enumerate(items):
            # Calculate current stock (simplified - in real app, sum movements)
            current_qty = self.inventory_service.get_item_stock_quantity(item.id)
            
            # Determine status
            status = tr('common.active')
            status_color = QColor(144, 238, 144)  # Light green
            
            if current_qty <= item.reorder_level:
                status = tr('inventory.reorder_level')
                status_color = QColor(255, 215, 0)  # Gold
            
            if current_qty <= 0:
                status = tr('common.inactive')
                status_color = QColor(255, 107, 107)  # Light red
            
            self.stock_table.setItem(row, 0, QTableWidgetItem(str(item.id)))
            self.stock_table.setItem(row, 1, QTableWidgetItem(str(item.code)))
            self.stock_table.setItem(row, 2, QTableWidgetItem(item.name_ar))
            self.stock_table.setItem(row, 3, QTableWidgetItem(f"{current_qty:.2f}"))
            self.stock_table.setItem(row, 4, QTableWidgetItem(f"{item.reorder_level:.2f}"))
            
            status_item = QTableWidgetItem(status)
            status_item.setBackground(status_color)
            self.stock_table.setItem(row, 5, status_item)
            
            self.stock_table.setItem(row, 6, QTableWidgetItem(f"{item.sale_price:.2f}"))
    
    def filter_stock(self):
        """Filter stock table based on search text"""
        search_text = self.search_input.text().lower()
        for row in range(self.stock_table.rowCount()):
            show_row = False
            for col in range(self.stock_table.columnCount()):
                item = self.stock_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.stock_table.setRowHidden(row, not show_row)


class InventoryManagementWidget(QWidget):
    """Main inventory management widget with tabs"""
    
    def __init__(self, inventory_service, warehouse_service, unit_service, parent=None):
        super().__init__(parent)
        self.inventory_service = inventory_service
        self.warehouse_service = warehouse_service
        self.unit_service = unit_service
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(tr('inventory.title'))
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.stock_movement_widget = StockMovementWidget(
            self.inventory_service, 
            self.warehouse_service,
            self.unit_service
        )
        self.current_stock_widget = CurrentStockWidget(self.inventory_service)
        
        self.tab_widget.addTab(self.stock_movement_widget, tr('inventory.stock_movements'))
        self.tab_widget.addTab(self.current_stock_widget, tr('inventory.current_stock'))
        
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
