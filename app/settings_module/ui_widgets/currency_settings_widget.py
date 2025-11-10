from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView, QLineEdit, QLabel, QCheckBox, QMessageBox, QHeaderView
from app.i18n.translations import tr, get_language
from PySide6.QtCore import Qt
from PySide6.QtCore import QAbstractTableModel, Qt, Signal
from PySide6.QtGui import QColor
from decimal import Decimal

from app.application.services import CurrencyService # Import CurrencyService
from app.domain.settings_models import Currency # Import Currency model

class CurrenciesTableModel(QAbstractTableModel):
    def __init__(self, currencies=None, currency_service=None, parent_widget=None):
        super().__init__()
        self._currencies = currencies or []
        self.currency_service = currency_service
        self.parent_widget = parent_widget
        self.headers = ["ID", "Code", "Name (AR)", "Name (EN)", "Symbol", "Exchange Rate", "Is Active"]

    def rowCount(self, parent=None):
        return len(self._currencies)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        currency = self._currencies[index.row()]
        if role == Qt.DisplayRole:
            if index.column() == 0: return currency.id
            if index.column() == 1: return currency.code
            if index.column() == 2: return currency.name_ar
            if index.column() == 3: return currency.name_en
            if index.column() == 4: return currency.symbol
            if index.column() == 5: return float(currency.exchange_rate)
            if index.column() == 6: return "Yes" if currency.is_active else "No"
        elif role == Qt.CheckStateRole and index.column() == 6:
            return Qt.Checked if currency.is_active else Qt.Unchecked
        elif role == Qt.UserRole:
            return currency # Return the full Currency object
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return super().headerData(section, orientation, role)

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.CheckStateRole or index.column() != 6:
            return False
        currency = self._currencies[index.row()]
        new_active_state = (value == Qt.Checked)
        if currency.is_active != new_active_state:
            try:
                self.currency_service.update_currency(
                    currency.id,
                    name_ar=currency.name_ar,
                    name_en=currency.name_en,
                    code=currency.code,
                    symbol=currency.symbol,
                    exchange_rate=currency.exchange_rate,
                    is_active=new_active_state
                )
                currency.is_active = new_active_state
                self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.CheckStateRole])
                
                if self.parent_widget:
                    self.parent_widget.load_currencies()
                
                return True
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Failed to update currency active status: {e}")
                return False
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        if index.column() == 6:
            return super().flags(index) | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
        return super().flags(index) | Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def update_data(self, currencies):
        self.beginResetModel()
        self._currencies = currencies
        self.endResetModel()

    def get_currency_at_row(self, row):
        if 0 <= row < len(self._currencies):
            return self._currencies[row]
        return None

