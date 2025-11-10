from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QFormLayout, QGroupBox, QHeaderView, QDoubleSpinBox
from PySide6.QtCore import QDate
from app.application.services import ARAPService, CompanyService # Assuming CompanyService is needed for branch/company IDs
#from app.infrastructure.database import get_db # No longer needed
from decimal import Decimal

class InvoiceWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.arap_service = ARAPService()
        self.company_service = CompanyService() # Initialize CompanyService
        self.init_ui()
        self.load_invoices()

    def init_ui(self):
        self.setWindowTitle("Invoices")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Invoice form
        form_group_box = QGroupBox("Invoice Details")
        form_layout = QFormLayout()

        self.company_id_input = QComboBox()
        self.load_companies_to_combobox(self.company_id_input)
        form_layout.addRow(QLabel("Company:"), self.company_id_input)

        self.branch_id_input = QComboBox()
        self.load_branches_to_combobox(self.branch_id_input, self.company_id_input.currentData())
        form_layout.addRow(QLabel("Branch:"), self.branch_id_input)

        self.invoice_type_input = QComboBox()
        self.invoice_type_input.addItems(["Sales Invoice", "Purchase Invoice"])
        form_layout.addRow(QLabel("Invoice Type:"), self.invoice_type_input)

        self.customer_id_input = QLineEdit()
        self.customer_id_input.setPlaceholderText("Customer ID (for Sales Invoice)")
        form_layout.addRow(QLabel("Customer ID:"), self.customer_id_input)

        self.vendor_id_input = QLineEdit()
        self.vendor_id_input.setPlaceholderText("Vendor ID (for Purchase Invoice)")
        form_layout.addRow(QLabel("Vendor ID:"), self.vendor_id_input)

        self.invoice_no_input = QLineEdit()
        self.invoice_no_input.setPlaceholderText("Invoice No.")
        form_layout.addRow(QLabel("Invoice Number:"), self.invoice_no_input)

        self.invoice_date_input = QDateEdit(QDate.currentDate())
        self.invoice_date_input.setCalendarPopup(True)
        form_layout.addRow(QLabel("Invoice Date:"), self.invoice_date_input)

        self.due_date_input = QDateEdit(QDate.currentDate().addDays(30)) # Default 30 days due
        self.due_date_input.setCalendarPopup(True)
        form_layout.addRow(QLabel("Due Date:"), self.due_date_input)

        self.total_amount_input = QDoubleSpinBox()
        self.total_amount_input.setRange(0.00, 999999999.99)
        self.total_amount_input.setPrefix("$")
        form_layout.addRow(QLabel("Total Amount:"), self.total_amount_input)

        self.total_tax_input = QDoubleSpinBox()
        self.total_tax_input.setRange(0.00, 999999999.99)
        self.total_tax_input.setPrefix("$")
        form_layout.addRow(QLabel("Total Tax:"), self.total_tax_input)

        self.currency_input = QLineEdit("USD")
        self.currency_input.setPlaceholderText("Currency (e.g., USD)")
        form_layout.addRow(QLabel("Currency:"), self.currency_input)

        self.status_input = QComboBox()
        self.status_input.addItems(["Draft", "Issued", "Paid", "Cancelled"])
        form_layout.addRow(QLabel("Status:"), self.status_input)

        add_button = QPushButton("Add Invoice")
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        add_button.clicked.connect(self.add_invoice)
        form_layout.addRow(add_button)

        form_group_box.setLayout(form_layout)
        main_layout.addWidget(form_group_box)

        # Invoice table
        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(11) # Increased column count
        self.invoices_table.setHorizontalHeaderLabels(["ID", "Company", "Branch", "Type", "Customer/Vendor", "Invoice No.", "Date", "Due Date", "Total Amount", "Total Tax", "Status", "Currency"])
        self.invoices_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        main_layout.addWidget(self.invoices_table)

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

    def load_invoices(self):
        self.invoices_table.setRowCount(0)
        invoices = self.arap_service.get_all_invoices()
        self.invoices_table.setRowCount(len(invoices))
        for row, invoice in enumerate(invoices):
            status_map = {0: "Draft", 1: "Issued", 2: "Paid", 3: "Cancelled"}
            company = self.company_service.get_company_by_id(invoice.company_id)
            company_name = company.name_en if company else "Unknown Company"
            branch = self.company_service.get_branch_by_id(invoice.branch_id)
            branch_name = branch.name_en if branch else "Unknown Branch"
            customer_vendor_name = ""
            if invoice.invoice_type == 0 and invoice.customer_id: # Sales Invoice
                customer = self.arap_service.get_customer_by_id(invoice.customer_id)
                customer_vendor_name = customer.name_en if customer else "Unknown Customer"
            elif invoice.invoice_type == 1 and invoice.vendor_id: # Purchase Invoice
                vendor = self.arap_service.get_vendor_by_id(invoice.vendor_id)
                customer_vendor_name = vendor.name_en if vendor else "Unknown Vendor"

            self.invoices_table.setItem(row, 0, QTableWidgetItem(str(invoice.id)))
            self.invoices_table.setItem(row, 1, QTableWidgetItem(company_name))
            self.invoices_table.setItem(row, 2, QTableWidgetItem(branch_name))
            self.invoices_table.setItem(row, 3, QTableWidgetItem("Sales" if invoice.invoice_type == 0 else "Purchase"))
            self.invoices_table.setItem(row, 4, QTableWidgetItem(customer_vendor_name))
            self.invoices_table.setItem(row, 5, QTableWidgetItem(invoice.invoice_no))
            self.invoices_table.setItem(row, 6, QTableWidgetItem(str(invoice.invoice_date)))
            self.invoices_table.setItem(row, 7, QTableWidgetItem(str(invoice.due_date)))
            self.invoices_table.setItem(row, 8, QTableWidgetItem(str(invoice.total_amount)))
            self.invoices_table.setItem(row, 9, QTableWidgetItem(str(invoice.total_tax)))
            self.invoices_table.setItem(row, 10, QTableWidgetItem(status_map.get(invoice.status, "Unknown")))
            self.invoices_table.setItem(row, 11, QTableWidgetItem(invoice.currency))

    def add_invoice(self):
        try:
            company_id = self.company_id_input.currentData()
            branch_id = self.branch_id_input.currentData()
            invoice_type = self.invoice_type_input.currentIndex()
            customer_id = int(self.customer_id_input.text()) if self.customer_id_input.text() else None
            vendor_id = int(self.vendor_id_input.text()) if self.vendor_id_input.text() else None
            invoice_no = self.invoice_no_input.text()
            invoice_date = self.invoice_date_input.date().toPython()
            due_date = self.due_date_input.date().toPython()
            total_amount = Decimal(self.total_amount_input.value())
            total_tax = Decimal(self.total_tax_input.value())
            currency = self.currency_input.text()
            status = self.status_input.currentIndex()

            if not company_id or not branch_id or not invoice_no or not total_amount or not currency:
                QMessageBox.warning(self, "Input Error", "Company, Branch, Invoice No., Total Amount, and Currency are required.")
                return

            if invoice_type == 0 and not customer_id: # Sales Invoice
                QMessageBox.warning(self, "Input Error", "Customer ID is required for sales invoices.")
                return
            if invoice_type == 1 and not vendor_id: # Purchase Invoice
                QMessageBox.warning(self, "Input Error", "Vendor ID is required for purchase invoices.")
                return

            self.arap_service.create_invoice(
                company_id=company_id,
                branch_id=branch_id,
                invoice_type=invoice_type,
                customer_id=customer_id,
                vendor_id=vendor_id,
                invoice_no=invoice_no,
                invoice_date=invoice_date,
                due_date=due_date,
                total_amount=total_amount,
                total_tax=total_tax,
                currency=currency,
                status=status
            )
            self.clear_form()
            self.load_invoices()
            QMessageBox.information(self, "Success", "Invoice added successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.company_id_input.setCurrentIndex(0)
        self.branch_id_input.setCurrentIndex(0)
        self.invoice_type_input.setCurrentIndex(0)
        self.customer_id_input.clear()
        self.vendor_id_input.clear()
        self.invoice_no_input.clear()
        self.invoice_date_input.setDate(QDate.currentDate())
        self.due_date_input.setDate(QDate.currentDate().addDays(30))
        self.total_amount_input.setValue(0.0)
        self.total_tax_input.setValue(0.0)
        self.currency_input.setText("USD")
        self.status_input.setCurrentIndex(0)
