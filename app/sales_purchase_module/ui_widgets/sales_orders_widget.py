"""
Labeeb ERP - Sales Orders Widget
واجهة أوامر المبيعات الكاملة
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QGroupBox, QFormLayout,
    QLineEdit, QDateEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QTextEdit, QDoubleSpinBox,
    QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor

from app.ui.base_widget import TranslatableWidget
from app.i18n.translations import tr


class SalesOrdersWidget(TranslatableWidget):
    """واجهة أوامر المبيعات الكاملة"""
    
    def __init__(self, backend, arap_service, branch_service, company_service, parent=None):
        super().__init__(parent)
        
        self.backend = backend
        self.arap_service = arap_service
        self.branch_service = branch_service
        self.company_service = company_service
        
        self.current_order_id = None
        self.order_items = []
        self.all_orders = []
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_panel = self.create_order_form()
        splitter.addWidget(left_panel)
        
        right_panel = self.create_orders_list()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter)
    
    def create_order_form(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        header_group = QGroupBox(tr('sales.order_details'))
        header_layout = QFormLayout()
        
        self.order_no_input = QLineEdit()
        self.order_no_input.setReadOnly(True)
        header_layout.addRow(tr('sales.order_no') + ":", self.order_no_input)
        
        self.order_date_input = QDateEdit()
        self.order_date_input.setDate(QDate.currentDate())
        self.order_date_input.setCalendarPopup(True)
        header_layout.addRow(tr('sales.order_date') + ":", self.order_date_input)
        
        self.customer_combo = QComboBox()
        self.customer_combo.setEditable(True)
        header_layout.addRow(tr('sales.customer') + ":", self.customer_combo)
        
        self.delivery_date_input = QDateEdit()
        self.delivery_date_input.setDate(QDate.currentDate().addDays(7))
        self.delivery_date_input.setCalendarPopup(True)
        header_layout.addRow(tr('sales.delivery_date') + ":", self.delivery_date_input)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            tr('sales.pending'),
            tr('sales.confirmed'),
            tr('sales.processing'),
            tr('sales.completed'),
            tr('sales.cancelled')
        ])
        header_layout.addRow(tr('common.status') + ":", self.status_combo)
        
        header_group.setLayout(header_layout)
        layout.addWidget(header_group)
        
        items_group = QGroupBox(tr('sales.order_items'))
        items_layout = QVBoxLayout()
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels([
            tr('sales.item_name'),
            tr('sales.quantity'),
            tr('sales.unit_price'),
            tr('sales.total'),
            tr('common.actions')
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.items_table.setAlternatingRowColors(True)
        items_layout.addWidget(self.items_table)
        
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)
        
        totals_group = QGroupBox(tr('sales.total'))
        totals_layout = QFormLayout()
        
        self.total_label = QLabel("0.00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2196F3;")
        totals_layout.addRow(tr('sales.total') + ":", self.total_label)
        
        totals_group.setLayout(totals_layout)
        layout.addWidget(totals_group)
        
        notes_group = QGroupBox(tr('sales.notes'))
        notes_layout = QVBoxLayout()
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        notes_layout.addWidget(self.notes_input)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        buttons_layout = QHBoxLayout()
        
        self.save_btn = QPushButton(tr('common.save'))
        self.save_btn.clicked.connect(self.save_document)
        self.save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;")
        buttons_layout.addWidget(self.save_btn)
        
        self.new_btn = QPushButton(tr('common.new'))
        self.new_btn.clicked.connect(self.new_document)
        self.new_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px;")
        buttons_layout.addWidget(self.new_btn)
        
        self.convert_btn = QPushButton(tr('sales.convert_to_invoice'))
        self.convert_btn.clicked.connect(self.convert_to_invoice)
        self.convert_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 10px;")
        buttons_layout.addWidget(self.convert_btn)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        return widget
    
    def create_orders_list(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr('sales.search_orders'))
        self.search_input.textChanged.connect(self.filter_orders)
        search_layout.addWidget(self.search_input)
        
        refresh_btn = QPushButton(tr('common.refresh'))
        refresh_btn.clicked.connect(self.refresh_data)
        search_layout.addWidget(refresh_btn)
        
        layout.addLayout(search_layout)
        
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(7)
        self.orders_table.setHorizontalHeaderLabels([
            "ID",
            tr('sales.order_no'),
            tr('sales.order_date'),
            tr('sales.customer'),
            tr('sales.total_amount'),
            tr('common.status'),
            tr('common.actions')
        ])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.orders_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.orders_table)
        
        return widget
    
    def load_data(self):
        try:
            self.customer_combo.clear()
            self.customer_combo.addItem(tr('sales.cash_customer'), None)
            customers = self.arap_service.get_all_customers()
            for customer in customers:
                self.customer_combo.addItem(
                    customer.name_ar or customer.name_en,
                    customer.id
                )
            
            self.order_no_input.setText(self.generate_order_number())
            self.refresh_data()
            
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error loading data: {str(e)}")
    
    def save_document(self):
        """حفظ أمر المبيعات"""
        try:
            if not self.customer_combo.currentData():
                QMessageBox.warning(self, tr('common.warning'), tr('sales.select_customer'))
                return
            
            if len(self.order_items) == 0:
                QMessageBox.warning(self, tr('common.warning'), tr('sales.add_items'))
                return
            
            order_data = {
                'order_no': self.order_no_input.text(),
                'order_date': self.order_date_input.date().toPython(),
                'delivery_date': self.delivery_date_input.date().toPython(),
                'customer_id': self.customer_combo.currentData(),
                'status': self.status_combo.currentText(),
                'total': float(self.total_label.text()),
                'notes': self.notes_input.toPlainText(),
                'items': self.order_items,
                'company_id': 1,
                'branch_id': 1
            }
            
            if self.backend.create_sales_order(order_data):
                QMessageBox.information(self, tr('common.success'), tr('sales.order_saved'))
                self.new_document()
                self.refresh_data()
            else:
                QMessageBox.critical(self, tr('common.error'), tr('sales.save_failed'))
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error saving order: {str(e)}")
    
    def new_document(self):
        self.current_order_id = None
        self.order_no_input.setText(self.generate_order_number())
        self.order_date_input.setDate(QDate.currentDate())
        self.delivery_date_input.setDate(QDate.currentDate().addDays(7))
        self.customer_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        self.items_table.setRowCount(0)
        self.order_items.clear()
        self.notes_input.clear()
        self.total_label.setText("0.00")
    
    def delete_document(self):
        """حذف أمر المبيعات"""
        if not self.current_order_id:
            QMessageBox.warning(self, tr('common.warning'), tr('sales.no_order_selected'))
            return
        
        reply = QMessageBox.question(
            self,
            tr('common.confirm'),
            tr('sales.confirm_delete'),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.backend.delete_sales_order(self.current_order_id):
                    QMessageBox.information(self, tr('common.success'), tr('sales.order_deleted'))
                    self.new_document()
                    self.refresh_data()
                else:
                    QMessageBox.critical(self, tr('common.error'), tr('sales.delete_failed'))
            except Exception as e:
                QMessageBox.critical(self, tr('common.error'), f"Error deleting order: {str(e)}")
    
    def print_document(self):
        """طباعة أمر المبيعات"""
        if not self.current_order_id:
            QMessageBox.information(self, tr('common.info'), tr('sales.save_before_print'))
            return
        
        try:
            from PySide6.QtPrintSupport import QPrinter, QPrintDialog
            from PySide6.QtGui import QPainter, QFont
            
            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer, self)
            
            if dialog.exec() == QPrintDialog.Accepted:
                painter = QPainter(printer)
                painter.setFont(QFont("Arial", 12))
                
                y = 100
                painter.drawText(100, y, f"أمر مبيعات رقم: {self.order_no_input.text()}")
                y += 50
                painter.drawText(100, y, f"التاريخ: {self.order_date_input.date().toString('dd/MM/yyyy')}")
                y += 50
                painter.drawText(100, y, f"العميل: {self.customer_combo.currentText()}")
                y += 50
                painter.drawText(100, y, f"الإجمالي: {self.total_label.text()}")
                
                painter.end()
                QMessageBox.information(self, tr('common.success'), tr('sales.print_success'))
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error printing: {str(e)}")
    
    def convert_to_invoice(self):
        """تحويل أمر المبيعات إلى فاتورة"""
        if not self.current_order_id:
            QMessageBox.warning(self, tr('common.warning'), tr('sales.no_order_selected'))
            return
        
        reply = QMessageBox.question(
            self,
            tr('common.confirm'),
            tr('sales.confirm_convert_to_invoice'),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                invoice_data = {
                    'order_id': self.current_order_id,
                    'invoice_no': self.backend.generate_invoice_number("sales"),
                    'invoice_date': QDate.currentDate().toPython(),
                    'customer_id': self.customer_combo.currentData(),
                    'total': float(self.total_label.text()),
                    'notes': self.notes_input.toPlainText(),
                    'items': self.order_items,
                    'company_id': 1,
                    'branch_id': 1
                }
                
                if self.backend.create_sales_invoice_from_order(invoice_data):
                    QMessageBox.information(self, tr('common.success'), tr('sales.converted_to_invoice'))
                    self.refresh_data()
                else:
                    QMessageBox.critical(self, tr('common.error'), tr('sales.convert_failed'))
            except Exception as e:
                QMessageBox.critical(self, tr('common.error'), f"Error converting: {str(e)}")
    
    def refresh_data(self):
        self.orders_table.setRowCount(0)
    
    def filter_orders(self):
        """تصفية الأوامر"""
        search_text = self.search_input.text().lower()
        
        for row in range(self.orders_table.rowCount()):
            show_row = True
            
            if search_text:
                order_no = self.orders_table.item(row, 1).text().lower()
                customer = self.orders_table.item(row, 3).text().lower()
                if search_text not in order_no and search_text not in customer:
                    show_row = False
            
            self.orders_table.setRowHidden(row, not show_row)
    
    def first_document(self):
        """الأمر الأول"""
        if self.orders_table.rowCount() > 0:
            order_id = int(self.orders_table.item(0, 0).text())
            self.load_order(order_id)
    
    def last_document(self):
        """الأمر الأخير"""
        row_count = self.orders_table.rowCount()
        if row_count > 0:
            order_id = int(self.orders_table.item(row_count - 1, 0).text())
            self.load_order(order_id)
    
    def next_document(self):
        """الأمر التالي"""
        if not self.current_order_id:
            return
        
        for row in range(self.orders_table.rowCount()):
            if int(self.orders_table.item(row, 0).text()) == self.current_order_id:
                if row < self.orders_table.rowCount() - 1:
                    next_order_id = int(self.orders_table.item(row + 1, 0).text())
                    self.load_order(next_order_id)
                break
    
    def previous_document(self):
        """الأمر السابق"""
        if not self.current_order_id:
            return
        
        for row in range(self.orders_table.rowCount()):
            if int(self.orders_table.item(row, 0).text()) == self.current_order_id:
                if row > 0:
                    prev_order_id = int(self.orders_table.item(row - 1, 0).text())
                    self.load_order(prev_order_id)
                break
    
    def generate_order_number(self):
        from datetime import datetime
        return f"SO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def refresh_translations(self):
        super().refresh_translations()
        self.load_data()