class CurrencySettingsWidget(QWidget):
    currency_updated = Signal() # Signal to notify other parts of the app

    def __init__(self, company_id: int, currency_service: CurrencyService, parent=None):
        super().__init__(parent)
        self.company_id = company_id
        self.currency_service = currency_service
        self.selected_currency_id = None
        self.init_ui()
        self.load_currencies()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Form Layout
        form_layout = QHBoxLayout()
        self.name_ar_input = QLineEdit()
        self.name_ar_input.setPlaceholderText("Currency Name (AR)")
        self.name_en_input = QLineEdit()
        self.name_en_input.setPlaceholderText("Currency Name (EN)")
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Currency Code (e.g., USD)")
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("Symbol (e.g., $)")
        self.exchange_rate_input = QLineEdit("1.0")
        self.exchange_rate_input.setPlaceholderText(tr("settings.exchange_rate"))
        self.is_active_checkbox = QCheckBox("Is Active")

        form_layout.addWidget(QLabel("Name (AR):"))
        form_layout.addWidget(self.name_ar_input)
        form_layout.addWidget(QLabel("Name (EN):"))
        form_layout.addWidget(self.name_en_input)
        form_layout.addWidget(QLabel("Code:"))
        form_layout.addWidget(self.code_input)
        form_layout.addWidget(QLabel("Symbol:"))
        form_layout.addWidget(self.symbol_input)
        form_layout.addWidget(QLabel("Exchange Rate:"))
        form_layout.addWidget(self.exchange_rate_input)
        form_layout.addWidget(self.is_active_checkbox)
        main_layout.addLayout(form_layout)

        # Buttons Layout
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Currency")
        self.add_button.clicked.connect(self.add_currency)
        self.update_button = QPushButton("Update Currency")
        self.update_button.clicked.connect(self.update_currency)
        self.delete_button = QPushButton("Delete Currency")
        self.delete_button.clicked.connect(self.delete_currency)
        self.clear_button = QPushButton("Clear Form")
        self.clear_button.clicked.connect(self.clear_form)

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
        self.currencies_table = QTableView()
        self.currencies_model = CurrenciesTableModel(currency_service=self.currency_service, parent_widget=self)
        self.currencies_table.setModel(self.currencies_model)
        self.currencies_table.clicked.connect(self.select_currency)
        self.currencies_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Apply styling to table
        table_style = """
            QTableView {
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
        self.currencies_table.setStyleSheet(table_style)
        self.currencies_table.setAlternatingRowColors(True)

        main_layout.addWidget(self.currencies_table)

        self.setLayout(main_layout)

    def load_currencies(self):
        currencies = self.currency_service.get_all_currencies()
        self.currencies_model.update_data(currencies)
        self.currencies_table.resizeColumnsToContents()

    def clear_form(self):
        self.selected_currency_id = None
        self.name_ar_input.clear()
        self.name_en_input.clear()
        self.code_input.clear()
        self.symbol_input.clear()
        self.exchange_rate_input.setText("1.0")
        self.is_active_checkbox.setChecked(False)
        self.add_button.setEnabled(True)
        self.update_button.setEnabled(False)
        self.delete_button.setEnabled(False)

    def select_currency(self, index):
        currency = self.currencies_model.get_currency_at_row(index.row())
        if currency:
            self.selected_currency_id = currency.id
            self.name_ar_input.setText(currency.name_ar)
            self.name_en_input.setText(currency.name_en or "")
            self.code_input.setText(currency.code)
            self.symbol_input.setText(currency.symbol)
            self.exchange_rate_input.setText(str(currency.exchange_rate))
            self.is_active_checkbox.setChecked(currency.is_active)
            self.add_button.setEnabled(False)
            self.update_button.setEnabled(True)
            self.delete_button.setEnabled(True)

    def add_currency(self):
        name_ar = self.name_ar_input.text().strip()
        name_en = self.name_en_input.text().strip()
        code = self.code_input.text().strip().upper()
        symbol = self.symbol_input.text().strip()
        exchange_rate_str = self.exchange_rate_input.text().strip()
        is_active = self.is_active_checkbox.isChecked()

        if not name_ar or not code or not symbol:
            QMessageBox.warning(self, "Input Error", "Currency Arabic Name, Code and Symbol cannot be empty.")
            return

        try:
            exchange_rate = Decimal(exchange_rate_str)
            if exchange_rate <= 0:
                QMessageBox.warning(self, "Input Error", "Exchange Rate must be a positive number.")
                return
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Invalid value for Exchange Rate. Please enter a number.")
            return

        try:
            self.currency_service.create_currency(name_ar, name_en if name_en else None, code, symbol, exchange_rate, is_active=is_active)
            QMessageBox.information(self, "Success", "Currency added successfully.")
            self.clear_form()
            self.load_currencies()
            self.currency_updated.emit()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def update_currency(self):
        if not self.selected_currency_id:
            QMessageBox.warning(self, "Selection Error", "Please select a currency to update.")
            return

        name_ar = self.name_ar_input.text().strip()
        name_en = self.name_en_input.text().strip()
        code = self.code_input.text().strip().upper()
        symbol = self.symbol_input.text().strip()
        exchange_rate_str = self.exchange_rate_input.text().strip()
        is_active = self.is_active_checkbox.isChecked()

        if not name_ar or not code or not symbol:
            QMessageBox.warning(self, "Input Error", "Currency Arabic Name, Code and Symbol cannot be empty.")
            return

        try:
            exchange_rate = Decimal(exchange_rate_str)
            if exchange_rate <= 0:
                QMessageBox.warning(self, "Input Error", "Exchange Rate must be a positive number.")
                return
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Invalid value for Exchange Rate. Please enter a number.")
            return

        try:
            self.currency_service.update_currency(self.selected_currency_id, name_ar=name_ar, name_en=name_en if name_en else None, code=code, symbol=symbol, exchange_rate=exchange_rate, is_active=is_active)
            QMessageBox.information(self, "Success", "Currency updated successfully.")
            self.clear_form()
            self.load_currencies()
            self.currency_updated.emit()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def delete_currency(self):
        if not self.selected_currency_id:
            QMessageBox.warning(self, "Selection Error", "Please select a currency to delete.")
            return

        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this currency?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.currency_service.delete_currency(self.selected_currency_id)
                QMessageBox.information(self, "Success", "Currency deleted successfully.")
                self.clear_form()
                self.load_currencies()
                self.currency_updated.emit() # Emit signal
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete currency: {e}")


    def refresh_translations(self):
        """Refresh all translatable elements"""
        from app.i18n.translations import tr, get_language
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QPushButton, QLabel, QGroupBox
        
        # Update layout direction
        current_lang = get_language()
        if current_lang == 'ar':
            self.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)
        
        # Update all buttons
        for button in self.findChildren(QPushButton):
            button_text = button.text().lower()
            if 'add' in button_text or 'إضافة' in button_text:
                button.setText(tr('common.add'))
            elif 'save' in button_text or 'حفظ' in button_text:
                button.setText(tr('common.save'))
            elif 'edit' in button_text or 'تعديل' in button_text:
                button.setText(tr('common.edit'))
            elif 'delete' in button_text or 'حذف' in button_text:
                button.setText(tr('common.delete'))
            elif 'cancel' in button_text or 'إلغاء' in button_text:
                button.setText(tr('common.cancel'))
            elif 'refresh' in button_text or 'تحديث' in button_text:
                button.setText(tr('common.refresh'))
            elif 'close' in button_text or 'إغلاق' in button_text:
                button.setText(tr('common.close'))
