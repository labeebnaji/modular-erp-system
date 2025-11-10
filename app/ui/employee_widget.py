from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QSpinBox, QFormLayout, QGroupBox, QHeaderView, QCheckBox, QDoubleSpinBox
from PySide6.QtCore import QDate
from app.application.services import PayrollService, CompanyService, BranchService # Added BranchService
#from app.infrastructure.database import get_db # No longer needed
from decimal import Decimal

class EmployeeWidget(QWidget):
    def __init__(self, payroll_service, company_service, branch_service, parent=None):
        super().__init__(parent)
        self.payroll_service = payroll_service
        self.company_service = company_service
        self.branch_service = branch_service
        self.init_ui()
        self.load_employees()

    def init_ui(self):
        self.setWindowTitle("Employee Management")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Employee form
        form_group_box = QGroupBox("Employee Details")
        form_layout = QFormLayout()

        self.company_id_input = QComboBox()
        self.load_companies_to_combobox(self.company_id_input)
        form_layout.addRow(QLabel("Company:"), self.company_id_input)

        self.branch_id_input = QComboBox()
        self.load_branches_to_combobox(self.branch_id_input, self.company_id_input.currentData())
        form_layout.addRow(QLabel("Branch:"), self.branch_id_input)

        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("First Name")
        # Icon placeholder: self.first_name_input.addAction(QIcon("path/to/first_name_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("First Name:"), self.first_name_input)

        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Last Name")
        # Icon placeholder: self.last_name_input.addAction(QIcon("path/to/last_name_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Last Name:"), self.last_name_input)

        self.employee_code_input = QLineEdit()
        self.employee_code_input.setPlaceholderText("Employee Code")
        # Icon placeholder: self.employee_code_input.addAction(QIcon("path/to/employee_code_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Employee Code:"), self.employee_code_input)

        self.job_title_input = QLineEdit()
        self.job_title_input.setPlaceholderText("Job Title")
        # Icon placeholder: self.job_title_input.addAction(QIcon("path/to/job_title_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Job Title:"), self.job_title_input)

        self.department_input = QLineEdit()
        self.department_input.setPlaceholderText("Department")
        # Icon placeholder: self.department_input.addAction(QIcon("path/to/department_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Department:"), self.department_input)

        self.hire_date_input = QDateEdit(QDate.currentDate())
        self.hire_date_input.setCalendarPopup(True)
        form_layout.addRow(QLabel("Hire Date:"), self.hire_date_input)

        self.salary_input = QDoubleSpinBox()
        self.salary_input.setRange(0.00, 999999999.99)
        self.salary_input.setPrefix("$")
        form_layout.addRow(QLabel("Salary:"), self.salary_input)

        self.is_active_input = QCheckBox("Is Active")
        self.is_active_input.setChecked(True)
        form_layout.addRow(QLabel("Active:"), self.is_active_input)

        add_button = QPushButton("Add Employee")
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        add_button.clicked.connect(self.add_employee)
        
        # Apply styling to button
        button_style = """
            QPushButton {
                background-color: #ADD8E6;
                border: 1px solid #87CEEB;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #87CEEB;
            }
        """
        add_button.setStyleSheet(button_style)
        
        form_layout.addRow(add_button)

        form_group_box.setLayout(form_layout)
        main_layout.addWidget(form_group_box)

        # Employee table
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(10) # Increased column count
        self.employees_table.setHorizontalHeaderLabels(["ID", "Company", "Branch", "First Name", "Last Name", "Code", "Job Title", "Department", "Hire Date", "Salary", "Active"])
        self.employees_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        
        # Apply styling to table
        table_style = """
            QTableWidget {
                alternate-background-color: #F0F8FF;
                background-color: #FFFFFF;
                selection-background-color: #ADD8E6;
            }
            QHeaderView::section {
                background-color: #87CEEB;
                color: white;
                padding: 4px;
                border: 1px solid #6A9FBC;
            }
        """
        self.employees_table.setStyleSheet(table_style)
        self.employees_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.employees_table)

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
        combobox.addItem("Select Branch", 0) # Default empty item
        for branch in branches:
            if branch.company_id == company_id: # Basic filtering
                combobox.addItem(f"{branch.name_en} ({branch.code})", branch.id)

    def load_employees(self):
        self.employees_table.setRowCount(0)
        employees = self.payroll_service.get_all_employees()
        self.employees_table.setRowCount(len(employees))
        for row, emp in enumerate(employees):
            company = self.company_service.get_company_by_id(emp.company_id)
            company_name = company.name_en if company else "Unknown Company"
            branch = self.branch_service.get_branch_by_id(emp.branch_id)
            branch_name = branch.name_en if branch else "Unknown Branch"

            self.employees_table.setItem(row, 0, QTableWidgetItem(str(emp.id)))
            self.employees_table.setItem(row, 1, QTableWidgetItem(company_name))
            self.employees_table.setItem(row, 2, QTableWidgetItem(branch_name))
            self.employees_table.setItem(row, 3, QTableWidgetItem(emp.first_name_ar or emp.first_name_en or ""))
            self.employees_table.setItem(row, 4, QTableWidgetItem(emp.last_name_ar or emp.last_name_en or ""))
            self.employees_table.setItem(row, 5, QTableWidgetItem(emp.position or ""))
            self.employees_table.setItem(row, 6, QTableWidgetItem(str(emp.hire_date) if emp.hire_date else ""))
            self.employees_table.setItem(row, 8, QTableWidgetItem(str(emp.hire_date)))
            self.employees_table.setItem(row, 9, QTableWidgetItem(str(emp.salary)))
            self.employees_table.setItem(row, 10, QTableWidgetItem("Yes" if emp.is_active else "No"))

    def add_employee(self):
        try:
            company_id = self.company_id_input.currentData()
            branch_id = self.branch_id_input.currentData()
            first_name = self.first_name_input.text()
            last_name = self.last_name_input.text()
            employee_code = self.employee_code_input.text()
            job_title = self.job_title_input.text()
            department = self.department_input.text()
            hire_date = self.hire_date_input.date().toPython()
            salary = Decimal(self.salary_input.value())
            is_active = self.is_active_input.isChecked()

            if not company_id or not branch_id or not first_name or not employee_code or not job_title or not hire_date or not salary:
                QMessageBox.warning(self, "Input Error", "Company, Branch, First Name, Employee Code, Job Title, Hire Date, and Salary are required.")
                return

            self.payroll_service.create_employee(
                company_id=company_id,
                branch_id=branch_id,
                first_name=first_name,
                last_name=last_name,
                employee_code=employee_code,
                job_title=job_title,
                department=department,
                hire_date=hire_date,
                salary=salary,
                is_active=is_active
            )
            self.clear_form()
            self.load_employees()
            QMessageBox.information(self, "Success", "Employee added successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.company_id_input.setCurrentIndex(0)
        self.branch_id_input.setCurrentIndex(0)
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.employee_code_input.clear()
        self.job_title_input.clear()
        self.department_input.clear()
        self.hire_date_input.setDate(QDate.currentDate())
        self.salary_input.setValue(0.0)
        self.is_active_input.setChecked(True)
