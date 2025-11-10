"""
Labeeb ERP - Stock Movements Widget
واجهة حركات المخزون
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLineEdit, QDateEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QDoubleSpinBox, QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor

from app.ui.base_widget import TranslatableWidget
from app.i18n.translations import tr


class StockMovementsWidget(TranslatableWidget):
    """واجهة حركات المخزون"""
    
    def __init__(self, backend, inventory_service, warehouse_service, unit_service, parent=None):
        super().__init__(parent)
        
        self.backend = backend
        self.inventory_service = inventory_service
        self.warehouse_service = warehouse_service
        self.unit_service = unit_service
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        form_group = QGroupBox(tr('inventory.add_movement'))
        form_layout = QFormLayout()
        
        self.item_combo = QComboBox()
        self.item_combo.setEditable(True)
        form_layout.addRow(tr('common.name') + ":", self.item_combo)
        
        self.movement_type_combo = QComboBox()
        self.movement_type_combo.addItem(tr('inventory.stock_in'), 0)
        self.movement_type_combo.addItem(tr('inventory.stock_out'), 1)
        self.movement_type_combo.addItem(tr('inventory.adjustment'), 3)
        form_layout.addRow(tr('common.type') + ":", self.movement_type_combo)
        
        self.warehouse_combo = QComboBox()
        form_layout.addRow(tr('inventory.warehouse') + ":", self.warehouse_combo)
        
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setRange(0.01, 999999.99)
        self.quantity_input.setDecimals(2)
        form_layout.addRow(tr('common.quantity') + ":", self.quantity_input)
        
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0.00, 999999.99)
        self.cost_input.setDecimals(2)
        form_layout.addRow(tr('common.price') + ":", self.cost_input)
        
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form_layout.addRow(tr('common.date') + ":", self.date_input)
        
        self.ref_no_input = QLineEdit()
        self.ref_no_input.setPlaceholderText(tr('common.code'))
        form_layout.addRow(tr('common.code') + ":", self.ref_no_input)
        
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText(tr('common.description'))
        form_layout.addRow(tr('common.description') + ":", self.notes_input)
        
        button_layout = QHBoxLayout()
        self.add_button = QPushButton(tr('common.add'))
        self.add_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        self.add_button.clicked.connect(self.add_stock_movement)
        
        self.clear_button = QPushButton(tr('common.clear'))
        self.clear_button.setStyleSheet("background-color: #9E9E9E; color: white; padding: 8px;")
        self.clear_button.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.clear_button)
        form_layout.addRow(button_layout)
        
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr('common.search'))
        self.search_input.textChanged.connect(self.filter_movements)
        search_layout.addWidget(QLabel(tr('common.search') + ":"))
        search_layout.addWidget(self.search_input)
        
        refresh_btn = QPushButton(tr('common.refresh'))
        refresh_btn.clicked.connect(self.refresh_data)
        search_layout.addWidget(refresh_btn)
        search_layout.addStretch()
        
        main_layout.addLayout(search_layout)
        
        self.movements_table = QTableWidget()
        self.movements_table.setColumnCount(8)
        self.movements_table.setHorizontalHeaderLabels([
            "ID", tr('common.name'), tr('common.type'), 
            tr('common.quantity'), tr('common.price'), 
            tr('common.date'), tr('common.code'), tr('common.description')
        ])
        self.movements_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.movements_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.movements_table)
    
    def load_data(self):
        try:
            self.item_combo.clear()
            items = self.inventory_service.get_all_items()
            for item in items:
                self.item_combo.addItem(f"{item.name_ar} ({item.code})", item.id)
            
            self.warehouse_combo.clear()
            warehouses = self.warehouse_service.get_all_warehouses(company_id=1)
            for warehouse in warehouses:
                self.warehouse_combo.addItem(warehouse.name_ar or warehouse.name_en, warehouse.id)
            
            self.refresh_data()
            
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error loading data: {str(e)}")
    
    def refresh_data(self):
        try:
            self.movements_table.setRowCount(0)
            movements = self.backend.get_all_stock_movements()
            
            movement_types = {
                0: tr('inventory.stock_in'),
                1: tr('inventory.stock_out'),
                2: tr('inventory.transfer'),
                3: tr('inventory.adjustment')
            }
            
            for movement in movements:
                row = self.movements_table.rowCount()
                self.movements_table.insertRow(row)
                
                self.movements_table.setItem(row, 0, QTableWidgetItem(str(movement['id'])))
                self.movements_table.setItem(row, 1, QTableWidgetItem(movement['item_name']))
                self.movements_table.setItem(row, 2, QTableWidgetItem(movement['movement_type_name']))
                self.movements_table.setItem(row, 3, QTableWidgetItem(f"{movement['quantity']:.2f}"))
                self.movements_table.setItem(row, 4, QTableWidgetItem(f"{movement['cost']:.2f}"))
                self.movements_table.setItem(row, 5, QTableWidgetItem(movement['movement_date']))
                self.movements_table.setItem(row, 6, QTableWidgetItem(movement['ref_no'] or ""))
                self.movements_table.setItem(row, 7, QTableWidgetItem(movement['memo'] or ""))
                
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error refreshing data: {str(e)}")
    
    def add_stock_movement(self):
        try:
            item_id = self.item_combo.currentData()
            movement_type = self.movement_type_combo.currentData()
            warehouse_id = self.warehouse_combo.currentData()
            quantity = self.quantity_input.value()
            cost = self.cost_input.value()
            movement_date = self.date_input.date().toPython()
            ref_no = self.ref_no_input.text()
            memo = self.notes_input.text()
            
            if not item_id:
                QMessageBox.warning(self, tr('common.warning'), tr('messages.required_field'))
                return
            
            movement_data = {
                'item_id': item_id,
                'movement_type': movement_type,
                'warehouse_id': warehouse_id,
                'quantity': quantity,
                'cost': cost,
                'movement_date': movement_date,
                'ref_no': ref_no,
                'memo': memo,
                'company_id': 1,
                'branch_id': 1,
                'user_id': 1
            }
            
            if self.backend.create_stock_movement(movement_data):
                QMessageBox.information(self, tr('common.success'), tr('messages.save_success'))
                self.clear_form()
                self.refresh_data()
            else:
                QMessageBox.critical(self, tr('common.error'), tr('messages.save_failed'))
                
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"{tr('common.error')}: {str(e)}")
    
    def clear_form(self):
        self.item_combo.setCurrentIndex(0)
        self.movement_type_combo.setCurrentIndex(0)
        self.warehouse_combo.setCurrentIndex(0)
        self.quantity_input.setValue(0.0)
        self.cost_input.setValue(0.0)
        self.date_input.setDate(QDate.currentDate())
        self.ref_no_input.clear()
        self.notes_input.clear()
    
    def filter_movements(self):
        search_text = self.search_input.text().lower()
        for row in range(self.movements_table.rowCount()):
            show_row = False
            for col in range(self.movements_table.columnCount()):
                item = self.movements_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.movements_table.setRowHidden(row, not show_row)
    
    def new_document(self):
        self.clear_form()
    
    def save_document(self):
        self.add_stock_movement()
    
    def refresh_translations(self):
        super().refresh_translations()
        self.load_data()
