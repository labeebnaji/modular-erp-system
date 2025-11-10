from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QSpinBox, QCheckBox, QComboBox
from PySide6.QtCore import QDate
from app.application.services import CashBankService, AccountService
#from app.infrastructure.database import get_db # No longer needed
from decimal import Decimal

class BankReconciliationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cash_bank_service = CashBankService()
        self.account_service = AccountService()
        self.init_ui()
        self.load_bank_reconciliations()

    def init_ui(self):
        self.setWindowTitle("Bank Reconciliations")
        main_layout = QVBoxLayout()

        # Bank Reconciliation form
        form_layout = QHBoxLayout()
        self.bank_account_id_input = QLineEdit()
        self.bank_account_id_input.setPlaceholderText("Bank Account ID")
        self.reconciliation_date_input = QDateEdit(calendarPopup=True)
        self.reconciliation_date_input.setDate(QDate.currentDate())
        self.statement_balance_input = QLineEdit()
        self.statement_balance_input.setPlaceholderText("Statement Balance")

        add_button = QPushButton("Add Reconciliation")
        add_button.clicked.connect(self.add_bank_reconciliation)

        form_layout.addWidget(self.bank_account_id_input)
        form_layout.addWidget(self.reconciliation_date_input)
        form_layout.addWidget(self.statement_balance_input)
        form_layout.addWidget(add_button)

        main_layout.addLayout(form_layout)

        # Bank Reconciliation table
        self.reconciliations_table = QTableWidget()
        self.reconciliations_table.setColumnCount(5)
        self.reconciliations_table.setHorizontalHeaderLabels(["ID", "Bank Account ID", "Reconciliation Date", "Statement Balance", "Created At"])
        main_layout.addWidget(self.reconciliations_table)

        self.setLayout(main_layout)

    def load_bank_reconciliations(self):
        self.reconciliations_table.setRowCount(0)
        reconciliations = self.cash_bank_service.get_all_bank_reconciliations()
        self.reconciliations_table.setRowCount(len(reconciliations))
        for row, recon in enumerate(reconciliations):
            self.reconciliations_table.setItem(row, 0, QTableWidgetItem(str(recon.id)))
            self.reconciliations_table.setItem(row, 1, QTableWidgetItem(str(recon.bank_account_id)))
            self.reconciliations_table.setItem(row, 2, QTableWidgetItem(str(recon.reconciliation_date)))
            self.reconciliations_table.setItem(row, 3, QTableWidgetItem(str(recon.statement_balance)))
            self.reconciliations_table.setItem(row, 4, QTableWidgetItem(str(recon.created_at.strftime('%Y-%m-%d %H:%M:%S'))))

    def add_bank_reconciliation(self):
        try:
            bank_account_id = int(self.bank_account_id_input.text())
            reconciliation_date = self.reconciliation_date_input.date().toPythonDate()
            statement_balance = float(self.statement_balance_input.text())

            if not bank_account_id or not statement_balance:
                QMessageBox.warning(self, "Input Error", "Bank Account ID and Statement Balance are required.")
                return

            # Assuming company_id is 1 for now
            self.cash_bank_service.create_bank_reconciliation(
                company_id=1,
                bank_account_id=bank_account_id,
                reconciliation_date=reconciliation_date,
                statement_balance=statement_balance
            )
            self.clear_form()
            self.load_bank_reconciliations()
            QMessageBox.information(self, "Success", "Bank Reconciliation added successfully.")
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numbers for Bank Account ID and Statement Balance.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.bank_account_id_input.clear()
        self.reconciliation_date_input.setDate(QDate.currentDate())
        self.statement_balance_input.clear()
