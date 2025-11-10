from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView, QLineEdit, QLabel, QCheckBox, QMessageBox, QComboBox, QHeaderView
from app.i18n.translations import tr, get_language
from PySide6.QtCore import Qt
from PySide6.QtCore import QAbstractTableModel, Qt, Signal
from PySide6.QtGui import QColor

from app.application.services import PaymentMethodService # Import PaymentMethodService
from app.domain.settings_models import PaymentMethod # Import PaymentMethod model

class PaymentMethodsTableModel(QAbstractTableModel):
    def __init__(self, methods=None, payment_method_service=None, parent_widget=None):
        super().__init__()
        self._methods = methods or []
        self.payment_method_service = payment_method_service
        self.parent_widget = parent_widget
        self.headers = ["ID", "Name (AR)", "Name (EN)", "Is Active"]

    def rowCount(self, parent=None):
        return len(self._methods)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        method = self._methods[index.row()]
        if role == Qt.DisplayRole:
            if index.column() == 0: return method.id
            if index.column() == 1: return method.name_ar
            if index.column() == 2: return method.name_en
            if index.column() == 3: return "Yes" if method.is_active else "No"
        elif role == Qt.CheckStateRole and index.column() == 3:
            return Qt.Checked if method.is_active else Qt.Unchecked
        elif role == Qt.UserRole:
            return method # Return the full PaymentMethod object
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return super().headerData(section, orientation, role)

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.CheckStateRole or index.column() != 3:
            return False
        method = self._methods[index.row()]
        new_active_state = (value == Qt.Checked)
        if method.is_active != new_active_state:
            try:
                self.payment_method_service.update_payment_method(
                    method.id,
                    name_ar=method.name_ar,
                    name_en=method.name_en,
                    is_active=new_active_state
                )
                method.is_active = new_active_state
                self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.CheckStateRole])
                
                if self.parent_widget:
                    self.parent_widget.load_payment_methods()
                
                return True
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Failed to update payment method active status: {e}")
                return False
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        if index.column() == 3:
            return super().flags(index) | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
        return super().flags(index) | Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def update_data(self, methods):
        self.beginResetModel()
        self._methods = methods
        self.endResetModel()

    def get_payment_method_at_row(self, row):
        if 0 <= row < len(self._methods):
            return self._methods[row]
        return None

class PaymentMethodSettingsWidget(QWidget):
    payment_method_updated = Signal() # Signal to notify other parts of the app

    def __init__(self, company_id: int, payment_method_service: PaymentMethodService, parent=None):
        super().__init__(parent)
        self.company_id = company_id
        self.payment_method_service = payment_method_service
        self.selected_method_id = None
        self.init_ui()
        self.load_payment_methods()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Form Layout
        form_layout = QHBoxLayout()
        self.name_ar_input = QLineEdit()
        self.name_ar_input.setPlaceholderText("Payment Method Name (AR)")
        self.name_en_input = QLineEdit()
        self.name_en_input.setPlaceholderText("Payment Method Name (EN)")
        self.type_combo = QComboBox()
        self.type_combo.addItems(['Cash', 'Credit', 'Bank Transfer', 'Cheque', 'To Account', 'Coupon', 'Network'])
        self.is_active_checkbox = QCheckBox("Is Active")
        self.is_active_checkbox.setChecked(True)

        form_layout.addWidget(QLabel("Name (AR):"))
        form_layout.addWidget(self.name_ar_input)
        form_layout.addWidget(QLabel("Name (EN):"))
        form_layout.addWidget(self.name_en_input)
        form_layout.addWidget(QLabel("Type:"))
        form_layout.addWidget(self.type_combo)
        form_layout.addWidget(self.is_active_checkbox)
        main_layout.addLayout(form_layout)

        # Buttons Layout
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Payment Method")
        self.add_button.clicked.connect(self.add_payment_method)
        self.update_button = QPushButton("Update Payment Method")
        self.update_button.clicked.connect(self.update_payment_method)
        self.delete_button = QPushButton("Delete Payment Method")
        self.delete_button.clicked.connect(self.delete_payment_method)
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
        self.methods_table = QTableView()
        self.methods_model = PaymentMethodsTableModel(payment_method_service=self.payment_method_service, parent_widget=self)
        self.methods_table.setModel(self.methods_model)
        self.methods_table.clicked.connect(self.select_payment_method)
        self.methods_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

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
        self.methods_table.setStyleSheet(table_style)
        self.methods_table.setAlternatingRowColors(True)

        main_layout.addWidget(self.methods_table)

        self.setLayout(main_layout)

    def load_payment_methods(self):
        methods = self.payment_method_service.get_all_payment_methods(self.company_id)
        self.methods_model.update_data(methods)
        self.methods_table.resizeColumnsToContents()

    def clear_form(self):
        self.selected_method_id = None
        self.name_ar_input.clear()
        self.name_en_input.clear()
        self.type_combo.setCurrentIndex(0) # Reset to 'Cash'
        self.is_active_checkbox.setChecked(True)
        self.add_button.setEnabled(True)
        self.update_button.setEnabled(False)
        self.delete_button.setEnabled(False)

    def select_payment_method(self, index):
        method = self.methods_model.get_payment_method_at_row(index.row())
        if method:
            self.selected_method_id = method.id
            self.name_ar_input.setText(method.name_ar)
            self.name_en_input.setText(method.name_en)
            self.type_combo.setCurrentText(method.type)
            self.is_active_checkbox.setChecked(method.is_active)
            self.add_button.setEnabled(False)
            self.update_button.setEnabled(True)
            self.delete_button.setEnabled(True)

    def add_payment_method(self):
        name_ar = self.name_ar_input.text().strip()
        name_en = self.name_en_input.text().strip()
        type_ = self.type_combo.currentText()
        is_active = self.is_active_checkbox.isChecked()

        if not name_ar:
            QMessageBox.warning(self, "Input Error", "Payment Method Arabic Name cannot be empty.")
            return

        try:
            self.payment_method_service.create_payment_method(self.company_id, name_ar, name_en if name_en else None, type_, is_active)
            QMessageBox.information(self, "Success", "Payment Method added successfully.")
            self.clear_form()
            self.load_payment_methods()
            self.payment_method_updated.emit() # Emit signal
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def update_payment_method(self):
        if not self.selected_method_id:
            QMessageBox.warning(self, "Selection Error", "Please select a payment method to update.")
            return

        name_ar = self.name_ar_input.text().strip()
        name_en = self.name_en_input.text().strip()
        type_ = self.type_combo.currentText()
        is_active = self.is_active_checkbox.isChecked()

        if not name_ar:
            QMessageBox.warning(self, "Input Error", "Payment Method Arabic Name cannot be empty.")
            return

        try:
            self.payment_method_service.update_payment_method(self.selected_method_id, name_ar=name_ar, name_en=name_en if name_en else None, type=type_, is_active=is_active)
            QMessageBox.information(self, "Success", "Payment Method updated successfully.")
            self.clear_form()
            self.load_payment_methods()
            self.payment_method_updated.emit() # Emit signal
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def delete_payment_method(self):
        if not self.selected_method_id:
            QMessageBox.warning(self, "Selection Error", "Please select a payment method to delete.")
            return

        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this payment method?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.payment_method_service.delete_payment_method(self.selected_method_id)
                QMessageBox.information(self, "Success", "Payment Method deleted successfully.")
                self.clear_form()
                self.load_payment_methods()
                self.payment_method_updated.emit() # Emit signal
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete payment method: {e}")


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
