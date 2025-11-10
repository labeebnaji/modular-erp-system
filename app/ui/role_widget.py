from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QFormLayout, QGroupBox, QHeaderView, QCheckBox
from app.application.services import IAMService, CompanyService # Added CompanyService
#from app.infrastructure.database import get_db # No longer needed

class RoleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.iam_service = IAMService()
        self.company_service = CompanyService() # Initialize CompanyService
        self.init_ui()
        self.load_roles()

    def init_ui(self):
        self.setWindowTitle("Role Management")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Role form
        form_group_box = QGroupBox("Role Details")
        form_layout = QFormLayout()

        self.company_id_input = QComboBox()
        self.load_companies_to_combobox(self.company_id_input)
        form_layout.addRow(QLabel("Company:"), self.company_id_input)

        self.branch_id_input = QComboBox()
        self.load_branches_to_combobox(self.branch_id_input, self.company_id_input.currentData())
        form_layout.addRow(QLabel("Branch:"), self.branch_id_input)

        self.role_name_input = QLineEdit()
        self.role_name_input.setPlaceholderText("Role Name (e.g., Admin, User)")
        # Icon placeholder: self.role_name_input.addAction(QIcon("path/to/role_name_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Role Name:"), self.role_name_input)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Description")
        # Icon placeholder: self.description_input.addAction(QIcon("path/to/description_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Description:"), self.description_input)

        self.is_active_input = QCheckBox("Is Active")
        self.is_active_input.setChecked(True)
        form_layout.addRow(QLabel("Active:"), self.is_active_input)

        add_button = QPushButton("Add Role")
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        add_button.clicked.connect(self.add_role)
        form_layout.addRow(add_button)

        form_group_box.setLayout(form_layout)
        main_layout.addWidget(form_group_box)

        # Role table
        self.roles_table = QTableWidget()
        self.roles_table.setColumnCount(6) # Increased column count
        self.roles_table.setHorizontalHeaderLabels(["ID", "Company", "Branch", "Role Name", "Description", "Active"])
        self.roles_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        main_layout.addWidget(self.roles_table)

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

    def load_roles(self):
        self.roles_table.setRowCount(0)
        roles = self.iam_service.get_all_roles()
        self.roles_table.setRowCount(len(roles))
        for row, role in enumerate(roles):
            company = self.company_service.get_company_by_id(role.company_id)
            company_name = company.name_en if company else "Unknown Company"
            branch = self.company_service.get_branch_by_id(role.branch_id)
            branch_name = branch.name_en if branch else "Unknown Branch"

            self.roles_table.setItem(row, 0, QTableWidgetItem(str(role.id)))
            self.roles_table.setItem(row, 1, QTableWidgetItem(company_name))
            self.roles_table.setItem(row, 2, QTableWidgetItem(branch_name))
            self.roles_table.setItem(row, 3, QTableWidgetItem(role.name))
            self.roles_table.setItem(row, 4, QTableWidgetItem(role.description))
            self.roles_table.setItem(row, 5, QTableWidgetItem("Yes" if role.is_active else "No"))

    def add_role(self):
        try:
            company_id = self.company_id_input.currentData()
            branch_id = self.branch_id_input.currentData()
            role_name = self.role_name_input.text()
            description = self.description_input.text()
            is_active = self.is_active_input.isChecked()

            if not company_id or not branch_id or not role_name:
                QMessageBox.warning(self, "Input Error", "Company, Branch, and Role Name are required.")
                return

            self.iam_service.create_role(
                company_id=company_id,
                branch_id=branch_id,
                name=role_name,
                description=description,
                is_active=is_active
            )
            self.clear_form()
            self.load_roles()
            QMessageBox.information(self, "Success", "Role added successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.company_id_input.setCurrentIndex(0)
        self.branch_id_input.setCurrentIndex(0)
        self.role_name_input.clear()
        self.description_input.clear()
        self.is_active_input.setChecked(True)
