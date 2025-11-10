from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QFormLayout, QGroupBox, QHeaderView
from PySide6.QtCore import QDate
from PySide6.QtGui import QFont, QColor
from app.application.services import TaxService, CompanyService, BranchService, AccountService, JournalService
from app.ui.styles import BUTTON_STYLE, TABLE_STYLE, GROUPBOX_STYLE
from app.i18n.translations import tr
from decimal import Decimal

class TaxReportWidget(QWidget):
    def __init__(self, tax_service, company_service, branch_service, parent=None):
        super().__init__(parent)
        self.tax_service = tax_service
        self.company_service = company_service
        self.branch_service = branch_service
        self.init_ui()
        self.load_tax_reports()

    def init_ui(self):
        self.setWindowTitle("Tax Reports")
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
        generate_button.clicked.connect(self.load_tax_reports)
        filter_layout.addRow(generate_button)

        filter_group_box.setLayout(filter_layout)
        filter_group_box.setStyleSheet(GROUPBOX_STYLE)
        main_layout.addWidget(filter_group_box)

        # Tax Reports table
        self.tax_reports_table = QTableWidget()
        self.tax_reports_table.setColumnCount(8)
        self.tax_reports_table.setHorizontalHeaderLabels([
            "#", "Company", "Branch", "Tax Name", "Tax Rate", 
            "Taxable Amount", "Tax Amount", "Period"
        ])
        self.tax_reports_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tax_reports_table.setStyleSheet(TABLE_STYLE)
        self.tax_reports_table.setAlternatingRowColors(True)
        main_layout.addWidget(self.tax_reports_table)

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

    def load_tax_reports(self):
        """Generate tax reports with full logic"""
        company_id = self.company_id_input.currentData()
        branch_id = self.branch_id_input.currentData()
        from_date = self.start_date_input.date().toPython()
        to_date = self.end_date_input.date().toPython()
        
        if not company_id:
            QMessageBox.warning(self, "Warning", "Please select a company")
            return
        
        self.tax_reports_table.setRowCount(0)
        
        # Get all tax settings for the company
        tax_settings = self.tax_service.get_all_tax_settings()
        company_tax_settings = [ts for ts in tax_settings if ts.company_id == company_id]
        
        if not company_tax_settings:
            QMessageBox.information(self, "No Data", "No tax settings found for the selected company")
            return
        
        # Calculate tax amounts for each tax setting
        tax_reports = []
        
        for tax_setting in company_tax_settings:
            # Calculate total taxable amount and tax collected
            taxable_amount, tax_amount = self.calculate_tax_amounts(
                tax_setting, company_id, branch_id, from_date, to_date
            )
            
            if taxable_amount > 0 or tax_amount > 0:
                company = self.company_service.get_company_by_id(company_id)
                company_name = company.name_en if company else "Unknown"
                
                branch = self.branch_service.get_branch_by_id(branch_id) if branch_id else None
                branch_name = branch.name_en if branch else "All Branches"
                
                tax_reports.append({
                    'company_name': company_name,
                    'branch_name': branch_name,
                    'tax_name': tax_setting.tax_name,
                    'tax_rate': tax_setting.tax_rate,
                    'taxable_amount': taxable_amount,
                    'tax_amount': tax_amount,
                    'period': f"{from_date} to {to_date}"
                })
        
        # Display reports
        self.display_tax_reports(tax_reports)
    
    def calculate_tax_amounts(self, tax_setting, company_id, branch_id, from_date, to_date):
        """Calculate taxable amount and tax collected for a tax setting"""
        # Simplified calculation based on revenue accounts
        account_service = AccountService()
        journal_service = JournalService()
        
        # Get revenue accounts
        accounts = account_service.get_all_accounts()
        revenue_accounts = [acc for acc in accounts if acc.type == 3]  # Revenue type
        
        total_revenue = Decimal('0.00')
        
        # Calculate total revenue for the period
        for account in revenue_accounts:
            balance = self.calculate_account_period_balance(
                account.id, from_date, to_date, company_id, branch_id, journal_service
            )
            total_revenue += abs(balance)  # Revenue is normally credit, so we take absolute
        
        # Calculate taxable amount (assuming all revenue is taxable for simplicity)
        taxable_amount = total_revenue
        
        # Calculate tax amount
        tax_amount = taxable_amount * (tax_setting.tax_rate / Decimal('100'))
        
        return taxable_amount, tax_amount
    
    def calculate_account_period_balance(self, account_id, from_date, to_date, company_id, branch_id, journal_service):
        """Calculate account balance for a specific period"""
        all_entries = journal_service.get_all_journal_entries()
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
            
            entry_with_lines = journal_service.get_journal_entry_with_lines(entry.id)
            if entry_with_lines and entry_with_lines.lines:
                for line in entry_with_lines.lines:
                    if line.account_id == account_id:
                        balance += (line.credit - line.debit)  # Revenue convention
        
        return balance
    
    def display_tax_reports(self, tax_reports):
        """Display the tax reports"""
        self.tax_reports_table.setRowCount(len(tax_reports))
        
        total_taxable = Decimal('0.00')
        total_tax = Decimal('0.00')
        
        for row, report in enumerate(tax_reports):
            self.tax_reports_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.tax_reports_table.setItem(row, 1, QTableWidgetItem(report['company_name']))
            self.tax_reports_table.setItem(row, 2, QTableWidgetItem(report['branch_name']))
            self.tax_reports_table.setItem(row, 3, QTableWidgetItem(report['tax_name']))
            self.tax_reports_table.setItem(row, 4, QTableWidgetItem(f"{report['tax_rate']:.2f}%"))
            self.tax_reports_table.setItem(row, 5, QTableWidgetItem(f"{report['taxable_amount']:,.2f}"))
            self.tax_reports_table.setItem(row, 6, QTableWidgetItem(f"{report['tax_amount']:,.2f}"))
            self.tax_reports_table.setItem(row, 7, QTableWidgetItem(report['period']))
            
            total_taxable += report['taxable_amount']
            total_tax += report['tax_amount']
        
        # Add totals row if there are reports
        if tax_reports:
            self.add_totals_row(len(tax_reports), total_taxable, total_tax)
    
    def add_totals_row(self, row, total_taxable, total_tax):
        """Add totals row to the table"""
        self.tax_reports_table.insertRow(row)
        
        # Create bold items for totals
        font = QFont()
        font.setBold(True)
        
        total_label = QTableWidgetItem("TOTALS")
        total_label.setFont(font)
        
        total_taxable_item = QTableWidgetItem(f"{total_taxable:,.2f}")
        total_taxable_item.setFont(font)
        
        total_tax_item = QTableWidgetItem(f"{total_tax:,.2f}")
        total_tax_item.setFont(font)
        
        self.tax_reports_table.setItem(row, 3, total_label)
        self.tax_reports_table.setItem(row, 5, total_taxable_item)
        self.tax_reports_table.setItem(row, 6, total_tax_item)
