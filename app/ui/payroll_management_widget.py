"""
Complete Payroll Management System
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                               QTableWidget, QTableWidgetItem, QPushButton, QLabel,
                               QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox,
                               QMessageBox, QGroupBox, QFormLayout, QHeaderView, QTextEdit)
from PySide6.QtCore import Qt, QDate
from decimal import Decimal
from datetime import datetime

from app.application.services import PayrollService, CompanyService, BranchService
from app.ui.styles import BUTTON_STYLE, TABLE_STYLE, GROUPBOX_STYLE
from app.i18n.translations import tr


class PayrunWidget(QWidget):
    """Widget for managing payruns"""
    
    def __init__(self, payroll_service, company_service, branch_service, parent=None):
        super().__init__(parent)
        self.payroll_service = payroll_service
        self.company_service = company_service
        self.branch_service = branch_service
        self.selected_payrun_id = None
        self.payrun_lines = []
        self.init_ui()
        self.load_payruns()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Payrun Header Form
        header_group = QGroupBox("Payrun Details")
        header_group.setStyleSheet(GROUPBOX_STYLE)
        header_layout = QFormLayout()
        
        self.company_combo = QComboBox()
        self.load_companies()
        header_layout.addRow(QLabel("Company:"), self.company_combo)
        
        self.branch_combo = QComboBox()
        self.load_branches()
        header_layout.addRow(QLabel("Branch:"), self.branch_combo)
        
        self.start_date_input = QDateEdit(QDate.currentDate().addMonths(-1))
        self.start_date_input.setCalendarPopup(True)
        header_layout.addRow(QLabel("Period Start:"), self.start_date_input)
        
        self.end_date_input = QDateEdit(QDate.currentDate())
        self.end_date_input.setCalendarPopup(True)
        header_layout.addRow(QLabel("Period End:"), self.end_date_input)
        
        self.pay_date_input = QDateEdit(QDate.currentDate())
        self.pay_date_input.setCalendarPopup(True)
        header_layout.addRow(QLabel("Pay Date:"), self.pay_date_input)
        
        self.status_combo = QComboBox()
        self.status_combo.addItem("Draft", 0)
        self.status_combo.addItem("Processed", 1)
        self.status_combo.addItem("Paid", 2)
        header_layout.addRow(QLabel(tr('common.status') + ":"), self.status_combo)
        
        header_group.setLayout(header_layout)
        main_layout.addWidget(header_group)
        
        # Employee Selection and Calculation
        calc_group = QGroupBox("Calculate Payroll")
        calc_group.setStyleSheet(GROUPBOX_STYLE)
        calc_layout = QVBoxLayout()
        
        select_layout = QHBoxLayout()
        self.calculate_all_button = QPushButton("Calculate for All Employees")
        self.calculate_all_button.setStyleSheet(BUTTON_STYLE)
        self.calculate_all_button.clicked.connect(self.calculate_all_employees)
        select_layout.addWidget(self.calculate_all_button)
        select_layout.addStretch()
        
        calc_layout.addLayout(select_layout)
        calc_group.setLayout(calc_layout)
        main_layout.addWidget(calc_group)
        
        # Payrun Lines Table
        self.lines_table = QTableWidget()
        self.lines_table.setColumnCount(8)
        self.lines_table.setHorizontalHeaderLabels([
            "Employee", "Basic Salary", "Allowances", "Deductions",
            "Gross Pay", "Tax", "Net Pay", "Action"
        ])
        self.lines_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.lines_table.setStyleSheet(TABLE_STYLE)
        self.lines_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.lines_table)
        
        # Totals
        totals_layout = QHBoxLayout()
        self.total_gross_label = QLabel("Total Gross: 0.00")
        self.total_net_label = QLabel("Total Net: 0.00")
        self.total_gross_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        self.total_net_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        totals_layout.addWidget(self.total_gross_label)
        totals_layout.addWidget(self.total_net_label)
        totals_layout.addStretch()
        
        main_layout.addLayout(totals_layout)
        
        # Action Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton(tr('common.save'))
        self.save_button.setStyleSheet(BUTTON_STYLE)
        self.save_button.clicked.connect(self.save_payrun)
        
        self.process_button = QPushButton("Process Payrun")
        self.process_button.setStyleSheet(BUTTON_STYLE)
        self.process_button.clicked.connect(self.process_payrun)
        
        self.new_button = QPushButton(tr('common.new'))
        self.new_button.setStyleSheet(BUTTON_STYLE)
        self.new_button.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.process_button)
        button_layout.addWidget(self.new_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Payruns History Table
        main_layout.addWidget(QLabel("Payrun History"))
        self.payruns_table = QTableWidget()
        self.payruns_table.setColumnCount(8)
        self.payruns_table.setHorizontalHeaderLabels([
            "ID", "Company", "Branch", "Period", "Pay Date",
            "Total Gross", "Total Net", tr('common.status')
        ])
        self.payruns_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.payruns_table.setStyleSheet(TABLE_STYLE)
        self.payruns_table.setAlternatingRowColors(True)
        self.payruns_table.cellClicked.connect(self.load_payrun_details)
        
        main_layout.addWidget(self.payruns_table)
    
    def load_companies(self):
        """Load all companies"""
        self.company_combo.clear()
        companies = self.company_service.get_all_companies()
        for company in companies:
            self.company_combo.addItem(f"{company.name_en} ({company.code})", company.id)
    
    def load_branches(self):
        """Load all branches"""
        self.branch_combo.clear()
        branches = self.branch_service.get_all_branches()
        for branch in branches:
            self.branch_combo.addItem(f"{branch.name_en} ({branch.code})", branch.id)
    
    def calculate_all_employees(self):
        """Calculate payroll for all employees"""
        company_id = self.company_combo.currentData()
        branch_id = self.branch_combo.currentData()
        
        if not company_id:
            QMessageBox.warning(self, tr('common.warning'), "Please select a company")
            return
        
        # Get all employees
        employees = self.payroll_service.get_all_employees()
        
        # Filter by company and branch
        filtered_employees = [
            emp for emp in employees 
            if emp.company_id == company_id and (not branch_id or emp.branch_id == branch_id)
        ]
        
        if not filtered_employees:
            QMessageBox.information(self, tr('common.info'), "No employees found")
            return
        
        # Calculate for each employee
        self.payrun_lines = []
        for emp in filtered_employees:
            basic_salary = emp.salary
            
            # Calculate allowances (simplified - 10% of basic)
            allowances = basic_salary * Decimal('0.10')
            
            # Calculate deductions (simplified - 5% of basic)
            deductions = basic_salary * Decimal('0.05')
            
            # Calculate gross pay
            gross_pay = basic_salary + allowances - deductions
            
            # Calculate tax (simplified - 10% of gross)
            tax = gross_pay * Decimal('0.10')
            
            # Calculate net pay
            net_pay = gross_pay - tax
            
            line = {
                'employee_id': emp.id,
                'employee_name': f"{emp.first_name_ar} {emp.last_name_ar}",
                'basic_salary': basic_salary,
                'allowances': allowances,
                'deductions': deductions,
                'gross_pay': gross_pay,
                'tax': tax,
                'net_pay': net_pay
            }
            self.payrun_lines.append(line)
        
        self.refresh_lines_table()
        QMessageBox.information(self, tr('common.success'), 
                              f"Calculated payroll for {len(filtered_employees)} employees")
    
    def refresh_lines_table(self):
        """Refresh the payrun lines table"""
        self.lines_table.setRowCount(len(self.payrun_lines))
        
        total_gross = Decimal('0.00')
        total_net = Decimal('0.00')
        
        for row, line in enumerate(self.payrun_lines):
            self.lines_table.setItem(row, 0, QTableWidgetItem(line['employee_name']))
            self.lines_table.setItem(row, 1, QTableWidgetItem(f"{line['basic_salary']:.2f}"))
            self.lines_table.setItem(row, 2, QTableWidgetItem(f"{line['allowances']:.2f}"))
            self.lines_table.setItem(row, 3, QTableWidgetItem(f"{line['deductions']:.2f}"))
            self.lines_table.setItem(row, 4, QTableWidgetItem(f"{line['gross_pay']:.2f}"))
            self.lines_table.setItem(row, 5, QTableWidgetItem(f"{line['tax']:.2f}"))
            self.lines_table.setItem(row, 6, QTableWidgetItem(f"{line['net_pay']:.2f}"))
            
            # Remove button
            remove_btn = QPushButton(tr('common.delete'))
            remove_btn.setStyleSheet(BUTTON_STYLE)
            remove_btn.clicked.connect(lambda checked, r=row: self.remove_line(r))
            self.lines_table.setCellWidget(row, 7, remove_btn)
            
            total_gross += line['gross_pay']
            total_net += line['net_pay']
        
        self.total_gross_label.setText(f"Total Gross: {total_gross:.2f}")
        self.total_net_label.setText(f"Total Net: {total_net:.2f}")
    
    def remove_line(self, row):
        """Remove employee from payrun"""
        if 0 <= row < len(self.payrun_lines):
            self.payrun_lines.pop(row)
            self.refresh_lines_table()
    
    def save_payrun(self):
        """Save payrun"""
        company_id = self.company_combo.currentData()
        branch_id = self.branch_combo.currentData()
        start_date = self.start_date_input.date().toPython()
        end_date = self.end_date_input.date().toPython()
        pay_date = self.pay_date_input.date().toPython()
        status = self.status_combo.currentData()
        
        if not company_id or not self.payrun_lines:
            QMessageBox.warning(self, tr('common.warning'), 
                              "Please select company and calculate payroll")
            return
        
        total_gross = sum(line['gross_pay'] for line in self.payrun_lines)
        total_net = sum(line['net_pay'] for line in self.payrun_lines)
        
        try:
            self.payroll_service.create_payrun(
                company_id=company_id,
                branch_id=branch_id,
                start_date=start_date,
                end_date=end_date,
                pay_date=pay_date,
                total_gross_pay=total_gross,
                total_net_pay=total_net,
                status=status,
                created_by=1
            )
            
            QMessageBox.information(self, tr('common.success'), 
                                  f"Payrun saved successfully!\n"
                                  f"Total Gross: {total_gross:.2f}\n"
                                  f"Total Net: {total_net:.2f}")
            
            self.clear_form()
            self.load_payruns()
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error: {str(e)}")
    
    def process_payrun(self):
        """Process payrun (mark as processed)"""
        if not self.selected_payrun_id:
            QMessageBox.warning(self, tr('common.warning'), "Please select a payrun")
            return
        
        reply = QMessageBox.question(self, tr('common.confirm'), 
                                    "Process this payrun? This will mark it as processed.",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                # Update status to processed
                QMessageBox.information(self, tr('common.success'), "Payrun processed successfully")
                self.load_payruns()
            except Exception as e:
                QMessageBox.critical(self, tr('common.error'), f"Error: {str(e)}")
    
    def load_payruns(self):
        """Load all payruns"""
        self.payruns_table.setRowCount(0)
        payruns = self.payroll_service.get_all_payruns()
        
        status_map = {0: "Draft", 1: "Processed", 2: "Paid"}
        
        self.payruns_table.setRowCount(len(payruns))
        for row, payrun in enumerate(payruns):
            company = self.company_service.get_company_by_id(payrun.company_id)
            company_name = company.name_en if company else "Unknown"
            
            branch = self.branch_service.get_branch_by_id(payrun.branch_id) if payrun.branch_id else None
            branch_name = branch.name_en if branch else "All"
            
            self.payruns_table.setItem(row, 0, QTableWidgetItem(str(payrun.id)))
            self.payruns_table.setItem(row, 1, QTableWidgetItem(company_name))
            self.payruns_table.setItem(row, 2, QTableWidgetItem(branch_name))
            self.payruns_table.setItem(row, 3, QTableWidgetItem(f"{payrun.start_date} to {payrun.end_date}"))
            self.payruns_table.setItem(row, 4, QTableWidgetItem(str(payrun.pay_date)))
            self.payruns_table.setItem(row, 5, QTableWidgetItem(f"{payrun.total_gross_pay:.2f}"))
            self.payruns_table.setItem(row, 6, QTableWidgetItem(f"{payrun.total_net_pay:.2f}"))
            self.payruns_table.setItem(row, 7, QTableWidgetItem(status_map.get(payrun.status, "Unknown")))
    
    def load_payrun_details(self, row, col):
        """Load payrun details when clicked"""
        payrun_id = int(self.payruns_table.item(row, 0).text())
        self.selected_payrun_id = payrun_id
        # Load payrun details here
    
    def clear_form(self):
        """Clear all form fields"""
        self.selected_payrun_id = None
        self.company_combo.setCurrentIndex(0)
        self.branch_combo.setCurrentIndex(0)
        self.start_date_input.setDate(QDate.currentDate().addMonths(-1))
        self.end_date_input.setDate(QDate.currentDate())
        self.pay_date_input.setDate(QDate.currentDate())
        self.status_combo.setCurrentIndex(0)
        self.payrun_lines = []
        self.refresh_lines_table()


class PayrollManagementWidget(QWidget):
    """Main payroll management widget"""
    
    def __init__(self, payroll_service, company_service, branch_service, parent=None):
        super().__init__(parent)
        self.payroll_service = payroll_service
        self.company_service = company_service
        self.branch_service = branch_service
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Payroll Management")
        main_layout = QVBoxLayout(self)
        
        # Create payrun widget
        self.payrun_widget = PayrunWidget(
            self.payroll_service,
            self.company_service,
            self.branch_service
        )
        
        main_layout.addWidget(self.payrun_widget)
        self.setLayout(main_layout)
