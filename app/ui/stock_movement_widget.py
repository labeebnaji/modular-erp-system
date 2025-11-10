from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QSpinBox, QFormLayout, QGroupBox, QHeaderView
from PySide6.QtCore import QDate
from app.application.services import InventoryService, CompanyService # Added CompanyService
#from app.infrastructure.database import get_db # No longer needed
from decimal import Decimal

class StockMovementWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inventory_service = InventoryService()
        self.company_service = CompanyService() # Initialize CompanyService
        self.init_ui()
        self.load_stock_movements()

    def init_ui(self):
        self.setWindowTitle("Stock Movements")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Stock Movement form
        form_group_box = QGroupBox("Record New Stock Movement")
        form_layout = QFormLayout()

        self.company_id_input = QComboBox()
        self.load_companies_to_combobox(self.company_id_input)
        form_layout.addRow(QLabel("Company:"), self.company_id_input)

        self.branch_id_input = QComboBox()
        self.load_branches_to_combobox(self.branch_id_input, self.company_id_input.currentData())
        form_layout.addRow(QLabel("Branch:"), self.branch_id_input)

        self.item_id_input = QComboBox()
        self.load_items_into_combobox()
        form_layout.addRow(QLabel("Item:"), self.item_id_input)

        self.movement_date_input = QDateEdit(QDate.currentDate())
        self.movement_date_input.setCalendarPopup(True)
        form_layout.addRow(QLabel("Movement Date:"), self.movement_date_input)

        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 1000000)
        form_layout.addRow(QLabel("Quantity:"), self.quantity_input)

        self.movement_type_input = QComboBox()
        self.movement_type_input.addItems(["In", "Out", "Transfer", "Adjustment", "Waste"])
        form_layout.addRow(QLabel("Type:"), self.movement_type_input)

        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Location")
        # Icon placeholder: self.location_input.addAction(QIcon("path/to/location_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Location:"), self.location_input)

        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("Reference")
        # Icon placeholder: self.reference_input.addAction(QIcon("path/to/ref_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Reference:"), self.reference_input)

        add_button = QPushButton("Record Movement")
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        add_button.clicked.connect(self.add_stock_movement)
        form_layout.addRow(add_button)

        form_group_box.setLayout(form_layout)
        main_layout.addWidget(form_group_box)

        self.stock_movements_table = QTableWidget()
        self.stock_movements_table.setColumnCount(10) # Increased column count
        self.stock_movements_table.setHorizontalHeaderLabels(["ID", "Company", "Branch", "Item", "Date", "Type", "Quantity", "Location", "Reference", "Actions"])
        self.stock_movements_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        main_layout.addWidget(self.stock_movements_table)

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
        branches = self.company_service.get_all_branches() # This needs to be filtered by company_id in a real scenario
        combobox.addItem("Select Branch", 0)
        for branch in branches:
            if branch.company_id == company_id: # Basic filtering
                combobox.addItem(f"{branch.name_en} ({branch.code})", branch.id)

    def load_items_into_combobox(self):
        self.item_id_input.clear()
        items = self.inventory_service.get_all_items()
        for item in items:
            self.item_id_input.addItem(f"{item.name_en} ({item.code})", item.id)

    def load_stock_movements(self):
        self.stock_movements_table.setRowCount(0)
        try:
            movements = self.inventory_service.get_all_stock_movements()
            self.stock_movements_table.setRowCount(len(movements))
            for row, movement in enumerate(movements):
                company = self.company_service.get_company_by_id(movement.company_id)
                company_name = company.name_en if company else "Unknown Company"
                branch = self.company_service.get_branch_by_id(movement.branch_id)
                branch_name = branch.name_en if branch else "Unknown Branch"
                item = self.inventory_service.get_item_by_id(movement.item_id)
                item_name = item.name_en if item else "Unknown Item"

                self.stock_movements_table.setItem(row, 0, QTableWidgetItem(str(movement.id)))
                self.stock_movements_table.setItem(row, 1, QTableWidgetItem(company_name))
                self.stock_movements_table.setItem(row, 2, QTableWidgetItem(branch_name))
                self.stock_movements_table.setItem(row, 3, QTableWidgetItem(item_name))
                self.stock_movements_table.setItem(row, 4, QTableWidgetItem(str(movement.movement_date)))
                self.stock_movements_table.setItem(row, 5, QTableWidgetItem(self.movement_type_input.itemText(movement.movement_type)))
                self.stock_movements_table.setItem(row, 6, QTableWidgetItem(str(movement.quantity)))
                self.stock_movements_table.setItem(row, 7, QTableWidgetItem(movement.location if hasattr(movement, 'location') else "N/A")) # Assuming location is a field
                self.stock_movements_table.setItem(row, 8, QTableWidgetItem(movement.ref_no if movement.ref_no else "N/A"))
                # Add actions (e.g., Edit, Delete buttons) later
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load stock movements: {e}")

    def add_stock_movement(self):
        company_id = self.company_id_input.currentData()
        branch_id = self.branch_id_input.currentData()
        item_id = self.item_id_input.currentData()
        movement_date = self.movement_date_input.date().toPython()
        quantity = Decimal(self.quantity_input.value())
        movement_type = self.movement_type_input.currentIndex()
        location = self.location_input.text()
        reference = self.reference_input.text()

        if not company_id or not branch_id or not item_id or not quantity:
            QMessageBox.warning(self, "Input Error", "Company, Branch, Item, and Quantity are required.")
            return

        try:
            self.inventory_service.record_stock_movement(
                company_id=company_id,
                branch_id=branch_id,
                item_id=item_id,
                movement_date=movement_date,
                quantity=quantity,
                movement_type=movement_type,
                location=location,
                ref_no=reference
            )
            QMessageBox.information(self, "Success", "Stock Movement recorded successfully.")
            self.clear_form()
            self.load_stock_movements()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to record stock movement: {e}")

    def clear_form(self):
        self.company_id_input.setCurrentIndex(0)
        self.branch_id_input.setCurrentIndex(0)
        self.item_id_input.setCurrentIndex(0)
        self.movement_date_input.setDate(QDate.currentDate())
        self.quantity_input.setValue(0)
        self.movement_type_input.setCurrentIndex(0)
        self.location_input.clear()
        self.reference_input.clear()
