"""
Labeeb ERP - Current Stock Widget
واجهة المخزون الحالي
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QMessageBox, QHeaderView, QComboBox,
    QDialog, QFormLayout, QDoubleSpinBox, QSpinBox, QCheckBox, QDialogButtonBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.ui.base_widget import TranslatableWidget
from app.i18n.translations import tr


class CurrentStockWidget(TranslatableWidget):
    """واجهة المخزون الحالي"""
    
    def __init__(self, backend, inventory_service, warehouse_service, parent=None):
        super().__init__(parent)
        
        self.backend = backend
        self.inventory_service = inventory_service
        self.warehouse_service = warehouse_service
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr('common.search'))
        self.search_input.textChanged.connect(self.filter_stock)
        filter_layout.addWidget(QLabel(tr('common.search') + ":"))
        filter_layout.addWidget(self.search_input)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems([
            tr('common.all'),
            tr('inventory.in_stock'),
            tr('inventory.low_stock'),
            tr('inventory.out_of_stock')
        ])
        self.status_filter.currentIndexChanged.connect(self.filter_stock)
        filter_layout.addWidget(QLabel(tr('common.status') + ":"))
        filter_layout.addWidget(self.status_filter)
        
        self.refresh_button = QPushButton(tr('common.refresh'))
        self.refresh_button.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        self.refresh_button.clicked.connect(self.refresh_data)
        filter_layout.addWidget(self.refresh_button)
        
        self.edit_button = QPushButton(tr('common.edit'))
        self.edit_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        self.edit_button.clicked.connect(self.edit_item)
        filter_layout.addWidget(self.edit_button)
        
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)
        
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(7)
        self.stock_table.setHorizontalHeaderLabels([
            "ID", tr('common.code'), tr('common.name'), 
            tr('common.quantity'), tr('inventory.reorder_level'),
            tr('common.status'), tr('common.price')
        ])
        self.stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stock_table.setAlternatingRowColors(True)
        self.stock_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        main_layout.addWidget(self.stock_table)
        
        summary_layout = QHBoxLayout()
        
        self.total_items_label = QLabel(f"{tr('inventory.total_items')}: 0")
        self.total_items_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        summary_layout.addWidget(self.total_items_label)
        
        self.low_stock_label = QLabel(f"{tr('inventory.low_stock_items')}: 0")
        self.low_stock_label.setStyleSheet("font-weight: bold; font-size: 14px; color: orange;")
        summary_layout.addWidget(self.low_stock_label)
        
        self.out_of_stock_label = QLabel(f"{tr('inventory.out_of_stock_items')}: 0")
        self.out_of_stock_label.setStyleSheet("font-weight: bold; font-size: 14px; color: red;")
        summary_layout.addWidget(self.out_of_stock_label)
        
        summary_layout.addStretch()
        main_layout.addLayout(summary_layout)
    
    def load_data(self):
        self.refresh_data()
    
    def refresh_data(self):
        try:
            self.stock_table.setRowCount(0)
            stock_levels = self.backend.get_all_stock_levels()
            
            total_items = 0
            low_stock_count = 0
            out_of_stock_count = 0
            
            for stock in stock_levels:
                row = self.stock_table.rowCount()
                self.stock_table.insertRow(row)
                
                item_id = stock['item_id']
                item = self.inventory_service.get_item_by_id(item_id)
                
                if not item:
                    continue
                
                total_items += 1
                current_qty = stock['current_stock']
                reorder_level = stock['reorder_level']
                
                status = tr('inventory.in_stock')
                status_color = QColor(144, 238, 144)
                
                if current_qty <= reorder_level and current_qty > 0:
                    status = tr('inventory.low_stock')
                    status_color = QColor(255, 215, 0)
                    low_stock_count += 1
                elif current_qty <= 0:
                    status = tr('inventory.out_of_stock')
                    status_color = QColor(255, 107, 107)
                    out_of_stock_count += 1
                
                self.stock_table.setItem(row, 0, QTableWidgetItem(str(item_id)))
                self.stock_table.setItem(row, 1, QTableWidgetItem(str(item.code)))
                self.stock_table.setItem(row, 2, QTableWidgetItem(item.name_ar))
                self.stock_table.setItem(row, 3, QTableWidgetItem(f"{current_qty:.2f}"))
                self.stock_table.setItem(row, 4, QTableWidgetItem(f"{reorder_level:.2f}"))
                
                status_item = QTableWidgetItem(status)
                status_item.setBackground(status_color)
                self.stock_table.setItem(row, 5, status_item)
                
                self.stock_table.setItem(row, 6, QTableWidgetItem(f"{item.sale_price:.2f}"))
            
            self.total_items_label.setText(f"{tr('inventory.total_items')}: {total_items}")
            self.low_stock_label.setText(f"{tr('inventory.low_stock_items')}: {low_stock_count}")
            self.out_of_stock_label.setText(f"{tr('inventory.out_of_stock_items')}: {out_of_stock_count}")
            
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error refreshing data: {str(e)}")
    
    def filter_stock(self):
        search_text = self.search_input.text().lower()
        status_filter = self.status_filter.currentIndex()
        
        for row in range(self.stock_table.rowCount()):
            show_row = True
            
            if search_text:
                code = self.stock_table.item(row, 1).text().lower()
                name = self.stock_table.item(row, 2).text().lower()
                if search_text not in code and search_text not in name:
                    show_row = False
            
            if status_filter > 0 and show_row:
                status = self.stock_table.item(row, 5).text()
                if status_filter == 1 and status != tr('inventory.in_stock'):
                    show_row = False
                elif status_filter == 2 and status != tr('inventory.low_stock'):
                    show_row = False
                elif status_filter == 3 and status != tr('inventory.out_of_stock'):
                    show_row = False
            
            self.stock_table.setRowHidden(row, not show_row)
    
    def edit_item(self):
        """فتح نافذة تعديل الصنف المحدد"""
        selected_rows = self.stock_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, tr('common.warning'), tr('inventory.select_item_to_edit'))
            return
        
        row = selected_rows[0].row()
        item_id = int(self.stock_table.item(row, 0).text())
        item = self.inventory_service.get_item_by_id(item_id)
        
        if not item:
            QMessageBox.critical(self, tr('common.error'), "Item not found")
            return
        
        dialog = ItemEditDialog(item, self.inventory_service, self)
        if dialog.exec():
            self.refresh_data()
            QMessageBox.information(self, tr('common.success'), tr('inventory.item_updated'))
    
    def refresh_translations(self):
        super().refresh_translations()
        self.load_data()


class ItemEditDialog(QDialog):
    """نافذة تعديل الصنف"""
    
    def __init__(self, item, inventory_service, parent=None):
        super().__init__(parent)
        self.item = item
        self.inventory_service = inventory_service
        
        self.setWindowTitle(tr('inventory.edit_item'))
        self.setMinimumWidth(400)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Code (read-only)
        self.code_label = QLabel(str(self.item.code))
        form_layout.addRow(tr('common.code') + ":", self.code_label)
        
        # Arabic Name
        self.name_ar_input = QLineEdit(self.item.name_ar)
        form_layout.addRow(tr('common.name') + " (عربي):", self.name_ar_input)
        
        # English Name
        self.name_en_input = QLineEdit(self.item.name_en or "")
        form_layout.addRow(tr('common.name') + " (English):", self.name_en_input)
        
        # Sale Price
        self.sale_price_input = QDoubleSpinBox()
        self.sale_price_input.setRange(0, 999999999)
        self.sale_price_input.setDecimals(2)
        self.sale_price_input.setValue(float(self.item.sale_price or 0))
        form_layout.addRow(tr('items.selling_price') + ":", self.sale_price_input)
        
        # Cost Price
        self.cost_price_input = QDoubleSpinBox()
        self.cost_price_input.setRange(0, 999999999)
        self.cost_price_input.setDecimals(2)
        self.cost_price_input.setValue(float(self.item.cost_price or 0))
        form_layout.addRow(tr('items.cost_price') + ":", self.cost_price_input)
        
        # Reorder Level
        self.reorder_level_input = QSpinBox()
        self.reorder_level_input.setRange(0, 999999)
        self.reorder_level_input.setValue(int(self.item.reorder_level or 0))
        form_layout.addRow(tr('inventory.reorder_level') + ":", self.reorder_level_input)
        
        # Barcode
        self.barcode_input = QLineEdit(self.item.barcode or "")
        form_layout.addRow("Barcode:", self.barcode_input)
        
        # Is Active
        self.is_active_checkbox = QCheckBox()
        self.is_active_checkbox.setChecked(self.item.is_active)
        form_layout.addRow(tr('common.active') + ":", self.is_active_checkbox)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.save_changes)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def save_changes(self):
        """حفظ التغييرات على الصنف"""
        try:
            updates = {
                'name_ar': self.name_ar_input.text(),
                'name_en': self.name_en_input.text(),
                'sale_price': self.sale_price_input.value(),
                'cost_price': self.cost_price_input.value(),
                'reorder_level': self.reorder_level_input.value(),
                'barcode': self.barcode_input.text(),
                'is_active': self.is_active_checkbox.isChecked()
            }
            
            self.inventory_service.update_item(self.item.id, **updates)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error saving item: {str(e)}")
