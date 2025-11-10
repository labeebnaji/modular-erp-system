from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView, QLineEdit, QLabel, QCheckBox, QMessageBox
from PySide6.QtCore import QAbstractTableModel, Qt, Signal
from PySide6.QtGui import QColor
from decimal import Decimal
from PySide6.QtWidgets import QHeaderView # Added for QTableView header

from app.application.services import UnitService # Import UnitService
from app.domain.settings_models import Unit # Import Unit model

class UnitsTableModel(QAbstractTableModel):
    def __init__(self, units=None, unit_service=None, parent_widget=None):
        super().__init__()
        self._units = units or []
        self.unit_service = unit_service
        self.parent_widget = parent_widget # Store reference to parent widget
        self.headers = ["ID", "Name (AR)", "Name (EN)", "Base Quantity", "Is Active"]

    def rowCount(self, parent=None):
        return len(self._units)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        unit = self._units[index.row()]
        if role == Qt.DisplayRole:
            if index.column() == 0: return unit.id
            if index.column() == 1: return unit.name_ar
            if index.column() == 2: return unit.name_en
            if index.column() == 3: return unit.base_quantity
            if index.column() == 4: return "Yes" if unit.is_active else "No"
        elif role == Qt.CheckStateRole and index.column() == 4:
            return Qt.Checked if unit.is_active else Qt.Unchecked
        elif role == Qt.UserRole:
            return unit # Return the full Unit object
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return super().headerData(section, orientation, role)

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.CheckStateRole or index.column() != 4:
            return False
        unit = self._units[index.row()]
        new_active_state = (value == Qt.Checked)
        if unit.is_active != new_active_state:
            try:
                # Update the unit via service
                self.unit_service.update_unit(
                    unit.id,
                    name_ar=unit.name_ar,
                    name_en=unit.name_en,
                    base_quantity=unit.base_quantity,
                    is_active=new_active_state
                )
                unit.is_active = new_active_state
                self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.CheckStateRole])
                
                # Immediately reload units in the parent widget to ensure UI refresh
                if self.parent_widget:
                    self.parent_widget.load_units()
                
                return True
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Failed to update unit active status: {e}")
                return False
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        if index.column() == 4: # 'Is Active' column
            return super().flags(index) | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
        return super().flags(index) | Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def update_data(self, units):
        self.beginResetModel()
        self._units = units
        self.endResetModel()

    def get_unit_at_row(self, row):
        if 0 <= row < len(self._units):
            return self._units[row]
        return None

