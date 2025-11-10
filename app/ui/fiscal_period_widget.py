from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QSpinBox, QFormLayout, QGroupBox, QHeaderView, QCheckBox
from PySide6.QtCore import QDate
from app.application.services import CompanyService
#from app.infrastructure.database import get_db # No longer needed

class FiscalPeriodWidget(QWidget):
    def __init__(self, fiscal_period_service, company_service, parent=None):
        super().__init__(parent)
        self.fiscal_period_service = fiscal_period_service
        self.company_service = company_service
        self.init_ui()
        self.load_fiscal_periods()

    def init_ui(self):
        self.setWindowTitle("Fiscal Period Management")
        # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # Fiscal Period form
        form_group_box = QGroupBox("Fiscal Period Details")
        form_layout = QFormLayout()

        self.company_id_input = QComboBox()
        self.load_companies_to_combobox(self.company_id_input)
        form_layout.addRow(QLabel("Company:"), self.company_id_input)

        self.year_input = QSpinBox()
        self.year_input.setRange(1900, 2100)
        self.year_input.setValue(QDate.currentDate().year())
        form_layout.addRow(QLabel("Year:"), self.year_input)

        self.start_date_input = QDateEdit(QDate.currentDate())
        self.start_date_input.setCalendarPopup(True)
        form_layout.addRow(QLabel("Start Date:"), self.start_date_input)

        self.end_date_input = QDateEdit(QDate.currentDate())
        self.end_date_input.setCalendarPopup(True)
        form_layout.addRow(QLabel("End Date:"), self.end_date_input)

        self.is_closed_input = QCheckBox("Is Closed")
        self.is_closed_input.setChecked(False)
        form_layout.addRow(QLabel("Closed:"), self.is_closed_input)

        add_button = QPushButton("Add Fiscal Period")
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        add_button.clicked.connect(self.add_fiscal_period)
        
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

        # Fiscal Period table
        self.fiscal_periods_table = QTableWidget()
        self.fiscal_periods_table.setColumnCount(6) # Increased column count
        self.fiscal_periods_table.setHorizontalHeaderLabels(["ID", "Company", "Year", "Start Date", "End Date", "Closed"])
        self.fiscal_periods_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        
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
        self.fiscal_periods_table.setStyleSheet(table_style)
        self.fiscal_periods_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.fiscal_periods_table)

        main_layout.addStretch(1) # Add stretch to push content upwards and fill remaining space

        self.setLayout(main_layout)

    def load_companies_to_combobox(self, combobox):
        combobox.clear()
        companies = self.company_service.get_all_companies()
        combobox.addItem("Select Company", 0) # Default empty item
        for company in companies:
            combobox.addItem(f"{company.name_en} ({company.code})", company.id)

    def load_fiscal_periods(self):
        self.fiscal_periods_table.setRowCount(0)
        periods = self.fiscal_period_service.get_all_fiscal_periods()
        self.fiscal_periods_table.setRowCount(len(periods))
        for row, period in enumerate(periods):
            company = self.company_service.get_company_by_id(period.company_id)
            company_name = company.name_en if company else "Unknown Company"

            self.fiscal_periods_table.setItem(row, 0, QTableWidgetItem(str(period.id)))
            self.fiscal_periods_table.setItem(row, 1, QTableWidgetItem(company_name))
            self.fiscal_periods_table.setItem(row, 2, QTableWidgetItem(str(period.year)))
            self.fiscal_periods_table.setItem(row, 3, QTableWidgetItem(str(period.start_date)))
            self.fiscal_periods_table.setItem(row, 4, QTableWidgetItem(str(period.end_date)))
            self.fiscal_periods_table.setItem(row, 5, QTableWidgetItem("Open" if period.is_open else "Closed"))

    def add_fiscal_period(self):
        try:
            company_id = self.company_id_input.currentData()
            year = self.year_input.value()
            start_date = self.start_date_input.date().toPython()
            end_date = self.end_date_input.date().toPython()
            is_closed = self.is_closed_input.isChecked()

            if not company_id or not year or not start_date or not end_date:
                QMessageBox.warning(self, "Input Error", "Company, Year, Start Date, and End Date are required.")
                return

            self.fiscal_period_service.create_fiscal_period(
                company_id=company_id,
                year=year,
                start_date=start_date,
                end_date=end_date,
                is_closed=is_closed
            )
            self.clear_form()
            self.load_fiscal_periods()
            QMessageBox.information(self, "Success", "Fiscal Period added successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.company_id_input.setCurrentIndex(0)
        self.year_input.setValue(QDate.currentDate().year())
        self.start_date_input.setDate(QDate.currentDate())
        self.end_date_input.setDate(QDate.currentDate())
        self.is_closed_input.setChecked(False)
