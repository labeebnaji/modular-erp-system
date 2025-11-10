"""
Labeeb ERP - Stock Transfer Widget
واجهة نقل المخزون بين المستودعات
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLineEdit, QDateEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QDoubleSpinBox, QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt, QDate

from app.ui.base_widget import TranslatableWidget
from app.i18n.translations import tr


class StockTransferWidget(TranslatableWidget):
    """واجهة نقل المخزون بين المستودعات"""
    
    def __init__(self, backend, inventory_service, warehouse_service, parent=None):
        super().__init__(parent)
        
        self.backend = backend
        self.inventory_service = inventory_service
        self.warehouse_service = warehouse_service
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        form_group = QGroupBox(tr('inventory.transfer_stock'))
        form_layout = QFormLayout()
        
        self.item_combo = QComboBox()
        self.item_combo.setEditable(True)
        self.item_combo.currentIndexChanged.connect(self.on_item_selected)
        form_layout.addRow(tr('common.name') + ":", self.item_combo)
        
        self.from_warehouse_combo = QComboBox()
        form_layout.addRow(tr('inventory.from_warehouse') + ":", self.from_warehouse_combo)
        
        self.to_warehouse_combo = QComboBox()
        form_layout.addRow(tr('inventory.to_warehouse') + ":", self.to_warehouse_combo)
        
        self.available_qty_label = QLabel("0.00")
        self.available_qty_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        form_layout.addRow(tr('inventory.available_quantity') + ":", self.available_qty_label)
        
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setRange(0.01, 999999.99)
        self.quantity_input.setDecimals(2)
        form_layout.addRow(tr('common.quantity') + ":", self.quantity_input)
        
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form_layout.addRow(tr('common.date') + ":", self.date_input)
        
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText(tr('common.description'))
        form_layout.addRow(tr('common.description') + ":", self.notes_input)
        
        button_layout = QHBoxLayout()
        
        self.transfer_button = QPushButton(tr('inventory.transfer'))
        self.transfer_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;")
        self.transfer_button.clicked.connect(self.transfer_stock)
        
        self.clear_button = QPushButton(tr('common.clear'))
        self.clear_button.setStyleSheet("background-color: #9E9E9E; color: white; padding: 10px;")
        self.clear_button.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.transfer_button)
        button_layout.addWidget(self.clear_button)
        form_layout.addRow(button_layout)
        
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        history_group = QGroupBox(tr('inventory.transfer_history'))
        history_layout = QVBoxLayout()
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr('common.search'))
        self.search_input.textChanged.connect(self.filter_transfers)
        search_layout.addWidget(self.search_input)
        
        refresh_btn = QPushButton(tr('common.refresh'))
        refresh_btn.clicked.connect(self.refresh_data)
        search_layout.addWidget(refresh_btn)
        
        history_layout.addLayout(search_layout)
        
        self.transfers_table = QTableWidget()
        self.transfers_table.setColumnCount(7)
        self.transfers_table.setHorizontalHeaderLabels([
            "ID", tr('common.name'), tr('inventory.from_warehouse'),
            tr('inventory.to_warehouse'), tr('common.quantity'),
            tr('common.date'), tr('common.description')
        ])
        self.transfers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transfers_table.setAlternatingRowColors(True)
        
        history_layout.addWidget(self.transfers_table)
        
        history_group.setLayout(history_layout)
        main_layout.addWidget(history_group)
    
    def load_data(self):
        try:
            self.item_combo.clear()
            items = self.inventory_service.get_all_items()
            for item in items:
                self.item_combo.addItem(f"{item.name_ar} ({item.code})", item.id)
            
            self.from_warehouse_combo.clear()
            self.to_warehouse_combo.clear()
            warehouses = self.warehouse_service.get_all_warehouses(company_id=1)
            for warehouse in warehouses:
                warehouse_name = warehouse.name_ar or warehouse.name_en
                self.from_warehouse_combo.addItem(warehouse_name, warehouse.id)
                self.to_warehouse_combo.addItem(warehouse_name, warehouse.id)
            
            self.refresh_data()
            
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error loading data: {str(e)}")
    
    def on_item_selected(self):
        item_id = self.item_combo.currentData()
        if item_id:
            try:
                stock_level = self.backend.get_item_stock_level(item_id)
                self.available_qty_label.setText(f"{stock_level.get('current_stock', 0):.2f}")
            except Exception as e:
                print(f"Error loading stock level: {e}")
    
    def transfer_stock(self):
        try:
            item_id = self.item_combo.currentData()
            from_warehouse = self.from_warehouse_combo.currentData()
            to_warehouse = self.to_warehouse_combo.currentData()
            quantity = self.quantity_input.value()
            notes = self.notes_input.text()
            
            if not item_id:
                QMessageBox.warning(self, tr('common.warning'), tr('sales.select_item'))
                return
            
            if not from_warehouse or not to_warehouse:
                QMessageBox.warning(self, tr('common.warning'), tr('inventory.select_warehouses'))
                return
            
            if from_warehouse == to_warehouse:
                QMessageBox.warning(self, tr('common.warning'), tr('inventory.same_warehouse_error'))
                return
            
            if quantity <= 0:
                QMessageBox.warning(self, tr('common.warning'), tr('sales.invalid_amount'))
                return
            
            if self.backend.transfer_stock(item_id, from_warehouse, to_warehouse, quantity, notes):
                QMessageBox.information(self, tr('common.success'), tr('inventory.transfer_success'))
                self.clear_form()
                self.refresh_data()
            else:
                QMessageBox.critical(self, tr('common.error'), tr('inventory.transfer_failed'))
                
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"{tr('common.error')}: {str(e)}")
    
    def clear_form(self):
        self.item_combo.setCurrentIndex(0)
        self.from_warehouse_combo.setCurrentIndex(0)
        self.to_warehouse_combo.setCurrentIndex(0)
        self.quantity_input.setValue(0.0)
        self.date_input.setDate(QDate.currentDate())
        self.notes_input.clear()
        self.available_qty_label.setText("0.00")
    
    def refresh_data(self):
        self.transfers_table.setRowCount(0)
    
    def filter_transfers(self):
        search_text = self.search_input.text().lower()
        for row in range(self.transfers_table.rowCount()):
            show_row = False
            for col in range(self.transfers_table.columnCount()):
                item = self.transfers_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.transfers_table.setRowHidden(row, not show_row)
    
    def new_document(self):
        self.clear_form()
    
    def save_document(self):
        self.transfer_stock()
    
    def refresh_translations(self):
        super().refresh_translations()
        self.load_data()
