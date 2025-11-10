from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QSpinBox, QFormLayout, QGroupBox, QHeaderView, QCheckBox # Removed QDoubleSpinBox
from PySide6.QtCore import QDate
from app.application.services import CostCenterProjectService, CompanyService # Added CompanyService
#from app.infrastructure.database import get_db # No longer needed
from decimal import Decimal

class ProjectWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cost_center_project_service = CostCenterProjectService()
        self.company_service = CompanyService() # Initialize CompanyService
        self.init_ui()
        self.clear_form() # Call clear_form to set the initial code
        self.load_projects()

    def init_ui(self):
        self.setWindowTitle("Project Management")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Project form
        form_group_box = QGroupBox("Project Details")
        form_layout = QFormLayout()

        self.company_id_input = QComboBox()
        self.load_companies_to_combobox(self.company_id_input)
        form_layout.addRow(QLabel("Company:"), self.company_id_input)

        # self.branch_id_input = QComboBox() # Removed branch_id as it's not in Project model
        # self.load_branches_to_combobox(self.branch_id_input, self.company_id_input.currentData())
        # form_layout.addRow(QLabel("Branch:"), self.branch_id_input)

        self.name_en_input = QLineEdit()
        self.name_en_input.setPlaceholderText("Project Name (English)")
        # Icon placeholder: self.name_en_input.addAction(QIcon("path/to/project_name_en_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Project Name (EN):"), self.name_en_input)

        self.name_ar_input = QLineEdit()
        self.name_ar_input.setPlaceholderText("Project Name (Arabic)")
        # Icon placeholder: self.name_ar_input.addAction(QIcon("path/to/project_name_ar_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Project Name (AR):"), self.name_ar_input)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Project Code")
        self.code_input.setReadOnly(True) # Make code field read-only
        # Icon placeholder: self.code_input.addAction(QIcon("path/to/project_code_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Code:"), self.code_input)

        # self.description_input = QLineEdit() # Removed description as it's not in Project model
        # self.description_input.setPlaceholderText("Description")
        # # Icon placeholder: self.description_input.addAction(QIcon("path/to/description_icon.png"), QLineEdit.LeadingPosition)
        # form_layout.addRow(QLabel("Description:"), self.description_input)

        self.start_date_input = QDateEdit(QDate.currentDate())
        self.start_date_input.setCalendarPopup(True)
        form_layout.addRow(QLabel("Start Date:"), self.start_date_input)

        self.end_date_input = QDateEdit(QDate.currentDate().addMonths(6))
        self.end_date_input.setCalendarPopup(True)
        form_layout.addRow(QLabel("End Date:"), self.end_date_input)

        # self.budget_input = QDoubleSpinBox() # Removed budget as it's not in Project model
        # self.budget_input.setRange(0.00, 999999999.99)
        # self.budget_input.setPrefix("$")
        # form_layout.addRow(QLabel("Budget:"), self.budget_input)

        self.is_active_input = QCheckBox("Is Active")
        self.is_active_input.setChecked(True)
        form_layout.addRow(QLabel("Active:"), self.is_active_input)

        add_button = QPushButton("Add Project")
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        add_button.clicked.connect(self.add_project)
        form_layout.addRow(add_button)

        form_group_box.setLayout(form_layout)
        main_layout.addWidget(form_group_box)

        # Project table
        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(7) # Updated column count based on Project model
        self.projects_table.setHorizontalHeaderLabels(["ID", "Company", "Name (EN)", "Name (AR)", "Code", "Start Date", "End Date", "Active"]) # Updated headers
        self.projects_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        main_layout.addWidget(self.projects_table)

        main_layout.addStretch(1) # Add stretch to push content upwards and fill remaining space

        self.setLayout(main_layout)

    def load_companies_to_combobox(self, combobox):
        combobox.clear()
        companies = self.company_service.get_all_companies()
        combobox.addItem("Select Company", 0) # Default empty item
        for company in companies:
            combobox.addItem(f"{company.name_en} ({company.code})", company.id)

    # Removed load_branches_to_combobox as branch_id is not in Project model
    # def load_branches_to_combobox(self, combobox, company_id):
    #     combobox.clear()
    #     branches = self.company_service.get_all_branches()
    #     combobox.addItem("Select Branch", 0)
    #     for branch in branches:
    #         if branch.company_id == company_id: # Basic filtering
    #             combobox.addItem(f"{branch.name_en} ({branch.code})", branch.id)

    def load_projects(self):
        self.projects_table.setRowCount(0)
        projects = self.cost_center_project_service.get_all_projects()
        self.projects_table.setRowCount(len(projects))
        for row, project in enumerate(projects):
            company = self.company_service.get_company_by_id(project.company_id)
            company_name = company.name_en if company else "Unknown Company"
            # Removed branch as it's not in Project model
            # branch = self.company_service.get_branch_by_id(project.branch_id)
            # branch_name = branch.name_en if branch else "Unknown Branch"

            self.projects_table.setItem(row, 0, QTableWidgetItem(str(project.id)))
            self.projects_table.setItem(row, 1, QTableWidgetItem(company_name))
            # Removed branch_name from table
            self.projects_table.setItem(row, 2, QTableWidgetItem(project.name_en))
            self.projects_table.setItem(row, 3, QTableWidgetItem(project.name_ar))
            self.projects_table.setItem(row, 4, QTableWidgetItem(str(project.code))) # Ensure code is displayed as string
            # Removed description from table
            self.projects_table.setItem(row, 5, QTableWidgetItem(str(project.start_date)))
            self.projects_table.setItem(row, 6, QTableWidgetItem(str(project.end_date)))
            # Removed budget from table
            self.projects_table.setItem(row, 7, QTableWidgetItem("Yes" if project.is_active else "No")) # Shifted index

    def add_project(self):
        try:
            company_id = self.company_id_input.currentData()
            # branch_id = self.branch_id_input.currentData() # Removed branch_id
            name_en = self.name_en_input.text()
            name_ar = self.name_ar_input.text()
            # code = self.code_input.text() # Removed, as it's auto-generated
            # description = self.description_input.text() # Removed description
            start_date = self.start_date_input.date().toPython()
            end_date = self.end_date_input.date().toPython()
            # budget = Decimal(self.budget_input.value()) # Removed budget
            is_active = self.is_active_input.isChecked()

            if not company_id or not name_en or not start_date or not end_date:
                QMessageBox.warning(self, "Input Error", "Company, English Name, Start Date, and End Date are required.")
                return

            self.cost_center_project_service.create_project(
                company_id=company_id,
                name_en=name_en,
                name_ar=name_ar,
                start_date=start_date,
                end_date=end_date,
                is_active=is_active
            )
            self.clear_form()
            self.load_projects()
            QMessageBox.information(self, "Success", "Project added successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.company_id_input.setCurrentIndex(0)
        # self.branch_id_input.setCurrentIndex(0) # Removed branch_id
        self.name_en_input.clear()
        self.name_ar_input.clear()
        next_code = self.cost_center_project_service.get_next_project_code()
        self.code_input.setText(str(next_code)) # Set next auto-incrementing code
        # self.description_input.clear() # Removed description
        self.start_date_input.setDate(QDate.currentDate())
        self.end_date_input.setDate(QDate.currentDate().addMonths(6))
        # self.budget_input.setValue(0.0) # Removed budget
        self.is_active_input.setChecked(True)
