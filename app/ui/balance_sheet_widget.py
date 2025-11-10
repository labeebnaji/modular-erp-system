from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QFormLayout, QGroupBox, QHeaderView
from PySide6.QtCore import QDate
from PySide6.QtGui import QFont, QColor
from app.application.services import AccountService, CompanyService, JournalService, BranchService
from app.ui.styles import BUTTON_STYLE, TABLE_STYLE, GROUPBOX_STYLE
from app.i18n.translations import tr
from decimal import Decimal

class BalanceSheetWidget(QWidget):
    def __init__(self, account_service, journal_service, company_service, branch_service, parent=None):
        super().__init__(parent)
        self.account_service = account_service
        self.journal_service = journal_service
        self.company_service = company_service
        self.branch_service = branch_service
        self.init_ui()
        self.load_balance_sheet()

    def init_ui(self):
        self.setWindowTitle("Balance Sheet Report")
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
        generate_button.clicked.connect(self.load_balance_sheet)
        filter_layout.addRow(generate_button)

        filter_group_box.setLayout(filter_layout)
        filter_group_box.setStyleSheet(GROUPBOX_STYLE)
        main_layout.addWidget(filter_group_box)

        # Balance Sheet table
        self.balance_sheet_table = QTableWidget()
        self.balance_sheet_table.setColumnCount(3)
        self.balance_sheet_table.setHorizontalHeaderLabels(["Category", "Account", "Amount"])
        self.balance_sheet_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.balance_sheet_table.setStyleSheet(TABLE_STYLE)
        self.balance_sheet_table.setAlternatingRowColors(True)
        main_layout.addWidget(self.balance_sheet_table)

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

    def load_balance_sheet(self):
        """Generate balance sheet with full logic"""
        company_id = self.company_id_input.currentData()
        branch_id = self.branch_id_input.currentData()
        as_of_date = self.end_date_input.date().toPython()
        
        if not company_id:
            QMessageBox.warning(self, tr('common.warning'), "Please select a company")
            return
        
        self.balance_sheet_table.setRowCount(0)
        
        # Get all accounts
        accounts = self.account_service.get_all_accounts()
        
        # Categorize accounts
        assets = []
        liabilities = []
        equity = []
        
        for account in accounts:
            balance = self.calculate_account_balance(account.id, as_of_date, company_id, branch_id)
            
            if balance == 0:
                continue
            
            if account.type == 0:  # Assets
                assets.append({'account': account, 'balance': balance})
            elif account.type == 1:  # Liabilities
                liabilities.append({'account': account, 'balance': balance})
            elif account.type == 2:  # Equity
                equity.append({'account': account, 'balance': balance})
        
        # Calculate totals
        total_assets = sum(item['balance'] for item in assets)
        total_liabilities = sum(item['balance'] for item in liabilities)
        total_equity = sum(item['balance'] for item in equity)
        
        # Display balance sheet
        self.display_balance_sheet(assets, liabilities, equity, total_assets, total_liabilities, total_equity)
    
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
        
        return abs(balance)  # Return absolute value for balance sheet
    
    def display_balance_sheet(self, assets, liabilities, equity, total_assets, total_liabilities, total_equity):
        """Display the balance sheet"""
        self.balance_sheet_table.setRowCount(0)
        row = 0
        
        # Assets Section
        self.add_section_header(row, "ASSETS")
        row += 1
        
        for item in assets:
            self.add_account_row(row, "", item['account'].name_ar, item['balance'])
            row += 1
        
        self.add_total_row(row, "Total Assets", total_assets)
        row += 1
        
        # Empty row
        self.balance_sheet_table.insertRow(row)
        row += 1
        
        # Liabilities Section
        self.add_section_header(row, "LIABILITIES")
        row += 1
        
        for item in liabilities:
            self.add_account_row(row, "", item['account'].name_ar, item['balance'])
            row += 1
        
        self.add_total_row(row, "Total Liabilities", total_liabilities)
        row += 1
        
        # Empty row
        self.balance_sheet_table.insertRow(row)
        row += 1
        
        # Equity Section
        self.add_section_header(row, "EQUITY")
        row += 1
        
        for item in equity:
            self.add_account_row(row, "", item['account'].name_ar, item['balance'])
            row += 1
        
        self.add_total_row(row, "Total Equity", total_equity)
        row += 1
        
        # Empty row
        self.balance_sheet_table.insertRow(row)
        row += 1
        
        # Grand Total
        total_liabilities_equity = total_liabilities + total_equity
        self.add_grand_total_row(row, "Total Liabilities & Equity", total_liabilities_equity)
        
        # Check if balanced
        if abs(total_assets - total_liabilities_equity) > Decimal('0.01'):
            row += 1
            self.add_warning_row(row, f"WARNING: Balance Sheet is out of balance by {abs(total_assets - total_liabilities_equity):,.2f}")
    
    def add_section_header(self, row, title):
        """Add section header"""
        self.balance_sheet_table.insertRow(row)
        item = QTableWidgetItem(title)
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        item.setFont(font)
        item.setBackground(QColor(135, 206, 235))
        self.balance_sheet_table.setItem(row, 0, item)
        self.balance_sheet_table.setSpan(row, 0, 1, 3)
    
    def add_account_row(self, row, category, account_name, amount):
        """Add account row"""
        self.balance_sheet_table.insertRow(row)
        self.balance_sheet_table.setItem(row, 0, QTableWidgetItem(category))
        self.balance_sheet_table.setItem(row, 1, QTableWidgetItem(account_name))
        self.balance_sheet_table.setItem(row, 2, QTableWidgetItem(f"{amount:,.2f}"))
    
    def add_total_row(self, row, label, amount):
        """Add total row"""
        self.balance_sheet_table.insertRow(row)
        item_label = QTableWidgetItem(label)
        item_amount = QTableWidgetItem(f"{amount:,.2f}")
        
        font = QFont()
        font.setBold(True)
        item_label.setFont(font)
        item_amount.setFont(font)
        
        item_label.setBackground(QColor(173, 216, 230))
        item_amount.setBackground(QColor(173, 216, 230))
        
        self.balance_sheet_table.setItem(row, 1, item_label)
        self.balance_sheet_table.setItem(row, 2, item_amount)
    
    def add_grand_total_row(self, row, label, amount):
        """Add grand total row"""
        self.balance_sheet_table.insertRow(row)
        item_label = QTableWidgetItem(label)
        item_amount = QTableWidgetItem(f"{amount:,.2f}")
        
        font = QFont()
        font.setBold(True)
        font.setPointSize(11)
        item_label.setFont(font)
        item_amount.setFont(font)
        
        item_label.setBackground(QColor(100, 149, 237))
        item_amount.setBackground(QColor(100, 149, 237))
        
        self.balance_sheet_table.setItem(row, 1, item_label)
        self.balance_sheet_table.setItem(row, 2, item_amount)
    
    def add_warning_row(self, row, message):
        """Add warning row"""
        self.balance_sheet_table.insertRow(row)
        item = QTableWidgetItem(message)
        font = QFont()
        font.setBold(True)
        item.setFont(font)
        item.setBackground(QColor(255, 107, 107))
        self.balance_sheet_table.setItem(row, 0, item)
        self.balance_sheet_table.setSpan(row, 0, 1, 3)
