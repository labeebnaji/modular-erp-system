from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QSpinBox, QFormLayout, QGroupBox, QHeaderView, QDoubleSpinBox
from PySide6.QtCore import QDate
from app.application.services import SalesPurchaseService, ARAPService, CompanyService # Added CompanyService
#from app.infrastructure.database import get_db # No longer needed
from decimal import Decimal

class PurchaseOrderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sales_purchase_service = SalesPurchaseService()
        self.arap_service = ARAPService()
        self.company_service = CompanyService() # Initialize CompanyService
        self.init_ui()
        self.load_purchase_orders()

    def init_ui(self):
        self.setWindowTitle("Purchase Orders")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Purchase Order form
        form_group_box = QGroupBox("Purchase Order Details")
        form_layout = QFormLayout()

        self.company_id_input = QComboBox()
        self.load_companies_to_combobox(self.company_id_input)
        form_layout.addRow(QLabel("Company:"), self.company_id_input)

        self.branch_id_input = QComboBox()
        self.load_branches_to_combobox(self.branch_id_input, self.company_id_input.currentData())
        form_layout.addRow(QLabel("Branch:"), self.branch_id_input)

        self.vendor_id_input = QLineEdit()
        self.vendor_id_input.setPlaceholderText("Vendor ID")
        # Icon placeholder: self.vendor_id_input.addAction(QIcon("path/to/vendor_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Vendor ID:"), self.vendor_id_input)

        self.order_no_input = QLineEdit()
        self.order_no_input.setPlaceholderText("Order No.")
        # Icon placeholder: self.order_no_input.addAction(QIcon("path/to/order_no_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Order Number:"), self.order_no_input)

        self.order_date_input = QDateEdit(QDate.currentDate())
        self.order_date_input.setCalendarPopup(True)
        form_layout.addRow(QLabel("Order Date:"), self.order_date_input)

        self.total_amount_input = QDoubleSpinBox()
        self.total_amount_input.setRange(0.00, 999999999.99)
        self.total_amount_input.setPrefix("$")
        # Icon placeholder: self.total_amount_input.addAction(QIcon("path/to/amount_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Total Amount:"), self.total_amount_input)

        self.total_tax_input = QDoubleSpinBox()
        self.total_tax_input.setRange(0.00, 999999999.99)
        self.total_tax_input.setPrefix("$")
        form_layout.addRow(QLabel("Total Tax:"), self.total_tax_input)

        self.currency_input = QLineEdit("USD")
        self.currency_input.setPlaceholderText("Currency (e.g., USD)")
        # Icon placeholder: self.currency_input.addAction(QIcon("path/to/currency_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Currency:"), self.currency_input)

        self.status_input = QComboBox()
        self.status_input.addItems(["Draft", "Confirmed", "Received", "Billed", "Cancelled"])
        form_layout.addRow(QLabel("Status:"), self.status_input)

        add_button = QPushButton("Add Purchase Order")
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        add_button.clicked.connect(self.add_purchase_order)
        form_layout.addRow(add_button)

        form_group_box.setLayout(form_layout)
        main_layout.addWidget(form_group_box)

        # Purchase Order table
        self.purchase_orders_table = QTableWidget()
        self.purchase_orders_table.setColumnCount(11) # Increased column count
        self.purchase_orders_table.setHorizontalHeaderLabels(["ID", "Company", "Branch", "Vendor ID", "Order No.", "Date", "Total Amount", "Total Tax", "Status", "Currency", "Created At"])
        self.purchase_orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        main_layout.addWidget(self.purchase_orders_table)

        main_layout.addStretch(1) # Add stretch to push content upwards and fill remaining space

        self.setLayout(main_layout)

    def load_companies_to_combobox(self, combobox):
        combobox.clear()
        companies = self.company_service.get_all_companies()
        combobox.addItem("Select Company", 0) # Default empty item
        for company in companies:
            combobox.addItem(f"{company.name_en} ({company.code})", company.id)

    def load_branches_to_combobox(self, combobox, company_id):
        combobox.clear()
        branches = self.company_service.get_all_branches() # This needs to be filtered by company_id in a real scenario
        combobox.addItem("Select Branch", 0)
        for branch in branches:
            if branch.company_id == company_id: # Basic filtering
                combobox.addItem(f"{branch.name_en} ({branch.code})", branch.id)

    def load_purchase_orders(self):
        self.purchase_orders_table.setRowCount(0)
        purchase_orders = self.sales_purchase_service.get_all_purchase_orders()
        self.purchase_orders_table.setRowCount(len(purchase_orders))
        for row, order in enumerate(purchase_orders):
            status_map = {0: "Draft", 1: "Confirmed", 2: "Received", 3: "Billed", 4: "Cancelled"}
            company = self.company_service.get_company_by_id(order.company_id)
            company_name = company.name_en if company else "Unknown Company"
            branch = self.company_service.get_branch_by_id(order.branch_id)
            branch_name = branch.name_en if branch else "Unknown Branch"

            self.purchase_orders_table.setItem(row, 0, QTableWidgetItem(str(order.id)))
            self.purchase_orders_table.setItem(row, 1, QTableWidgetItem(company_name))
            self.purchase_orders_table.setItem(row, 2, QTableWidgetItem(branch_name))
            self.purchase_orders_table.setItem(row, 3, QTableWidgetItem(str(order.vendor_id)))
            self.purchase_orders_table.setItem(row, 4, QTableWidgetItem(order.order_no))
            self.purchase_orders_table.setItem(row, 5, QTableWidgetItem(str(order.order_date)))
            self.purchase_orders_table.setItem(row, 6, QTableWidgetItem(str(order.total_amount)))
            self.purchase_orders_table.setItem(row, 7, QTableWidgetItem(str(order.total_tax)))
            self.purchase_orders_table.setItem(row, 8, QTableWidgetItem(status_map.get(order.status, "Unknown")))
            self.purchase_orders_table.setItem(row, 9, QTableWidgetItem(order.currency))
            self.purchase_orders_table.setItem(row, 10, QTableWidgetItem(str(order.created_at.strftime('%Y-%m-%d %H:%M:%S'))))

    def add_purchase_order(self):
        try:
            company_id = self.company_id_input.currentData()
            branch_id = self.branch_id_input.currentData()
            vendor_id = int(self.vendor_id_input.text()) if self.vendor_id_input.text() else None
            order_no = self.order_no_input.text()
            order_date = self.order_date_input.date().toPython()
            total_amount = Decimal(self.total_amount_input.value())
            total_tax = Decimal(self.total_tax_input.value())
            currency = self.currency_input.text()
            status = self.status_input.currentIndex()

            if not company_id or not branch_id or not vendor_id or not order_no or not total_amount or not currency:
                QMessageBox.warning(self, "Input Error", "Company, Branch, Vendor ID, Order No., Total Amount, and Currency are required.")
                return

            self.sales_purchase_service.create_purchase_order(
                company_id=company_id,
                branch_id=branch_id,
                vendor_id=vendor_id,
                order_no=order_no,
                order_date=order_date,
                total_amount=total_amount,
                total_tax=total_tax,
                currency=currency,
                status=status
            )
            self.clear_form()
            self.load_purchase_orders()
            QMessageBox.information(self, "Success", "Purchase Order added successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.company_id_input.setCurrentIndex(0)
        self.branch_id_input.setCurrentIndex(0)
        self.vendor_id_input.clear()
        self.order_no_input.clear()
        self.order_date_input.setDate(QDate.currentDate())
        self.total_amount_input.setValue(0.0)
        self.total_tax_input.setValue(0.0)
        self.currency_input.setText("USD")
        self.status_input.setCurrentIndex(0)
