from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QSpinBox
from PySide6.QtCore import QDate
from app.application.services import CashBankService, AccountService
#from app.infrastructure.database import get_db # No longer needed
from decimal import Decimal

class BankTransactionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cash_bank_service = CashBankService()
        self.account_service = AccountService()
        self.init_ui()
        self.load_bank_transactions()

    def init_ui(self):
        self.setWindowTitle("Bank Transactions")
        main_layout = QVBoxLayout()

        # Bank Transaction form
        form_layout = QHBoxLayout()
        self.account_id_input = QLineEdit()
        self.account_id_input.setPlaceholderText("Account ID")
        self.transaction_date_input = QDateEdit(calendarPopup=True)
        self.transaction_date_input.setDate(QDate.currentDate())
        self.transaction_type_input = QComboBox()
        self.transaction_type_input.addItems(["Deposit", "Withdrawal", "Transfer"])
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Description")
        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("Reference Number")

        add_button = QPushButton("Add Transaction")
        add_button.clicked.connect(self.add_bank_transaction)

        form_layout.addWidget(self.account_id_input)
        form_layout.addWidget(self.transaction_date_input)
        form_layout.addWidget(self.transaction_type_input)
        form_layout.addWidget(self.amount_input)
        form_layout.addWidget(self.description_input)
        form_layout.addWidget(self.reference_input)
        form_layout.addWidget(add_button)

        main_layout.addLayout(form_layout)

        # Bank Transaction table
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(8)
        self.transactions_table.setHorizontalHeaderLabels(["ID", "Account ID", "Transaction Date", "Type", "Amount", "Description", "Reference", "Created At"])
        main_layout.addWidget(self.transactions_table)

        self.setLayout(main_layout)

    def load_bank_transactions(self):
        self.transactions_table.setRowCount(0)
        transactions = self.cash_bank_service.get_all_bank_transactions()
        self.transactions_table.setRowCount(len(transactions))
        for row, transaction in enumerate(transactions):
            self.transactions_table.setItem(row, 0, QTableWidgetItem(str(transaction.id)))
            self.transactions_table.setItem(row, 1, QTableWidgetItem(str(transaction.account_id)))
            self.transactions_table.setItem(row, 2, QTableWidgetItem(str(transaction.transaction_date)))
            self.transactions_table.setItem(row, 3, QTableWidgetItem(transaction.transaction_type))
            self.transactions_table.setItem(row, 4, QTableWidgetItem(str(transaction.amount)))
            self.transactions_table.setItem(row, 5, QTableWidgetItem(transaction.description))
            self.transactions_table.setItem(row, 6, QTableWidgetItem(transaction.reference_number))
            self.transactions_table.setItem(row, 7, QTableWidgetItem(str(transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'))))

    def add_bank_transaction(self):
        try:
            account_id = int(self.account_id_input.text())
            transaction_date = self.transaction_date_input.date().toPythonDate()
            transaction_type = self.transaction_type_input.currentText()
            amount = float(self.amount_input.text())
            description = self.description_input.text()
            reference_number = self.reference_input.text()

            if not account_id or not amount:
                QMessageBox.warning(self, "Input Error", "Account ID and Amount are required.")
                return

            # Assuming company_id is 1 for now
            self.cash_bank_service.create_bank_transaction(
                company_id=1,
                account_id=account_id,
                transaction_date=transaction_date,
                transaction_type=transaction_type,
                amount=amount,
                description=description,
                reference_number=reference_number
            )
            self.clear_form()
            self.load_bank_transactions()
            QMessageBox.information(self, "Success", "Bank Transaction added successfully.")
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numbers for Account ID and Amount.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.account_id_input.clear()
        self.transaction_date_input.setDate(QDate.currentDate())
        self.transaction_type_input.setCurrentIndex(0)
        self.amount_input.clear()
        self.description_input.clear()
        self.reference_input.clear()
