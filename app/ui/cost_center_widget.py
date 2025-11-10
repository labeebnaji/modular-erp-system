from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QFormLayout, QGroupBox, QHeaderView, QCheckBox
from app.application.services import CostCenterProjectService, CompanyService # Added CompanyService
#from app.infrastructure.database import get_db # No longer needed

class CostCenterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cost_center_project_service = CostCenterProjectService()
        self.company_service = CompanyService() # Initialize CompanyService
        self.init_ui()
        self.clear_form() # Call clear_form to set the initial code
        self.load_cost_centers()

    def init_ui(self):
        self.setWindowTitle("Cost Center Management")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Cost Center form
        form_group_box = QGroupBox("Cost Center Details")
        form_layout = QFormLayout()

        self.company_id_input = QComboBox()
        self.load_companies_to_combobox(self.company_id_input)
        form_layout.addRow(QLabel("Company:"), self.company_id_input)

        self.branch_id_input = QComboBox()
        self.load_branches_to_combobox(self.branch_id_input, self.company_id_input.currentData())
        form_layout.addRow(QLabel("Branch:"), self.branch_id_input)

        self.name_en_input = QLineEdit()
        self.name_en_input.setPlaceholderText("Cost Center Name (English)")
        # Icon placeholder: self.name_en_input.addAction(QIcon("path/to/cost_center_name_en_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Cost Center Name (EN):"), self.name_en_input)

        self.name_ar_input = QLineEdit()
        self.name_ar_input.setPlaceholderText("Cost Center Name (Arabic)")
        # Icon placeholder: self.name_ar_input.addAction(QIcon("path/to/cost_center_name_ar_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Cost Center Name (AR):"), self.name_ar_input)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Cost Center Code")
        self.code_input.setReadOnly(True) # Make code field read-only
        # Icon placeholder: self.code_input.addAction(QIcon("path/to/cost_center_code_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Code:"), self.code_input)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Description")
        # Icon placeholder: self.description_input.addAction(QIcon("path/to/description_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Description:"), self.description_input)

        self.is_active_input = QCheckBox("Is Active")
        self.is_active_input.setChecked(True)
        form_layout.addRow(QLabel("Active:"), self.is_active_input)

        add_button = QPushButton("Add Cost Center")
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        add_button.clicked.connect(self.add_cost_center)
        form_layout.addRow(add_button)

        form_group_box.setLayout(form_layout)
        main_layout.addWidget(form_group_box)

        # Cost Center table
        self.cost_centers_table = QTableWidget()
        self.cost_centers_table.setColumnCount(8) # Increased column count
        self.cost_centers_table.setHorizontalHeaderLabels(["ID", "Company", "Branch", "Name (EN)", "Name (AR)", "Code", "Description", "Active"])
        self.cost_centers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        main_layout.addWidget(self.cost_centers_table)

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

    def load_cost_centers(self):
        self.cost_centers_table.setRowCount(0)
        cost_centers = self.cost_center_project_service.get_all_cost_centers()
        self.cost_centers_table.setRowCount(len(cost_centers))
        for row, cc in enumerate(cost_centers):
            company = self.company_service.get_company_by_id(cc.company_id)
            company_name = company.name_en if company else "Unknown Company"
            branch = self.company_service.get_branch_by_id(cc.branch_id)
            branch_name = branch.name_en if branch else "Unknown Branch"

            self.cost_centers_table.setItem(row, 0, QTableWidgetItem(str(cc.id)))
            self.cost_centers_table.setItem(row, 1, QTableWidgetItem(company_name))
            self.cost_centers_table.setItem(row, 2, QTableWidgetItem(branch_name))
            self.cost_centers_table.setItem(row, 3, QTableWidgetItem(cc.name_en))
            self.cost_centers_table.setItem(row, 4, QTableWidgetItem(cc.name_ar))
            self.cost_centers_table.setItem(row, 5, QTableWidgetItem(str(cc.code))) # Ensure code is displayed as string
            self.cost_centers_table.setItem(row, 6, QTableWidgetItem(cc.description or ""))
            self.cost_centers_table.setItem(row, 7, QTableWidgetItem("Yes" if cc.is_active else "No"))

    def add_cost_center(self):
        try:
            company_id = self.company_id_input.currentData()
            branch_id = self.branch_id_input.currentData()
            name_en = self.name_en_input.text()
            name_ar = self.name_ar_input.text()
            # code = self.code_input.text() # Removed, as it's auto-generated
            description = self.description_input.text()
            is_active = self.is_active_input.isChecked()

            if not company_id or not branch_id or not name_en:
                QMessageBox.warning(self, "Input Error", "Company, Branch, and English Name are required.")
                return

            self.cost_center_project_service.create_cost_center(
                company_id=company_id,
                # branch_id=branch_id, # Removed branch_id because the model definition for CostCenter doesn't include it.
                name_en=name_en,
                name_ar=name_ar,
                # code=code, # Removed, as it's auto-generated
                description=description,
                is_active=is_active
            )
            self.clear_form()
            self.load_cost_centers()
            QMessageBox.information(self, "Success", "Cost Center added successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.company_id_input.setCurrentIndex(0)
        self.branch_id_input.setCurrentIndex(0)
        self.name_en_input.clear()
        self.name_ar_input.clear()
        next_code = self.cost_center_project_service.get_next_cost_center_code()
        self.code_input.setText(str(next_code)) # Set next auto-incrementing code
        self.description_input.clear()
        self.is_active_input.setChecked(True)
