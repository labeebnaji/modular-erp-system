from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QCheckBox, QFormLayout, QGroupBox, QHeaderView, QDoubleSpinBox
from PySide6.QtCore import QDate
from app.application.services import ARAPService
#from app.infrastructure.database import get_db # No longer needed
from decimal import Decimal
from datetime import datetime

class SupplierWidget(QWidget):
    def __init__(self, arap_service, parent=None):
        super().__init__(parent)
        self.arap_service = arap_service
        self.init_ui()
        self.load_suppliers()

    def init_ui(self):
        self.setWindowTitle("Suppliers")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Supplier form
        form_group_box = QGroupBox("Supplier Details")
        form_layout = QFormLayout()

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
        form_layout.addRow(add_button)

        form_group_box.setLayout(form_layout)
        main_layout.addWidget(form_group_box)

        # Supplier table
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setColumnCount(9)
        self.suppliers_table.setHorizontalHeaderLabels(["ID", "Arabic Name", "English Name", "Email", "Phone", "Address", "Credit Limit", "Payment Terms", "Created At"])
        self.suppliers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        main_layout.addWidget(self.suppliers_table)

        main_layout.addStretch(1) # Add stretch to push content upwards and fill remaining space

        self.setLayout(main_layout)

    def load_suppliers(self):
        self.suppliers_table.setRowCount(0)
        suppliers = self.arap_service.get_all_suppliers()
        self.suppliers_table.setRowCount(len(suppliers))
        for row, supplier in enumerate(suppliers):
            self.suppliers_table.setItem(row, 0, QTableWidgetItem(str(supplier.id)))
            self.suppliers_table.setItem(row, 1, QTableWidgetItem(supplier.name_ar))
            self.suppliers_table.setItem(row, 2, QTableWidgetItem(supplier.name_en))
            self.suppliers_table.setItem(row, 3, QTableWidgetItem(supplier.email))
            self.suppliers_table.setItem(row, 4, QTableWidgetItem(supplier.phone_number))
            self.suppliers_table.setItem(row, 5, QTableWidgetItem(supplier.address))
            self.suppliers_table.setItem(row, 6, QTableWidgetItem(str(supplier.credit_limit)))
            self.suppliers_table.setItem(row, 7, QTableWidgetItem(supplier.payment_terms))
            self.suppliers_table.setItem(row, 8, QTableWidgetItem(str(supplier.created_at.strftime('%Y-%m-%d %H:%M:%S')))) # Assuming created_at exists

    def add_supplier(self):
        try:
            name_ar = self.name_ar_input.text()
            name_en = self.name_en_input.text()
            email = self.email_input.text()
            phone = self.phone_input.text()
            address = self.address_input.text()
            credit_limit = Decimal(self.credit_limit_input.value())
            payment_terms = self.payment_terms_input.text()

            if not name_ar:
                QMessageBox.warning(self, "Input Error", "Arabic Name is required.")
                return

            # Assuming company_id is 1 for now
            self.arap_service.create_supplier(
                name_ar=name_ar,
                name_en=name_en,
                code="SUP" + datetime.now().strftime("%Y%m%d%H%M%S"), # Generate a simple code
                email=email,
                phone_number=phone,
                address=address,
                credit_limit=credit_limit,
                payment_terms=payment_terms,
                contact_person="", # Placeholder
                tax_id="", # Placeholder
                supplier_group="" # Placeholder
            )
            self.clear_form()
            self.load_suppliers()
            QMessageBox.information(self, "Success", "Supplier added successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.name_ar_input.clear()
        self.name_en_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.address_input.clear()
        self.credit_limit_input.setValue(0.0)
        self.payment_terms_input.clear()
