"""
Labeeb ERP - Sales Invoices Page
صفحة فواتير المبيعات
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QPushButton, QLabel, QLineEdit,
                               QComboBox, QDateEdit, QTextEdit, QGroupBox,
                               QFormLayout, QMessageBox, QHeaderView, QSpinBox,
                               QDoubleSpinBox, QSplitter)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
from decimal import Decimal
from datetime import date

from app.ui.base_widget import TranslatableWidget
from app.i18n.translations import tr


class SalesInvoicesPage(TranslatableWidget):
    """صفحة فواتير المبيعات"""
    
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
        
        # Current invoice data
        self.current_invoice_id = None
        self.invoice_items = []
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """تهيئة الواجهة"""
        main_layout = QVBoxLayout(self)
        
        # Create splitter for two-panel layout
        splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel - Invoice Form
        left_panel = self.create_invoice_form()
        splitter.addWidget(left_panel)
        
        # Right Panel - Invoices List
        right_panel = self.create_invoices_list()
        splitter.addWidget(right_panel)
        
        # Set splitter sizes (40% form, 60% list)
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter)
    
    def create_invoice_form(self):
        """إنشاء نموذج الفاتورة"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Invoice Header Group
        header_group = QGroupBox(tr('sales.invoice_details'))
        header_layout = QFormLayout()
        
        # Invoice Number
        self.invoice_no_input = QLineEdit()
        self.invoice_no_input.setPlaceholderText(tr('sales.invoice_no'))
        self.invoice_no_input.setReadOnly(True)
        header_layout.addRow(tr('sales.invoice_no'), self.invoice_no_input)
        
        # Invoice Date
        self.invoice_date_input = QDateEdit()
        self.invoice_date_input.setDate(QDate.currentDate())
        self.invoice_date_input.setCalendarPopup(True)
        header_layout.addRow(tr('sales.invoice_date'), self.invoice_date_input)
        
        # Customer
        self.customer_combo = QComboBox()
        header_layout.addRow(tr('sales.customer'), self.customer_combo)
        
        # Branch
        self.branch_combo = QComboBox()
        header_layout.addRow(tr('common.branch'), self.branch_combo)
        
        # Payment Method
        self.payment_method_combo = QComboBox()
        header_layout.addRow(tr('common.payment_method'), self.payment_method_combo)
        
        header_group.setLayout(header_layout)
        layout.addWidget(header_group)
        
        # Invoice Items Group
        items_group = QGroupBox(tr('sales.invoice_items'))
        items_layout = QVBoxLayout()
        
        # Item selection
        item_selection_layout = QHBoxLayout()
        
        self.item_combo = QComboBox()
        self.item_combo.setMinimumWidth(200)
        item_selection_layout.addWidget(QLabel(tr('sales.item_name')))
        item_selection_layout.addWidget(self.item_combo, 1)
        
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(10000)
        self.quantity_input.setValue(1)
        item_selection_layout.addWidget(QLabel(tr('sales.quantity')))
        item_selection_layout.addWidget(self.quantity_input)
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setMinimum(0)
        self.price_input.setMaximum(999999.99)
        self.price_input.setDecimals(2)
        item_selection_layout.addWidget(QLabel(tr('sales.unit_price')))
        item_selection_layout.addWidget(self.price_input)
        
        add_item_btn = QPushButton(tr('sales.add_item'))
        add_item_btn.clicked.connect(self.add_item_to_invoice)
        item_selection_layout.addWidget(add_item_btn)
        
        items_layout.addLayout(item_selection_layout)
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(6)
        self.items_table.setHorizontalHeaderLabels([
            tr('sales.item_name'),
            tr('sales.quantity'),
            tr('sales.unit_price'),
            tr('sales.discount'),
            tr('sales.tax'),
            tr('sales.total')
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        items_layout.addWidget(self.items_table)
        
        # Remove item button
        remove_item_btn = QPushButton(tr('sales.remove_item'))
        remove_item_btn.clicked.connect(self.remove_item_from_invoice)
        items_layout.addWidget(remove_item_btn)
        
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)
        
        # Totals Group
        totals_group = QGroupBox(tr('sales.total'))
        totals_layout = QFormLayout()
        
        self.subtotal_label = QLabel("0.00")
        totals_layout.addRow(tr('sales.subtotal'), self.subtotal_label)
        
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setMinimum(0)
        self.discount_input.setMaximum(100)
        self.discount_input.setSuffix("%")
        self.discount_input.valueChanged.connect(self.calculate_totals)
        totals_layout.addRow(tr('sales.discount'), self.discount_input)
        
        self.tax_label = QLabel("0.00")
        totals_layout.addRow(tr('sales.tax'), self.tax_label)
        
        self.total_label = QLabel("0.00")
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3;")
        totals_layout.addRow(tr('sales.total'), self.total_label)
        
        totals_group.setLayout(totals_layout)
        layout.addWidget(totals_group)
        
        # Notes
        notes_group = QGroupBox(tr('sales.notes'))
        notes_layout = QVBoxLayout()
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        notes_layout.addWidget(self.notes_input)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        # Action Buttons
        buttons_layout = QHBoxLayout()
        
        self.save_btn = QPushButton(tr('common.save'))
        self.save_btn.clicked.connect(self.save_document)
        self.save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        buttons_layout.addWidget(self.save_btn)
        
        self.new_btn = QPushButton(tr('common.new'))
        self.new_btn.clicked.connect(self.new_document)
        buttons_layout.addWidget(self.new_btn)
        
        self.print_btn = QPushButton(tr('sales.print_invoice'))
        self.print_btn.clicked.connect(self.print_invoice)
        buttons_layout.addWidget(self.print_btn)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        return widget
    
    def create_invoices_list(self):
        """إنشاء قائمة الفواتير"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Search and Filter
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr('sales.search_invoices'))
        self.search_input.textChanged.connect(self.filter_invoices)
        search_layout.addWidget(self.search_input)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems([
            tr('sales.all_invoices'),
            tr('sales.paid'),
            tr('sales.unpaid'),
            tr('sales.partial')
        ])
        self.status_filter.currentIndexChanged.connect(self.filter_invoices)
        search_layout.addWidget(self.status_filter)
        
        refresh_btn = QPushButton(tr('common.refresh'))
        refresh_btn.clicked.connect(self.refresh_data)
        search_layout.addWidget(refresh_btn)
        
        layout.addLayout(search_layout)
        
        # Invoices Table
        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(7)
        self.invoices_table.setHorizontalHeaderLabels([
            tr('sales.invoice_no'),
            tr('sales.invoice_date'),
            tr('sales.customer'),
            tr('sales.total_amount'),
            tr('sales.paid_amount'),
            tr('sales.payment_status'),
            tr('common.actions')
        ])
        self.invoices_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.invoices_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.invoices_table.cellDoubleClicked.connect(self.load_invoice)
        
        layout.addWidget(self.invoices_table)
        
        return widget
    
    def load_data(self):
        """تحميل البيانات"""
        try:
            # Load customers
            self.customer_combo.clear()
            customers = self.arap_service.get_all_customers()
            for customer in customers:
                self.customer_combo.addItem(
                    customer.name_ar or customer.name_en,
                    customer.id
                )
            
            # Load branches
            self.branch_combo.clear()
            branches = self.branch_service.get_all_branches()
            for branch in branches:
                self.branch_combo.addItem(
                    branch.name_ar or branch.name_en,
                    branch.id
                )
            
            # Load payment methods
            self.payment_method_combo.clear()
            payment_methods = self.payment_method_service.get_all_payment_methods()
            for pm in payment_methods:
                self.payment_method_combo.addItem(
                    pm.name_ar or pm.name_en,
                    pm.id
                )
            
            # Load items
            self.item_combo.clear()
            items = self.inventory_service.get_all_items()
            for item in items:
                self.item_combo.addItem(
                    item.name_ar or item.name_en,
                    item.id
                )
                # Store item price as data
                if hasattr(item, 'sale_price'):
                    self.item_combo.setItemData(
                        self.item_combo.count() - 1,
                        float(item.sale_price),
                        Qt.UserRole + 1
                    )
            
            # Load invoices
            self.refresh_data()
            
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error loading data: {str(e)}")
    
    def add_item_to_invoice(self):
        """إضافة صنف للفاتورة"""
        try:
            item_id = self.item_combo.currentData()
            if not item_id:
                return
            
            item_name = self.item_combo.currentText()
            quantity = self.quantity_input.value()
            price = self.price_input.value()
            
            # Calculate line total
            line_total = quantity * price
            discount = 0
            tax = line_total * 0.15  # 15% VAT
            total = line_total - discount + tax
            
            # Add to table
            row = self.items_table.rowCount()
            self.items_table.insertRow(row)
            
            self.items_table.setItem(row, 0, QTableWidgetItem(item_name))
            self.items_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
            self.items_table.setItem(row, 2, QTableWidgetItem(f"{price:.2f}"))
            self.items_table.setItem(row, 3, QTableWidgetItem(f"{discount:.2f}"))
            self.items_table.setItem(row, 4, QTableWidgetItem(f"{tax:.2f}"))
            self.items_table.setItem(row, 5, QTableWidgetItem(f"{total:.2f}"))
            
            # Store item data
            self.invoice_items.append({
                'item_id': item_id,
                'item_name': item_name,
                'quantity': quantity,
                'price': price,
                'discount': discount,
                'tax': tax,
                'total': total
            })
            
            # Calculate totals
            self.calculate_totals()
            
            # Reset inputs
            self.quantity_input.setValue(1)
            
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error adding item: {str(e)}")
    
    def remove_item_from_invoice(self):
        """حذف صنف من الفاتورة"""
        current_row = self.items_table.currentRow()
        if current_row >= 0:
            self.items_table.removeRow(current_row)
            if current_row < len(self.invoice_items):
                self.invoice_items.pop(current_row)
            self.calculate_totals()
    
    def calculate_totals(self):
        """حساب الإجماليات"""
        subtotal = 0
        tax_total = 0
        
        for i in range(self.items_table.rowCount()):
            quantity = float(self.items_table.item(i, 1).text())
            price = float(self.items_table.item(i, 2).text())
            line_total = quantity * price
            subtotal += line_total
            
            # Calculate tax (15%)
            tax = line_total * 0.15
            tax_total += tax
        
        # Apply discount
        discount_percent = self.discount_input.value()
        discount_amount = subtotal * (discount_percent / 100)
        
        # Calculate final total
        total = subtotal - discount_amount + tax_total
        
        # Update labels
        self.subtotal_label.setText(f"{subtotal:.2f}")
        self.tax_label.setText(f"{tax_total:.2f}")
        self.total_label.setText(f"{total:.2f}")
    
    def save_document(self):
        """حفظ الفاتورة"""
        try:
            # Validate
            if not self.customer_combo.currentData():
                QMessageBox.warning(self, tr('common.warning'), "Please select a customer")
                return
            
            if self.items_table.rowCount() == 0:
                QMessageBox.warning(self, tr('common.warning'), "Please add at least one item")
                return
            
            # Prepare invoice data
            invoice_data = {
                'invoice_no': self.invoice_no_input.text() or self.generate_invoice_number(),
                'invoice_date': self.invoice_date_input.date().toPython(),
                'customer_id': self.customer_combo.currentData(),
                'branch_id': self.branch_combo.currentData(),
                'payment_method_id': self.payment_method_combo.currentData(),
                'subtotal': float(self.subtotal_label.text()),
                'discount': self.discount_input.value(),
                'tax': float(self.tax_label.text()),
                'total': float(self.total_label.text()),
                'notes': self.notes_input.toPlainText(),
                'items': self.invoice_items
            }
            
            # Save invoice (you'll need to implement this in the service)
            # self.sales_purchase_service.create_sales_invoice(invoice_data)
            
            QMessageBox.information(self, tr('common.success'), "Invoice saved successfully!")
            self.new_document()
            self.refresh_data()
            
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error saving invoice: {str(e)}")
    
    def new_document(self):
        """إنشاء فاتورة جديدة"""
        self.current_invoice_id = None
        self.invoice_no_input.clear()
        self.invoice_date_input.setDate(QDate.currentDate())
        self.customer_combo.setCurrentIndex(0)
        self.branch_combo.setCurrentIndex(0)
        self.payment_method_combo.setCurrentIndex(0)
        self.items_table.setRowCount(0)
        self.invoice_items.clear()
        self.discount_input.setValue(0)
        self.notes_input.clear()
        self.calculate_totals()
    
    def delete_document(self):
        """حذف الفاتورة"""
        if not self.current_invoice_id:
            QMessageBox.warning(self, tr('common.warning'), "No invoice selected")
            return
        
        reply = QMessageBox.question(
            self,
            tr('common.confirm'),
            "Are you sure you want to delete this invoice?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Delete invoice (implement in service)
                # self.sales_purchase_service.delete_invoice(self.current_invoice_id)
                QMessageBox.information(self, tr('common.success'), "Invoice deleted successfully!")
                self.new_document()
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, tr('common.error'), f"Error deleting invoice: {str(e)}")
    
    def refresh_data(self):
        """تحديث البيانات"""
        try:
            self.invoices_table.setRowCount(0)
            # Load invoices from database
            # invoices = self.sales_purchase_service.get_all_sales_invoices()
            # for invoice in invoices:
            #     self.add_invoice_to_table(invoice)
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error refreshing data: {str(e)}")
    
    def filter_invoices(self):
        """تصفية الفواتير"""
        search_text = self.search_input.text().lower()
        status_filter = self.status_filter.currentIndex()
        
        for row in range(self.invoices_table.rowCount()):
            show_row = True
            
            # Search filter
            if search_text:
                invoice_no = self.invoices_table.item(row, 0).text().lower()
                customer = self.invoices_table.item(row, 2).text().lower()
                if search_text not in invoice_no and search_text not in customer:
                    show_row = False
            
            # Status filter
            if status_filter > 0 and show_row:
                status = self.invoices_table.item(row, 5).text()
                if status_filter == 1 and status != tr('sales.paid'):
                    show_row = False
                elif status_filter == 2 and status != tr('sales.unpaid'):
                    show_row = False
                elif status_filter == 3 and status != tr('sales.partial'):
                    show_row = False
            
            self.invoices_table.setRowHidden(row, not show_row)
    
    def load_invoice(self, row, column):
        """تحميل فاتورة للتعديل"""
        # Implement loading invoice data
        pass
    
    def print_invoice(self):
        """طباعة الفاتورة"""
        QMessageBox.information(self, tr('common.info'), "Print functionality coming soon!")
    
    def generate_invoice_number(self):
        """توليد رقم فاتورة"""
        from datetime import datetime
        return f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def refresh_translations(self):
        """تحديث الترجمات"""
        super().refresh_translations()
        # Update all translatable elements
        self.load_data()
