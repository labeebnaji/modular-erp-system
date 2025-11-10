"""
Labeeb ERP - Purchase Invoices Widget
واجهة فواتير المشتريات الكاملة
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QGroupBox, QFormLayout,
    QLineEdit, QDateEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QTextEdit, QSpinBox, QDoubleSpinBox,
    QMessageBox, QHeaderView, QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QColor
from decimal import Decimal
from datetime import datetime

from app.ui.base_widget import TranslatableWidget
from app.i18n.translations import tr


class PaymentDialog(QDialog):
    """نافذة إدخال طرق الدفع المتعددة"""
    
    def __init__(self, payment_methods, total_amount, parent=None):
        super().__init__(parent)
        self.payment_methods = payment_methods
        self.total_amount = total_amount
        self.payments = []
        
        self.setWindowTitle(tr('sales.payment_methods'))
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        total_label = QLabel(f"{tr('sales.total_amount')}: {self.total_amount:.2f}")
        total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3;")
        layout.addWidget(total_label)
        
        self.payment_table = QTableWidget()
        self.payment_table.setColumnCount(4)
        self.payment_table.setHorizontalHeaderLabels([
            tr('common.payment_method'),
            tr('sales.amount'),
            tr('sales.transaction_details'),
            tr('common.actions')
        ])
        self.payment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.payment_table)
        
        add_group = QGroupBox(tr('sales.add_payment'))
        add_layout = QHBoxLayout()
        
        self.payment_method_combo = QComboBox()
        for pm in self.payment_methods:
            self.payment_method_combo.addItem(pm['name'], pm['id'])
        add_layout.addWidget(QLabel(tr('common.payment_method') + ":"))
        add_layout.addWidget(self.payment_method_combo)
        
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 999999.99)
        self.amount_input.setDecimals(2)
        self.amount_input.setValue(self.total_amount)
        add_layout.addWidget(QLabel(tr('sales.amount') + ":"))
        add_layout.addWidget(self.amount_input)
        
        self.transaction_input = QLineEdit()
        self.transaction_input.setPlaceholderText(tr('sales.transaction_details'))
        add_layout.addWidget(self.transaction_input)
        
        add_btn = QPushButton(tr('common.add'))
        add_btn.clicked.connect(self.add_payment)
        add_layout.addWidget(add_btn)
        
        add_group.setLayout(add_layout)
        layout.addWidget(add_group)
        
        self.remaining_label = QLabel(f"{tr('sales.remaining')}: {self.total_amount:.2f}")
        self.remaining_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.remaining_label)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def add_payment(self):
        payment_method_id = self.payment_method_combo.currentData()
        payment_method_name = self.payment_method_combo.currentText()
        amount = self.amount_input.value()
        transaction_details = self.transaction_input.text()
        
        if amount <= 0:
            QMessageBox.warning(self, tr('common.warning'), tr('sales.invalid_amount'))
            return
        
        row = self.payment_table.rowCount()
        self.payment_table.insertRow(row)
        
        self.payment_table.setItem(row, 0, QTableWidgetItem(payment_method_name))
        self.payment_table.setItem(row, 1, QTableWidgetItem(f"{amount:.2f}"))
        self.payment_table.setItem(row, 2, QTableWidgetItem(transaction_details))
        
        remove_btn = QPushButton(tr('common.delete'))
        remove_btn.clicked.connect(lambda: self.remove_payment(row))
        self.payment_table.setCellWidget(row, 3, remove_btn)
        
        self.payments.append({
            'payment_method_id': payment_method_id,
            'payment_method_name': payment_method_name,
            'amount': amount,
            'transaction_details': transaction_details
        })
        
        self.update_remaining()
        self.amount_input.setValue(0)
        self.transaction_input.clear()
    
    def remove_payment(self, row):
        if row < len(self.payments):
            self.payments.pop(row)
            self.payment_table.removeRow(row)
            self.update_remaining()
    
    def update_remaining(self):
        total_paid = sum(p['amount'] for p in self.payments)
        remaining = self.total_amount - total_paid
        self.remaining_label.setText(f"{tr('sales.remaining')}: {remaining:.2f}")
        
        if remaining < 0:
            self.remaining_label.setStyleSheet("font-size: 14px; font-weight: bold; color: red;")
        elif remaining > 0:
            self.remaining_label.setStyleSheet("font-size: 14px; font-weight: bold; color: orange;")
        else:
            self.remaining_label.setStyleSheet("font-size: 14px; font-weight: bold; color: green;")
    
    def get_payments(self):
        return self.payments


class PurchaseInvoicesWidget(TranslatableWidget):
    """واجهة فواتير المشتريات الكاملة"""
    
    def __init__(self, backend, arap_service, inventory_service, unit_service,
                 payment_method_service, branch_service, company_service,
                 currency_service, warehouse_service, parent=None):
        super().__init__(parent)
        
        self.backend = backend
        self.arap_service = arap_service
        self.inventory_service = inventory_service
        self.unit_service = unit_service
        self.payment_method_service = payment_method_service
        self.branch_service = branch_service
        self.company_service = company_service
        self.currency_service = currency_service
        self.warehouse_service = warehouse_service
        
        self.current_invoice_id = None
        self.invoice_items = []
        self.all_invoices = []
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_panel = self.create_invoice_form()
        splitter.addWidget(left_panel)
        
        right_panel = self.create_invoices_list()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter)
    
    def create_invoice_form(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        header_group = QGroupBox(tr('sales.invoice_details'))
        header_layout = QFormLayout()
        
        self.invoice_no_input = QLineEdit()
        self.invoice_no_input.setPlaceholderText(tr('sales.invoice_no'))
        self.invoice_no_input.setReadOnly(True)
        header_layout.addRow(tr('sales.invoice_no') + ":", self.invoice_no_input)
        
        self.invoice_date_input = QDateEdit()
        self.invoice_date_input.setDate(QDate.currentDate())
        self.invoice_date_input.setCalendarPopup(True)
        header_layout.addRow(tr('sales.invoice_date') + ":", self.invoice_date_input)
        
        self.supplier_combo = QComboBox()
        self.supplier_combo.setEditable(True)
        header_layout.addRow(tr('sales.supplier') + ":", self.supplier_combo)
        
        self.branch_combo = QComboBox()
        header_layout.addRow(tr('common.branch') + ":", self.branch_combo)
        
        self.warehouse_combo = QComboBox()
        header_layout.addRow(tr('inventory.warehouse') + ":", self.warehouse_combo)
        
        self.currency_combo = QComboBox()
        header_layout.addRow(tr('common.currency') + ":", self.currency_combo)
        
        header_group.setLayout(header_layout)
        layout.addWidget(header_group)
        
        items_group = QGroupBox(tr('sales.invoice_items'))
        items_layout = QVBoxLayout()
        
        item_selection_layout = QHBoxLayout()
        
        self.item_combo = QComboBox()
        self.item_combo.setEditable(True)
        self.item_combo.setMinimumWidth(200)
        self.item_combo.currentIndexChanged.connect(self.on_item_selected)
        item_selection_layout.addWidget(QLabel(tr('sales.item_name') + ":"))
        item_selection_layout.addWidget(self.item_combo, 1)
        
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setMinimum(0.01)
        self.quantity_input.setMaximum(999999.99)
        self.quantity_input.setDecimals(2)
        self.quantity_input.setValue(1)
        self.quantity_input.valueChanged.connect(self.calculate_line_total)
        item_selection_layout.addWidget(QLabel(tr('sales.quantity') + ":"))
        item_selection_layout.addWidget(self.quantity_input)
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setMinimum(0)
        self.price_input.setMaximum(999999.99)
        self.price_input.setDecimals(2)
        self.price_input.valueChanged.connect(self.calculate_line_total)
        item_selection_layout.addWidget(QLabel(tr('sales.unit_price') + ":"))
        item_selection_layout.addWidget(self.price_input)
        
        self.line_discount_input = QDoubleSpinBox()
        self.line_discount_input.setMinimum(0)
        self.line_discount_input.setMaximum(100)
        self.line_discount_input.setDecimals(2)
        self.line_discount_input.setSuffix("%")
        self.line_discount_input.valueChanged.connect(self.calculate_line_total)
        item_selection_layout.addWidget(QLabel(tr('sales.discount') + ":"))
        item_selection_layout.addWidget(self.line_discount_input)
        
        self.line_total_label = QLabel("0.00")
        self.line_total_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        item_selection_layout.addWidget(QLabel(tr('sales.total') + ":"))
        item_selection_layout.addWidget(self.line_total_label)
        
        add_item_btn = QPushButton(tr('sales.add_item'))
        add_item_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        add_item_btn.clicked.connect(self.add_item_to_invoice)
        item_selection_layout.addWidget(add_item_btn)
        
        items_layout.addLayout(item_selection_layout)
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(7)
        self.items_table.setHorizontalHeaderLabels([
            tr('sales.item_name'),
            tr('sales.quantity'),
            tr('sales.unit_price'),
            tr('sales.discount'),
            tr('sales.tax'),
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
        
        self.subtotal_label = QLabel("0.00")
        totals_layout.addRow(tr('sales.subtotal') + ":", self.subtotal_label)
        
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setMinimum(0)
        self.discount_input.setMaximum(100)
        self.discount_input.setDecimals(2)
        self.discount_input.setSuffix("%")
        self.discount_input.valueChanged.connect(self.calculate_totals)
        totals_layout.addRow(tr('sales.discount') + ":", self.discount_input)
        
        self.charges_input = QDoubleSpinBox()
        self.charges_input.setMinimum(0)
        self.charges_input.setMaximum(999999.99)
        self.charges_input.setDecimals(2)
        self.charges_input.valueChanged.connect(self.calculate_totals)
        totals_layout.addRow(tr('sales.charges') + ":", self.charges_input)
        
        self.tax_label = QLabel("0.00")
        totals_layout.addRow(tr('sales.tax') + ":", self.tax_label)
        
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
        
        self.print_btn = QPushButton(tr('sales.print_invoice'))
        self.print_btn.clicked.connect(self.print_document)
        self.print_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 10px;")
        buttons_layout.addWidget(self.print_btn)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        return widget
    
    def create_invoices_list(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
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
        
        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(8)
        self.invoices_table.setHorizontalHeaderLabels([
            "ID",
            tr('sales.invoice_no'),
            tr('sales.invoice_date'),
            tr('sales.supplier'),
            tr('sales.total_amount'),
            tr('sales.paid_amount'),
            tr('sales.payment_status'),
            tr('common.actions')
        ])
        self.invoices_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.invoices_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.invoices_table.setAlternatingRowColors(True)
        self.invoices_table.cellDoubleClicked.connect(self.load_invoice_from_table)
        
        layout.addWidget(self.invoices_table)
        
        return widget
    
    def load_data(self):
        try:
            self.supplier_combo.clear()
            self.supplier_combo.addItem(tr('sales.cash_supplier'), None)
            suppliers = self.arap_service.get_all_suppliers()
            for supplier in suppliers:
                self.supplier_combo.addItem(
                    supplier.name_ar or supplier.name_en,
                    supplier.id
                )
            
            self.branch_combo.clear()
            branches = self.branch_service.get_all_branches()
            for branch in branches:
                self.branch_combo.addItem(
                    branch.name_ar or branch.name_en,
                    branch.id
                )
            
            self.warehouse_combo.clear()
            warehouses = self.warehouse_service.get_all_warehouses(company_id=1)
            for warehouse in warehouses:
                self.warehouse_combo.addItem(
                    warehouse.name_ar or warehouse.name_en,
                    warehouse.id
                )
            
            self.currency_combo.clear()
            currencies = self.currency_service.get_all_currencies()
            for currency in currencies:
                self.currency_combo.addItem(
                    f"{currency.name_ar} ({currency.code})",
                    currency.id
                )
            
            self.item_combo.clear()
            items = self.inventory_service.get_all_items()
            for item in items:
                self.item_combo.addItem(
                    f"{item.name_ar} - {item.code}",
                    item.id
                )
            
            self.refresh_data()
            self.invoice_no_input.setText(self.generate_invoice_number())
            
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error loading data: {str(e)}")
    
    def on_item_selected(self):
        item_id = self.item_combo.currentData()
        if item_id:
            try:
                item = self.inventory_service.get_item_by_id(item_id)
                if item:
                    self.price_input.setValue(float(item.cost_price))
                    self.calculate_line_total()
            except Exception as e:
                print(f"Error loading item: {e}")
    
    def calculate_line_total(self):
        quantity = self.quantity_input.value()
        price = self.price_input.value()
        discount = self.line_discount_input.value()
        
        subtotal = quantity * price
        discount_amount = subtotal * (discount / 100)
        total = subtotal - discount_amount
        
        self.line_total_label.setText(f"{total:.2f}")
    
    def add_item_to_invoice(self):
        try:
            item_id = self.item_combo.currentData()
            if not item_id:
                QMessageBox.warning(self, tr('common.warning'), tr('sales.select_item'))
                return
            
            item_name = self.item_combo.currentText()
            quantity = self.quantity_input.value()
            price = self.price_input.value()
            discount = self.line_discount_input.value()
            
            subtotal = quantity * price
            discount_amount = subtotal * (discount / 100)
            line_total = subtotal - discount_amount
            tax = line_total * 0.15
            total = line_total + tax
            
            row = self.items_table.rowCount()
            self.items_table.insertRow(row)
            
            self.items_table.setItem(row, 0, QTableWidgetItem(item_name))
            self.items_table.setItem(row, 1, QTableWidgetItem(f"{quantity:.2f}"))
            self.items_table.setItem(row, 2, QTableWidgetItem(f"{price:.2f}"))
            self.items_table.setItem(row, 3, QTableWidgetItem(f"{discount:.2f}%"))
            self.items_table.setItem(row, 4, QTableWidgetItem(f"{tax:.2f}"))
            self.items_table.setItem(row, 5, QTableWidgetItem(f"{total:.2f}"))
            
            remove_btn = QPushButton(tr('common.delete'))
            remove_btn.setStyleSheet("background-color: #f44336; color: white;")
            remove_btn.clicked.connect(lambda: self.remove_item_from_invoice(row))
            self.items_table.setCellWidget(row, 6, remove_btn)
            
            self.invoice_items.append({
                'item_id': item_id,
                'item_name': item_name,
                'quantity': quantity,
                'price': price,
                'discount': discount,
                'tax': tax,
                'total': total
            })
            
            self.calculate_totals()
            
            self.quantity_input.setValue(1)
            self.line_discount_input.setValue(0)
            self.item_combo.setCurrentIndex(0)
            
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error adding item: {str(e)}")
    
    def remove_item_from_invoice(self, row):
        if row < len(self.invoice_items):
            self.invoice_items.pop(row)
            self.items_table.removeRow(row)
            self.calculate_totals()
    
    def calculate_totals(self):
        subtotal = sum(item['total'] - item['tax'] for item in self.invoice_items)
        
        discount_percent = self.discount_input.value()
        discount_amount = subtotal * (discount_percent / 100)
        
        charges = self.charges_input.value()
        
        tax_total = sum(item['tax'] for item in self.invoice_items)
        
        total = subtotal - discount_amount + charges + tax_total
        
        self.subtotal_label.setText(f"{subtotal:.2f}")
        self.tax_label.setText(f"{tax_total:.2f}")
        self.total_label.setText(f"{total:.2f}")
    
    def save_document(self):
        try:
            if not self.supplier_combo.currentData() and self.supplier_combo.currentIndex() != 0:
                QMessageBox.warning(self, tr('common.warning'), tr('sales.select_supplier'))
                return
            
            if len(self.invoice_items) == 0:
                QMessageBox.warning(self, tr('common.warning'), tr('sales.add_items'))
                return
            
            payment_methods = []
            for pm in self.payment_method_service.get_all_payment_methods():
                payment_methods.append({
                    'id': pm.id,
                    'name': pm.name_ar or pm.name_en
                })
            
            total_amount = float(self.total_label.text())
            payment_dialog = PaymentDialog(payment_methods, total_amount, self)
            
            if payment_dialog.exec() == QDialog.Accepted:
                payments = payment_dialog.get_payments()
                
                if not payments:
                    QMessageBox.warning(self, tr('common.warning'), tr('sales.add_payment'))
                    return
                
                invoice_data = {
                    'invoice_no': self.invoice_no_input.text(),
                    'invoice_date': self.invoice_date_input.date().toPython(),
                    'supplier_id': self.supplier_combo.currentData(),
                    'branch_id': self.branch_combo.currentData(),
                    'warehouse_id': self.warehouse_combo.currentData(),
                    'currency': self.currency_combo.currentText().split('(')[1].rstrip(')'),
                    'subtotal': float(self.subtotal_label.text()),
                    'discount': self.discount_input.value(),
                    'charges': self.charges_input.value(),
                    'tax': float(self.tax_label.text()),
                    'total': total_amount,
                    'notes': self.notes_input.toPlainText(),
                    'items': self.invoice_items,
                    'payments': payments,
                    'company_id': 1,
                    'user_id': 1
                }
                
                if self.backend.create_purchase_invoice(invoice_data):
                    QMessageBox.information(self, tr('common.success'), tr('sales.invoice_saved'))
                    self.new_document()
                    self.refresh_data()
                else:
                    QMessageBox.critical(self, tr('common.error'), tr('sales.save_failed'))
            
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error saving invoice: {str(e)}")
    
    def new_document(self):
        self.current_invoice_id = None
        self.invoice_no_input.setText(self.generate_invoice_number())
        self.invoice_date_input.setDate(QDate.currentDate())
        self.supplier_combo.setCurrentIndex(0)
        self.branch_combo.setCurrentIndex(0)
        self.warehouse_combo.setCurrentIndex(0)
        self.currency_combo.setCurrentIndex(0)
        self.items_table.setRowCount(0)
        self.invoice_items.clear()
        self.discount_input.setValue(0)
        self.charges_input.setValue(0)
        self.notes_input.clear()
        self.calculate_totals()
    
    def delete_document(self):
        if not self.current_invoice_id:
            QMessageBox.warning(self, tr('common.warning'), tr('sales.no_invoice_selected'))
            return
        
        reply = QMessageBox.question(
            self,
            tr('common.confirm'),
            tr('sales.confirm_delete'),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.backend.delete_sales_invoice(self.current_invoice_id):
                    QMessageBox.information(self, tr('common.success'), tr('sales.invoice_deleted'))
                    self.new_document()
                    self.refresh_data()
                else:
                    QMessageBox.critical(self, tr('common.error'), tr('sales.delete_failed'))
            except Exception as e:
                QMessageBox.critical(self, tr('common.error'), f"Error deleting invoice: {str(e)}")
    
    def print_document(self):
        if not self.current_invoice_id:
            QMessageBox.information(self, tr('common.info'), tr('sales.save_before_print'))
            return
        
        QMessageBox.information(self, tr('common.info'), tr('sales.print_coming_soon'))
    
    def refresh_data(self):
        try:
            self.invoices_table.setRowCount(0)
            self.all_invoices = self.backend.get_all_purchase_invoices()
            
            for invoice in self.all_invoices:
                row = self.invoices_table.rowCount()
                self.invoices_table.insertRow(row)
                
                self.invoices_table.setItem(row, 0, QTableWidgetItem(str(invoice['id'])))
                self.invoices_table.setItem(row, 1, QTableWidgetItem(invoice['invoice_no']))
                self.invoices_table.setItem(row, 2, QTableWidgetItem(invoice['invoice_date']))
                self.invoices_table.setItem(row, 3, QTableWidgetItem(invoice['customer_name']))
                self.invoices_table.setItem(row, 4, QTableWidgetItem(f"{invoice['total']:.2f}"))
                
                paid_amount = sum(p['amount'] for p in invoice.get('payments', []))
                self.invoices_table.setItem(row, 5, QTableWidgetItem(f"{paid_amount:.2f}"))
                
                if paid_amount >= invoice['total']:
                    status = tr('sales.paid')
                    color = QColor(144, 238, 144)
                elif paid_amount > 0:
                    status = tr('sales.partial')
                    color = QColor(255, 215, 0)
                else:
                    status = tr('sales.unpaid')
                    color = QColor(255, 107, 107)
                
                status_item = QTableWidgetItem(status)
                status_item.setBackground(color)
                self.invoices_table.setItem(row, 6, status_item)
                
                view_btn = QPushButton(tr('common.view'))
                view_btn.clicked.connect(lambda checked, inv_id=invoice['id']: self.load_invoice(inv_id))
                self.invoices_table.setCellWidget(row, 7, view_btn)
            
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error refreshing data: {str(e)}")
    
    def filter_invoices(self):
        search_text = self.search_input.text().lower()
        status_filter = self.status_filter.currentIndex()
        
        for row in range(self.invoices_table.rowCount()):
            show_row = True
            
            if search_text:
                invoice_no = self.invoices_table.item(row, 1).text().lower()
                supplier = self.invoices_table.item(row, 3).text().lower()
                if search_text not in invoice_no and search_text not in supplier:
                    show_row = False
            
            if status_filter > 0 and show_row:
                status = self.invoices_table.item(row, 6).text()
                if status_filter == 1 and status != tr('sales.paid'):
                    show_row = False
                elif status_filter == 2 and status != tr('sales.unpaid'):
                    show_row = False
                elif status_filter == 3 and status != tr('sales.partial'):
                    show_row = False
            
            self.invoices_table.setRowHidden(row, not show_row)
    
    def load_invoice_from_table(self, row, column):
        invoice_id = int(self.invoices_table.item(row, 0).text())
        self.load_invoice(invoice_id)
    
    def load_invoice(self, invoice_id):
        QMessageBox.information(self, tr('common.info'), "Load invoice functionality coming soon")
    
    def first_document(self):
        if self.all_invoices:
            self.load_invoice(self.all_invoices[0]['id'])
    
    def last_document(self):
        if self.all_invoices:
            self.load_invoice(self.all_invoices[-1]['id'])
    
    def next_document(self):
        """الفاتورة التالية"""
        if not self.current_invoice_id or not self.all_invoices:
            return
        
        current_index = next((i for i, inv in enumerate(self.all_invoices) if inv['id'] == self.current_invoice_id), -1)
        if current_index >= 0 and current_index < len(self.all_invoices) - 1:
            self.load_invoice(self.all_invoices[current_index + 1]['id'])
    
    def previous_document(self):
        """الفاتورة السابقة"""
        if not self.current_invoice_id or not self.all_invoices:
            return
        
        current_index = next((i for i, inv in enumerate(self.all_invoices) if inv['id'] == self.current_invoice_id), -1)
        if current_index > 0:
            self.load_invoice(self.all_invoices[current_index - 1]['id'])
    
    def generate_invoice_number(self):
        return self.backend.generate_invoice_number("purchase")
    
    def refresh_translations(self):
        super().refresh_translations()
        self.load_data()
