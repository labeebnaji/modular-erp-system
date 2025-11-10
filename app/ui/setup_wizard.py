from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QFormLayout, QTabWidget, QWidget, QCheckBox
from PySide6.QtCore import Qt
from decimal import Decimal
from werkzeug.security import generate_password_hash # Import generate_password_hash

from app.application.services import IAMService, CompanyService, CurrencyService, BranchService, WarehouseService # Import necessary services
from app.domain.models import Currency # Import Currency model

class SetupWizard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Initial System Setup")
        self.setFixedSize(600, 500)

        self.iam_service = IAMService()
        self.company_service = CompanyService()
        self.currency_service = CurrencyService()
        self.branch_service = BranchService() # New
        self.warehouse_service = WarehouseService() # New
        
        # Ensure default currencies are created before UI is built and populates combo
        self._create_default_currencies_if_not_exist() # Create without company_id initially

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        # self._create_user_tab()
        self._create_company_tab()
        self._create_branches_warehouses_tab() # New tab for branches and warehouses
        # self._create_currencies_tab()
        # self._create_loyalty_tab()
        
        self._populate_currencies_combo() # Populate after currencies are created and tabs exist

        self.save_button = QPushButton("Save Setup and Start System")
        self.save_button.clicked.connect(self._save_setup)
        self.main_layout.addWidget(self.save_button)

    # Removed _create_user_tab

    def _create_company_tab(self):
        company_tab = QWidget()
        layout = QFormLayout(company_tab)

        self.company_name_ar_input = QLineEdit()
        self.company_name_en_input = QLineEdit()
        self.company_phone_input = QLineEdit()
        self.company_email_input = QLineEdit()
        self.company_address_input = QLineEdit()
        self.base_currency_combo = QComboBox()
        
        # Admin User fields - moved from _create_user_tab
        self.admin_username_input = QLineEdit()
        self.admin_password_input = QLineEdit()
        self.admin_password_input.setEchoMode(QLineEdit.Password)
        self.admin_email_input = QLineEdit()

        layout.addRow(QLabel("Company Name (Arabic - Required):"), self.company_name_ar_input)
        layout.addRow(QLabel("Company Name (English):"), self.company_name_en_input)
        layout.addRow(QLabel("Phone Number:"), self.company_phone_input)
        layout.addRow(QLabel("Email:"), self.company_email_input)
        layout.addRow(QLabel("Address:"), self.company_address_input)
        layout.addRow(QLabel("Base Currency (Required):"), self.base_currency_combo)
        layout.addRow(QLabel("Admin Username (Required):"), self.admin_username_input)
        layout.addRow(QLabel("Admin Password (Required):"), self.admin_password_input)
        layout.addRow(QLabel("Admin Email:"), self.admin_email_input)

        self.tab_widget.addTab(company_tab, "Company Setup")

    def _create_branches_warehouses_tab(self):
        branches_warehouses_tab = QWidget()
        layout = QVBoxLayout(branches_warehouses_tab)

        # Branches Section
        branch_label = QLabel("Branches (at least one required):")
        layout.addWidget(branch_label)
        
        self.branch_name_ar_input = QLineEdit()
        self.branch_name_en_input = QLineEdit()
        self.branch_address_input = QLineEdit()
        self.branch_phone_input = QLineEdit()
        # Removed self.branch_email_input
        self.branch_base_currency_combo = QComboBox()

        branch_form_layout = QFormLayout()
        branch_form_layout.addRow(QLabel("Branch Name (Arabic - Required):"), self.branch_name_ar_input)
        branch_form_layout.addRow(QLabel("Branch Name (English):"), self.branch_name_en_input)
        branch_form_layout.addRow(QLabel("Address:"), self.branch_address_input)
        branch_form_layout.addRow(QLabel("Phone Number:"), self.branch_phone_input)
        # Removed email field from UI
        branch_form_layout.addRow(QLabel("Base Currency (Required):"), self.branch_base_currency_combo)
        layout.addLayout(branch_form_layout)

        # Warehouses Section
        warehouse_label = QLabel("Warehouses (at least one required):")
        layout.addWidget(warehouse_label)

        self.warehouse_name_ar_input = QLineEdit()
        self.warehouse_name_en_input = QLineEdit()
        self.warehouse_location_input = QLineEdit()
        self.warehouse_base_currency_combo = QComboBox()

        warehouse_form_layout = QFormLayout()
        warehouse_form_layout.addRow(QLabel("Warehouse Name (Arabic - Required):"), self.warehouse_name_ar_input)
        warehouse_form_layout.addRow(QLabel("Warehouse Name (English):"), self.warehouse_name_en_input)
        warehouse_form_layout.addRow(QLabel("Location:"), self.warehouse_location_input)
        warehouse_form_layout.addRow(QLabel("Base Currency (Required):"), self.warehouse_base_currency_combo)
        layout.addLayout(warehouse_form_layout)

        self.tab_widget.addTab(branches_warehouses_tab, "Branches & Warehouses Setup")

    # Removed _create_currencies_tab

    # Removed _create_loyalty_tab

    # Removed _toggle_loyalty_fields

    def _populate_currencies_combo(self):
        self.base_currency_combo.clear()
        self.branch_base_currency_combo.clear()
        self.warehouse_base_currency_combo.clear()

        self.base_currency_combo.addItem("Select Currency", -1) # Add a placeholder
        self.branch_base_currency_combo.addItem("Select Currency", -1)
        self.warehouse_base_currency_combo.addItem("Select Currency", -1)

        currencies = self.currency_service.get_all_currencies() # Fetch all currencies
        for currency in currencies:
            self.base_currency_combo.addItem(f"{currency.name_en} ({currency.code})", currency.id)
            self.branch_base_currency_combo.addItem(f"{currency.name_en} ({currency.code})", currency.id)
            self.warehouse_base_currency_combo.addItem(f"{currency.name_en} ({currency.code})", currency.id)

    def _save_setup(self):
        # 1. Validate Company and Admin User Data
        company_name_ar = self.company_name_ar_input.text()
        company_name_en = self.company_name_en_input.text()
        admin_username = self.admin_username_input.text()
        admin_password = self.admin_password_input.text()
        selected_company_currency_id = self.base_currency_combo.currentData()

        if not company_name_ar:
            QMessageBox.warning(self, "Input Error", "Company Name (Arabic) is required.")
            self.tab_widget.setCurrentIndex(0) # Switch to Company tab
            return
        if not company_name_en: # Company Name (English) is now required
            QMessageBox.warning(self, "Input Error", "Company Name (English) is required.")
            self.tab_widget.setCurrentIndex(0)
            return
        if not admin_username or not admin_password:
            QMessageBox.warning(self, "Input Error", "Admin Username and Password are required.")
            self.tab_widget.setCurrentIndex(0)
            return
        if selected_company_currency_id == -1 or selected_company_currency_id is None:
            QMessageBox.warning(self, "Input Error", "Please select a Base Currency for the Company.")
            self.tab_widget.setCurrentIndex(0)
            return

        # 2. Validate Branch Data
        branch_name_ar = self.branch_name_ar_input.text()
        selected_branch_currency_id = self.branch_base_currency_combo.currentData()

        if not branch_name_ar:
            QMessageBox.warning(self, "Input Error", "At least one Branch Name (Arabic) is required.")
            self.tab_widget.setCurrentIndex(1) # Switch to Branches & Warehouses tab
            return
        if selected_branch_currency_id == -1 or selected_branch_currency_id is None:
            QMessageBox.warning(self, "Input Error", "Please select a Base Currency for the Branch.")
            self.tab_widget.setCurrentIndex(1)
            return
        
        # 3. Validate Warehouse Data
        warehouse_name_ar = self.warehouse_name_ar_input.text()
        selected_warehouse_currency_id = self.warehouse_base_currency_combo.currentData()

        if not warehouse_name_ar:
            QMessageBox.warning(self, "Input Error", "At least one Warehouse Name (Arabic) is required.")
            self.tab_widget.setCurrentIndex(1)
            return
        if selected_warehouse_currency_id == -1 or selected_warehouse_currency_id is None:
            QMessageBox.warning(self, "Input Error", "Please select a Base Currency for the Warehouse.")
            self.tab_widget.setCurrentIndex(1)
            return

        # Hash the admin password before storing
        admin_password_hash = generate_password_hash(admin_password)

        try:
            # 4. Create Company with Admin User details
            new_company = self.company_service.create_company(
                name_ar=company_name_ar,
                name_en=self.company_name_en_input.text(),
                # Removed base_currency_id from company, as currencies are now branch/warehouse level
                phone_number=self.company_phone_input.text(),
                email=self.company_email_input.text(),
                address=self.company_address_input.text(),
                admin_username=admin_username,
                admin_password_hash=admin_password_hash,
                created_by=1 # Will be updated to use the created admin user ID later
            )
            new_company_id = new_company.id

            # 5. Create Admin User linked to the new company
            admin_user = self.iam_service.create_user(
                username=admin_username,
                password=admin_password, # Password will be hashed internally by service
                email=self.admin_email_input.text(),
                full_name_ar=f"مسؤول {company_name_ar}",
                full_name_en=f"Admin {self.company_name_en_input.text()}",
                company_id=new_company_id
            )
            # Update created_by for company to the actual admin_user_id
            self.company_service.update_company_created_by(new_company_id, admin_user.id)

            # 6. Create Default Branch
            new_branch = self.branch_service.create_branch( # Corrected service call
                company_id=new_company_id,
                name_ar=branch_name_ar,
                name_en=self.branch_name_en_input.text(),
                address=self.branch_address_input.text(),
                phone_number=self.branch_phone_input.text(),
                # Removed email from branch creation
                base_currency_id=selected_branch_currency_id,
                created_by=admin_user.id
            )
            new_branch_id = new_branch.id

            # 7. Create Default Warehouse
            self.warehouse_service.create_warehouse( # Corrected service call
                company_id=new_company_id,
                branch_id=new_branch_id,
                name_ar=warehouse_name_ar,
                name_en=self.warehouse_name_en_input.text(),
                location=self.warehouse_location_input.text(),
                base_currency_id=selected_warehouse_currency_id,
                created_by=admin_user.id
            )

            QMessageBox.information(self, "Setup Complete", "System setup successfully!")
            self.accept() # Close the dialog if setup is successful

        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Setup Error: {e}")
            return
        except Exception as e:
            QMessageBox.critical(self, "Critical Error", f"An unexpected error occurred during setup: {e}")
            return

    def _create_default_currencies_if_not_exist(self):
        # This function creates default currencies if they don't exist.
        default_currencies = [
            {"name_ar": "ريال سعودي", "name_en": "SAR", "code": "SAR", "symbol": "﷼", "exchange_rate": 1.0},
            {"name_ar": "ريال يمني", "name_en": "YER", "code": "YER", "symbol": "﷼", "exchange_rate": 0.004},
            {"name_ar": "دولار أمريكي", "name_en": "USD", "code": "USD", "symbol": "$", "exchange_rate": 3.75} 
        ]
        
        for curr_data in default_currencies:
            existing_currency = self.currency_service.get_currency_by_code(code=curr_data["code"])
            if not existing_currency:
                try:
                    self.currency_service.create_currency(**curr_data)
                    print(f"Default currency {curr_data['code']} created.")
                except Exception as e:
                    print(f"Error creating default currency {curr_data['code']}: {e}")

    # Removed _link_currencies_to_company
