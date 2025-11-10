from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QFormLayout, QGroupBox, QHeaderView
from PySide6.QtCore import QDate
from PySide6.QtGui import QFont, QColor
from app.application.services import AccountService, CompanyService, JournalService, BranchService
from app.ui.styles import BUTTON_STYLE, TABLE_STYLE, GROUPBOX_STYLE
from app.i18n.translations import tr
from decimal import Decimal

class TrialBalanceWidget(QWidget):
    def __init__(self, account_service, journal_service, company_service, branch_service, parent=None):
        super().__init__(parent)
        self.account_service = account_service
        self.journal_service = journal_service
        self.company_service = company_service
        self.branch_service = branch_service
        self.init_ui()
        self.load_trial_balance()

    def init_ui(self):
        self.setWindowTitle("Trial Balance Report")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Report Filters form
        filter_group_box = QGroupBox("Report Filters")
        filter_layout = QFormLayout()

        self.company_id_input = QComboBox()
        self.load_companies_to_combobox(self.company_id_input)
        filter_layout.addRow(QLabel("Company:"), self.company_id_input)

        self.branch_id_input = QComboBox()
        self.load_branches_to_combobox(self.branch_id_input, self.company_id_input.currentData())
        filter_layout.addRow(QLabel("Branch:"), self.branch_id_input)

        self.end_date_input = QDateEdit(QDate.currentDate())
        self.end_date_input.setCalendarPopup(True)
        filter_layout.addRow(QLabel("As of Date:"), self.end_date_input)

        generate_button = QPushButton("Generate Report")
        generate_button.setStyleSheet(BUTTON_STYLE)
        generate_button.clicked.connect(self.load_trial_balance)
        filter_layout.addRow(generate_button)

        filter_group_box.setLayout(filter_layout)
        filter_group_box.setStyleSheet(GROUPBOX_STYLE)
        main_layout.addWidget(filter_group_box)

        # Trial Balance table
        self.trial_balance_table = QTableWidget()
        self.trial_balance_table.setColumnCount(4)
        self.trial_balance_table.setHorizontalHeaderLabels(["Account Code", "Account Name", "Debit", "Credit"])
        self.trial_balance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.trial_balance_table.setStyleSheet(TABLE_STYLE)
        self.trial_balance_table.setAlternatingRowColors(True)
        main_layout.addWidget(self.trial_balance_table)

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
        branches = self.company_service.get_all_branches()
        combobox.addItem("Select Branch", 0)
        for branch in branches:
            if branch.company_id == company_id: # Basic filtering
                combobox.addItem(f"{branch.name_en} ({branch.code})", branch.id)

    def load_trial_balance(self):
        """Generate trial balance with full logic"""
        company_id = self.company_id_input.currentData()
        branch_id = self.branch_id_input.currentData()
        as_of_date = self.end_date_input.date().toPython()
        
        if not company_id:
            QMessageBox.warning(self, tr('common.warning'), "Please select a company")
            return
        
        self.trial_balance_table.setRowCount(0)
        
        # Get all accounts
        accounts = self.account_service.get_all_accounts()
        
        # Calculate balances
        account_balances = []
        total_debits = Decimal('0.00')
        total_credits = Decimal('0.00')
        
        for account in accounts:
            balance = self.calculate_account_balance(account.id, as_of_date, company_id, branch_id)
            
            if balance == 0:
                continue
            
            # Determine debit/credit based on account type and balance
            debit_amount = Decimal('0.00')
            credit_amount = Decimal('0.00')
            
            if account.type in [0, 4]:  # Assets and Expenses - normal debit balance
                if balance >= 0:
                    debit_amount = balance
                else:
                    credit_amount = abs(balance)
            else:  # Liabilities, Equity, Revenue - normal credit balance
                if balance >= 0:
                    credit_amount = balance
                else:
                    debit_amount = abs(balance)
            
            account_balances.append({
                'account': account,
                'debit': debit_amount,
                'credit': credit_amount
            })
            
            total_debits += debit_amount
            total_credits += credit_amount
        
        # Display trial balance
        self.display_trial_balance(account_balances, total_debits, total_credits)
    
    def calculate_account_balance(self, account_id, as_of_date, company_id, branch_id):
        """Calculate account balance up to a specific date"""
        all_entries = self.journal_service.get_all_journal_entries()
        balance = Decimal('0.00')
        
        for entry in all_entries:
            if entry.date > as_of_date:
                continue
            if entry.company_id != company_id:
                continue
            if branch_id and entry.branch_id != branch_id:
                continue
            if entry.status != 2:  # Only posted entries
                continue
            
            entry_with_lines = self.journal_service.get_journal_entry_with_lines(entry.id)
            if entry_with_lines and entry_with_lines.lines:
                for line in entry_with_lines.lines:
                    if line.account_id == account_id:
                        balance += (line.debit - line.credit)
        
        return balance
    
    def display_trial_balance(self, account_balances, total_debits, total_credits):
        """Display the trial balance"""
        self.trial_balance_table.setRowCount(len(account_balances) + 2)  # +2 for totals and balance check
        
        # Display accounts
        for row, data in enumerate(account_balances):
            account = data['account']
            debit = data['debit']
            credit = data['credit']
            
            self.trial_balance_table.setItem(row, 0, QTableWidgetItem(str(account.code)))
            self.trial_balance_table.setItem(row, 1, QTableWidgetItem(account.name_ar))
            self.trial_balance_table.setItem(row, 2, QTableWidgetItem(f"{debit:,.2f}" if debit > 0 else ""))
            self.trial_balance_table.setItem(row, 3, QTableWidgetItem(f"{credit:,.2f}" if credit > 0 else ""))
        
        # Add totals row
        totals_row = len(account_balances)
        self.add_total_row(totals_row, "TOTALS", total_debits, total_credits)
        
        # Add balance check row
        balance_row = totals_row + 1
        difference = total_debits - total_credits
        balance_status = "BALANCED" if difference == 0 else f"OUT OF BALANCE: {difference:,.2f}"
        
        self.trial_balance_table.setItem(balance_row, 1, QTableWidgetItem(balance_status))
        
        # Color code the balance status
        balance_item = self.trial_balance_table.item(balance_row, 1)
        font = QFont()
        font.setBold(True)
        balance_item.setFont(font)
        
        if difference == 0:
            balance_item.setBackground(QColor(144, 238, 144))  # Light green
        else:
            balance_item.setBackground(QColor(255, 107, 107))  # Light red
    
    def add_total_row(self, row, label, debit_total, credit_total):
        """Add totals row"""
        label_item = QTableWidgetItem(label)
        debit_item = QTableWidgetItem(f"{debit_total:,.2f}")
        credit_item = QTableWidgetItem(f"{credit_total:,.2f}")
        
        font = QFont()
        font.setBold(True)
        
        label_item.setFont(font)
        debit_item.setFont(font)
        credit_item.setFont(font)
        
        # Add border/background
        label_item.setBackground(QColor(135, 206, 235))
        debit_item.setBackground(QColor(135, 206, 235))
        credit_item.setBackground(QColor(135, 206, 235))
        
        self.trial_balance_table.setItem(row, 1, label_item)
        self.trial_balance_table.setItem(row, 2, debit_item)
        self.trial_balance_table.setItem(row, 3, credit_item)
