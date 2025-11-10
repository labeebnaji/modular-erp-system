from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QDoubleSpinBox, QFormLayout, QGroupBox, QHeaderView
from app.application.services import TaxService, CompanyService # Added CompanyService
#from app.infrastructure.database import get_db # No longer needed
from decimal import Decimal

class TaxSettingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tax_service = TaxService()
        self.company_service = CompanyService() # Initialize CompanyService
        self.init_ui()
        self.load_tax_settings()

    def init_ui(self):
        self.setWindowTitle("Tax Settings")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Tax Setting form
        form_group_box = QGroupBox("Tax Setting Details")
        form_layout = QFormLayout()

        self.company_id_input = QComboBox()
        self.load_companies_to_combobox(self.company_id_input)
        form_layout.addRow(QLabel("Company:"), self.company_id_input)

        self.branch_id_input = QComboBox()
        self.load_branches_to_combobox(self.branch_id_input, self.company_id_input.currentData())
        form_layout.addRow(QLabel("Branch:"), self.branch_id_input)

        self.tax_name_input = QLineEdit()
        self.tax_name_input.setPlaceholderText("Tax Name (e.g., VAT, Sales Tax)")
        # Icon placeholder: self.tax_name_input.addAction(QIcon("path/to/tax_name_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Tax Name:"), self.tax_name_input)

        self.tax_rate_input = QDoubleSpinBox()
        self.tax_rate_input.setRange(0.00, 100.00)
        self.tax_rate_input.setSuffix("%")
        # Icon placeholder: self.tax_rate_input.addAction(QIcon("path/to/tax_rate_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Tax Rate:"), self.tax_rate_input)

        self.tax_type_input = QComboBox()
        self.tax_type_input.addItems(["Sales Tax", "Purchase Tax", "VAT"])
        form_layout.addRow(QLabel("Tax Type:"), self.tax_type_input)

        add_button = QPushButton("Add Tax Setting")
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        add_button.clicked.connect(self.add_tax_setting)
        form_layout.addRow(add_button)

        form_group_box.setLayout(form_layout)
        main_layout.addWidget(form_group_box)

        # Tax Settings table
        self.tax_settings_table = QTableWidget()
        self.tax_settings_table.setColumnCount(6) # Increased column count
        self.tax_settings_table.setHorizontalHeaderLabels(["ID", "Company", "Branch", "Tax Name", "Rate", "Type"])
        self.tax_settings_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        main_layout.addWidget(self.tax_settings_table)

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

    def load_tax_settings(self):
        self.tax_settings_table.setRowCount(0)
        settings = self.tax_service.get_all_tax_settings()
        self.tax_settings_table.setRowCount(len(settings))
        for row, setting in enumerate(settings):
            company = self.company_service.get_company_by_id(setting.company_id)
            company_name = company.name_en if company else "Unknown Company"
            branch = self.company_service.get_branch_by_id(setting.branch_id)
            branch_name = branch.name_en if branch else "Unknown Branch"

            self.tax_settings_table.setItem(row, 0, QTableWidgetItem(str(setting.id)))
            self.tax_settings_table.setItem(row, 1, QTableWidgetItem(company_name))
            self.tax_settings_table.setItem(row, 2, QTableWidgetItem(branch_name))
            self.tax_settings_table.setItem(row, 3, QTableWidgetItem(setting.tax_name))
            self.tax_settings_table.setItem(row, 4, QTableWidgetItem(str(setting.tax_rate)))
            self.tax_settings_table.setItem(row, 5, QTableWidgetItem(setting.tax_type))

    def add_tax_setting(self):
        try:
            company_id = self.company_id_input.currentData()
            branch_id = self.branch_id_input.currentData()
            tax_name = self.tax_name_input.text()
            tax_rate = Decimal(self.tax_rate_input.value())
            tax_type = self.tax_type_input.currentText()

            if not company_id or not branch_id or not tax_name or not tax_rate or not tax_type:
                QMessageBox.warning(self, "Input Error", "Company, Branch, Tax Name, Tax Rate, and Tax Type are required.")
                return

            self.tax_service.create_tax_setting(
                company_id=company_id,
                branch_id=branch_id,
                tax_name=tax_name,
                tax_rate=tax_rate,
                tax_type=tax_type
            )
            self.clear_form()
            self.load_tax_settings()
            QMessageBox.information(self, "Success", "Tax Setting added successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.company_id_input.setCurrentIndex(0)
        self.branch_id_input.setCurrentIndex(0)
        self.tax_name_input.clear()
        self.tax_rate_input.setValue(0.0)
        self.tax_type_input.setCurrentIndex(0)
