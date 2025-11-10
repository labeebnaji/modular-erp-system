from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QSpinBox, QFormLayout, QGroupBox, QHeaderView, QCheckBox
from PySide6.QtCore import QDate
from app.application.services import IAMService, CompanyService # Added CompanyService
#from app.infrastructure.database import get_db # No longer needed
from werkzeug.security import generate_password_hash # Import for password hashing

class UserWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.iam_service = IAMService()
        self.company_service = CompanyService() # Initialize CompanyService
        self.init_ui()
        self.load_users()

    def init_ui(self):
        self.setWindowTitle("User Management")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # User form
        form_group_box = QGroupBox("User Details")
        form_layout = QFormLayout()

        self.company_id_input = QComboBox()
        self.load_companies_to_combobox(self.company_id_input)
        form_layout.addRow(QLabel("Company:"), self.company_id_input)

        self.branch_id_input = QComboBox()
        self.load_branches_to_combobox(self.branch_id_input, self.company_id_input.currentData())
        form_layout.addRow(QLabel("Branch:"), self.branch_id_input)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        # Icon placeholder: self.username_input.addAction(QIcon("path/to/username_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Username:"), self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Password")
        # Icon placeholder: self.password_input.addAction(QIcon("path/to/password_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Password:"), self.password_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        # Icon placeholder: self.email_input.addAction(QIcon("path/to/email_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Email:"), self.email_input)

        self.is_active_input = QCheckBox("Is Active")
        self.is_active_input.setChecked(True)
        form_layout.addRow(QLabel("Active:"), self.is_active_input)

        add_button = QPushButton("Add User")
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        add_button.clicked.connect(self.add_user)
        form_layout.addRow(add_button)

        form_group_box.setLayout(form_layout)
        main_layout.addWidget(form_group_box)

        # User table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(7) # Increased column count
        self.users_table.setHorizontalHeaderLabels(["ID", "Company", "Branch", "Username", "Email", "Active", "Created At"])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        main_layout.addWidget(self.users_table)

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

    def load_users(self):
        self.users_table.setRowCount(0)
        users = self.iam_service.get_all_users()
        self.users_table.setRowCount(len(users))
        for row, user in enumerate(users):
            company = self.company_service.get_company_by_id(user.company_id)
            company_name = company.name_en if company else "Unknown Company"
            branch = self.company_service.get_branch_by_id(user.branch_id)
            branch_name = branch.name_en if branch else "Unknown Branch"

            self.users_table.setItem(row, 0, QTableWidgetItem(str(user.id)))
            self.users_table.setItem(row, 1, QTableWidgetItem(company_name))
            self.users_table.setItem(row, 2, QTableWidgetItem(branch_name))
            self.users_table.setItem(row, 3, QTableWidgetItem(user.username))
            self.users_table.setItem(row, 4, QTableWidgetItem(user.email))
            self.users_table.setItem(row, 5, QTableWidgetItem("Yes" if user.is_active else "No"))
            self.users_table.setItem(row, 6, QTableWidgetItem(str(user.created_at.strftime('%Y-%m-%d %H:%M:%S'))))

    def add_user(self):
        try:
            company_id = self.company_id_input.currentData()
            branch_id = self.branch_id_input.currentData()
            username = self.username_input.text()
            password = self.password_input.text()
            email = self.email_input.text()
            is_active = self.is_active_input.isChecked()

            if not company_id or not branch_id or not username or not password or not email:
                QMessageBox.warning(self, "Input Error", "Company, Branch, Username, Password, and Email are required.")
                return

            hashed_password = generate_password_hash(password) # Hash the password

            self.iam_service.create_user(
                company_id=company_id,
                branch_id=branch_id,
                username=username,
                hashed_password=hashed_password,
                email=email,
                is_active=is_active
            )
            self.clear_form()
            self.load_users()
            QMessageBox.information(self, "Success", "User added successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.company_id_input.setCurrentIndex(0)
        self.branch_id_input.setCurrentIndex(0)
        self.username_input.clear()
        self.password_input.clear()
        self.email_input.clear()
        self.is_active_input.setChecked(True)
