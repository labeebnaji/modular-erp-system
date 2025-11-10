from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QSpinBox, QFormLayout, QGroupBox, QHeaderView, QDoubleSpinBox
from PySide6.QtCore import QDate
from app.application.services import PayrollService, CompanyService # Added CompanyService
#from app.infrastructure.database import get_db # No longer needed
from decimal import Decimal

class PayrunWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.payroll_service = PayrollService()
        self.company_service = CompanyService() # Initialize CompanyService
        self.init_ui()
        self.load_payruns()

    def init_ui(self):
        self.setWindowTitle("Payrun Management")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Payrun form
        form_group_box = QGroupBox("Payrun Details")
        form_layout = QFormLayout()

        self.company_id_input = QComboBox()
        self.load_companies_to_combobox(self.company_id_input)
        form_layout.addRow(QLabel("Company:"), self.company_id_input)

        self.branch_id_input = QComboBox()
        self.load_branches_to_combobox(self.branch_id_input, self.company_id_input.currentData())
        form_layout.addRow(QLabel("Branch:"), self.branch_id_input)

        self.payrun_name_input = QLineEdit()
        self.payrun_name_input.setPlaceholderText("Payrun Name (e.g., Monthly Payroll)")
        # Icon placeholder: self.payrun_name_input.addAction(QIcon("path/to/payrun_name_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Payrun Name:"), self.payrun_name_input)

        self.start_date_input = QDateEdit(QDate.currentDate().addDays(-30))
        self.start_date_input.setCalendarPopup(True)
        form_layout.addRow(QLabel("Start Date:"), self.start_date_input)

        self.end_date_input = QDateEdit(QDate.currentDate())
        self.end_date_input.setCalendarPopup(True)
        form_layout.addRow(QLabel("End Date:"), self.end_date_input)

        self.payment_date_input = QDateEdit(QDate.currentDate().addDays(5))
        self.payment_date_input.setCalendarPopup(True)
        form_layout.addRow(QLabel("Payment Date:"), self.payment_date_input)

        self.total_amount_input = QDoubleSpinBox()
        self.total_amount_input.setRange(0.00, 999999999.99)
        self.total_amount_input.setPrefix("$")
        form_layout.addRow(QLabel("Total Amount:"), self.total_amount_input)

        self.status_input = QComboBox()
        self.status_input.addItems(["Draft", "Approved", "Paid", "Cancelled"])
        form_layout.addRow(QLabel("Status:"), self.status_input)

        add_button = QPushButton("Add Payrun")
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        add_button.clicked.connect(self.add_payrun)
        form_layout.addRow(add_button)

        form_group_box.setLayout(form_layout)
        main_layout.addWidget(form_group_box)

        # Payrun table
        self.payruns_table = QTableWidget()
        self.payruns_table.setColumnCount(9) # Increased column count
        self.payruns_table.setHorizontalHeaderLabels(["ID", "Company", "Branch", "Payrun Name", "Start Date", "End Date", "Payment Date", "Total Amount", "Status"])
        self.payruns_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        main_layout.addWidget(self.payruns_table)

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
        branches = self.company_service.get_all_branches()
        combobox.addItem("Select Branch", 0)
        for branch in branches:
            if branch.company_id == company_id: # Basic filtering
                combobox.addItem(f"{branch.name_en} ({branch.code})", branch.id)

    def load_payruns(self):
        self.payruns_table.setRowCount(0)
        payruns = self.payroll_service.get_all_payruns()
        self.payruns_table.setRowCount(len(payruns))
        for row, payrun in enumerate(payruns):
            company = self.company_service.get_company_by_id(payrun.company_id)
            company_name = company.name_en if company else "Unknown Company"
            branch = self.company_service.get_branch_by_id(payrun.branch_id)
            branch_name = branch.name_en if branch else "Unknown Branch"

            self.payruns_table.setItem(row, 0, QTableWidgetItem(str(payrun.id)))
            self.payruns_table.setItem(row, 1, QTableWidgetItem(company_name))
            self.payruns_table.setItem(row, 2, QTableWidgetItem(branch_name))
            self.payruns_table.setItem(row, 3, QTableWidgetItem(payrun.payrun_name))
            self.payruns_table.setItem(row, 4, QTableWidgetItem(str(payrun.start_date)))
            self.payruns_table.setItem(row, 5, QTableWidgetItem(str(payrun.end_date)))
            self.payruns_table.setItem(row, 6, QTableWidgetItem(str(payrun.payment_date)))
            self.payruns_table.setItem(row, 7, QTableWidgetItem(str(payrun.total_amount)))
            self.payruns_table.setItem(row, 8, QTableWidgetItem(payrun.status))

    def add_payrun(self):
        try:
            company_id = self.company_id_input.currentData()
            branch_id = self.branch_id_input.currentData()
            payrun_name = self.payrun_name_input.text()
            start_date = self.start_date_input.date().toPython()
            end_date = self.end_date_input.date().toPython()
            payment_date = self.payment_date_input.date().toPython()
            total_amount = Decimal(self.total_amount_input.value())
            status = self.status_input.currentText()

            if not company_id or not branch_id or not payrun_name or not start_date or not end_date or not payment_date or not total_amount:
                QMessageBox.warning(self, "Input Error", "Company, Branch, Payrun Name, Start Date, End Date, Payment Date, and Total Amount are required.")
                return

            self.payroll_service.create_payrun(
                company_id=company_id,
                branch_id=branch_id,
                payrun_name=payrun_name,
                start_date=start_date,
                end_date=end_date,
                payment_date=payment_date,
                total_amount=total_amount,
                status=status
            )
            self.clear_form()
            self.load_payruns()
            QMessageBox.information(self, "Success", "Payrun added successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.company_id_input.setCurrentIndex(0)
        self.branch_id_input.setCurrentIndex(0)
        self.payrun_name_input.clear()
        self.start_date_input.setDate(QDate.currentDate().addDays(-30))
        self.end_date_input.setDate(QDate.currentDate())
        self.payment_date_input.setDate(QDate.currentDate().addDays(5))
        self.total_amount_input.setValue(0.0)
        self.status_input.setCurrentIndex(0)
