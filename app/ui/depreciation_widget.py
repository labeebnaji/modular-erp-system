from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QSpinBox, QFormLayout, QGroupBox, QHeaderView, QDoubleSpinBox
from PySide6.QtCore import QDate
from app.application.services import FixedAssetService, CompanyService # Added CompanyService
#from app.infrastructure.database import get_db # No longer needed
from decimal import Decimal

class DepreciationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fixed_asset_service = FixedAssetService()
        self.company_service = CompanyService() # Initialize CompanyService
        self.init_ui()
        self.load_depreciations()

    def init_ui(self):
        self.setWindowTitle("Depreciation")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Depreciation form
        form_group_box = QGroupBox("Depreciation Entry Details")
        form_layout = QFormLayout()

        self.company_id_input = QComboBox()
        self.load_companies_to_combobox(self.company_id_input)
        form_layout.addRow(QLabel("Company:"), self.company_id_input)

        self.branch_id_input = QComboBox()
        self.load_branches_to_combobox(self.branch_id_input, self.company_id_input.currentData())
        form_layout.addRow(QLabel("Branch:"), self.branch_id_input)

        self.fixed_asset_id_input = QComboBox()
        self.load_fixed_assets_to_combobox(self.fixed_asset_id_input)
        form_layout.addRow(QLabel("Fixed Asset:"), self.fixed_asset_id_input)

        self.depreciation_date_input = QDateEdit(QDate.currentDate())
        self.depreciation_date_input.setCalendarPopup(True)
        form_layout.addRow(QLabel("Depreciation Date:"), self.depreciation_date_input)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.00, 999999999.99)
        self.amount_input.setPrefix("$")
        # Icon placeholder: self.amount_input.addAction(QIcon("path/to/amount_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Amount:"), self.amount_input)

        add_button = QPushButton("Add Depreciation")
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        add_button.clicked.connect(self.add_depreciation)
        form_layout.addRow(add_button)

        form_group_box.setLayout(form_layout)
        main_layout.addWidget(form_group_box)

        # Depreciation table
        self.depreciation_table = QTableWidget()
        self.depreciation_table.setColumnCount(6) # Increased column count
        self.depreciation_table.setHorizontalHeaderLabels(["ID", "Company", "Branch", "Fixed Asset", "Depreciation Date", "Amount"])
        self.depreciation_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        main_layout.addWidget(self.depreciation_table)

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

    def load_fixed_assets_to_combobox(self, combobox):
        combobox.clear()
        fixed_assets = self.fixed_asset_service.get_all_fixed_assets()
        combobox.addItem("Select Fixed Asset", 0)
        for asset in fixed_assets:
            combobox.addItem(f"{asset.asset_name} (ID: {asset.id})", asset.id)

    def load_depreciations(self):
        self.depreciation_table.setRowCount(0)
        depreciations = self.fixed_asset_service.get_all_depreciations()
        self.depreciation_table.setRowCount(len(depreciations))
        for row, dep in enumerate(depreciations):
            company = self.company_service.get_company_by_id(dep.company_id)
            company_name = company.name_en if company else "Unknown Company"
            branch = self.company_service.get_branch_by_id(dep.branch_id)
            branch_name = branch.name_en if branch else "Unknown Branch"
            fixed_asset = self.fixed_asset_service.get_fixed_asset_by_id(dep.fixed_asset_id)
            fixed_asset_name = fixed_asset.asset_name if fixed_asset else "Unknown Asset"

            self.depreciation_table.setItem(row, 0, QTableWidgetItem(str(dep.id)))
            self.depreciation_table.setItem(row, 1, QTableWidgetItem(company_name))
            self.depreciation_table.setItem(row, 2, QTableWidgetItem(branch_name))
            self.depreciation_table.setItem(row, 3, QTableWidgetItem(fixed_asset_name))
            self.depreciation_table.setItem(row, 4, QTableWidgetItem(str(dep.depreciation_date)))
            self.depreciation_table.setItem(row, 5, QTableWidgetItem(str(dep.amount)))

    def add_depreciation(self):
        try:
            company_id = self.company_id_input.currentData()
            branch_id = self.branch_id_input.currentData()
            fixed_asset_id = self.fixed_asset_id_input.currentData()
            depreciation_date = self.depreciation_date_input.date().toPython()
            amount = Decimal(self.amount_input.value())

            if not company_id or not branch_id or not fixed_asset_id or not amount:
                QMessageBox.warning(self, "Input Error", "Company, Branch, Fixed Asset, Depreciation Date, and Amount are required.")
                return

            self.fixed_asset_service.create_depreciation(
                company_id=company_id,
                branch_id=branch_id,
                fixed_asset_id=fixed_asset_id,
                depreciation_date=depreciation_date,
                amount=amount
            )
            self.clear_form()
            self.load_depreciations()
            QMessageBox.information(self, "Success", "Depreciation added successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.company_id_input.setCurrentIndex(0)
        self.branch_id_input.setCurrentIndex(0)
        self.fixed_asset_id_input.setCurrentIndex(0)
        self.depreciation_date_input.setDate(QDate.currentDate())
        self.amount_input.setValue(0.0)
