from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QFormLayout, QGroupBox, QHeaderView, QDoubleSpinBox
from PySide6.QtCore import QDate
from app.application.services import ARAPService, CompanyService # Assuming CompanyService is needed for branch/company IDs
#from app.infrastructure.database import get_db # No longer needed
from decimal import Decimal

class PaymentWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.arap_service = ARAPService()
        self.company_service = CompanyService() # Initialize CompanyService
        self.init_ui()
        self.load_payments()

    def init_ui(self):
        self.setWindowTitle("Payments")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Payment form
        form_group_box = QGroupBox("Payment Details")
        form_layout = QFormLayout()

        self.company_id_input = QComboBox()
        self.load_companies_to_combobox(self.company_id_input)
        form_layout.addRow(QLabel("Company:"), self.company_id_input)

        self.branch_id_input = QComboBox()
        self.load_branches_to_combobox(self.branch_id_input, self.company_id_input.currentData())
        form_layout.addRow(QLabel("Branch:"), self.branch_id_input)

        self.invoice_id_input = QLineEdit()
        self.invoice_id_input.setPlaceholderText("Invoice ID (if applicable)")
        # Icon placeholder: self.invoice_id_input.addAction(QIcon("path/to/invoice_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Invoice ID:"), self.invoice_id_input)

        self.payment_date_input = QDateEdit(QDate.currentDate())
        self.payment_date_input.setCalendarPopup(True)
        form_layout.addRow(QLabel("Payment Date:"), self.payment_date_input)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.00, 999999999.99)
        self.amount_input.setPrefix("$")
        # Icon placeholder: self.amount_input.addAction(QIcon("path/to/amount_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Amount:"), self.amount_input)

        self.payment_method_input = QComboBox()
        self.payment_method_input.addItems(["Cash", "Bank Transfer", "Credit Card", "Check"])
        form_layout.addRow(QLabel("Payment Method:"), self.payment_method_input)

        self.currency_input = QLineEdit("USD")
        self.currency_input.setPlaceholderText("Currency (e.g., USD)")
        form_layout.addRow(QLabel("Currency:"), self.currency_input)

        self.reference_number_input = QLineEdit()
        self.reference_number_input.setPlaceholderText("Reference Number")
        # Icon placeholder: self.reference_number_input.addAction(QIcon("path/to/ref_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Reference Number:"), self.reference_number_input)

        add_button = QPushButton("Add Payment")
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        add_button.clicked.connect(self.add_payment)
        form_layout.addRow(add_button)

        form_group_box.setLayout(form_layout)
        main_layout.addWidget(form_group_box)

        # Payment table
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(9) # Increased column count
        self.payments_table.setHorizontalHeaderLabels(["ID", "Company", "Branch", "Invoice ID", "Payment Date", "Amount", "Method", "Reference", "Created At"])
        self.payments_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        main_layout.addWidget(self.payments_table)

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

    def load_payments(self):
        self.payments_table.setRowCount(0)
        payments = self.arap_service.get_all_payments()
        self.payments_table.setRowCount(len(payments))
        for row, payment in enumerate(payments):
            company = self.company_service.get_company_by_id(payment.company_id)
            company_name = company.name_en if company else "Unknown Company"
            branch = self.company_service.get_branch_by_id(payment.branch_id)
            branch_name = branch.name_en if branch else "Unknown Branch"

            self.payments_table.setItem(row, 0, QTableWidgetItem(str(payment.id)))
            self.payments_table.setItem(row, 1, QTableWidgetItem(company_name))
            self.payments_table.setItem(row, 2, QTableWidgetItem(branch_name))
            self.payments_table.setItem(row, 3, QTableWidgetItem(str(payment.invoice_id) if payment.invoice_id else ""))
            self.payments_table.setItem(row, 4, QTableWidgetItem(str(payment.payment_date)))
            self.payments_table.setItem(row, 5, QTableWidgetItem(str(payment.amount)))
            self.payments_table.setItem(row, 6, QTableWidgetItem(payment.payment_method))
            self.payments_table.setItem(row, 7, QTableWidgetItem(payment.ref_no if payment.ref_no else "N/A"))
            self.payments_table.setItem(row, 8, QTableWidgetItem(str(payment.created_at.strftime('%Y-%m-%d %H:%M:%S'))))

    def add_payment(self):
        try:
            company_id = self.company_id_input.currentData()
            branch_id = self.branch_id_input.currentData()
            invoice_id = int(self.invoice_id_input.text()) if self.invoice_id_input.text() else None
            payment_date = self.payment_date_input.date().toPython()
            amount = Decimal(self.amount_input.value())
            payment_method = self.payment_method_input.currentText()
            currency = self.currency_input.text() # Assuming currency input is added
            ref_no = self.reference_number_input.text()

            if not company_id or not branch_id or not amount or not currency:
                QMessageBox.warning(self, "Input Error", "Company, Branch, Amount, and Currency are required.")
                return

            self.arap_service.record_payment(
                company_id=company_id,
                branch_id=branch_id,
                invoice_id=invoice_id,
                payment_date=payment_date,
                amount=amount,
                currency=currency,
                payment_method=payment_method,
                ref_no=ref_no
            )
            self.clear_form()
            self.load_payments()
            QMessageBox.information(self, "Success", "Payment added successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.company_id_input.setCurrentIndex(0)
        self.branch_id_input.setCurrentIndex(0)
        self.invoice_id_input.clear()
        self.payment_date_input.setDate(QDate.currentDate())
        self.amount_input.setValue(0.0)
        self.payment_method_input.setCurrentIndex(0)
        self.currency_input.setText("USD") # Reset currency
        self.reference_number_input.clear()
