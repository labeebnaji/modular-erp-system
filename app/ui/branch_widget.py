from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QSpinBox, QFormLayout, QGroupBox, QHeaderView, QCheckBox, QDoubleSpinBox
from app.application.services import CompanyService, BranchService # Assuming CompanyService handles branches
from app.ui.base_widget import TranslatableWidget
from app.i18n.translations import tr, get_language
from PySide6.QtCore import Qt
#from app.infrastructure.database import get_db # No longer needed

class BranchWidget(QWidget):
    def __init__(self, company_service, branch_service, parent=None):
        super().__init__(parent)
        self.company_service = company_service
        self.branch_service = branch_service
        self.init_ui()
        self.clear_form() # Call clear_form to set the initial code
        self.load_branches()

    def init_ui(self):
        self.setWindowTitle("Branch Management")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Branch form
        form_group_box = QGroupBox("Branch Details")
        form_layout = QFormLayout()

        self.company_id_input = QComboBox()
        self.load_companies_to_combobox(self.company_id_input)
        form_layout.addRow(QLabel("Company:"), self.company_id_input)

        self.name_en_input = QLineEdit()
        self.name_en_input.setPlaceholderText("Branch Name (English)")
        # Icon placeholder: self.name_en_input.addAction(QIcon("path/to/branch_name_en_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Branch Name (EN):"), self.name_en_input)

        self.name_ar_input = QLineEdit()
        self.name_ar_input.setPlaceholderText("Branch Name (Arabic)")
        # Icon placeholder: self.name_ar_input.addAction(QIcon("path/to/branch_name_ar_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Branch Name (AR):"), self.name_ar_input)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText(tr("branch.branch_code"))
        self.code_input.setReadOnly(True) # Make code field read-only
        # Icon placeholder: self.code_input.addAction(QIcon("path/to/branch_code_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Branch Code:"), self.code_input)

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Address")
        # Icon placeholder: self.address_input.addAction(QIcon("path/to/address_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Address:"), self.address_input)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone")
        # Icon placeholder: self.phone_input.addAction(QIcon("path/to/phone_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Phone:"), self.phone_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        # Icon placeholder: self.email_input.addAction(QIcon("path/to/email_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Email:"), self.email_input)

        self.is_active_input = QCheckBox("Is Active")
        self.is_active_input.setChecked(True)
        form_layout.addRow(QLabel("Active:"), self.is_active_input)

        add_button = QPushButton("Add Branch")
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        add_button.clicked.connect(self.add_branch)
        
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

        # Branch table
        self.branches_table = QTableWidget()
        self.branches_table.setColumnCount(9) # Increased column count
        self.branches_table.setHorizontalHeaderLabels(["ID", "Company", "Name (EN)", "Name (AR)", "Code", "Address", "Phone", "Email", "Active"])
        self.branches_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        
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
        self.branches_table.setStyleSheet(table_style)
        self.branches_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.branches_table)

        main_layout.addStretch(1) # Add stretch to push content upwards and fill remaining space

        self.setLayout(main_layout)

    def load_companies_to_combobox(self, combobox):
        combobox.clear()
        companies = self.company_service.get_all_companies()
        combobox.addItem("Select Company", 0) # Default empty item
        for company in companies:
            combobox.addItem(f"{company.name_en} ({company.code})", company.id)

    def load_branches(self):
        self.branches_table.setRowCount(0)
        branches = self.branch_service.get_all_branches()
        self.branches_table.setRowCount(len(branches))
        for row, branch in enumerate(branches):
            company = self.company_service.get_company_by_id(branch.company_id)
            company_name = company.name_en if company else "Unknown Company"

            self.branches_table.setItem(row, 0, QTableWidgetItem(str(branch.id)))
            self.branches_table.setItem(row, 1, QTableWidgetItem(company_name))
            self.branches_table.setItem(row, 2, QTableWidgetItem(branch.name_en))
            self.branches_table.setItem(row, 3, QTableWidgetItem(branch.name_ar))
            self.branches_table.setItem(row, 4, QTableWidgetItem(str(branch.code))) # Ensure code is displayed as string
            self.branches_table.setItem(row, 5, QTableWidgetItem(branch.address or ""))
            self.branches_table.setItem(row, 6, QTableWidgetItem(branch.phone_number or "")) # Corrected from branch.phone
            self.branches_table.setItem(row, 7, QTableWidgetItem(branch.email or ""))
            self.branches_table.setItem(row, 8, QTableWidgetItem("Yes" if branch.is_active else "No"))

    def add_branch(self):
        try:
            company_id = self.company_id_input.currentData()
            name_en = self.name_en_input.text()
            name_ar = self.name_ar_input.text()
            # code = self.code_input.text() # Removed, as it's auto-generated
            address = self.address_input.text()
            phone = self.phone_input.text()
            email = self.email_input.text()
            is_active = self.is_active_input.isChecked()

            if not company_id or not name_en:
                QMessageBox.warning(self, "Input Error", "Company and English Name are required.")
                return

            self.branch_service.create_branch(
                company_id=company_id,
                name_en=name_en,
                name_ar=name_ar,
                # code=code, # Removed, as it's auto-generated
                address=address,
                phone_number=phone, # Corrected from 'phone' to 'phone_number'
                email=email,
                is_active=is_active
            )
            self.clear_form()
            self.load_branches()
            QMessageBox.information(self, "Success", "Branch added successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.company_id_input.setCurrentIndex(0)
        self.name_en_input.clear()
        self.name_ar_input.clear()
        next_code = self.branch_service.get_next_branch_code()
        self.code_input.setText(str(next_code)) # Set next auto-incrementing code
        self.address_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.is_active_input.setChecked(True)

    def refresh_translations(self):
        """Refresh all translatable elements"""
        super().refresh_translations()
        self.setWindowTitle(tr('windows.branch'))
        
        # Update buttons
        if hasattr(self, 'add_button'):
            self.add_button.setText(tr('common.add'))
        if hasattr(self, 'save_button'):
            self.save_button.setText(tr('common.save'))
        if hasattr(self, 'cancel_button'):
            self.cancel_button.setText(tr('common.cancel'))
