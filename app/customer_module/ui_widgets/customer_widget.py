from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QCheckBox, QFormLayout, QGroupBox, QHeaderView, QDoubleSpinBox
from PySide6.QtCore import QDate
from app.application.services import ARAPService
#from app.infrastructure.database import get_db # No longer needed
from decimal import Decimal
from datetime import datetime # Added for code generation
from app.ui.base_widget import TranslatableWidget
from app.i18n.translations import tr, get_language
from PySide6.QtCore import Qt

class CustomerWidget(QWidget):
    def __init__(self, arap_service, parent=None):
        super().__init__(parent)
        self.arap_service = arap_service
        self.current_customer_id = None # To store the ID of the customer being edited
        self.init_ui()
        self.clear_form() # Call clear_form to set the initial code
        self.load_customers()

    def init_ui(self):
        self.setWindowTitle("Customers")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or code...")
        self.search_input.returnPressed.connect(self.search_customers) # Trigger search on Enter
        search_button = QPushButton(tr("common.search"))
        search_button.clicked.connect(self.search_customers)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        main_layout.addLayout(search_layout)

        # Customer form
        form_group_box = QGroupBox("Customer Details")
        form_layout = QFormLayout()

        self.id_label = QLabel("ID: New")
        form_layout.addRow(self.id_label)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText(tr("customers.customer_code"))
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

        # self.mobile_input = QLineEdit()
        # self.mobile_input.setPlaceholderText("Mobile Number")
        # form_layout.addRow(QLabel("Mobile:"), self.mobile_input) # Removed mobile_input

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Address")
        # Icon placeholder: self.address_input.addAction(QIcon("path/to/icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Address:"), self.address_input)

        self.customer_group_input = QLineEdit()
        self.customer_group_input.setPlaceholderText("Customer Group")
        form_layout.addRow(QLabel("Group:"), self.customer_group_input)

        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("Type (e.g., 0 for Individual)")
        form_layout.addRow(QLabel("Type:"), self.type_input)

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

        # CRUD buttons
        crud_buttons_layout = QHBoxLayout()
        self.add_update_button = QPushButton("Add Customer")
        self.add_update_button.clicked.connect(self.add_update_customer)
        edit_button = QPushButton("Edit Selected")
        edit_button.clicked.connect(self.edit_customer)
        
        # Apply styling to buttons
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
        self.add_update_button.setStyleSheet(button_style)
        edit_button.setStyleSheet(button_style)
        search_button.setStyleSheet(button_style)
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_customer)
        clear_button = QPushButton("Clear Form")
        clear_button.clicked.connect(self.clear_form)

        crud_buttons_layout.addWidget(self.add_update_button)
        crud_buttons_layout.addWidget(edit_button)
        crud_buttons_layout.addWidget(delete_button)
        crud_buttons_layout.addWidget(clear_button)
        form_layout.addRow(crud_buttons_layout)

        form_group_box.setLayout(form_layout)
        main_layout.addWidget(form_group_box)

        # Customer table
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(12) # Reduced column count by 1
        self.customers_table.setHorizontalHeaderLabels(["ID", "Code", "Arabic Name", "English Name", "Email", "Phone", "Address", "Group", "Type", "Credit Limit", "Payment Terms", "Created At"]) # Removed "Mobile"
        self.customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        self.customers_table.itemSelectionChanged.connect(self.populate_form_from_table_selection)
        
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
        self.customers_table.setStyleSheet(table_style)
        self.customers_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.customers_table)

        main_layout.addStretch(1) # Add stretch to push content upwards and fill remaining space

        self.setLayout(main_layout)

    def load_customers(self, search_query=None):
        self.customers_table.setRowCount(0)
        customers = self.arap_service.get_all_customers()

        if search_query:
            customers = [c for c in customers if search_query.lower() in c.name_ar.lower() or \
                         (c.name_en and search_query.lower() in c.name_en.lower()) or \
                         (c.code and search_query.lower() in c.code.lower())]

        self.customers_table.setRowCount(len(customers))
        for row, customer in enumerate(customers):
            self.customers_table.setItem(row, 0, QTableWidgetItem(str(customer.id)))
            self.customers_table.setItem(row, 1, QTableWidgetItem(str(customer.code))) # Ensure code is displayed as string
            self.customers_table.setItem(row, 2, QTableWidgetItem(customer.name_ar))
            self.customers_table.setItem(row, 3, QTableWidgetItem(customer.name_en))
            self.customers_table.setItem(row, 4, QTableWidgetItem(customer.email or ""))
            self.customers_table.setItem(row, 5, QTableWidgetItem(customer.phone_number or ""))
            # self.customers_table.setItem(row, 6, QTableWidgetItem(customer.mobile_number)) # Removed mobile_number
            self.customers_table.setItem(row, 6, QTableWidgetItem(customer.address or "")) # Shifted index
            self.customers_table.setItem(row, 7, QTableWidgetItem(customer.customer_group or "")) # Shifted index
            self.customers_table.setItem(row, 8, QTableWidgetItem(str(customer.type)))
            self.customers_table.setItem(row, 9, QTableWidgetItem(str(customer.credit_limit)))
            self.customers_table.setItem(row, 10, QTableWidgetItem(customer.payment_terms or ""))
            self.customers_table.setItem(row, 11, QTableWidgetItem(str(customer.created_at.strftime('%Y-%m-%d %H:%M:%S')) if customer.created_at else "")) # Shifted index

    def search_customers(self):
        query = self.search_input.text()
        self.load_customers(query)

    def add_update_customer(self):
        try:
            name_ar = self.name_ar_input.text()
            name_en = self.name_en_input.text()
            # code = self.code_input.text() # Removed, as it's auto-generated
            email = self.email_input.text()
            phone = self.phone_input.text()
            # mobile = self.mobile_input.text() # Removed mobile
            address = self.address_input.text()
            customer_group = self.customer_group_input.text()
            type_str = self.type_input.text()
            credit_limit = Decimal(self.credit_limit_input.value())
            payment_terms = self.payment_terms_input.text()

            if not name_ar:
                QMessageBox.warning(self, "Input Error", "Arabic Name is required.")
                return

            customer_type = int(type_str) if type_str else 0 # Default to 0 if empty

            if self.current_customer_id: # Update existing customer
                self.arap_service.update_customer(
                    self.current_customer_id,
                    name_ar=name_ar,
                    name_en=name_en,
                    # code=code, # Removed, as it's auto-generated and shouldn't be updated manually
                    email=email,
                    phone_number=phone,
                    # mobile_number=mobile, # Removed mobile_number from update
                    address=address,
                    customer_group=customer_group,
                    type=customer_type,
                    credit_limit=credit_limit,
                    payment_terms=payment_terms
                )
                QMessageBox.information(self, "Success", "Customer updated successfully.")
            else: # Add new customer
                self.arap_service.create_customer(
                    name_ar=name_ar,
                    name_en=name_en,
                    # code=code, # Removed, as it's auto-generated
                    email=email,
                    phone_number=phone,
                    # mobile_number=mobile, # Removed mobile_number from create
                    address=address,
                    customer_group=customer_group,
                    type=customer_type,
                    credit_limit=credit_limit,
                    payment_terms=payment_terms
                )
                QMessageBox.information(self, "Success", "Customer added successfully.")
            self.clear_form()
            self.load_customers()
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def populate_form_from_table_selection(self):
        selected_items = self.customers_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            self.current_customer_id = int(self.customers_table.item(row, 0).text())
            self.id_label.setText(f"ID: {self.current_customer_id}")
            self.code_input.setText(self.customers_table.item(row, 1).text())
            self.name_ar_input.setText(self.customers_table.item(row, 2).text())
            self.name_en_input.setText(self.customers_table.item(row, 3).text())
            self.email_input.setText(self.customers_table.item(row, 4).text() or "")
            self.phone_input.setText(self.customers_table.item(row, 5).text() or "")
            # self.mobile_input.setText(self.customers_table.item(row, 6).text()) # Removed mobile_input
            self.address_input.setText(self.customers_table.item(row, 6).text() or "") # Shifted index
            self.customer_group_input.setText(self.customers_table.item(row, 7).text() or "") # Shifted index
            self.type_input.setText(self.customers_table.item(row, 8).text() or "") # Shifted index
            self.credit_limit_input.setValue(float(self.customers_table.item(row, 9).text())) # Shifted index
            self.payment_terms_input.setText(self.customers_table.item(row, 10).text() or "") # Shifted index
            self.add_update_button.setText("Update Customer")
        else:
            self.clear_form()

    def edit_customer(self):
        selected_items = self.customers_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "Please select a customer to edit.")
            return
        self.populate_form_from_table_selection()

    def delete_customer(self):
        selected_items = self.customers_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "Please select a customer to delete.")
            return

        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this customer?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            row = selected_items[0].row()
            customer_id = int(self.customers_table.item(row, 0).text())
            try:
                self.arap_service.delete_customer(customer_id)
                self.load_customers() # Refresh the table
                self.clear_form()
                QMessageBox.information(self, "Success", "Customer deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while deleting customer: {e}")

    def clear_form(self):
        self.current_customer_id = None
        self.id_label.setText("ID: New")
        next_code = self.arap_service.get_next_customer_code()
        self.code_input.setText(str(next_code)) # Set next auto-incrementing code
        self.name_ar_input.clear()
        self.name_en_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        # self.mobile_input.clear() # Removed mobile_input
        self.address_input.clear()
        self.customer_group_input.clear()
        self.type_input.clear()
        self.credit_limit_input.setValue(0.0)
        self.payment_terms_input.clear()
        self.add_update_button.setText("Add Customer")

    def refresh_translations(self):
        """Refresh all translatable elements"""
        super().refresh_translations()
        self.setWindowTitle(tr('windows.customers'))
        
        # Update buttons
        if hasattr(self, 'add_button'):
            self.add_button.setText(tr('common.add'))
        if hasattr(self, 'edit_button'):
            self.edit_button.setText(tr('common.edit'))
        if hasattr(self, 'delete_button'):
            self.delete_button.setText(tr('common.delete'))
        if hasattr(self, 'refresh_button'):
            self.refresh_button.setText(tr('common.refresh'))
