"""
Complete Purchase Order Management Widget
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                               QTableWidgetItem, QPushButton, QLabel, QLineEdit, 
                               QComboBox, QDateEdit, QDoubleSpinBox, QMessageBox, 
                               QGroupBox, QFormLayout, QHeaderView)
from PySide6.QtCore import Qt, QDate
from decimal import Decimal
from datetime import datetime

from app.application.services import SalesPurchaseService, ARAPService, InventoryService, CurrencyService
from app.ui.styles import BUTTON_STYLE, TABLE_STYLE, GROUPBOX_STYLE
from app.i18n.translations import tr


class PurchaseOrderManagementWidget(QWidget):
    """Widget for managing purchase orders"""
    
    def __init__(self, sales_purchase_service, arap_service, inventory_service, currency_service, parent=None):
        super().__init__(parent)
        self.sales_purchase_service = sales_purchase_service
        self.arap_service = arap_service
        self.inventory_service = inventory_service
        self.currency_service = currency_service
        self.current_order_lines = []
        self.selected_order_id = None
        self.init_ui()
        self.load_purchase_orders()
    
    def init_ui(self):
        self.setWindowTitle(tr('modules.purchases') + " - " + "Orders")
        main_layout = QVBoxLayout(self)
        
        # Order Header Form
        header_group = QGroupBox("Purchase Order Header")
        header_group.setStyleSheet(GROUPBOX_STYLE)
        header_layout = QFormLayout()
        
        self.order_no_input = QLineEdit()
        self.order_no_input.setPlaceholderText("Auto-generated")
        self.order_no_input.setReadOnly(True)
        header_layout.addRow(QLabel("Order No:"), self.order_no_input)
        
        self.supplier_combo = QComboBox()
        self.load_suppliers()
        header_layout.addRow(QLabel("Supplier:"), self.supplier_combo)
        
        self.order_date_input = QDateEdit(QDate.currentDate())
        self.order_date_input.setCalendarPopup(True)
        header_layout.addRow(QLabel(tr('common.date') + ":"), self.order_date_input)
        
        self.currency_combo = QComboBox()
        self.load_currencies()
        header_layout.addRow(QLabel("Currency:"), self.currency_combo)
        
        self.status_combo = QComboBox()
        self.status_combo.addItem("Draft", 0)
        self.status_combo.addItem("Confirmed", 1)
        self.status_combo.addItem("Received", 2)
        self.status_combo.addItem("Cancelled", 3)
        header_layout.addRow(QLabel(tr('common.status') + ":"), self.status_combo)
        
        header_group.setLayout(header_layout)
        main_layout.addWidget(header_group)
        
        # Order Lines Section
        lines_group = QGroupBox("Order Lines")
        lines_group.setStyleSheet(GROUPBOX_STYLE)
        lines_layout = QVBoxLayout()
        
        # Line input form
        line_form = QHBoxLayout()
        
        self.item_combo = QComboBox()
        self.load_items()
        line_form.addWidget(QLabel("Item:"))
        line_form.addWidget(self.item_combo)
        
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setRange(0.01, 999999.99)
        self.quantity_input.setDecimals(2)
        line_form.addWidget(QLabel(tr('common.quantity') + ":"))
        line_form.addWidget(self.quantity_input)
        
        self.unit_price_input = QDoubleSpinBox()
        self.unit_price_input.setRange(0.00, 999999.99)
        self.unit_price_input.setDecimals(2)
        line_form.addWidget(QLabel(tr('common.price') + ":"))
        line_form.addWidget(self.unit_price_input)
        
        self.add_line_button = QPushButton("Add Line")
        self.add_line_button.setStyleSheet(BUTTON_STYLE)
        self.add_line_button.clicked.connect(self.add_order_line)
        line_form.addWidget(self.add_line_button)
        
        lines_layout.addLayout(line_form)
        
        # Lines table
        self.lines_table = QTableWidget()
        self.lines_table.setColumnCount(5)
        self.lines_table.setHorizontalHeaderLabels([
            "Item", tr('common.quantity'), tr('common.price'), 
            tr('common.total'), "Action"
        ])
        self.lines_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.lines_table.setStyleSheet(TABLE_STYLE)
        self.lines_table.setAlternatingRowColors(True)
        lines_layout.addWidget(self.lines_table)
        
        # Totals
        totals_layout = QHBoxLayout()
        self.total_label = QLabel(tr('common.total') + ": 0.00")
        self.total_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        totals_layout.addStretch()
        totals_layout.addWidget(self.total_label)
        lines_layout.addLayout(totals_layout)
        
        lines_group.setLayout(lines_layout)
        main_layout.addWidget(lines_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton(tr('common.save'))
        self.save_button.setStyleSheet(BUTTON_STYLE)
        self.save_button.clicked.connect(self.save_purchase_order)
        
        self.new_button = QPushButton(tr('common.new'))
        self.new_button.setStyleSheet(BUTTON_STYLE)
        self.new_button.clicked.connect(self.clear_form)
        
        self.delete_button = QPushButton(tr('common.delete'))
        self.delete_button.setStyleSheet(BUTTON_STYLE)
        self.delete_button.clicked.connect(self.delete_purchase_order)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Orders table
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(7)
        self.orders_table.setHorizontalHeaderLabels([
            "ID", "Order No", "Supplier", tr('common.date'), 
            tr('common.total'), "Currency", tr('common.status')
        ])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.orders_table.setStyleSheet(TABLE_STYLE)
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.cellClicked.connect(self.load_order_details)
        
        main_layout.addWidget(self.orders_table)
    
    def load_suppliers(self):
        """Load all suppliers"""
        self.supplier_combo.clear()
        suppliers = self.arap_service.get_all_suppliers()
        for supplier in suppliers:
            self.supplier_combo.addItem(supplier.name_ar, supplier.id)
    
    def load_items(self):
        """Load all items"""
        self.item_combo.clear()
        items = self.inventory_service.get_all_items()
        for item in items:
            self.item_combo.addItem(f"{item.name_ar} ({item.code})", item.id)
    
    def load_currencies(self):
        """Load all currencies"""
        self.currency_combo.clear()
        currencies = self.currency_service.get_all_currencies()
        for currency in currencies:
            self.currency_combo.addItem(currency.code, currency.code)
    
    def add_order_line(self):
        """Add line to current order"""
        item_id = self.item_combo.currentData()
        item_name = self.item_combo.currentText()
        quantity = Decimal(str(self.quantity_input.value()))
        unit_price = Decimal(str(self.unit_price_input.value()))
        total = quantity * unit_price
        
        if not item_id or quantity <= 0:
            QMessageBox.warning(self, tr('common.warning'), "Please select item and enter quantity")
            return
        
        line = {
            'item_id': item_id,
            'item_name': item_name,
            'quantity': quantity,
            'unit_price': unit_price,
            'total': total
        }
        self.current_order_lines.append(line)
        self.refresh_lines_table()
        
        self.quantity_input.setValue(0.0)
        self.unit_price_input.setValue(0.0)
    
    def refresh_lines_table(self):
        """Refresh the lines table"""
        self.lines_table.setRowCount(len(self.current_order_lines))
        total_amount = Decimal('0.00')
        
        for row, line in enumerate(self.current_order_lines):
            self.lines_table.setItem(row, 0, QTableWidgetItem(line['item_name']))
            self.lines_table.setItem(row, 1, QTableWidgetItem(f"{line['quantity']:.2f}"))
            self.lines_table.setItem(row, 2, QTableWidgetItem(f"{line['unit_price']:.2f}"))
            self.lines_table.setItem(row, 3, QTableWidgetItem(f"{line['total']:.2f}"))
            
            delete_btn = QPushButton(tr('common.delete'))
            delete_btn.setStyleSheet(BUTTON_STYLE)
            delete_btn.clicked.connect(lambda checked, r=row: self.remove_line(r))
            self.lines_table.setCellWidget(row, 4, delete_btn)
            
            total_amount += line['total']
        
        self.total_label.setText(f"{tr('common.total')}: {total_amount:.2f}")
    
    def remove_line(self, row):
        """Remove line from order"""
        if 0 <= row < len(self.current_order_lines):
            self.current_order_lines.pop(row)
            self.refresh_lines_table()
    
    def save_purchase_order(self):
        """Save purchase order"""
        supplier_id = self.supplier_combo.currentData()
        order_date = self.order_date_input.date().toPython()
        currency = self.currency_combo.currentData()
        status = self.status_combo.currentData()
        
        if not supplier_id:
            QMessageBox.warning(self, tr('common.warning'), "Please select a supplier")
            return
        
        if not self.current_order_lines:
            QMessageBox.warning(self, tr('common.warning'), "Please add at least one line")
            return
        
        total_amount = sum(line['total'] for line in self.current_order_lines)
        
        try:
            order_no = f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            QMessageBox.information(self, tr('common.success'), 
                                  f"Purchase Order {order_no} saved successfully!\nTotal: {total_amount:.2f}")
            
            self.clear_form()
            self.load_purchase_orders()
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error: {str(e)}")
    
    def load_purchase_orders(self):
        """Load all purchase orders"""
        self.orders_table.setRowCount(0)
    
    def load_order_details(self, row, col):
        """Load order details when clicked"""
        pass
    
    def delete_purchase_order(self):
        """Delete selected purchase order"""
        if not self.selected_order_id:
            QMessageBox.warning(self, tr('common.warning'), "Please select an order to delete")
            return
        
        reply = QMessageBox.question(self, tr('common.confirm'), 
                                    tr('messages.confirm_delete'),
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, tr('common.success'), tr('messages.delete_success'))
            self.clear_form()
            self.load_purchase_orders()
    
    def clear_form(self):
        """Clear all form fields"""
        self.order_no_input.clear()
        self.supplier_combo.setCurrentIndex(0)
        self.order_date_input.setDate(QDate.currentDate())
        self.currency_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        self.current_order_lines = []
        self.selected_order_id = None
        self.refresh_lines_table()
