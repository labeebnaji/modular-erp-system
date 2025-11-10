from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QSpinBox, QFormLayout, QGroupBox, QHeaderView, QDoubleSpinBox
from PySide6.QtCore import QDate
from app.application.services import CashBankService, CompanyService # Added CompanyService
#from app.infrastructure.database import get_db # No longer needed
from decimal import Decimal

class CashBankWidget(QWidget):
    def __init__(self, cash_bank_service, company_service, branch_service, parent=None):
        super().__init__(parent)
        self.cash_bank_service = cash_bank_service
        self.company_service = company_service
        self.branch_service = branch_service
        self.init_ui()
        self.load_cash_bank_entries()

    def init_ui(self):
        self.setWindowTitle("Cash & Bank Management")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Cash/Bank Entry form
        form_group_box = QGroupBox("Cash/Bank Entry Details")
        form_layout = QFormLayout()

        self.company_id_input = QComboBox()
        self.load_companies_to_combobox(self.company_id_input)
        form_layout.addRow(QLabel("Company:"), self.company_id_input)

        self.branch_id_input = QComboBox()
        self.load_branches_to_combobox(self.branch_id_input, self.company_id_input.currentData())
        form_layout.addRow(QLabel("Branch:"), self.branch_id_input)

        self.account_id_input = QLineEdit()
        self.account_id_input.setPlaceholderText("Account ID (e.g., Bank, Cash)")
        # Icon placeholder: self.account_id_input.addAction(QIcon("path/to/account_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Account ID:"), self.account_id_input)

        self.transaction_type_input = QComboBox()
        self.transaction_type_input.addItems(["Deposit", "Withdrawal", "Transfer"])
        form_layout.addRow(QLabel("Transaction Type:"), self.transaction_type_input)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.00, 999999999.99)
        self.amount_input.setPrefix("$")
        # Icon placeholder: self.amount_input.addAction(QIcon("path/to/amount_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Amount:"), self.amount_input)

        self.transaction_date_input = QDateEdit(QDate.currentDate())
        self.transaction_date_input.setCalendarPopup(True)
        form_layout.addRow(QLabel("Transaction Date:"), self.transaction_date_input)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Description")
        # Icon placeholder: self.description_input.addAction(QIcon("path/to/description_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Description:"), self.description_input)

        add_button = QPushButton("Add Transaction")
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        add_button.clicked.connect(self.add_cash_bank_entry)
        form_layout.addRow(add_button)

        form_group_box.setLayout(form_layout)
        main_layout.addWidget(form_group_box)

        # Cash/Bank Entries table
        self.cash_bank_table = QTableWidget()
        self.cash_bank_table.setColumnCount(8) # Increased column count
        self.cash_bank_table.setHorizontalHeaderLabels(["ID", "Company", "Branch", "Account ID", "Type", "Amount", "Date", "Description"])
        self.cash_bank_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        main_layout.addWidget(self.cash_bank_table)

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
        branches = self.branch_service.get_all_branches()
        combobox.addItem("Select Branch", 0)
        for branch in branches:
            if branch.company_id == company_id: # Basic filtering
                combobox.addItem(f"{branch.name_en} ({branch.code})", branch.id)

    def load_cash_bank_entries(self):
        self.cash_bank_table.setRowCount(0)
        entries = self.cash_bank_service.get_all_cash_bank_entries()
        self.cash_bank_table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            company = self.company_service.get_company_by_id(entry['company_id'])
            company_name = company.name_en if company else "Unknown Company"
            branch = self.branch_service.get_branch_by_id(entry['branch_id'])
            branch_name = branch.name_en if branch else "Unknown Branch"

            self.cash_bank_table.setItem(row, 0, QTableWidgetItem(str(entry['id'])))
            self.cash_bank_table.setItem(row, 1, QTableWidgetItem(company_name))
            self.cash_bank_table.setItem(row, 2, QTableWidgetItem(branch_name))
            self.cash_bank_table.setItem(row, 3, QTableWidgetItem(str(entry['account_id'])))
            self.cash_bank_table.setItem(row, 4, QTableWidgetItem(str(entry['type'])))
            self.cash_bank_table.setItem(row, 5, QTableWidgetItem(str(entry['amount'])))
            self.cash_bank_table.setItem(row, 6, QTableWidgetItem(str(entry['date'])))
            self.cash_bank_table.setItem(row, 7, QTableWidgetItem(entry['description']))

    def add_cash_bank_entry(self):
        try:
            company_id = self.company_id_input.currentData()
            branch_id = self.branch_id_input.currentData()
            account_id = int(self.account_id_input.text()) if self.account_id_input.text() else None
            transaction_type_text = self.transaction_type_input.currentText()
            amount = Decimal(self.amount_input.value())
            transaction_date = self.transaction_date_input.date().toPython()
            description = self.description_input.text()

            if not company_id or not branch_id or not account_id or not transaction_type_text or not amount:
                QMessageBox.warning(self, "Input Error", "Company, Branch, Account ID, Transaction Type, and Amount are required.")
                return
            
            if transaction_type_text == "Deposit" or transaction_type_text == "Withdrawal":
                # Map string type to integer for service
                type_mapping = {"Deposit": 0, "Withdrawal": 1, "Transfer": 2} # Assuming 2 for transfer, need to verify model
                service_transaction_type = type_mapping.get(transaction_type_text)
                if service_transaction_type is None:
                    raise ValueError(f"Invalid transaction type: {transaction_type_text}")

                self.cash_bank_service.create_bank_transaction(
                    company_id=company_id,
                    branch_id=branch_id,
                    bank_account_id=account_id,
                    transaction_type=service_transaction_type,
                    amount=amount,
                    currency="USD", # Default currency, needs to be dynamic later
                    transaction_date=transaction_date,
                    description=description
                )
            elif transaction_type_text == "Reconciliation": # Placeholder for reconciliation, need more inputs for this
                QMessageBox.warning(self, "Input Error", "Reconciliation not fully implemented yet. Please select Deposit or Withdrawal.")
                return
            else:
                QMessageBox.warning(self, "Input Error", "Invalid transaction type selected.")
                return

            self.clear_form()
            self.load_cash_bank_entries()
            QMessageBox.information(self, "Success", "Cash/Bank entry added successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.company_id_input.setCurrentIndex(0)
        self.branch_id_input.setCurrentIndex(0)
        self.account_id_input.clear()
        self.transaction_type_input.setCurrentIndex(0)
        self.amount_input.setValue(0.0)
        self.transaction_date_input.setDate(QDate.currentDate())
        self.description_input.clear()
