from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QCheckBox, QSpinBox, QFormLayout, QGroupBox, QHeaderView, QDoubleSpinBox
from app.application.services import InventoryService
#from app.infrastructure.database import get_db # No longer needed
from decimal import Decimal
from PySide6.QtCore import Qt # Added for Qt.UserRole
from app.ui.base_widget import TranslatableWidget
from app.i18n.translations import tr, get_language
from PySide6.QtCore import Qt

class ItemWidget(QWidget):
    def __init__(self, inventory_service: InventoryService, unit_service, parent=None):
        super().__init__(parent)
        self.inventory_service = inventory_service
        self.unit_service = unit_service
        self.init_ui()
        self.clear_form() # Call clear_form to set the initial code
        self.load_items()

    def init_ui(self):
        self.setWindowTitle("Items")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Item form
        form_group_box = QGroupBox("Item Details")
        form_layout = QFormLayout()

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText(tr("common.code"))
        self.code_input.setReadOnly(True) # Make code field read-only
        # Icon placeholder: self.code_input.addAction(QIcon("path/to/icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Code:"), self.code_input)

        self.name_ar_input = QLineEdit()
        self.name_ar_input.setPlaceholderText("Arabic Name")
        # Icon placeholder: self.name_ar_input.addAction(QIcon("path/to/icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Arabic Name:"), self.name_ar_input)

        self.name_en_input = QLineEdit()
        self.name_en_input.setPlaceholderText("English Name")
        # Icon placeholder: self.name_en_input.addAction(QIcon("path/to/icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("English Name:"), self.name_en_input)

        self.unit_combo = QComboBox()
        form_layout.addRow(QLabel("Unit:"), self.unit_combo)
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Barcode")
        # Icon placeholder: self.barcode_input.addAction(QIcon("path/to/icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Barcode:"), self.barcode_input)

        self.reorder_level_input = QSpinBox()
        self.reorder_level_input.setRange(0, 999999)
        # self.reorder_level_input.setPlaceholderText("Reorder Level") # QSpinBox doesn't have placeholder
        # Icon placeholder: self.reorder_level_input.addAction(QIcon("path/to/icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Reorder Level:"), self.reorder_level_input)

        self.costing_method_input = QComboBox()
        self.costing_method_input.addItems(["FIFO", "Weighted Average", "Specific"]) # Assuming enum values
        form_layout.addRow(QLabel("Costing Method:"), self.costing_method_input)

        self.is_active_input = QCheckBox("Active")
        self.is_active_input.setChecked(True)
        form_layout.addRow(QLabel("Is Active:"), self.is_active_input)

        add_button = QPushButton("Add Item")
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        add_button.clicked.connect(self.add_item)
        
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

        # Item table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(9) # Increased column count to include Is Active
        self.items_table.setHorizontalHeaderLabels(["ID", "Code", "Arabic Name", "English Name", "Unit", "Barcode", "Reorder Level", "Costing Method", "Active"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        
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
        self.items_table.setStyleSheet(table_style)
        self.items_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.items_table)

        main_layout.addStretch(1) # Add stretch to push content upwards and fill remaining space

        self.setLayout(main_layout)
        self.load_units_to_combo() # Load units initially

    def load_units_to_combo(self):
        self.unit_combo.clear()
        # Assuming current_company_id is available from the parent (MainWindow)
        # In a real application, you might pass company_id to ItemWidget's constructor
        # For now, we will assume company_id = 1.
        # A more robust solution would be to pass company_id from MainWindow when instantiating ItemWidget.
        # Or, if ItemWidget is part of a larger module, that module would manage the company_id.
        units = self.unit_service.get_all_units()
        active_units = [unit for unit in units if unit.is_active]
        for unit in active_units:
            self.unit_combo.addItem(unit.name_ar, unit.id) # Display Arabic name, store ID as UserRole data

    def load_items(self):
        self.items_table.setRowCount(0)
        items = self.inventory_service.get_all_items()
        self.items_table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.items_table.setItem(row, 0, QTableWidgetItem(str(item.id)))
            self.items_table.setItem(row, 1, QTableWidgetItem(str(item.code))) # Ensure code is displayed as string
            self.items_table.setItem(row, 2, QTableWidgetItem(item.name_ar))
            self.items_table.setItem(row, 3, QTableWidgetItem(item.name_en))
            self.items_table.setItem(row, 4, QTableWidgetItem(item.unit.name_ar if item.unit else "N/A")) # Display unit name from relationship
            self.items_table.setItem(row, 5, QTableWidgetItem(item.barcode if item.barcode else "N/A"))
            self.items_table.setItem(row, 6, QTableWidgetItem(str(item.reorder_level)))
            self.items_table.setItem(row, 7, QTableWidgetItem(str(item.costing_method)))
            self.items_table.setItem(row, 8, QTableWidgetItem(str(item.is_active)))

    def add_item(self):
        try:
            # code = self.code_input.text() # Removed, as it's auto-generated
            name_ar = self.name_ar_input.text()
            name_en = self.name_en_input.text()
            unit_id = self.unit_combo.currentData(Qt.UserRole) # Get unit ID from combo box
            barcode = self.barcode_input.text()
            reorder_level = self.reorder_level_input.value()
            costing_method = self.costing_method_input.currentIndex()
            is_active = self.is_active_input.isChecked()

            if not name_ar or unit_id is None:
                QMessageBox.warning(self, "Input Error", "Arabic Name and Unit are required.")
                return

            # Assuming company_id is 1 for now
            self.inventory_service.create_item(
                company_id=1,
                # code=code, # Removed, as it's auto-generated
                name_ar=name_ar,
                name_en=name_en,
                unit_id=unit_id,
                barcode=barcode,
                reorder_level=Decimal(reorder_level),
                costing_method=costing_method,
                is_active=is_active
            )
            self.clear_form()
            self.load_items()
            QMessageBox.information(self, "Success", "Item added successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        next_code = self.inventory_service.get_next_item_code()
        self.code_input.setText(str(next_code)) # Set next auto-incrementing code
        self.name_ar_input.clear()
        self.name_en_input.clear()
        self.unit_combo.setCurrentIndex(0) # Reset to first item
        self.barcode_input.clear()
        self.reorder_level_input.setValue(0)
        self.costing_method_input.setCurrentIndex(0)
        self.is_active_input.setChecked(True)

    def refresh_translations(self):
        """Refresh all translatable elements"""
        super().refresh_translations()
        self.setWindowTitle(tr('windows.items'))
        
        # Update buttons
        if hasattr(self, 'add_button'):
            self.add_button.setText(tr('common.add'))
        if hasattr(self, 'edit_button'):
            self.edit_button.setText(tr('common.edit'))
        if hasattr(self, 'delete_button'):
            self.delete_button.setText(tr('common.delete'))