class UnitsSettingsWidget(QWidget):
    unit_updated = Signal() # Signal to notify other parts of the app

    def __init__(self, company_id: int, unit_service: UnitService, parent=None):
        super().__init__(parent)
        self.company_id = company_id # Keep company_id for other purposes if needed, but not for UnitService.get_all_units
        self.unit_service = unit_service
        self.selected_unit_id = None
        self.init_ui()
        # self.load_units() # Load units now called after init_ui to ensure model is set up

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Form Layout
        form_layout = QHBoxLayout()
        self.name_ar_input = QLineEdit()
        self.name_ar_input.setPlaceholderText("Unit Name (AR)")
        self.name_en_input = QLineEdit()
        self.name_en_input.setPlaceholderText("Unit Name (EN)")
        self.base_quantity_input = QLineEdit("1.0")
        self.base_quantity_input.setPlaceholderText("Base Quantity")
        self.is_active_checkbox = QCheckBox("Is Active") # Changed from is_base_unit_checkbox

        form_layout.addWidget(QLabel("Name (AR):"))
        form_layout.addWidget(self.name_ar_input)
        form_layout.addWidget(QLabel("Name (EN):"))
        form_layout.addWidget(self.name_en_input)
        form_layout.addWidget(QLabel("Base Quantity:"))
        form_layout.addWidget(self.base_quantity_input)
        form_layout.addWidget(self.is_active_checkbox) # Changed from is_base_unit_checkbox
        main_layout.addLayout(form_layout)

        # Buttons Layout
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Unit")
        self.add_button.clicked.connect(self.add_unit)
        self.update_button = QPushButton("Update Unit")
        self.update_button.clicked.connect(self.update_unit)
        self.delete_button = QPushButton("Delete Unit")
        self.delete_button.clicked.connect(self.delete_unit)
        self.clear_button = QPushButton("Clear Form")
        self.clear_button.clicked.connect(self.clear_form)

        # Apply styling to buttons
        button_style = """
            QPushButton {
                background-color: #ADD8E6; /* Light Blue */
                border: 1px solid #87CEEB;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #87CEEB; /* Sky Blue */
            }
        """
        self.add_button.setStyleSheet(button_style)
        self.update_button.setStyleSheet(button_style)
        self.delete_button.setStyleSheet(button_style)
        self.clear_button.setStyleSheet(button_style)

        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.update_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.clear_button)
        main_layout.addLayout(buttons_layout)

        # Table View
        self.units_table = QTableView()
        self.units_model = UnitsTableModel(unit_service=self.unit_service, parent_widget=self) # Pass unit_service and self to model
        self.units_table.setModel(self.units_model)
        self.units_table.clicked.connect(self.select_unit)
        self.units_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns

        # Apply styling to table header and alternate rows
        table_style = """
            QTableView {
                alternate-background-color: #F0F8FF; /* AliceBlue */
                background-color: #FFFFFF;
                selection-background-color: #ADD8E6;
            }
            QHeaderView::section {
                background-color: #87CEEB; /* Sky Blue */
                color: white;
                padding: 4px;
                border: 1px solid #6A9FBC;
            }
        """
        self.units_table.setStyleSheet(table_style)
        self.units_table.setAlternatingRowColors(True)

        main_layout.addWidget(self.units_table)

        self.setLayout(main_layout)
        self.load_units() # Load units after init_ui

    def load_units(self):
        units = self.unit_service.get_all_units()
        self.units_model.update_data(units)
        self.units_table.resizeColumnsToContents()

    def clear_form(self):
        self.selected_unit_id = None
        self.name_ar_input.clear()
        self.name_en_input.clear()
        self.base_quantity_input.setText("1.0")
        self.is_active_checkbox.setChecked(False) # Changed from is_base_unit_checkbox
        self.add_button.setEnabled(True)
        self.update_button.setEnabled(False)
        self.delete_button.setEnabled(False)

    def select_unit(self, index):
        unit = self.units_model.get_unit_at_row(index.row())
        if unit:
            self.selected_unit_id = unit.id
            self.name_ar_input.setText(unit.name_ar)
            self.name_en_input.setText(unit.name_en)
            self.base_quantity_input.setText(str(unit.base_quantity))
            self.is_active_checkbox.setChecked(unit.is_active) # Changed from is_base_unit_checkbox
            self.add_button.setEnabled(False)
            self.update_button.setEnabled(True)
            self.delete_button.setEnabled(True)

    def add_unit(self):
        name_ar = self.name_ar_input.text().strip()
        name_en = self.name_en_input.text().strip()
        base_quantity_str = self.base_quantity_input.text().strip()
        is_active = self.is_active_checkbox.isChecked() # Changed from is_base_unit

        if not name_ar:
            QMessageBox.warning(self, "Input Error", "Unit Arabic Name cannot be empty.")
            return

        try:
            base_quantity = Decimal(base_quantity_str)
            if base_quantity <= 0:
                QMessageBox.warning(self, "Input Error", "Base Quantity must be a positive number.")
                return
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Invalid value for Base Quantity. Please enter a number.")
            return

        try:
            # company_id is no longer needed for Unit creation
            self.unit_service.create_unit(name_ar, name_en if name_en else None, base_quantity, is_active=is_active) # Pass is_active
            QMessageBox.information(self, "Success", "Unit added successfully.")
            self.clear_form()
            self.load_units()
            self.unit_updated.emit() # Emit signal
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def update_unit(self):
        if not self.selected_unit_id:
            QMessageBox.warning(self, "Selection Error", "Please select a unit to update.")
            return

        name_ar = self.name_ar_input.text().strip()
        name_en = self.name_en_input.text().strip()
        base_quantity_str = self.base_quantity_input.text().strip()
        is_active = self.is_active_checkbox.isChecked() # Changed from is_base_unit

        if not name_ar:
            QMessageBox.warning(self, "Input Error", "Unit Arabic Name cannot be empty.")
            return

        try:
            base_quantity = Decimal(base_quantity_str)
            if base_quantity <= 0:
                QMessageBox.warning(self, "Input Error", "Base Quantity must be a positive number.")
                return
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Invalid value for Base Quantity. Please enter a number.")
            return

        try:
            self.unit_service.update_unit(self.selected_unit_id, name_ar=name_ar, name_en=name_en if name_en else None, base_quantity=base_quantity, is_active=is_active) # Changed from is_base_unit
            QMessageBox.information(self, "Success", "Unit updated successfully.")
            self.clear_form()
            self.load_units()
            self.unit_updated.emit() # Emit signal
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def delete_unit(self):
        if not self.selected_unit_id:
            QMessageBox.warning(self, "Selection Error", "Please select a unit to delete.")
            return

        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this unit?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.unit_service.delete_unit(self.selected_unit_id)
                QMessageBox.information(self, "Success", "Unit deleted successfully.")
                self.clear_form()
                self.load_units()
                self.unit_updated.emit() # Emit signal
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete unit: {e}")

