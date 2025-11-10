from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QSpinBox, QComboBox, QFormLayout, QGroupBox, QHeaderView
from PySide6.QtCore import QDate, Qt
from app.application.services import JournalService, AccountService
from app.ui.base_widget import TranslatableWidget
from app.i18n.translations import tr, get_language
from decimal import Decimal

class JournalsWidget(TranslatableWidget):
    def __init__(self, journal_service, parent=None):
        super().__init__(parent)
        self.journal_service = journal_service
        self.account_service = AccountService()
        self.accounts = {account.id: account for account in self.account_service.get_all_accounts()}
        self.init_ui()
        self.load_journal_entries()

    def init_ui(self):
        self.setWindowTitle(tr("windows.journals"))
        # self.setGeometry(100, 100, 1200, 800) # Removed fixed geometry

        main_layout = QVBoxLayout(self)

        # --- Journal Entry Creation Form ---
        form_group_box = QGroupBox("Create New Journal Entry")
        form_main_layout = QVBoxLayout()

        # Header fields using QFormLayout
        header_form_layout = QFormLayout()
        self.company_id_input = QLineEdit("1") # Default for now
        self.company_id_input.setPlaceholderText("Company ID")
        header_form_layout.addRow(QLabel("Company ID:"), self.company_id_input)

        self.branch_id_input = QLineEdit("1") # Default for now
        self.branch_id_input.setPlaceholderText("Branch ID")
        header_form_layout.addRow(QLabel("Branch ID:"), self.branch_id_input)

        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        header_form_layout.addRow(QLabel("Date:"), self.date_input)

        self.period_input = QLineEdit(QDate.currentDate().toString("yyyy-MM"))
        self.period_input.setPlaceholderText("Period (YYYY-MM)")
        header_form_layout.addRow(QLabel("Period:"), self.period_input)

        self.ref_no_input = QLineEdit()
        self.ref_no_input.setPlaceholderText("Reference No.")
        header_form_layout.addRow(QLabel("Ref No:"), self.ref_no_input)

        self.created_by_input = QLineEdit("1") # Default for now
        self.created_by_input.setPlaceholderText("Created By (User ID)")
        header_form_layout.addRow(QLabel("Created By:"), self.created_by_input)
        form_main_layout.addLayout(header_form_layout)

        # Journal Lines Table
        form_main_layout.addWidget(QLabel("Journal Lines:"))
        self.lines_table = QTableWidget()
        self.lines_table.setColumnCount(6)
        self.lines_table.setHorizontalHeaderLabels(["Account ID", "Account Name", "Debit", "Credit", "Currency", "Memo"])
        self.lines_table.setRowCount(1) # Start with one empty line
        self.lines_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        self.lines_table.itemChanged.connect(self.calculate_totals) # Connect for auto-calculation

        self.add_line_button = QPushButton("Add Line")
        # Add icon placeholder for add_line_button: self.add_line_button.setIcon(QIcon("path/to/add_line_icon.png"))
        self.add_line_button.clicked.connect(self.add_journal_line_row)
        
        # Apply styling to lines table
        lines_table_style = """
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
        self.lines_table.setStyleSheet(lines_table_style)
        self.lines_table.setAlternatingRowColors(True)
        
        form_main_layout.addWidget(self.lines_table)
        form_main_layout.addWidget(self.add_line_button)

        # Totals display
        totals_layout = QHBoxLayout()
        self.total_debit_label = QLabel("Total Debit: 0.00")
        self.total_credit_label = QLabel("Total Credit: 0.00")
        totals_layout.addWidget(self.total_debit_label)
        totals_layout.addWidget(self.total_credit_label)
        form_main_layout.addLayout(totals_layout)

        self.create_journal_button = QPushButton("Create Journal Entry")
        # Add icon placeholder for create_journal_button: self.create_journal_button.setIcon(QIcon("path/to/save_icon.png"))
        self.create_journal_button.clicked.connect(self.create_journal_entry)
        
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
        self.add_line_button.setStyleSheet(button_style)
        self.create_journal_button.setStyleSheet(button_style)
        
        form_main_layout.addWidget(self.create_journal_button)

        form_group_box.setLayout(form_main_layout)
        main_layout.addWidget(form_group_box)

        # --- Existing Journal Entries ---
        main_layout.addWidget(QLabel("Existing Journal Entries"))
        self.journal_entries_table = QTableWidget()
        self.journal_entries_table.setColumnCount(8)
        self.journal_entries_table.setHorizontalHeaderLabels(["ID", "Company", "Branch", "Date", "Period", "Ref No", "Status", "Created By"])
        self.journal_entries_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        
        # Apply styling to journal entries table
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
        self.journal_entries_table.setStyleSheet(table_style)
        self.journal_entries_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.journal_entries_table)

        main_layout.addStretch(1) # Add stretch to push content upwards and fill remaining space

        self.setLayout(main_layout)

    def add_journal_line_row(self):
        row_count = self.lines_table.rowCount()
        self.lines_table.setRowCount(row_count + 1)
        self.lines_table.setItem(row_count, 4, QTableWidgetItem("USD")) # Default currency
        # Add a QComboBox for account selection
        account_id_combo = QComboBox()
        account_id_combo.addItem("", 0) # Empty item
        for acc_id, account in self.accounts.items():
            account_id_combo.addItem(f"{account.code} - {account.name_ar}", acc_id)
        account_id_combo.currentIndexChanged.connect(self.update_account_name_in_table)
        self.lines_table.setCellWidget(row_count, 0, account_id_combo)

    def update_account_name_in_table(self, index):
        combo = self.sender()
        row = self.lines_table.indexAt(combo.pos()).row()
        account_id = combo.itemData(index)
        if account_id and account_id in self.accounts:
            account = self.accounts[account_id]
            self.lines_table.setItem(row, 1, QTableWidgetItem(account.name_ar))
        else:
            self.lines_table.setItem(row, 1, QTableWidgetItem(""))

    def calculate_totals(self):
        total_debit = Decimal(0)
        total_credit = Decimal(0)
        for row in range(self.lines_table.rowCount()):
            debit_item = self.lines_table.item(row, 2)
            credit_item = self.lines_table.item(row, 3)
            try:
                if debit_item and debit_item.text():
                    total_debit += Decimal(debit_item.text())
                if credit_item and credit_item.text():
                    total_credit += Decimal(credit_item.text())
            except ValueError:
                pass # Ignore invalid number formats for now
        self.total_debit_label.setText(f"Total Debit: {total_debit:.2f}")
        self.total_credit_label.setText(f"Total Credit: {total_credit:.2f}")

    def create_journal_entry(self):
        try:
            company_id = int(self.company_id_input.text())
            branch_id = int(self.branch_id_input.text())
            entry_date = self.date_input.date().toPython()
            period = self.period_input.text()
            ref_no = self.ref_no_input.text()
            created_by = int(self.created_by_input.text())

            lines_data = []
            for row in range(self.lines_table.rowCount()):
                account_id_combo = self.lines_table.cellWidget(row, 0)
                account_id = account_id_combo.currentData()

                debit_item = self.lines_table.item(row, 2)
                credit_item = self.lines_table.item(row, 3)
                currency_item = self.lines_table.item(row, 4)
                memo_item = self.lines_table.item(row, 5)

                debit = Decimal(debit_item.text()) if debit_item and debit_item.text() else Decimal(0)
                credit = Decimal(credit_item.text()) if credit_item and credit_item.text() else Decimal(0)
                currency = currency_item.text() if currency_item and currency_item.text() else "USD"
                memo = memo_item.text() if memo_item and memo_item.text() else None

                if not account_id or (debit == 0 and credit == 0):
                    continue # Skip empty lines

                lines_data.append({
                    'account_id': account_id,
                    'debit': debit,
                    'credit': credit,
                    'currency': currency,
                    'memo': memo
                })

            if not lines_data:
                QMessageBox.warning(self, "Input Error", "At least one journal line is required.")
                return

            # Validate if debits equal credits before sending to service
            total_debit_ui = sum(line['debit'] for line in lines_data)
            total_credit_ui = sum(line['credit'] for line in lines_data)
            if total_debit_ui != total_credit_ui:
                QMessageBox.warning(self, "Validation Error", f"Debits ({total_debit_ui:.2f}) do not equal Credits ({total_credit_ui:.2f}).")
                return

            self.journal_service.create_journal_entry(
                company_id=company_id,
                branch_id=branch_id,
                entry_date=entry_date,
                period=period,
                ref_no=ref_no,
                created_by=created_by,
                lines_data=lines_data
            )
            self.clear_form()
            self.load_journal_entries()
            QMessageBox.information(self, "Success", "Journal Entry created successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.ref_no_input.clear()
        self.lines_table.clearContents()
        self.lines_table.setRowCount(1) # Reset to one empty line
        self.total_debit_label.setText("Total Debit: 0.00")
        self.total_credit_label.setText("Total Credit: 0.00")
        # Re-add combobox to the first row
        account_id_combo = QComboBox()
        account_id_combo.addItem("", 0) # Empty item
        for acc_id, account in self.accounts.items():
            account_id_combo.addItem(f"{account.code} - {account.name_ar}", acc_id)
        account_id_combo.currentIndexChanged.connect(self.update_account_name_in_table)
        self.lines_table.setCellWidget(0, 0, account_id_combo)


    def load_journal_entries(self):
        self.journal_entries_table.setRowCount(0)
        entries = self.journal_service.get_all_journal_entries()
        self.journal_entries_table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            status_map = {0: "Draft", 1: "Approved", 2: "Posted", 3: "Voided"}
            self.journal_entries_table.setItem(row, 0, QTableWidgetItem(str(entry.id)))
            self.journal_entries_table.setItem(row, 1, QTableWidgetItem(str(entry.company_id)))
            self.journal_entries_table.setItem(row, 2, QTableWidgetItem(str(entry.branch_id) if entry.branch_id else ""))
            self.journal_entries_table.setItem(row, 3, QTableWidgetItem(str(entry.date)))
            self.journal_entries_table.setItem(row, 4, QTableWidgetItem(entry.period))
            self.journal_entries_table.setItem(row, 5, QTableWidgetItem(entry.ref_no))
            self.journal_entries_table.setItem(row, 6, QTableWidgetItem(status_map.get(entry.status, "Unknown")))
            self.journal_entries_table.setItem(row, 7, QTableWidgetItem(str(entry.created_by)))

    def refresh_translations(self):
        """Refresh all translatable elements"""
        super().refresh_translations()
        
        # Update window title
        self.setWindowTitle(tr('windows.journals'))
        
        # Update buttons if they exist
        for button in self.findChildren(QPushButton):
            button_text = button.text().lower()
            if 'add' in button_text or 'إضافة' in button_text:
                button.setText(tr('common.add'))
            elif 'post' in button_text or 'ترحيل' in button_text:
                button.setText(tr('journals.post'))
            elif 'delete' in button_text or 'حذف' in button_text:
                button.setText(tr('common.delete'))
            elif 'refresh' in button_text or 'تحديث' in button_text:
                button.setText(tr('common.refresh'))
