from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QFormLayout, QGroupBox, QHeaderView
from PySide6.QtCore import QDate
from PySide6.QtGui import QFont, QColor
from app.application.services import AccountService, CompanyService, JournalService, BranchService
from app.ui.styles import BUTTON_STYLE, TABLE_STYLE, GROUPBOX_STYLE
from app.i18n.translations import tr
from decimal import Decimal

class IncomeStatementWidget(QWidget):
    def __init__(self, account_service, journal_service, company_service, branch_service, parent=None):
        super().__init__(parent)
        self.account_service = account_service
        self.journal_service = journal_service
        self.company_service = company_service
        self.branch_service = branch_service
        self.init_ui()
        self.load_income_statement()

    def init_ui(self):
        self.setWindowTitle("Income Statement Report")
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

        self.start_date_input = QDateEdit(QDate.currentDate().addYears(-1))
        self.start_date_input.setCalendarPopup(True)
        filter_layout.addRow(QLabel("Start Date:"), self.start_date_input)

        self.end_date_input = QDateEdit(QDate.currentDate())
        self.end_date_input.setCalendarPopup(True)
        filter_layout.addRow(QLabel("End Date:"), self.end_date_input)

        generate_button = QPushButton("Generate Report")
        generate_button.setStyleSheet(BUTTON_STYLE)
        generate_button.clicked.connect(self.load_income_statement)
        filter_layout.addRow(generate_button)

        filter_group_box.setLayout(filter_layout)
        filter_group_box.setStyleSheet(GROUPBOX_STYLE)
        main_layout.addWidget(filter_group_box)

        # Income Statement table
        self.income_statement_table = QTableWidget()
        self.income_statement_table.setColumnCount(3)
        self.income_statement_table.setHorizontalHeaderLabels(["Category", "Account", "Amount"])
        self.income_statement_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.income_statement_table.setStyleSheet(TABLE_STYLE)
        self.income_statement_table.setAlternatingRowColors(True)
        main_layout.addWidget(self.income_statement_table)

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

    def load_income_statement(self):
        """Generate income statement with full logic"""
        company_id = self.company_id_input.currentData()
        branch_id = self.branch_id_input.currentData()
        from_date = self.start_date_input.date().toPython()
        to_date = self.end_date_input.date().toPython()
        
        if not company_id:
            QMessageBox.warning(self, tr('common.warning'), "Please select a company")
            return
        
        self.income_statement_table.setRowCount(0)
        
        # Get all accounts
        accounts = self.account_service.get_all_accounts()
        
        # Categorize accounts
        revenue_accounts = []
        expense_accounts = []
        
        for account in accounts:
            balance = self.calculate_period_balance(account.id, from_date, to_date, company_id, branch_id)
            
            if balance == 0:
                continue
            
            if account.type == 3:  # Revenue
                revenue_accounts.append({'account': account, 'balance': abs(balance)})
            elif account.type == 4:  # Expenses
                expense_accounts.append({'account': account, 'balance': abs(balance)})
        
        # Calculate totals
        total_revenue = sum(item['balance'] for item in revenue_accounts)
        total_expenses = sum(item['balance'] for item in expense_accounts)
        net_income = total_revenue - total_expenses
        
        # Display income statement
        self.display_income_statement(revenue_accounts, expense_accounts, total_revenue, total_expenses, net_income)
    
    def calculate_period_balance(self, account_id, from_date, to_date, company_id, branch_id):
        """Calculate account balance for a period"""
        all_entries = self.journal_service.get_all_journal_entries()
        balance = Decimal('0.00')
        
        for entry in all_entries:
            if entry.date < from_date or entry.date > to_date:
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
                        balance += (line.credit - line.debit)  # Revenue/Expense convention
        
        return balance
    
    def display_income_statement(self, revenue_accounts, expense_accounts, total_revenue, total_expenses, net_income):
        """Display the income statement"""
        self.income_statement_table.setRowCount(0)
        row = 0
        
        # Revenue Section
        self.add_section_header(row, "REVENUE")
        row += 1
        
        for item in revenue_accounts:
            self.add_account_row(row, "", item['account'].name_ar, item['balance'])
            row += 1
        
        self.add_total_row(row, "Total Revenue", total_revenue)
        row += 1
        
        # Empty row
        self.income_statement_table.insertRow(row)
        row += 1
        
        # Expenses Section
        self.add_section_header(row, "EXPENSES")
        row += 1
        
        for item in expense_accounts:
            self.add_account_row(row, "", item['account'].name_ar, item['balance'])
            row += 1
        
        self.add_total_row(row, "Total Expenses", total_expenses)
        row += 1
        
        # Empty row
        self.income_statement_table.insertRow(row)
        row += 1
        
        # Net Income
        self.add_net_income_row(row, "Net Income", net_income)
    
    def add_section_header(self, row, title):
        """Add section header"""
        self.income_statement_table.insertRow(row)
        item = QTableWidgetItem(title)
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        item.setFont(font)
        item.setBackground(QColor(135, 206, 235))
        self.income_statement_table.setItem(row, 0, item)
        self.income_statement_table.setSpan(row, 0, 1, 3)
    
    def add_account_row(self, row, category, account_name, amount):
        """Add account row"""
        self.income_statement_table.insertRow(row)
        self.income_statement_table.setItem(row, 0, QTableWidgetItem(category))
        self.income_statement_table.setItem(row, 1, QTableWidgetItem(account_name))
        self.income_statement_table.setItem(row, 2, QTableWidgetItem(f"{amount:,.2f}"))
    
    def add_total_row(self, row, label, amount):
        """Add total row"""
        self.income_statement_table.insertRow(row)
        item_label = QTableWidgetItem(label)
        item_amount = QTableWidgetItem(f"{amount:,.2f}")
        
        font = QFont()
        font.setBold(True)
        item_label.setFont(font)
        item_amount.setFont(font)
        
        item_label.setBackground(QColor(173, 216, 230))
        item_amount.setBackground(QColor(173, 216, 230))
        
        self.income_statement_table.setItem(row, 1, item_label)
        self.income_statement_table.setItem(row, 2, item_amount)
    
    def add_net_income_row(self, row, label, amount):
        """Add net income row"""
        self.income_statement_table.insertRow(row)
        item_label = QTableWidgetItem(label)
        item_amount = QTableWidgetItem(f"{amount:,.2f}")
        
        font = QFont()
        font.setBold(True)
        font.setPointSize(11)
        item_label.setFont(font)
        item_amount.setFont(font)
        
        # Color based on profit/loss
        if amount >= 0:
            color = QColor(144, 238, 144)  # Light green for profit
        else:
            color = QColor(255, 107, 107)  # Light red for loss
        
        item_label.setBackground(color)
        item_amount.setBackground(color)
        
        self.income_statement_table.setItem(row, 1, item_label)
        self.income_statement_table.setItem(row, 2, item_amount)
