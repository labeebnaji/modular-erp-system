from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QSpinBox, QFormLayout, QGroupBox, QHeaderView, QDoubleSpinBox
from PySide6.QtCore import QDate, Qt
from app.application.services import CompanyService
from app.application.services import CurrencyService # Import CurrencyService
#from app.infrastructure.database import get_db # No longer needed
from decimal import Decimal
from app.ui.base_widget import TranslatableWidget
from app.i18n.translations import tr, get_language
from PySide6.QtCore import Qt

class CompanyWidget(QWidget):
    def __init__(self, company_service: CompanyService, currency_service: CurrencyService, parent=None):
        super().__init__(parent)
        self.company_service = company_service
        self.currency_service = currency_service
        self.selected_company_id = None
        self.init_ui()
        self.clear_form() # Call clear_form to set the initial code
        self.load_companies()

    def init_ui(self):
        self.setWindowTitle("Company Management")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Company form
        form_group_box = QGroupBox("Company Details")
        form_layout = QFormLayout()

        self.name_en_input = QLineEdit()
        self.name_en_input.setPlaceholderText("Company Name (English)")
        # Icon placeholder: self.name_en_input.addAction(QIcon("path/to/company_name_en_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Company Name (EN):"), self.name_en_input)

        self.name_ar_input = QLineEdit()
        self.name_ar_input.setPlaceholderText("Company Name (Arabic)")
        # Icon placeholder: self.name_ar_input.addAction(QIcon("path/to/company_name_ar_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Company Name (AR):"), self.name_ar_input)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText(tr("company.company_code"))
        self.code_input.setReadOnly(True) # Make code field read-only
        # Icon placeholder: self.code_input.addAction(QIcon("path/to/company_code_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Company Code:"), self.code_input)

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

        self.base_currency_combo = QComboBox()
        form_layout.addRow(QLabel("Base Currency:"), self.base_currency_combo)
        
        self.secondary_currency_combo = QComboBox()
        self.secondary_currency_combo.addItem("None", None) # Allow no secondary currency
        form_layout.addRow(QLabel("Secondary Currency:"), self.secondary_currency_combo)
        self.add_button = QPushButton("Add Company") # Make add_button an instance attribute
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        self.add_button.clicked.connect(self.add_company)
        
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
        self.add_button.setStyleSheet(button_style)
        
        form_layout.addRow(self.add_button)

        form_group_box.setLayout(form_layout)
        main_layout.addWidget(form_group_box)

        # Company table
        self.companies_table = QTableWidget()
        self.companies_table.setColumnCount(9) # Increased column count for secondary currency
        self.companies_table.setHorizontalHeaderLabels(["ID", "Name (EN)", "Name (AR)", "Code", "Address", "Phone", "Email", "Base Currency", "Secondary Currency"])
        self.companies_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        
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
        self.companies_table.setStyleSheet(table_style)
        self.companies_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.companies_table)

        main_layout.addStretch(1) # Add stretch to push content upwards and fill remaining space

        self.setLayout(main_layout)

        self.load_currencies_to_combo()

    def load_currencies_to_combo(self):
        self.base_currency_combo.clear()
        self.secondary_currency_combo.clear()
        self.secondary_currency_combo.addItem("None", None) # Add None option for secondary currency
        
        current_company_id = 1 # Assuming a default company ID for now
        currencies = self.currency_service.get_all_currencies()
        for currency in currencies:
            self.base_currency_combo.addItem(currency.code, currency.id) # Display currency code, store ID
            self.secondary_currency_combo.addItem(currency.code, currency.id)

    def load_companies(self):
        self.companies_table.setRowCount(0)
        companies = self.company_service.get_all_companies()
        self.companies_table.setRowCount(len(companies))
        for row, company in enumerate(companies):
            self.companies_table.setItem(row, 0, QTableWidgetItem(str(company.id)))
            self.companies_table.setItem(row, 1, QTableWidgetItem(company.name_en))
            self.companies_table.setItem(row, 2, QTableWidgetItem(company.name_ar))
            self.companies_table.setItem(row, 3, QTableWidgetItem(str(company.code))) # Ensure code is displayed as string
            self.companies_table.setItem(row, 4, QTableWidgetItem(company.address))
            self.companies_table.setItem(row, 5, QTableWidgetItem(company.phone_number)) # Corrected from company.phone
            self.companies_table.setItem(row, 6, QTableWidgetItem(company.email))
            self.companies_table.setItem(row, 7, QTableWidgetItem(company.base_currency.code if company.base_currency else "N/A")) # Display code from relationship
            self.companies_table.setItem(row, 8, QTableWidgetItem(company.secondary_currency.code if company.secondary_currency else "N/A"))

    def select_company(self, index):
        company_id = self.companies_table.item(index.row(), 0).text()
        company = self.company_service.get_company_by_id(int(company_id))
        if company:
            self.selected_company_id = company.id
            self.name_en_input.setText(company.name_en)
            self.name_ar_input.setText(company.name_ar)
            self.code_input.setText(str(company.code))
            self.address_input.setText(company.address if company.address else "")
            self.phone_input.setText(company.phone_number if company.phone_number else "")
            self.email_input.setText(company.email if company.email else "")
            
            # Set base currency combo box
            base_currency_index = self.base_currency_combo.findData(company.base_currency_id)
            if base_currency_index >= 0:
                self.base_currency_combo.setCurrentIndex(base_currency_index)
            
            # Set secondary currency combo box
            secondary_currency_index = self.secondary_currency_combo.findData(company.secondary_currency_id)
            if secondary_currency_index >= 0:
                self.secondary_currency_combo.setCurrentIndex(secondary_currency_index)
            else:
                self.secondary_currency_combo.setCurrentIndex(0) # Select 'None'
            
            self.add_button.setText("Update Company")
   
    def add_company(self):
        try:
            name_en = self.name_en_input.text()
            name_ar = self.name_ar_input.text()
            # code = self.code_input.text() # Removed, as it's auto-generated
            address = self.address_input.text()
            phone = self.phone_input.text()
            email = self.email_input.text()
            base_currency_id = self.base_currency_combo.currentData(Qt.UserRole)
            secondary_currency_id = self.secondary_currency_combo.currentData(Qt.UserRole)

            if not name_en or base_currency_id is None:
                QMessageBox.warning(self, "Input Error", "English Name and Base Currency are required.")
                return

            # Assuming company_id is 1 for now
            if self.selected_company_id:
                self.company_service.update_company(
                    self.selected_company_id,
                    name_en=name_en,
                    name_ar=name_ar,
                    address=address if address else None,
                    phone_number=phone if phone else None,
                    email=email if email else None,
                    base_currency_id=base_currency_id,
                    secondary_currency_id=secondary_currency_id
                )
                QMessageBox.information(self, "Success", "Company updated successfully.")
            else:
                self.company_service.create_company(
                    name_en=name_en,
                    name_ar=name_ar,
                    # code=code, # Removed, as it's auto-generated
                    address=address,
                    phone_number=phone, # Corrected from 'phone' to 'phone_number'
                    email=email,
                    base_currency_id=base_currency_id,
                    secondary_currency_id=secondary_currency_id
                )
                QMessageBox.information(self, "Success", "Company added successfully.")
            self.clear_form()
            self.load_companies()
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def delete_company(self):
        if not self.selected_company_id:
            QMessageBox.warning(self, "Selection Error", "Please select a company to delete.")
            return

        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this company?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.company_service.delete_company(self.selected_company_id)
                QMessageBox.information(self, "Success", "Company deleted successfully.")
                self.clear_form()
                self.load_companies()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete company: {e}")

    def clear_form(self):
        self.selected_company_id = None
        next_code = self.company_service.get_next_company_code()
        self.name_en_input.clear()
        self.name_ar_input.clear()
        self.code_input.setText(str(next_code)) # Set next auto-incrementing code
        self.address_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.base_currency_combo.setCurrentIndex(0) # Reset to first item
        self.secondary_currency_combo.setCurrentIndex(0) # Reset to 'None'
        self.add_button.setText("Add Company")

    def refresh_translations(self):
        """Refresh all translatable elements"""
        super().refresh_translations()
        self.setWindowTitle(tr('windows.company'))
        
        # Update buttons
        if hasattr(self, 'add_button'):
            self.add_button.setText(tr('common.add'))
        if hasattr(self, 'save_button'):
            self.save_button.setText(tr('common.save'))
        if hasattr(self, 'cancel_button'):
            self.cancel_button.setText(tr('common.cancel'))
