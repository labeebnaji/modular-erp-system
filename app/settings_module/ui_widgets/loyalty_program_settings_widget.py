from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QTableView, QMessageBox, QHeaderView, QCheckBox, QComboBox
from app.i18n.translations import tr, get_language
from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator, QStandardItemModel, QStandardItem
from app.application.services import LoyaltyProgramService

class LoyaltyProgramSettingsWidget(QWidget):
    def __init__(self, company_id: int, loyalty_program_service: LoyaltyProgramService, parent=None):
        super().__init__(parent)
        self.company_id = company_id
        self.loyalty_program_service = loyalty_program_service
        self.current_selected_program_id = None
        self.init_ui()
        self._load_loyalty_programs()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Input Form
        form_group_box = QWidget()
        form_layout = QGridLayout(form_group_box)

        form_layout.addWidget(QLabel("Name (Arabic):"), 0, 0)
        self.name_ar_input = QLineEdit()
        form_layout.addWidget(self.name_ar_input, 0, 1)

        form_layout.addWidget(QLabel("Name (English):"), 1, 0)
        self.name_en_input = QLineEdit()
        form_layout.addWidget(self.name_en_input, 1, 1)

        form_layout.addWidget(QLabel("Program Type:"), 2, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItem("Points", "points")
        self.type_combo.addItem("Cashback", "cashback")
        self.type_combo.currentIndexChanged.connect(self._toggle_program_type_fields)
        form_layout.addWidget(self.type_combo, 2, 1)

        # Fields for Points type
        self.points_per_amount_label = QLabel("Points per Amount:")
        form_layout.addWidget(self.points_per_amount_label, 3, 0)
        self.points_per_amount_input = QLineEdit("1.0")
        self.points_per_amount_input.setValidator(QDoubleValidator(0.01, 1000000.00, 2))
        form_layout.addWidget(self.points_per_amount_input, 3, 1)

        self.point_value_label = QLabel("Point Value:")
        form_layout.addWidget(self.point_value_label, 4, 0)
        self.point_value_input = QLineEdit("0.01")
        self.point_value_input.setValidator(QDoubleValidator(0.01, 1000000.00, 2))
        form_layout.addWidget(self.point_value_input, 4, 1)

        self.min_redemption_points_label = QLabel("Min Redemption Points:")
        form_layout.addWidget(self.min_redemption_points_label, 5, 0)
        self.min_redemption_points_input = QLineEdit("100")
        self.min_redemption_points_input.setValidator(QDoubleValidator(0, 1000000.00, 0))
        form_layout.addWidget(self.min_redemption_points_input, 5, 1)

        # Fields for Cashback type
        self.cashback_percentage_label = QLabel("Cashback (%):")
        form_layout.addWidget(self.cashback_percentage_label, 6, 0)
        self.cashback_percentage_input = QLineEdit("0.0")
        self.cashback_percentage_input.setValidator(QDoubleValidator(0.0, 100.0, 2))
        form_layout.addWidget(self.cashback_percentage_input, 6, 1)

        self.min_purchase_amount_for_cashback_label = QLabel("Min Purchase for Cashback:")
        form_layout.addWidget(self.min_purchase_amount_for_cashback_label, 7, 0)
        self.min_purchase_amount_for_cashback_input = QLineEdit("0.0")
        self.min_purchase_amount_for_cashback_input.setValidator(QDoubleValidator(0.0, 10000000.0, 2))
        form_layout.addWidget(self.min_purchase_amount_for_cashback_input, 7, 1)

        self.is_active_checkbox = QCheckBox("Is Active")
        self.is_active_checkbox.setChecked(True)
        form_layout.addWidget(self.is_active_checkbox, 8, 1)

        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton(tr("common.save"))
        self.save_button.clicked.connect(self._save_loyalty_program)
        buttons_layout.addWidget(self.save_button)

        self.new_button = QPushButton(tr("common.new"))
        self.new_button.clicked.connect(self._clear_form)
        buttons_layout.addWidget(self.new_button)

        self.delete_button = QPushButton(tr("common.delete"))
        self.delete_button.clicked.connect(self._deactivate_loyalty_program)
        buttons_layout.addWidget(self.delete_button)

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
        self.save_button.setStyleSheet(button_style)
        self.new_button.setStyleSheet(button_style)
        self.delete_button.setStyleSheet(button_style)

        form_layout.addLayout(buttons_layout, 6, 0, 1, 2)
        main_layout.addWidget(form_group_box)

        # Table View
        self.loyalty_programs_table = QTableView()
        self.loyalty_programs_table.setSelectionBehavior(QTableView.SelectRows)
        self.loyalty_programs_table.setEditTriggers(QTableView.NoEditTriggers)
        self.loyalty_programs_table.clicked.connect(self._display_selected_program_details)
        self.loyalty_programs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

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
        self.loyalty_programs_table.setStyleSheet(table_style)
        self.loyalty_programs_table.setAlternatingRowColors(True)

        main_layout.addWidget(self.loyalty_programs_table)

        self.setLayout(main_layout)

    def _load_loyalty_programs(self):
        programs = self.loyalty_program_service.get_all_loyalty_programs(self.company_id)
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["ID", "Name (Arabic)", "Name (English)", "Type", "Points/Amount", "Point Value", "Min Redemption", "Cashback (%)", "Min Purchase for Cashback", "Active"])
        for program in programs:
            model.appendRow([
                QStandardItem(str(program.id)),
                QStandardItem(program.name_ar),
                QStandardItem(program.name_en),
                QStandardItem(program.type),
                QStandardItem(f"{program.points_per_amount:.2f}"),
                QStandardItem(f"{program.point_value:.2f}"),
                QStandardItem(str(program.min_redemption_points)),
                QStandardItem(f"{program.cashback_percentage:.2f}"),
                QStandardItem(f"{program.min_purchase_amount_for_cashback:.2f}"),
                QStandardItem("Yes" if program.is_active else "No")
            ])
        self.loyalty_programs_table.setModel(model)
        self.loyalty_programs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def _display_selected_program_details(self, index):
        row = index.row()
        model = self.loyalty_programs_table.model()
        self.current_selected_program_id = int(model.item(row, 0).text())
        self.name_ar_input.setText(model.item(row, 1).text())
        self.name_en_input.setText(model.item(row, 2).text())
        self.type_combo.setCurrentText(model.item(row, 3).text().capitalize()) # Set program type
        self.points_per_amount_input.setText(model.item(row, 4).text())
        self.point_value_input.setText(model.item(row, 5).text())
        self.min_redemption_points_input.setText(model.item(row, 6).text())
        self.cashback_percentage_input.setText(model.item(row, 7).text())
        self.min_purchase_amount_for_cashback_input.setText(model.item(row, 8).text())
        self.is_active_checkbox.setChecked(model.item(row, 9).text() == "Yes")
        self.save_button.setText(tr("common.update"))
        self._toggle_program_type_fields(self.type_combo.currentIndex()) # Update field visibility

    def _save_loyalty_program(self):
        name_ar = self.name_ar_input.text().strip()
        name_en = self.name_en_input.text().strip()
        program_type = self.type_combo.currentData() # Get selected type (e.g., "points", "cashback")
        is_active = self.is_active_checkbox.isChecked()

        if not name_ar:
            QMessageBox.warning(self, "Input Error", "Arabic Name cannot be empty.")
            return

        # Initialize all fields to default/zero, then populate based on type
        points_per_amount = 0.0
        point_value = 0.0
        min_redemption_points = 0
        cashback_percentage = 0.0
        min_purchase_amount_for_cashback = 0.0

        try:
            if program_type == "points":
                points_per_amount = float(self.points_per_amount_input.text())
                point_value = float(self.point_value_input.text())
                min_redemption_points = int(self.min_redemption_points_input.text())
            elif program_type == "cashback":
                cashback_percentage = float(self.cashback_percentage_input.text())
                min_purchase_amount_for_cashback = float(self.min_purchase_amount_for_cashback_input.text())
            # Add logic for other types if needed
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numeric values for program settings.")
            return

        try:
            if self.current_selected_program_id:
                # Update existing program
                self.loyalty_program_service.update_loyalty_program(
                    self.current_selected_program_id,
                    name_ar=name_ar,
                    name_en=name_en,
                    type=program_type,
                    points_per_amount=points_per_amount,
                    point_value=point_value,
                    min_redemption_points=min_redemption_points,
                    cashback_percentage=cashback_percentage,
                    min_purchase_amount_for_cashback=min_purchase_amount_for_cashback,
                    is_active=is_active
                )
                QMessageBox.information(self, "Success", "Loyalty Program updated successfully.")
            else:
                # Create new program
                self.loyalty_program_service.create_loyalty_program(
                    company_id=self.company_id,
                    name_ar=name_ar,
                    name_en=name_en,
                    type=program_type,
                    points_per_amount=points_per_amount,
                    point_value=point_value,
                    min_redemption_points=min_redemption_points,
                    cashback_percentage=cashback_percentage,
                    min_purchase_amount_for_cashback=min_purchase_amount_for_cashback,
                    is_active=is_active
                )
                QMessageBox.information(self, "Success", "Loyalty Program created successfully.")
            self._clear_form()
            self._load_loyalty_programs()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def _deactivate_loyalty_program(self):
        if not self.current_selected_program_id:
            QMessageBox.warning(self, "Selection Error", "Please select a loyalty program to deactivate.")
            return
        reply = QMessageBox.question(self, "Confirm Deactivation", "Are you sure you want to deactivate this loyalty program?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.loyalty_program_service.deactivate_loyalty_program(self.current_selected_program_id)
                QMessageBox.information(self, "Success", "Loyalty Program deactivated successfully.")
                self._clear_form()
                self._load_loyalty_programs()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to deactivate loyalty program: {e}")

    def _clear_form(self):
        self.name_ar_input.clear()
        self.name_en_input.clear()
        self.type_combo.setCurrentIndex(0) # Reset to default type (Points)
        self.points_per_amount_input.setText("1.0")
        self.point_value_input.setText("0.01")
        self.min_redemption_points_input.setText("100")
        self.cashback_percentage_input.setText("0.0")
        self.min_purchase_amount_for_cashback_input.setText("0.0")
        self.is_active_checkbox.setChecked(True)
        self.current_selected_program_id = None
        self.save_button.setText(tr("common.save"))
        self._toggle_program_type_fields(0) # Show fields for default type (Points)

    def _toggle_program_type_fields(self, index):
        selected_type = self.type_combo.itemData(index)

        # Hide all fields initially
        self.points_per_amount_label.setVisible(False)
        self.points_per_amount_input.setVisible(False)
        self.point_value_label.setVisible(False)
        self.point_value_input.setVisible(False)
        self.min_redemption_points_label.setVisible(False)
        self.min_redemption_points_input.setVisible(False)
        self.cashback_percentage_label.setVisible(False)
        self.cashback_percentage_input.setVisible(False)
        self.min_purchase_amount_for_cashback_label.setVisible(False)
        self.min_purchase_amount_for_cashback_input.setVisible(False)

        if selected_type == "points":
            self.points_per_amount_label.setVisible(True)
            self.points_per_amount_input.setVisible(True)
            self.point_value_label.setVisible(True)
            self.point_value_input.setVisible(True)
            self.min_redemption_points_label.setVisible(True)
            self.min_redemption_points_input.setVisible(True)
        elif selected_type == "cashback":
            self.cashback_percentage_label.setVisible(True)
            self.cashback_percentage_input.setVisible(True)
            self.min_purchase_amount_for_cashback_label.setVisible(True)
            self.min_purchase_amount_for_cashback_input.setVisible(True)

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
