from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from PySide6.QtCore import Qt, Signal, Slot
from app.application.services import ARAPService

class SupplierSelectionDialog(QDialog):
    supplier_selected = Signal(int, str) # Signal to emit selected supplier ID and name

    def __init__(self, arap_service: ARAPService, parent=None):
        super().__init__(parent)
        self.setWindowTitle("اختيار المورد")
        self.setGeometry(200, 200, 600, 400)
        self.arap_service = arap_service
        self.selected_supplier_id = None
        self.selected_supplier_name = None

        self.init_ui()
        self._load_suppliers()
        self._connect_signals()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Search input
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ابحث برقم/اسم المورد أو رقم الهاتف...")
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)

        # Supplier table
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setColumnCount(4) # ID, Code, Arabic Name, English Name
        self.suppliers_table.setHorizontalHeaderLabels(["المعرف", "الرمز", "الاسم العربي", "الاسم الإنجليزي"])
        self.suppliers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.suppliers_table.setSelectionMode(QTableWidget.SingleSelection)
        self.suppliers_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.suppliers_table)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.select_button = QPushButton("تحديد")
        self.cancel_button = QPushButton("إلغاء")
        buttons_layout.addWidget(self.select_button)
        buttons_layout.addWidget(self.cancel_button)
        main_layout.addLayout(buttons_layout)

        self.suppliers_table.horizontalHeader().setStretchLastSection(True)

    def _connect_signals(self):
        self.search_input.textChanged.connect(self._filter_suppliers)
        self.select_button.clicked.connect(self._on_select_supplier)
        self.cancel_button.clicked.connect(self.reject)
        self.suppliers_table.doubleClicked.connect(self._on_table_double_clicked)

    def _load_suppliers(self):
        self.suppliers_table.setRowCount(0) # Clear existing rows
        suppliers = self.arap_service.get_all_suppliers() # Assuming this method exists in ARAPService
        for row_num, supplier in enumerate(suppliers):
            self.suppliers_table.insertRow(row_num)
            self.suppliers_table.setItem(row_num, 0, QTableWidgetItem(str(supplier.id)))
            self.suppliers_table.setItem(row_num, 1, QTableWidgetItem(supplier.code or ""))
            self.suppliers_table.setItem(row_num, 2, QTableWidgetItem(supplier.name_ar or ""))
            self.suppliers_table.setItem(row_num, 3, QTableWidgetItem(supplier.name_en or ""))

    def _filter_suppliers(self, text):
        self.suppliers_table.setRowCount(0)
        all_suppliers = self.arap_service.get_all_suppliers()
        filtered_suppliers = [s for s in all_suppliers if
                              text.lower() in str(s.id).lower() or
                              text.lower() in (s.code or "").lower() or
                              text.lower() in (s.name_ar or "").lower() or
                              text.lower() in (s.name_en or "").lower()]
        for row_num, supplier in enumerate(filtered_suppliers):
            self.suppliers_table.insertRow(row_num)
            self.suppliers_table.setItem(row_num, 0, QTableWidgetItem(str(supplier.id)))
            self.suppliers_table.setItem(row_num, 1, QTableWidgetItem(supplier.code or ""))
            self.suppliers_table.setItem(row_num, 2, QTableWidgetItem(supplier.name_ar or ""))
            self.suppliers_table.setItem(row_num, 3, QTableWidgetItem(supplier.name_en or ""))

    def _on_select_supplier(self):
        selected_rows = self.suppliers_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_supplier_id = int(self.suppliers_table.item(row, 0).text())
            self.selected_supplier_name = self.suppliers_table.item(row, 2).text()
            self.supplier_selected.emit(self.selected_supplier_id, self.selected_supplier_name)
            self.accept()
        else:
            QMessageBox.warning(self, "تحديد مورد", "الرجاء تحديد مورد.")

    def _on_table_double_clicked(self, index):
        row = index.row()
        self.selected_supplier_id = int(self.suppliers_table.item(row, 0).text())
        self.selected_supplier_name = self.suppliers_table.item(row, 2).text()
        self.supplier_selected.emit(self.selected_supplier_id, self.selected_supplier_name)
        self.accept()
