from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QCheckBox, QFormLayout, QGroupBox, QHeaderView
from PySide6.QtCore import Qt
from app.application.services import AccountService
from app.ui.base_widget import TranslatableWidget
from app.i18n.translations import tr, get_language

class AccountsWidget(TranslatableWidget):
    def __init__(self, account_service, parent=None):
        super().__init__(parent)
        self.account_service = account_service
        self.init_ui()
        self.load_accounts()

    def init_ui(self):
        self.setWindowTitle(tr('windows.accounts'))

        main_layout = QVBoxLayout(self)

        # Form for adding/editing accounts
        self.form_group_box = QGroupBox()
        self.set_translatable_title(self.form_group_box, 'accounts.account_details')
        form_layout = QFormLayout()

        # Code
        self.code_label = QLabel()
        self.set_translatable_text(self.code_label, 'accounts.account_code')
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText(tr('accounts.account_code'))
        form_layout.addRow(self.code_label, self.code_input)

        # Arabic Name
        self.name_ar_label = QLabel()
        self.set_translatable_text(self.name_ar_label, 'accounts.account_name_ar')
        self.name_ar_input = QLineEdit()
        self.name_ar_input.setPlaceholderText(tr('accounts.account_name_ar'))
        form_layout.addRow(self.name_ar_label, self.name_ar_input)

        # English Name
        self.name_en_label = QLabel()
        self.set_translatable_text(self.name_en_label, 'accounts.account_name_en')
        self.name_en_input = QLineEdit()
        self.name_en_input.setPlaceholderText(tr('accounts.account_name_en'))
        form_layout.addRow(self.name_en_label, self.name_en_input)

        # Type
        self.type_label = QLabel()
        self.set_translatable_text(self.type_label, 'accounts.account_type')
        self.type_input = QComboBox()
        self.update_type_combo()
        form_layout.addRow(self.type_label, self.type_input)

        # Level
        self.level_label = QLabel()
        self.set_translatable_text(self.level_label, 'accounts.level')
        self.level_input = QLineEdit()
        self.level_input.setPlaceholderText(tr('accounts.level'))
        form_layout.addRow(self.level_label, self.level_input)

        # Parent ID
        self.parent_label = QLabel()
        self.set_translatable_text(self.parent_label, 'accounts.parent_account')
        self.parent_id_input = QLineEdit()
        self.parent_id_input.setPlaceholderText(tr('accounts.parent_account'))
        form_layout.addRow(self.parent_label, self.parent_id_input)

        # Currency
        self.currency_label = QLabel()
        self.set_translatable_text(self.currency_label, 'accounts.currency')
        self.currency_input = QLineEdit()
        self.currency_input.setPlaceholderText(tr('accounts.currency'))
        form_layout.addRow(self.currency_label, self.currency_input)

        # Is Postable
        self.is_postable_label = QLabel()
        self.set_translatable_text(self.is_postable_label, 'accounts.is_postable')
        self.is_postable_input = QCheckBox()
        self.is_postable_input.setChecked(True)
        form_layout.addRow(self.is_postable_label, self.is_postable_input)

        # Is Active
        self.is_active_label = QLabel()
        self.set_translatable_text(self.is_active_label, 'common.active')
        self.is_active_input = QCheckBox()
        self.is_active_input.setChecked(True)
        form_layout.addRow(self.is_active_label, self.is_active_input)

        # Add Button
        self.add_button = QPushButton()
        self.set_translatable_text(self.add_button, 'common.add')
        self.add_button.clicked.connect(self.add_account)
        
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
        self.add_button.setStyleSheet(button_style)
        
        form_layout.addRow(self.add_button)

        self.form_group_box.setLayout(form_layout)
        main_layout.addWidget(self.form_group_box)

        # Account table
        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(10)
        self.set_translatable_headers(self.accounts_table, [
            'common.id',
            'accounts.account_code',
            'accounts.account_name_ar',
            'accounts.account_name_en',
            'accounts.account_type',
            'accounts.level',
            'accounts.parent_account',
            'accounts.currency',
            'accounts.is_postable',
            'common.active'
        ])
        self.accounts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
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
        self.accounts_table.setStyleSheet(table_style)
        self.accounts_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.accounts_table)

        main_layout.addStretch(1) # Add stretch to push content upwards and fill remaining space

        self.setLayout(main_layout)

    def load_accounts(self):
        self.accounts_table.setRowCount(0)
        accounts = self.account_service.get_all_accounts()
        self.accounts_table.setRowCount(len(accounts))
        for row, account in enumerate(accounts):
            self.accounts_table.setItem(row, 0, QTableWidgetItem(str(account.id)))
            self.accounts_table.setItem(row, 1, QTableWidgetItem(account.code))
            self.accounts_table.setItem(row, 2, QTableWidgetItem(account.name_ar))
            self.accounts_table.setItem(row, 3, QTableWidgetItem(account.name_en))
            self.accounts_table.setItem(row, 4, QTableWidgetItem(str(account.type)))
            self.accounts_table.setItem(row, 5, QTableWidgetItem(str(account.level)))
            self.accounts_table.setItem(row, 6, QTableWidgetItem(str(account.parent_id) if account.parent_id else ""))
            self.accounts_table.setItem(row, 7, QTableWidgetItem(account.currency))
            self.accounts_table.setItem(row, 8, QTableWidgetItem(str(account.is_postable)))
            self.accounts_table.setItem(row, 9, QTableWidgetItem(str(account.is_active)))

    def add_account(self):
        try:
            code = self.code_input.text()
            name_ar = self.name_ar_input.text()
            name_en = self.name_en_input.text()
            account_type = self.type_input.currentIndex()
            level = int(self.level_input.text())
            parent_id = int(self.parent_id_input.text()) if self.parent_id_input.text() else None
            currency = self.currency_input.text()
            is_postable = self.is_postable_input.isChecked()
            is_active = self.is_active_input.isChecked()

            if not code or not name_ar or not currency:
                QMessageBox.warning(self, "Input Error", "Code, Arabic Name, and Currency are required.")
                return

            self.account_service.create_account(
                code=code,
                name_ar=name_ar,
                name_en=name_en,
                type=account_type,
                level=level,
                parent_id=parent_id,
                currency=currency,
                is_postable=is_postable,
                is_active=is_active
            )
            self.clear_form()
            self.load_accounts()
            QMessageBox.information(self, "Success", "Account added successfully.")
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numbers for Level and Parent ID.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.code_input.clear()
        self.name_ar_input.clear()
        self.name_en_input.clear()
        self.type_input.setCurrentIndex(0)
        self.level_input.clear()
        self.parent_id_input.clear()
        self.currency_input.clear()
        self.is_postable_input.setChecked(True)
        self.is_active_input.setChecked(True)

    def update_type_combo(self):
        """Update account type combo box with translations"""
        self.type_input.clear()
        self.type_input.addItem(tr('accounts.asset'), 0)
        self.type_input.addItem(tr('accounts.liability'), 1)
        self.type_input.addItem(tr('accounts.equity'), 2)
        self.type_input.addItem(tr('accounts.revenue'), 3)
        self.type_input.addItem(tr('accounts.expense'), 4)
    
    def refresh_translations(self):
        """Refresh all translatable elements"""
        super().refresh_translations()
        
        # Update window title
        self.setWindowTitle(tr('windows.accounts'))
        
        # Update form group box
        self.form_group_box.setTitle(tr('accounts.account_details'))
        
        # Update labels
        self.code_label.setText(tr('accounts.account_code'))
        self.name_ar_label.setText(tr('accounts.account_name_ar'))
        self.name_en_label.setText(tr('accounts.account_name_en'))
        self.type_label.setText(tr('accounts.account_type'))
        self.level_label.setText(tr('accounts.level'))
        self.parent_label.setText(tr('accounts.parent_account'))
        self.currency_label.setText(tr('accounts.currency'))
        
        # Update type combo
        current_index = self.type_input.currentIndex()
        self.update_type_combo()
        if current_index >= 0:
            self.type_input.setCurrentIndex(current_index)
        
        # Update table headers
        self.set_translatable_headers(self.accounts_table, [
            'accounts.account_code',
            'accounts.account_name_ar',
            'accounts.account_name_en',
            'accounts.account_type',
            'accounts.level',
            'common.status'
        ])
