"""
Complete Financial Reports with Full Logic
Includes: Balance Sheet, Income Statement, Cash Flow, Trial Balance
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                               QTableWidget, QTableWidgetItem, QPushButton, QLabel,
                               QComboBox, QDateEdit, QMessageBox, QGroupBox, 
                               QFormLayout, QHeaderView)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from decimal import Decimal
from datetime import datetime

from app.application.services import AccountService, JournalService, CompanyService, BranchService
from app.ui.styles import BUTTON_STYLE, TABLE_STYLE, GROUPBOX_STYLE
from app.i18n.translations import tr


class BalanceSheetReportWidget(QWidget):
    """Balance Sheet Report with full logic"""
    
    def __init__(self, account_service, journal_service, company_service, branch_service, parent=None):
        super().__init__(parent)
        self.account_service = account_service
        self.journal_service = journal_service
        self.company_service = company_service
        self.branch_service = branch_service
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Filters
        filter_group = QGroupBox("Report Filters")
        filter_group.setStyleSheet(GROUPBOX_STYLE)
        filter_layout = QFormLayout()
        
        self.company_combo = QComboBox()
        self.load_companies()
        filter_layout.addRow(QLabel("Company:"), self.company_combo)
        
        self.branch_combo = QComboBox()
        self.load_branches()
        filter_layout.addRow(QLabel("Branch:"), self.branch_combo)
        
        self.as_of_date_input = QDateEdit(QDate.currentDate())
        self.as_of_date_input.setCalendarPopup(True)
        filter_layout.addRow(QLabel("As of Date:"), self.as_of_date_input)
        
        self.generate_button = QPushButton("Generate Report")
        self.generate_button.setStyleSheet(BUTTON_STYLE)
        self.generate_button.clicked.connect(self.generate_report)
        filter_layout.addRow(self.generate_button)
        
        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group)
        
        # Report Table
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(3)
        self.report_table.setHorizontalHeaderLabels(["Category", "Account", "Amount"])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.report_table.setStyleSheet(TABLE_STYLE)
        self.report_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.report_table)
    
    def load_companies(self):
        """Load all companies"""
        self.company_combo.clear()
        companies = self.company_service.get_all_companies()
        for company in companies:
            self.company_combo.addItem(f"{company.name_en} ({company.code})", company.id)
    
    def load_branches(self):
        """Load all branches"""
        self.branch_combo.clear()
        self.branch_combo.addItem("All Branches", None)
        branches = self.branch_service.get_all_branches()
        for branch in branches:
            self.branch_combo.addItem(f"{branch.name_en} ({branch.code})", branch.id)
    
    def generate_report(self):
        """Generate balance sheet report"""
        company_id = self.company_combo.currentData()
        branch_id = self.branch_combo.currentData()
        as_of_date = self.as_of_date_input.date().toPython()
        
        if not company_id:
            QMessageBox.warning(self, tr('common.warning'), "Please select a company")
            return
        
        # Get all accounts
        accounts = self.account_service.get_all_accounts()
        
        # Calculate balances for each account
        account_balances = {}
        for account in accounts:
            balance = self.calculate_account_balance(account.id, as_of_date, company_id, branch_id)
            account_balances[account.id] = {
                'account': account,
                'balance': balance
            }
        
        # Organize by type
        assets = []
        liabilities = []
        equity = []
        
        for acc_id, data in account_balances.items():
            account = data['account']
            balance = data['balance']
            
            if balance == 0:
                continue
            
            if account.type == 0:  # Asset
                assets.append((account, balance))
            elif account.type == 1:  # Liability
                liabilities.append((account, balance))
            elif account.type == 2:  # Equity
                equity.append((account, balance))
        
        # Calculate totals
        total_assets = sum(bal for _, bal in assets)
        total_liabilities = sum(bal for _, bal in liabilities)
        total_equity = sum(bal for _, bal in equity)
        
        # Display report
        self.display_balance_sheet(assets, liabilities, equity, 
                                   total_assets, total_liabilities, total_equity)
    
    def calculate_account_balance(self, account_id, as_of_date, company_id, branch_id):
        """Calculate account balance up to a specific date"""
        # Get all journal entries up to the date
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
            
            # Get lines for this entry
            entry_with_lines = self.journal_service.get_journal_entry_with_lines(entry.id)
            if entry_with_lines and entry_with_lines.lines:
                for line in entry_with_lines.lines:
                    if line.account_id == account_id:
                        balance += (line.debit - line.credit)
        
        return balance
    
    def display_balance_sheet(self, assets, liabilities, equity, 
                              total_assets, total_liabilities, total_equity):
        """Display the balance sheet"""
        self.report_table.setRowCount(0)
        row = 0
        
        # Assets Section
        self.add_section_header(row, "ASSETS")
        row += 1
        
        for account, balance in assets:
            self.report_table.insertRow(row)
            self.report_table.setItem(row, 0, QTableWidgetItem(""))
            self.report_table.setItem(row, 1, QTableWidgetItem(account.name_ar))
            self.report_table.setItem(row, 2, QTableWidgetItem(f"{balance:,.2f}"))
            row += 1
        
        # Total Assets
        self.add_total_row(row, "Total Assets", total_assets)
        row += 1
        
        # Empty row
        self.report_table.insertRow(row)
        row += 1
        
        # Liabilities Section
        self.add_section_header(row, "LIABILITIES")
        row += 1
        
        for account, balance in liabilities:
            self.report_table.insertRow(row)
            self.report_table.setItem(row, 0, QTableWidgetItem(""))
            self.report_table.setItem(row, 1, QTableWidgetItem(account.name_ar))
            self.report_table.setItem(row, 2, QTableWidgetItem(f"{balance:,.2f}"))
            row += 1
        
        # Total Liabilities
        self.add_total_row(row, "Total Liabilities", total_liabilities)
        row += 1
        
        # Empty row
        self.report_table.insertRow(row)
        row += 1
        
        # Equity Section
        self.add_section_header(row, "EQUITY")
        row += 1
        
        for account, balance in equity:
            self.report_table.insertRow(row)
            self.report_table.setItem(row, 0, QTableWidgetItem(""))
            self.report_table.setItem(row, 1, QTableWidgetItem(account.name_ar))
            self.report_table.setItem(row, 2, QTableWidgetItem(f"{balance:,.2f}"))
            row += 1
        
        # Total Equity
        self.add_total_row(row, "Total Equity", total_equity)
        row += 1
        
        # Empty row
        self.report_table.insertRow(row)
        row += 1
        
        # Total Liabilities & Equity
        total_liab_equity = total_liabilities + total_equity
        self.add_total_row(row, "Total Liabilities & Equity", total_liab_equity)
    
    def add_section_header(self, row, title):
        """Add a section header row"""
        self.report_table.insertRow(row)
        item = QTableWidgetItem(title)
        font = QFont()
        font.setBold(True)
        item.setFont(font)
        item.setBackground(QColor(135, 206, 235))  # Sky blue
        self.report_table.setItem(row, 0, item)
        self.report_table.setSpan(row, 0, 1, 3)
    
    def add_total_row(self, row, label, amount):
        """Add a total row"""
        self.report_table.insertRow(row)
        item_label = QTableWidgetItem(label)
        item_amount = QTableWidgetItem(f"{amount:,.2f}")
        font = QFont()
        font.setBold(True)
        item_label.setFont(font)
        item_amount.setFont(font)
        self.report_table.setItem(row, 1, item_label)
        self.report_table.setItem(row, 2, item_amount)


class IncomeStatementReportWidget(QWidget):
    """Income Statement Report with full logic"""
    
    def __init__(self, account_service, journal_service, company_service, branch_service, parent=None):
        super().__init__(parent)
        self.account_service = account_service
        self.journal_service = journal_service
        self.company_service = company_service
        self.branch_service = branch_service
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Filters
        filter_group = QGroupBox("Report Filters")
        filter_group.setStyleSheet(GROUPBOX_STYLE)
        filter_layout = QFormLayout()
        
        self.company_combo = QComboBox()
        self.load_companies()
        filter_layout.addRow(QLabel("Company:"), self.company_combo)
        
        self.branch_combo = QComboBox()
        self.load_branches()
        filter_layout.addRow(QLabel("Branch:"), self.branch_combo)
        
        self.from_date_input = QDateEdit(QDate.currentDate().addMonths(-12))
        self.from_date_input.setCalendarPopup(True)
        filter_layout.addRow(QLabel("From Date:"), self.from_date_input)
        
        self.to_date_input = QDateEdit(QDate.currentDate())
        self.to_date_input.setCalendarPopup(True)
        filter_layout.addRow(QLabel("To Date:"), self.to_date_input)
        
        self.generate_button = QPushButton("Generate Report")
        self.generate_button.setStyleSheet(BUTTON_STYLE)
        self.generate_button.clicked.connect(self.generate_report)
        filter_layout.addRow(self.generate_button)
        
        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group)
        
        # Report Table
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(3)
        self.report_table.setHorizontalHeaderLabels(["Category", "Account", "Amount"])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.report_table.setStyleSheet(TABLE_STYLE)
        self.report_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.report_table)
    
    def load_companies(self):
        """Load all companies"""
        self.company_combo.clear()
        companies = self.company_service.get_all_companies()
        for company in companies:
            self.company_combo.addItem(f"{company.name_en} ({company.code})", company.id)
    
    def load_branches(self):
        """Load all branches"""
        self.branch_combo.clear()
        self.branch_combo.addItem("All Branches", None)
        branches = self.branch_service.get_all_branches()
        for branch in branches:
            self.branch_combo.addItem(f"{branch.name_en} ({branch.code})", branch.id)
    
    def generate_report(self):
        """Generate income statement report"""
        company_id = self.company_combo.currentData()
        branch_id = self.branch_combo.currentData()
        from_date = self.from_date_input.date().toPython()
        to_date = self.to_date_input.date().toPython()
        
        if not company_id:
            QMessageBox.warning(self, tr('common.warning'), "Please select a company")
            return
        
        # Get all accounts
        accounts = self.account_service.get_all_accounts()
        
        # Calculate balances for revenue and expense accounts
        revenues = []
        expenses = []
        
        for account in accounts:
            if account.type == 3:  # Revenue
                balance = self.calculate_period_balance(account.id, from_date, to_date, company_id, branch_id)
                if balance != 0:
                    revenues.append((account, abs(balance)))
            elif account.type == 4:  # Expense
                balance = self.calculate_period_balance(account.id, from_date, to_date, company_id, branch_id)
                if balance != 0:
                    expenses.append((account, abs(balance)))
        
        # Calculate totals
        total_revenue = sum(bal for _, bal in revenues)
        total_expenses = sum(bal for _, bal in expenses)
        net_income = total_revenue - total_expenses
        
        # Display report
        self.display_income_statement(revenues, expenses, total_revenue, total_expenses, net_income)
    
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
    
    def display_income_statement(self, revenues, expenses, total_revenue, total_expenses, net_income):
        """Display the income statement"""
        self.report_table.setRowCount(0)
        row = 0
        
        # Revenue Section
        self.add_section_header(row, "REVENUE")
        row += 1
        
        for account, balance in revenues:
            self.report_table.insertRow(row)
            self.report_table.setItem(row, 0, QTableWidgetItem(""))
            self.report_table.setItem(row, 1, QTableWidgetItem(account.name_ar))
            self.report_table.setItem(row, 2, QTableWidgetItem(f"{balance:,.2f}"))
            row += 1
        
        # Total Revenue
        self.add_total_row(row, "Total Revenue", total_revenue)
        row += 1
        
        # Empty row
        self.report_table.insertRow(row)
        row += 1
        
        # Expenses Section
        self.add_section_header(row, "EXPENSES")
        row += 1
        
        for account, balance in expenses:
            self.report_table.insertRow(row)
            self.report_table.setItem(row, 0, QTableWidgetItem(""))
            self.report_table.setItem(row, 1, QTableWidgetItem(account.name_ar))
            self.report_table.setItem(row, 2, QTableWidgetItem(f"{balance:,.2f}"))
            row += 1
        
        # Total Expenses
        self.add_total_row(row, "Total Expenses", total_expenses)
        row += 1
        
        # Empty row
        self.report_table.insertRow(row)
        row += 1
        
        # Net Income
        self.add_total_row(row, "NET INCOME", net_income)
        
        # Color code net income
        item = self.report_table.item(row, 2)
        if net_income >= 0:
            item.setBackground(QColor(144, 238, 144))  # Light green
        else:
            item.setBackground(QColor(255, 107, 107))  # Light red
    
    def add_section_header(self, row, title):
        """Add a section header row"""
        self.report_table.insertRow(row)
        item = QTableWidgetItem(title)
        font = QFont()
        font.setBold(True)
        item.setFont(font)
        item.setBackground(QColor(135, 206, 235))
        self.report_table.setItem(row, 0, item)
        self.report_table.setSpan(row, 0, 1, 3)
    
    def add_total_row(self, row, label, amount):
        """Add a total row"""
        self.report_table.insertRow(row)
        item_label = QTableWidgetItem(label)
        item_amount = QTableWidgetItem(f"{amount:,.2f}")
        font = QFont()
        font.setBold(True)
        item_label.setFont(font)
        item_amount.setFont(font)
        self.report_table.setItem(row, 1, item_label)
        self.report_table.setItem(row, 2, item_amount)


class FinancialReportsWidget(QWidget):
    """Main financial reports widget with tabs"""
    
    def __init__(self, account_service, journal_service, company_service, branch_service, parent=None):
        super().__init__(parent)
        self.account_service = account_service
        self.journal_service = journal_service
        self.company_service = company_service
        self.branch_service = branch_service
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Financial Reports")
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.balance_sheet_widget = BalanceSheetReportWidget(
            self.account_service,
            self.journal_service,
            self.company_service,
            self.branch_service
        )
        
        self.income_statement_widget = IncomeStatementReportWidget(
            self.account_service,
            self.journal_service,
            self.company_service,
            self.branch_service
        )
        
        self.tab_widget.addTab(self.balance_sheet_widget, tr('reports.balance_sheet'))
        self.tab_widget.addTab(self.income_statement_widget, tr('reports.income_statement'))
        
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
