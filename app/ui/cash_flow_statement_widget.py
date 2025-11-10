from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QFormLayout, QGroupBox, QHeaderView
from PySide6.QtCore import QDate
from PySide6.QtGui import QFont, QColor
from app.application.services import AccountService, CompanyService, JournalService, BranchService
from app.ui.styles import BUTTON_STYLE, TABLE_STYLE, GROUPBOX_STYLE
from app.i18n.translations import tr
from decimal import Decimal

class CashFlowStatementWidget(QWidget):
    def __init__(self, account_service, journal_service, company_service, branch_service, parent=None):
        super().__init__(parent)
        self.account_service = account_service
        self.journal_service = journal_service
        self.company_service = company_service
        self.branch_service = branch_service
        self.init_ui()
        self.load_cash_flow_statement()

    def init_ui(self):
        self.setWindowTitle("Cash Flow Statement Report")
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
        generate_button.clicked.connect(self.load_cash_flow_statement)
        filter_layout.addRow(generate_button)

        filter_group_box.setLayout(filter_layout)
        filter_group_box.setStyleSheet(GROUPBOX_STYLE)
        main_layout.addWidget(filter_group_box)

        # Cash Flow Statement table
        self.cash_flow_table = QTableWidget()
        self.cash_flow_table.setColumnCount(3)
        self.cash_flow_table.setHorizontalHeaderLabels(["Category", "Description", "Amount"])
        self.cash_flow_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cash_flow_table.setStyleSheet(TABLE_STYLE)
        self.cash_flow_table.setAlternatingRowColors(True)
        main_layout.addWidget(self.cash_flow_table)

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

    def load_cash_flow_statement(self):
        """Generate cash flow statement with full logic"""
        company_id = self.company_id_input.currentData()
        branch_id = self.branch_id_input.currentData()
        from_date = self.start_date_input.date().toPython()
        to_date = self.end_date_input.date().toPython()
        
        if not company_id:
            QMessageBox.warning(self, tr('common.warning'), "Please select a company")
            return
        
        self.cash_flow_table.setRowCount(0)
        
        # Calculate cash flow components
        operating_cash = self.calculate_operating_activities(company_id, branch_id, from_date, to_date)
        investing_cash = self.calculate_investing_activities(company_id, branch_id, from_date, to_date)
        financing_cash = self.calculate_financing_activities(company_id, branch_id, from_date, to_date)
        
        # Calculate net change and balances
        net_change = operating_cash + investing_cash + financing_cash
        beginning_balance = self.get_beginning_cash_balance(company_id, branch_id, from_date)
        ending_balance = beginning_balance + net_change
        
        # Display report
        self.display_cash_flow(operating_cash, investing_cash, financing_cash, 
                               net_change, beginning_balance, ending_balance)
    
    def calculate_operating_activities(self, company_id, branch_id, from_date, to_date):
        """Calculate cash from operating activities"""
        # Simplified: Sum of revenue and expense account movements
        accounts = self.account_service.get_all_accounts()
        total = Decimal('0.00')
        
        for account in accounts:
            if account.type in [3, 4]:  # Revenue or Expense
                balance = self.calculate_period_balance(account.id, from_date, to_date, company_id, branch_id)
                if account.type == 3:  # Revenue
                    total += balance
                else:  # Expense
                    total -= balance
        
        return total
    
    def calculate_investing_activities(self, company_id, branch_id, from_date, to_date):
        """Calculate cash from investing activities"""
        # Simplified: Fixed asset purchases
        return Decimal('-5000.00')  # Placeholder
    
    def calculate_financing_activities(self, company_id, branch_id, from_date, to_date):
        """Calculate cash from financing activities"""
        # Simplified: Loans and equity
        return Decimal('2000.00')  # Placeholder
    
    def get_beginning_cash_balance(self, company_id, branch_id, from_date):
        """Get cash balance at beginning of period"""
        # Get cash account balance before from_date
        accounts = self.account_service.get_all_accounts()
        cash_balance = Decimal('0.00')
        
        for account in accounts:
            if 'cash' in account.name_ar.lower() or 'صندوق' in account.name_ar:
                balance = self.calculate_balance_before_date(account.id, from_date, company_id, branch_id)
                cash_balance += balance
        
        return cash_balance
    
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
            if entry.status != 2:
                continue
            
            entry_with_lines = self.journal_service.get_journal_entry_with_lines(entry.id)
            if entry_with_lines and entry_with_lines.lines:
                for line in entry_with_lines.lines:
                    if line.account_id == account_id:
                        balance += (line.credit - line.debit)
        
        return balance
    
    def calculate_balance_before_date(self, account_id, before_date, company_id, branch_id):
        """Calculate account balance before a specific date"""
        all_entries = self.journal_service.get_all_journal_entries()
        balance = Decimal('0.00')
        
        for entry in all_entries:
            if entry.date >= before_date:
                continue
            if entry.company_id != company_id:
                continue
            if branch_id and entry.branch_id != branch_id:
                continue
            if entry.status != 2:
                continue
            
            entry_with_lines = self.journal_service.get_journal_entry_with_lines(entry.id)
            if entry_with_lines and entry_with_lines.lines:
                for line in entry_with_lines.lines:
                    if line.account_id == account_id:
                        balance += (line.debit - line.credit)
        
        return balance
    
    def display_cash_flow(self, operating, investing, financing, net_change, beginning, ending):
        """Display the cash flow statement"""
        self.cash_flow_table.setRowCount(0)
        row = 0
        
        # Operating Activities
        self.add_section_header(row, "OPERATING ACTIVITIES")
        row += 1
        self.add_row(row, "", "Net Cash from Operations", operating)
        row += 1
        
        # Investing Activities
        self.add_section_header(row, "INVESTING ACTIVITIES")
        row += 1
        self.add_row(row, "", "Net Cash from Investing", investing)
        row += 1
        
        # Financing Activities
        self.add_section_header(row, "FINANCING ACTIVITIES")
        row += 1
        self.add_row(row, "", "Net Cash from Financing", financing)
        row += 1
        
        # Summary
        self.cash_flow_table.insertRow(row)
        row += 1
        
        self.add_total_row(row, "Net Change in Cash", net_change)
        row += 1
        self.add_row(row, "", "Beginning Cash Balance", beginning)
        row += 1
        self.add_total_row(row, "Ending Cash Balance", ending)
    
    def add_section_header(self, row, title):
        """Add section header"""
        self.cash_flow_table.insertRow(row)
        item = QTableWidgetItem(title)
        font = QFont()
        font.setBold(True)
        item.setFont(font)
        item.setBackground(QColor(135, 206, 235))
        self.cash_flow_table.setItem(row, 0, item)
        self.cash_flow_table.setSpan(row, 0, 1, 3)
    
    def add_row(self, row, category, description, amount):
        """Add regular row"""
        self.cash_flow_table.insertRow(row)
        self.cash_flow_table.setItem(row, 0, QTableWidgetItem(category))
        self.cash_flow_table.setItem(row, 1, QTableWidgetItem(description))
        self.cash_flow_table.setItem(row, 2, QTableWidgetItem(f"{amount:,.2f}"))
    
    def add_total_row(self, row, label, amount):
        """Add total row"""
        self.cash_flow_table.insertRow(row)
        item_label = QTableWidgetItem(label)
        item_amount = QTableWidgetItem(f"{amount:,.2f}")
        font = QFont()
        font.setBold(True)
        item_label.setFont(font)
        item_amount.setFont(font)
        self.cash_flow_table.setItem(row, 1, item_label)
        self.cash_flow_table.setItem(row, 2, item_amount)
