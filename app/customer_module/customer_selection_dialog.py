from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QLabel
from PySide6.QtCore import Qt, Signal, Slot
from app.application.services import ARAPService

class CustomerSelectionDialog(QDialog):
    customer_selected = Signal(int, str) # Signal to emit selected customer ID and name

    def __init__(self, arap_service: ARAPService, parent=None):
        super().__init__(parent)
        self.setWindowTitle("اختيار العميل")
        self.setGeometry(200, 200, 600, 400) # x, y, width, height
        self.arap_service = arap_service
        self.selected_customer_id = None
        self.selected_customer_name = None

        self.init_ui()
        self._load_customers()
        self._connect_signals()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Search input
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ابحث برقم/اسم العميل أو رقم الهاتف...")
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)

        # Customer table
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(5) # ID, Code, Arabic Name, Phone, Address
        self.customers_table.setHorizontalHeaderLabels(["المعرف", "الرمز", "الاسم العربي", "رقم الهاتف", "العنوان"])
        self.customers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.customers_table.setSelectionMode(QTableWidget.SingleSelection)
        self.customers_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.customers_table)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.select_button = QPushButton("تحديد")
        self.cancel_button = QPushButton("إلغاء")
        buttons_layout.addWidget(self.select_button)
        buttons_layout.addWidget(self.cancel_button)
        main_layout.addLayout(buttons_layout)

        self.customers_table.horizontalHeader().setStretchLastSection(True)

    def _connect_signals(self):
        self.search_input.textChanged.connect(self._filter_customers)
        self.select_button.clicked.connect(self._on_select_customer)
        self.cancel_button.clicked.connect(self.reject)
        self.customers_table.doubleClicked.connect(self._on_table_double_clicked)

    def _load_customers(self):
        self.customers_table.setRowCount(0) # Clear existing rows
        customers = self.arap_service.get_all_customers() # Assuming this method exists in ARAPService
        for row_num, customer in enumerate(customers):
            self.customers_table.insertRow(row_num)
            self.customers_table.setItem(row_num, 0, QTableWidgetItem(str(customer.id)))
            self.customers_table.setItem(row_num, 1, QTableWidgetItem(customer.code or ""))
            self.customers_table.setItem(row_num, 2, QTableWidgetItem(customer.name_ar or customer.name_en or ""))
            self.customers_table.setItem(row_num, 3, QTableWidgetItem(customer.phone_number or ""))
            self.customers_table.setItem(row_num, 4, QTableWidgetItem(customer.address or ""))

    def _filter_customers(self, text):
        self.customers_table.setRowCount(0)
        all_customers = self.arap_service.get_all_customers()
        filtered_customers = [c for c in all_customers if
                              text.lower() in str(c.id).lower() or
                              text.lower() in (c.code or "").lower() or
                              text.lower() in (c.name_ar or "").lower() or
                              text.lower() in (c.name_en or "").lower() or
                              text.lower() in (c.phone_number or "").lower()]
        for row_num, customer in enumerate(filtered_customers):
            self.customers_table.insertRow(row_num)
            self.customers_table.setItem(row_num, 0, QTableWidgetItem(str(customer.id)))
            self.customers_table.setItem(row_num, 1, QTableWidgetItem(customer.code or ""))
            self.customers_table.setItem(row_num, 2, QTableWidgetItem(customer.name_ar or customer.name_en or ""))
            self.customers_table.setItem(row_num, 3, QTableWidgetItem(customer.phone_number or ""))
            self.customers_table.setItem(row_num, 4, QTableWidgetItem(customer.address or ""))

    def _on_select_customer(self):
        selected_rows = self.customers_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_customer_id = int(self.customers_table.item(row, 0).text())
            self.selected_customer_name = self.customers_table.item(row, 2).text()
            self.customer_selected.emit(self.selected_customer_id, self.selected_customer_name)
            self.accept()
        else:
            QMessageBox.warning(self, "تحديد عميل", "الرجاء تحديد عميل.")

    def _on_table_double_clicked(self, index):
        row = index.row()
        self.selected_customer_id = int(self.customers_table.item(row, 0).text())
        self.selected_customer_name = self.customers_table.item(row, 2).text()
        self.customer_selected.emit(self.selected_customer_id, self.selected_customer_name)
        self.accept()
