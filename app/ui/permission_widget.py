from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QFormLayout, QGroupBox, QHeaderView, QCheckBox
from app.application.services import IAMService, CompanyService # Added CompanyService
#from app.infrastructure.database import get_db # No longer needed

class PermissionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.iam_service = IAMService()
        self.company_service = CompanyService() # Initialize CompanyService
        self.init_ui()
        self.load_permissions()

    def init_ui(self):
        self.setWindowTitle("Permission Management")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Permission form
        form_group_box = QGroupBox("Permission Details")
        form_layout = QFormLayout()

        self.company_id_input = QComboBox()
        self.load_companies_to_combobox(self.company_id_input)
        form_layout.addRow(QLabel("Company:"), self.company_id_input)

        self.branch_id_input = QComboBox()
        self.load_branches_to_combobox(self.branch_id_input, self.company_id_input.currentData())
        form_layout.addRow(QLabel("Branch:"), self.branch_id_input)

        self.permission_name_input = QLineEdit()
        self.permission_name_input.setPlaceholderText("Permission Name (e.g., create_user, view_report)")
        # Icon placeholder: self.permission_name_input.addAction(QIcon("path/to/permission_name_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Permission Name:"), self.permission_name_input)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Description")
        # Icon placeholder: self.description_input.addAction(QIcon("path/to/description_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Description:"), self.description_input)

        self.is_active_input = QCheckBox("Is Active")
        self.is_active_input.setChecked(True)
        form_layout.addRow(QLabel("Active:"), self.is_active_input)

        add_button = QPushButton("Add Permission")
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        add_button.clicked.connect(self.add_permission)
        form_layout.addRow(add_button)

        form_group_box.setLayout(form_layout)
        main_layout.addWidget(form_group_box)

        # Permission table
        self.permissions_table = QTableWidget()
        self.permissions_table.setColumnCount(6) # Increased column count
        self.permissions_table.setHorizontalHeaderLabels(["ID", "Company", "Branch", "Permission Name", "Description", "Active"])
        self.permissions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        main_layout.addWidget(self.permissions_table)

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

    def load_permissions(self):
        self.permissions_table.setRowCount(0)
        permissions = self.iam_service.get_all_permissions()
        self.permissions_table.setRowCount(len(permissions))
        for row, permission in enumerate(permissions):
            company = self.company_service.get_company_by_id(permission.company_id)
            company_name = company.name_en if company else "Unknown Company"
            branch = self.company_service.get_branch_by_id(permission.branch_id)
            branch_name = branch.name_en if branch else "Unknown Branch"

            self.permissions_table.setItem(row, 0, QTableWidgetItem(str(permission.id)))
            self.permissions_table.setItem(row, 1, QTableWidgetItem(company_name))
            self.permissions_table.setItem(row, 2, QTableWidgetItem(branch_name))
            self.permissions_table.setItem(row, 3, QTableWidgetItem(permission.name))
            self.permissions_table.setItem(row, 4, QTableWidgetItem(permission.description))
            self.permissions_table.setItem(row, 5, QTableWidgetItem("Yes" if permission.is_active else "No"))

    def add_permission(self):
        try:
            company_id = self.company_id_input.currentData()
            branch_id = self.branch_id_input.currentData()
            permission_name = self.permission_name_input.text()
            description = self.description_input.text()
            is_active = self.is_active_input.isChecked()

            if not company_id or not branch_id or not permission_name:
                QMessageBox.warning(self, "Input Error", "Company, Branch, and Permission Name are required.")
                return

            self.iam_service.create_permission(
                company_id=company_id,
                branch_id=branch_id,
                name=permission_name,
                description=description,
                is_active=is_active
            )
            self.clear_form()
            self.load_permissions()
            QMessageBox.information(self, "Success", "Permission added successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.company_id_input.setCurrentIndex(0)
        self.branch_id_input.setCurrentIndex(0)
        self.permission_name_input.clear()
        self.description_input.clear()
        self.is_active_input.setChecked(True)
