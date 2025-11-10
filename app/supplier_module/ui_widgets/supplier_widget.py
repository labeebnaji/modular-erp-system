from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QCheckBox, QFormLayout, QGroupBox, QHeaderView, QDoubleSpinBox
from PySide6.QtCore import QDate
from app.application.services import ARAPService
#from app.infrastructure.database import get_db # No longer needed
from decimal import Decimal
from datetime import datetime
from app.ui.base_widget import TranslatableWidget
from app.i18n.translations import tr, get_language
from PySide6.QtCore import Qt

class SupplierWidget(QWidget):
    def __init__(self, arap_service, parent=None):
        super().__init__(parent)
        self.arap_service = arap_service
        self.init_ui()
        self.clear_form() # Call clear_form to set the initial code
        self.load_suppliers()

    def init_ui(self):
        self.setWindowTitle("Suppliers")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Supplier form
        form_group_box = QGroupBox("Supplier Details")
        form_layout = QFormLayout()

        self.code_input = QLineEdit() # Add code input field
        self.code_input.setPlaceholderText(tr("suppliers.supplier_code"))
        self.code_input.setReadOnly(True) # Make code field read-only
        form_layout.addRow(QLabel("Code:"), self.code_input)

        self.name_ar_input = QLineEdit()
        self.name_ar_input.setPlaceholderText("Arabic Name")
        # Icon placeholder: self.name_ar_input.addAction(QIcon("path/to/icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Arabic Name:"), self.name_ar_input)

        self.name_en_input = QLineEdit()
        self.name_en_input.setPlaceholderText("English Name")
        # Icon placeholder: self.name_en_input.addAction(QIcon("path/to/icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("English Name:"), self.name_en_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        # Icon placeholder: self.email_input.addAction(QIcon("path/to/icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Email:"), self.email_input)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone")
        # Icon placeholder: self.phone_input.addAction(QIcon("path/to/icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Phone:"), self.phone_input)

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Address")
        # Icon placeholder: self.address_input.addAction(QIcon("path/to/icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Address:"), self.address_input)

        self.contact_person_input = QLineEdit() # Added contact person
        self.contact_person_input.setPlaceholderText("Contact Person")
        form_layout.addRow(QLabel("Contact Person:"), self.contact_person_input)

        self.tax_id_input = QLineEdit() # Added tax ID
        self.tax_id_input.setPlaceholderText("Tax ID")
        form_layout.addRow(QLabel("Tax ID:"), self.tax_id_input)

        self.supplier_group_input = QLineEdit() # Added supplier group
        self.supplier_group_input.setPlaceholderText("Supplier Group")
        form_layout.addRow(QLabel("Supplier Group:"), self.supplier_group_input)

        self.credit_limit_input = QDoubleSpinBox()
        self.credit_limit_input.setRange(0.00, 999999999.99)
        self.credit_limit_input.setPrefix("$")
        # self.credit_limit_input.setPlaceholderText("Credit Limit") # QDoubleSpinBox doesn't have placeholder
        # Icon placeholder: self.credit_limit_input.addAction(QIcon("path/to/icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Credit Limit:"), self.credit_limit_input)

        self.payment_terms_input = QLineEdit()
        self.payment_terms_input.setPlaceholderText("Payment Terms")
        # Icon placeholder: self.payment_terms_input.addAction(QIcon("path/to/icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Payment Terms:"), self.payment_terms_input)

        add_button = QPushButton("Add Supplier")
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        add_button.clicked.connect(self.add_supplier)
        
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

        # Supplier table
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setColumnCount(12) # Increased column count to include Code and new fields
        self.suppliers_table.setHorizontalHeaderLabels(["ID", "Code", "Arabic Name", "English Name", "Email", "Phone", "Address", "Contact Person", "Tax ID", "Supplier Group", "Credit Limit", "Payment Terms"])
        self.suppliers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        
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
        self.suppliers_table.setStyleSheet(table_style)
        self.suppliers_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.suppliers_table)

        main_layout.addStretch(1) # Add stretch to push content upwards and fill remaining space

        self.setLayout(main_layout)

    def load_suppliers(self):
        self.suppliers_table.setRowCount(0)
        suppliers = self.arap_service.get_all_suppliers()
        self.suppliers_table.setRowCount(len(suppliers))
        for row, supplier in enumerate(suppliers):
            self.suppliers_table.setItem(row, 0, QTableWidgetItem(str(supplier.id)))
            self.suppliers_table.setItem(row, 1, QTableWidgetItem(str(supplier.code)))
            self.suppliers_table.setItem(row, 2, QTableWidgetItem(supplier.name_ar))
            self.suppliers_table.setItem(row, 3, QTableWidgetItem(supplier.name_en))
            self.suppliers_table.setItem(row, 4, QTableWidgetItem(supplier.email or ""))
            self.suppliers_table.setItem(row, 5, QTableWidgetItem(supplier.phone_number or ""))
            self.suppliers_table.setItem(row, 6, QTableWidgetItem(supplier.address or ""))
            self.suppliers_table.setItem(row, 7, QTableWidgetItem(supplier.contact_person or ""))
            self.suppliers_table.setItem(row, 8, QTableWidgetItem(supplier.tax_id or ""))
            self.suppliers_table.setItem(row, 9, QTableWidgetItem(supplier.supplier_group or ""))
            self.suppliers_table.setItem(row, 10, QTableWidgetItem(str(supplier.credit_limit)))
            self.suppliers_table.setItem(row, 11, QTableWidgetItem(supplier.payment_terms or ""))

    def add_supplier(self):
        try:
            name_ar = self.name_ar_input.text()
            name_en = self.name_en_input.text()
            email = self.email_input.text()
            phone = self.phone_input.text()
            address = self.address_input.text()
            contact_person = self.contact_person_input.text()
            tax_id = self.tax_id_input.text()
            supplier_group = self.supplier_group_input.text()
            credit_limit = Decimal(self.credit_limit_input.value())
            payment_terms = self.payment_terms_input.text()

            if not name_ar:
                QMessageBox.warning(self, "Input Error", "Arabic Name is required.")
                return

            # Assuming company_id is 1 for now
            self.arap_service.create_supplier(
                name_ar=name_ar,
                name_en=name_en,
                email=email,
                phone_number=phone,
                address=address,
                contact_person=contact_person,
                tax_id=tax_id,
                supplier_group=supplier_group,
                credit_limit=credit_limit,
                payment_terms=payment_terms
            )
            self.clear_form()
            self.load_suppliers()
            QMessageBox.information(self, "Success", "Supplier added successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        next_code = self.arap_service.get_next_supplier_code()
        self.code_input.setText(str(next_code)) # Set next auto-incrementing code
        self.name_ar_input.clear()
        self.name_en_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.address_input.clear()
        self.contact_person_input.clear()
        self.tax_id_input.clear()
        self.supplier_group_input.clear()
        self.credit_limit_input.setValue(0.0)
        self.payment_terms_input.clear()

    def refresh_translations(self):
        """Refresh all translatable elements"""
        super().refresh_translations()
        self.setWindowTitle(tr('windows.suppliers'))
        
        # Update buttons
        if hasattr(self, 'add_button'):
            self.add_button.setText(tr('common.add'))
        if hasattr(self, 'edit_button'):
            self.edit_button.setText(tr('common.edit'))
        if hasattr(self, 'delete_button'):
            self.delete_button.setText(tr('common.delete'))
        if hasattr(self, 'refresh_button'):
            self.refresh_button.setText(tr('common.refresh'))
