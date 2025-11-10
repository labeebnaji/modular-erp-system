"""
Complete Fixed Assets Management Widget with Depreciation
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                               QTableWidget, QTableWidgetItem, QPushButton, QLabel,
                               QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox,
                               QMessageBox, QGroupBox, QFormLayout, QHeaderView, QSpinBox)
from PySide6.QtCore import Qt, QDate
from decimal import Decimal
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from app.application.services import FixedAssetService, CompanyService, BranchService
from app.ui.styles import BUTTON_STYLE, TABLE_STYLE, GROUPBOX_STYLE
from app.i18n.translations import tr


class FixedAssetWidget(QWidget):
    """Widget for managing fixed assets"""
    
    def __init__(self, fixed_asset_service, company_service, branch_service, parent=None):
        super().__init__(parent)
        self.fixed_asset_service = fixed_asset_service
        self.company_service = company_service
        self.branch_service = branch_service
        self.selected_asset_id = None
        self.init_ui()
        self.load_fixed_assets()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Asset Form
        form_group = QGroupBox("Fixed Asset Details")
        form_group.setStyleSheet(GROUPBOX_STYLE)
        form_layout = QFormLayout()
        
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Auto-generated")
        form_layout.addRow(QLabel(tr('common.code') + ":"), self.code_input)
        
        self.name_ar_input = QLineEdit()
        self.name_ar_input.setPlaceholderText("Asset Name (Arabic)")
        form_layout.addRow(QLabel(tr('common.name') + " (AR):"), self.name_ar_input)
        
        self.name_en_input = QLineEdit()
        self.name_en_input.setPlaceholderText("Asset Name (English)")
        form_layout.addRow(QLabel(tr('common.name') + " (EN):"), self.name_en_input)
        
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Category (e.g., Vehicles, Equipment)")
        form_layout.addRow(QLabel("Category:"), self.category_input)
        
        self.acquisition_date_input = QDateEdit(QDate.currentDate())
        self.acquisition_date_input.setCalendarPopup(True)
        form_layout.addRow(QLabel("Acquisition Date:"), self.acquisition_date_input)
        
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0.00, 99999999.99)
        self.cost_input.setDecimals(2)
        self.cost_input.setPrefix("$ ")
        form_layout.addRow(QLabel("Cost:"), self.cost_input)
        
        self.salvage_value_input = QDoubleSpinBox()
        self.salvage_value_input.setRange(0.00, 99999999.99)
        self.salvage_value_input.setDecimals(2)
        self.salvage_value_input.setPrefix("$ ")
        form_layout.addRow(QLabel("Salvage Value:"), self.salvage_value_input)
        
        self.useful_life_input = QSpinBox()
        self.useful_life_input.setRange(1, 100)
        self.useful_life_input.setSuffix(" years")
        form_layout.addRow(QLabel("Useful Life:"), self.useful_life_input)
        
        self.depreciation_method_combo = QComboBox()
        self.depreciation_method_combo.addItem("Straight-Line", 0)
        self.depreciation_method_combo.addItem("Declining Balance", 1)
        form_layout.addRow(QLabel("Depreciation Method:"), self.depreciation_method_combo)
        
        self.company_combo = QComboBox()
        self.load_companies()
        form_layout.addRow(QLabel("Company:"), self.company_combo)
        
        self.branch_combo = QComboBox()
        self.load_branches()
        form_layout.addRow(QLabel("Branch:"), self.branch_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton(tr('common.save'))
        self.save_button.setStyleSheet(BUTTON_STYLE)
        self.save_button.clicked.connect(self.save_asset)
        
        self.new_button = QPushButton(tr('common.new'))
        self.new_button.setStyleSheet(BUTTON_STYLE)
        self.new_button.clicked.connect(self.clear_form)
        
        self.delete_button = QPushButton(tr('common.delete'))
        self.delete_button.setStyleSheet(BUTTON_STYLE)
        self.delete_button.clicked.connect(self.delete_asset)
        
        self.calculate_depreciation_button = QPushButton("Calculate Depreciation")
        self.calculate_depreciation_button.setStyleSheet(BUTTON_STYLE)
        self.calculate_depreciation_button.clicked.connect(self.calculate_depreciation)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.calculate_depreciation_button)
        button_layout.addStretch()
        
        form_layout.addRow(button_layout)
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        # Assets Table
        self.assets_table = QTableWidget()
        self.assets_table.setColumnCount(10)
        self.assets_table.setHorizontalHeaderLabels([
            "ID", tr('common.code'), tr('common.name'), "Category",
            "Acquisition Date", "Cost", "Salvage Value", "Useful Life",
            "Current Book Value", tr('common.status')
        ])
        self.assets_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.assets_table.setStyleSheet(TABLE_STYLE)
        self.assets_table.setAlternatingRowColors(True)
        self.assets_table.cellClicked.connect(self.load_asset_details)
        
        main_layout.addWidget(self.assets_table)
    
    def load_companies(self):
        """Load all companies"""
        self.company_combo.clear()
        companies = self.company_service.get_all_companies()
        for company in companies:
            self.company_combo.addItem(f"{company.name_en} ({company.code})", company.id)
    
    def load_branches(self):
        """Load all branches"""
        self.branch_combo.clear()
        branches = self.branch_service.get_all_branches()
        for branch in branches:
            self.branch_combo.addItem(f"{branch.name_en} ({branch.code})", branch.id)
    
    def load_fixed_assets(self):
        """Load all fixed assets"""
        self.assets_table.setRowCount(0)
        assets = self.fixed_asset_service.get_all_fixed_assets()
        
        self.assets_table.setRowCount(len(assets))
        for row, asset in enumerate(assets):
            self.assets_table.setItem(row, 0, QTableWidgetItem(str(asset.id)))
            self.assets_table.setItem(row, 1, QTableWidgetItem(asset.code))
            self.assets_table.setItem(row, 2, QTableWidgetItem(asset.name_ar))
            self.assets_table.setItem(row, 3, QTableWidgetItem(asset.asset_category or ""))
            self.assets_table.setItem(row, 4, QTableWidgetItem(str(asset.acquisition_date)))
            self.assets_table.setItem(row, 5, QTableWidgetItem(f"{asset.cost:.2f}"))
            self.assets_table.setItem(row, 6, QTableWidgetItem(f"{asset.salvage_value:.2f}"))
            self.assets_table.setItem(row, 7, QTableWidgetItem(f"{asset.useful_life_years} years"))
            self.assets_table.setItem(row, 8, QTableWidgetItem(f"{asset.current_book_value:.2f}"))
            self.assets_table.setItem(row, 9, QTableWidgetItem(tr('common.active') if asset.is_active else tr('common.inactive')))
    
    def load_asset_details(self, row, col):
        """Load asset details when clicked"""
        asset_id = int(self.assets_table.item(row, 0).text())
        asset = self.fixed_asset_service.get_fixed_asset_by_id(asset_id)
        
        if asset:
            self.selected_asset_id = asset.id
            self.code_input.setText(asset.code)
            self.name_ar_input.setText(asset.name_ar)
            self.name_en_input.setText(asset.name_en or "")
            self.category_input.setText(asset.asset_category or "")
            self.acquisition_date_input.setDate(QDate(asset.acquisition_date))
            self.cost_input.setValue(float(asset.cost))
            self.salvage_value_input.setValue(float(asset.salvage_value))
            self.useful_life_input.setValue(asset.useful_life_years)
            self.depreciation_method_combo.setCurrentIndex(asset.depreciation_method)
    
    def save_asset(self):
        """Save fixed asset"""
        name_ar = self.name_ar_input.text().strip()
        name_en = self.name_en_input.text().strip()
        category = self.category_input.text().strip()
        acquisition_date = self.acquisition_date_input.date().toPython()
        cost = Decimal(str(self.cost_input.value()))
        salvage_value = Decimal(str(self.salvage_value_input.value()))
        useful_life = self.useful_life_input.value()
        depreciation_method = self.depreciation_method_combo.currentData()
        company_id = self.company_combo.currentData()
        branch_id = self.branch_combo.currentData()
        
        if not name_ar or cost <= 0:
            QMessageBox.warning(self, tr('common.warning'), "Please enter asset name and cost")
            return
        
        try:
            if self.selected_asset_id:
                # Update existing asset
                self.fixed_asset_service.update_fixed_asset(
                    self.selected_asset_id,
                    name_ar=name_ar,
                    name_en=name_en,
                    asset_category=category,
                    acquisition_date=acquisition_date,
                    cost=cost,
                    salvage_value=salvage_value,
                    useful_life_years=useful_life,
                    depreciation_method=depreciation_method
                )
                QMessageBox.information(self, tr('common.success'), tr('messages.update_success'))
            else:
                # Create new asset
                code = f"FA-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                self.fixed_asset_service.create_fixed_asset(
                    company_id=company_id,
                    branch_id=branch_id,
                    code=code,
                    name_ar=name_ar,
                    name_en=name_en,
                    asset_category=category,
                    acquisition_date=acquisition_date,
                    cost=cost,
                    salvage_value=salvage_value,
                    useful_life_years=useful_life,
                    depreciation_method=depreciation_method,
                    current_book_value=cost,
                    created_by=1
                )
                QMessageBox.information(self, tr('common.success'), tr('messages.save_success'))
            
            self.clear_form()
            self.load_fixed_assets()
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error: {str(e)}")
    
    def delete_asset(self):
        """Delete selected asset"""
        if not self.selected_asset_id:
            QMessageBox.warning(self, tr('common.warning'), "Please select an asset to delete")
            return
        
        reply = QMessageBox.question(self, tr('common.confirm'), 
                                    tr('messages.confirm_delete'),
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.fixed_asset_service.delete_fixed_asset(self.selected_asset_id)
                QMessageBox.information(self, tr('common.success'), tr('messages.delete_success'))
                self.clear_form()
                self.load_fixed_assets()
            except Exception as e:
                QMessageBox.critical(self, tr('common.error'), f"Error: {str(e)}")
    
    def calculate_depreciation(self):
        """Calculate and record depreciation for selected asset"""
        if not self.selected_asset_id:
            QMessageBox.warning(self, tr('common.warning'), "Please select an asset")
            return
        
        asset = self.fixed_asset_service.get_fixed_asset_by_id(self.selected_asset_id)
        if not asset:
            return
        
        # Calculate depreciation
        depreciable_amount = asset.cost - asset.salvage_value
        
        if asset.depreciation_method == 0:  # Straight-Line
            annual_depreciation = depreciable_amount / asset.useful_life_years
        else:  # Declining Balance (simplified - 200% declining balance)
            rate = Decimal('2.0') / asset.useful_life_years
            annual_depreciation = asset.current_book_value * rate
        
        # Monthly depreciation
        monthly_depreciation = annual_depreciation / 12
        
        try:
            # Record depreciation
            self.fixed_asset_service.create_depreciation(
                company_id=asset.company_id,
                branch_id=asset.branch_id,
                asset_id=asset.id,
                depreciation_date=date.today(),
                amount=monthly_depreciation,
                created_by=1
            )
            
            # Update asset book value
            new_book_value = asset.current_book_value - monthly_depreciation
            if new_book_value < asset.salvage_value:
                new_book_value = asset.salvage_value
            
            self.fixed_asset_service.update_fixed_asset(
                asset.id,
                current_book_value=new_book_value
            )
            
            QMessageBox.information(self, tr('common.success'), 
                                  f"Depreciation recorded: {monthly_depreciation:.2f}\n"
                                  f"New Book Value: {new_book_value:.2f}")
            
            self.load_fixed_assets()
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error: {str(e)}")
    
    def clear_form(self):
        """Clear all form fields"""
        self.selected_asset_id = None
        self.code_input.clear()
        self.name_ar_input.clear()
        self.name_en_input.clear()
        self.category_input.clear()
        self.acquisition_date_input.setDate(QDate.currentDate())
        self.cost_input.setValue(0.0)
        self.salvage_value_input.setValue(0.0)
        self.useful_life_input.setValue(1)
        self.depreciation_method_combo.setCurrentIndex(0)


class DepreciationHistoryWidget(QWidget):
    """Widget for viewing depreciation history"""
    
    def __init__(self, fixed_asset_service, parent=None):
        super().__init__(parent)
        self.fixed_asset_service = fixed_asset_service
        self.init_ui()
        self.load_depreciation_history()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Filter section
        filter_layout = QHBoxLayout()
        
        self.asset_combo = QComboBox()
        self.load_assets()
        filter_layout.addWidget(QLabel("Asset:"))
        filter_layout.addWidget(self.asset_combo)
        
        self.from_date_input = QDateEdit(QDate.currentDate().addMonths(-12))
        self.from_date_input.setCalendarPopup(True)
        filter_layout.addWidget(QLabel("From:"))
        filter_layout.addWidget(self.from_date_input)
        
        self.to_date_input = QDateEdit(QDate.currentDate())
        self.to_date_input.setCalendarPopup(True)
        filter_layout.addWidget(QLabel("To:"))
        filter_layout.addWidget(self.to_date_input)
        
        self.filter_button = QPushButton(tr('common.search'))
        self.filter_button.setStyleSheet(BUTTON_STYLE)
        self.filter_button.clicked.connect(self.load_depreciation_history)
        filter_layout.addWidget(self.filter_button)
        
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)
        
        # Depreciation table
        self.depreciation_table = QTableWidget()
        self.depreciation_table.setColumnCount(6)
        self.depreciation_table.setHorizontalHeaderLabels([
            "ID", "Asset", "Date", "Amount", "Created By", "Created At"
        ])
        self.depreciation_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.depreciation_table.setStyleSheet(TABLE_STYLE)
        self.depreciation_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.depreciation_table)
    
    def load_assets(self):
        """Load all assets for filter"""
        self.asset_combo.clear()
        self.asset_combo.addItem("All Assets", None)
        assets = self.fixed_asset_service.get_all_fixed_assets()
        for asset in assets:
            self.asset_combo.addItem(f"{asset.name_ar} ({asset.code})", asset.id)
    
    def load_depreciation_history(self):
        """Load depreciation history"""
        self.depreciation_table.setRowCount(0)
        
        asset_id = self.asset_combo.currentData()
        from_date = self.from_date_input.date().toPython()
        to_date = self.to_date_input.date().toPython()
        
        # Get all depreciation records
        depreciations = self.fixed_asset_service.get_all_depreciations()
        
        # Filter by asset and date range
        filtered = []
        for dep in depreciations:
            if asset_id and dep.asset_id != asset_id:
                continue
            if dep.depreciation_date < from_date or dep.depreciation_date > to_date:
                continue
            filtered.append(dep)
        
        self.depreciation_table.setRowCount(len(filtered))
        for row, dep in enumerate(filtered):
            asset = self.fixed_asset_service.get_fixed_asset_by_id(dep.asset_id)
            asset_name = asset.name_ar if asset else "Unknown"
            
            self.depreciation_table.setItem(row, 0, QTableWidgetItem(str(dep.id)))
            self.depreciation_table.setItem(row, 1, QTableWidgetItem(asset_name))
            self.depreciation_table.setItem(row, 2, QTableWidgetItem(str(dep.depreciation_date)))
            self.depreciation_table.setItem(row, 3, QTableWidgetItem(f"{dep.amount:.2f}"))
            self.depreciation_table.setItem(row, 4, QTableWidgetItem(str(dep.created_by)))
            self.depreciation_table.setItem(row, 5, QTableWidgetItem(str(dep.created_at)))


class FixedAssetsManagementWidget(QWidget):
    """Main fixed assets management widget with tabs"""
    
    def __init__(self, fixed_asset_service, company_service, branch_service, parent=None):
        super().__init__(parent)
        self.fixed_asset_service = fixed_asset_service
        self.company_service = company_service
        self.branch_service = branch_service
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Fixed Assets Management")
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.asset_widget = FixedAssetWidget(
            self.fixed_asset_service,
            self.company_service,
            self.branch_service
        )
        self.depreciation_widget = DepreciationHistoryWidget(self.fixed_asset_service)
        
        self.tab_widget.addTab(self.asset_widget, "Fixed Assets")
        self.tab_widget.addTab(self.depreciation_widget, "Depreciation History")
        
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
