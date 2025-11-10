from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QSpinBox, QFormLayout, QGroupBox, QHeaderView, QDoubleSpinBox
from PySide6.QtCore import QDate
from app.application.services import FixedAssetService, CompanyService # Added CompanyService
#from app.infrastructure.database import get_db # No longer needed
from decimal import Decimal

class FixedAssetWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fixed_asset_service = FixedAssetService()
        self.company_service = CompanyService() # Initialize CompanyService
        self.init_ui()
        self.load_fixed_assets()

    def init_ui(self):
        self.setWindowTitle("Fixed Assets")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Fixed Asset form
        form_group_box = QGroupBox("Fixed Asset Details")
        form_layout = QFormLayout()

        self.company_id_input = QComboBox()
        self.load_companies_to_combobox(self.company_id_input)
        form_layout.addRow(QLabel("Company:"), self.company_id_input)

        self.branch_id_input = QComboBox()
        self.load_branches_to_combobox(self.branch_id_input, self.company_id_input.currentData())
        form_layout.addRow(QLabel("Branch:"), self.branch_id_input)

        self.asset_name_input = QLineEdit()
        self.asset_name_input.setPlaceholderText("Asset Name")
        # Icon placeholder: self.asset_name_input.addAction(QIcon("path/to/asset_name_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Asset Name:"), self.asset_name_input)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Description")
        # Icon placeholder: self.description_input.addAction(QIcon("path/to/description_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Description:"), self.description_input)

        self.acquisition_date_input = QDateEdit(QDate.currentDate())
        self.acquisition_date_input.setCalendarPopup(True)
        form_layout.addRow(QLabel("Acquisition Date:"), self.acquisition_date_input)

        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0.00, 999999999.99)
        self.cost_input.setPrefix("$")
        # Icon placeholder: self.cost_input.addAction(QIcon("path/to/cost_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Cost:"), self.cost_input)

        self.salvage_value_input = QDoubleSpinBox()
        self.salvage_value_input.setRange(0.00, 999999999.99)
        self.salvage_value_input.setPrefix("$")
        form_layout.addRow(QLabel("Salvage Value:"), self.salvage_value_input)

        self.useful_life_input = QSpinBox()
        self.useful_life_input.setRange(1, 100)
        self.useful_life_input.setSuffix(" years")
        form_layout.addRow(QLabel("Useful Life:"), self.useful_life_input)

        self.depreciation_method_input = QComboBox()
        self.depreciation_method_input.addItems(["Straight-Line", "Declining Balance"])
        form_layout.addRow(QLabel("Depreciation Method:"), self.depreciation_method_input)

        add_button = QPushButton("Add Fixed Asset")
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        add_button.clicked.connect(self.add_fixed_asset)
        form_layout.addRow(add_button)

        form_group_box.setLayout(form_layout)
        main_layout.addWidget(form_group_box)

        # Fixed Assets table
        self.fixed_assets_table = QTableWidget()
        self.fixed_assets_table.setColumnCount(10) # Increased column count
        self.fixed_assets_table.setHorizontalHeaderLabels(["ID", "Company", "Branch", "Asset Name", "Description", "Acquisition Date", "Cost", "Salvage Value", "Useful Life", "Depreciation Method"])
        self.fixed_assets_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        main_layout.addWidget(self.fixed_assets_table)

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

    def load_fixed_assets(self):
        self.fixed_assets_table.setRowCount(0)
        assets = self.fixed_asset_service.get_all_fixed_assets()
        self.fixed_assets_table.setRowCount(len(assets))
        for row, asset in enumerate(assets):
            company = self.company_service.get_company_by_id(asset.company_id)
            company_name = company.name_en if company else "Unknown Company"
            branch = self.company_service.get_branch_by_id(asset.branch_id)
            branch_name = branch.name_en if branch else "Unknown Branch"

            self.fixed_assets_table.setItem(row, 0, QTableWidgetItem(str(asset.id)))
            self.fixed_assets_table.setItem(row, 1, QTableWidgetItem(company_name))
            self.fixed_assets_table.setItem(row, 2, QTableWidgetItem(branch_name))
            self.fixed_assets_table.setItem(row, 3, QTableWidgetItem(asset.asset_name))
            self.fixed_assets_table.setItem(row, 4, QTableWidgetItem(asset.description))
            self.fixed_assets_table.setItem(row, 5, QTableWidgetItem(str(asset.acquisition_date)))
            self.fixed_assets_table.setItem(row, 6, QTableWidgetItem(str(asset.cost)))
            self.fixed_assets_table.setItem(row, 7, QTableWidgetItem(str(asset.salvage_value)))
            self.fixed_assets_table.setItem(row, 8, QTableWidgetItem(str(asset.useful_life)))
            self.fixed_assets_table.setItem(row, 9, QTableWidgetItem(asset.depreciation_method))

    def add_fixed_asset(self):
        try:
            company_id = self.company_id_input.currentData()
            branch_id = self.branch_id_input.currentData()
            asset_name = self.asset_name_input.text()
            description = self.description_input.text()
            acquisition_date = self.acquisition_date_input.date().toPython()
            cost = Decimal(self.cost_input.value())
            salvage_value = Decimal(self.salvage_value_input.value())
            useful_life = self.useful_life_input.value()
            depreciation_method = self.depreciation_method_input.currentText()

            if not company_id or not branch_id or not asset_name or not acquisition_date or not cost or not useful_life or not depreciation_method:
                QMessageBox.warning(self, "Input Error", "Company, Branch, Asset Name, Acquisition Date, Cost, Useful Life, and Depreciation Method are required.")
                return

            self.fixed_asset_service.create_fixed_asset(
                company_id=company_id,
                branch_id=branch_id,
                asset_name=asset_name,
                description=description,
                acquisition_date=acquisition_date,
                cost=cost,
                salvage_value=salvage_value,
                useful_life=useful_life,
                depreciation_method=depreciation_method
            )
            self.clear_form()
            self.load_fixed_assets()
            QMessageBox.information(self, "Success", "Fixed Asset added successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.company_id_input.setCurrentIndex(0)
        self.branch_id_input.setCurrentIndex(0)
        self.asset_name_input.clear()
        self.description_input.clear()
        self.acquisition_date_input.setDate(QDate.currentDate())
        self.cost_input.setValue(0.0)
        self.salvage_value_input.setValue(0.0)
        self.useful_life_input.setValue(1)
        self.depreciation_method_input.setCurrentIndex(0)
