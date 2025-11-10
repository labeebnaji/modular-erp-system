import sys
import os

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QStackedWidget, QPushButton, QMenuBar, QMenu, QHBoxLayout, QListWidget, QDialog
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSize, QCoreApplication
# import resources_rc # Removed the import for compiled resources
from datetime import date # Import date for journal entries
from decimal import Decimal # Import Decimal for financial calculations

from app.domain.models import *
from app.domain.settings_models import *
from app.infrastructure.database import init_db, SessionLocal, engine, Base
from app.application.services import (
    AccountService,
    JournalService,
    ARAPService,
    InventoryService,
    SalesPurchaseService,
    CashBankService,
    FixedAssetService,
    TaxService,
    IAMService,
    CompanyService,
    BranchService,
    FiscalPeriodService,
    CostCenterProjectService,
    PayrollService,
    NotificationsWorkflowsService,
    ReportingService,
    GeneralConfigurationService,
    UnitService, CurrencyService, PaymentMethodService, CouponService, ShiftService, LoyaltyProgramService, GiftCardService, WarehouseService # Added new services
)

from app.ui.accounts import AccountsWidget
from app.ui.journals import JournalsWidget
from app.customer_module.ui_widgets.customer_widget import CustomerWidget
from app.supplier_module.ui_widgets.supplier_widget import SupplierWidget
from app.ui.item_widget import ItemWidget
from app.sales_purchase_module.ui_widgets.sales_purchase_main_window import SalesPurchaseMainWindow
from app.inventory_module.ui_widgets.inventory_main_window import InventoryMainWindow
from app.ui.cash_bank import CashBankWidget
from app.ui.fixed_assets import FixedAssetsWidget
from app.ui.tax_compliance import TaxComplianceWidget
from app.ui.iam import IAMWidget
from app.ui.company_widget import CompanyWidget
from app.ui.branch_widget import BranchWidget
from app.ui.fiscal_period_widget import FiscalPeriodWidget
from app.ui.cost_center_project import CostCenterProjectWidget
from app.ui.employee_widget import EmployeeWidget
from app.ui.payroll import PayrollWidget
from app.ui.notifications_workflows import NotificationsWorkflowsWidget
from app.ui.reporting import ReportingWidget
from app.ui.general_configuration import GeneralConfigurationWidget
from app.ui.setup_wizard import SetupWizard # Import the new SetupWizard
from app.ui.language_settings_widget import LanguageSettingsWidget # Import Language Settings
from app.pos_module.pos_backend import POSBackend # Import POSBackend
from app.pos_module.ui_widgets.pos_main_window import POSMainWindow # Import POSMainWindow
from app.settings_module.ui_widgets.settings_window import SettingsWindow # Import SettingsWindow
from werkzeug.security import generate_password_hash # Import generate_password_hash
from datetime import datetime
from app.i18n.translations import tr, get_language, _translator

# Initialize the database
init_db()

class MainWindow(QMainWindow):
    # Placeholder Account IDs (in a real ERP, these would be configurable)
    CASH_ACCOUNT_ID = 1          # الصندوق
    ACCOUNTS_RECEIVABLE_ID = 2   # حسابات العملاء
    SALES_REVENUE_ACCOUNT_ID = 3 # إيرادات المبيعات
    INVENTORY_ACCOUNT_ID = 4     # المخزون
    COGS_ACCOUNT_ID = 5          # تكلفة البضاعة المباعة
    ACCOUNTS_PAYABLE_ID = 6      # حسابات الموردين (لاستخدام "إلى حساب مورد" للمبيعات)
    SALES_CHARGES_REVENUE_ACCOUNT_ID = 7 # إيرادات أعباء المبيعات
    SALES_DISCOUNT_ACCOUNT_ID = 10 # حساب الخصم الممنوح (جديد)
    SALES_RETURNS_ACCOUNT_ID = 8 # مردودات المبيعات
    RETURN_CHARGES_EXPENSE_ACCOUNT_ID = 9 # مصروف أعباء المرتجعات

    def __init__(self):
        super().__init__()
        self.current_company_id = 1 # Initialize current_company_id here
        
        # Apply layout direction based on current language
        current_lang = get_language()
        if current_lang == 'ar':
            self.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)
        
        self.setWindowTitle(tr('windows.main_window'))
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(200)
        self.main_layout.addWidget(self.sidebar)

        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        print("[MainWindow] Initializing services...")
        self.init_services()
        print("[MainWindow] Services initialized")
        
        # Instantiate the Settings window once here
        print("[MainWindow] Creating Settings window...")
        self.settings_window = SettingsWindow(self.current_company_id, self.unit_service, self.currency_service, self.payment_method_service, self.loyalty_program_service, self.gift_card_service, self.company_service) # Pass company_service
        print("[MainWindow] Settings window created")

        print("[MainWindow] Initializing widgets...")
        self.init_widgets()
        print("[MainWindow] Widgets initialized")
        
        print("[MainWindow] Populating sidebar...")
        self.populate_sidebar()
        print("[MainWindow] Sidebar populated")

        self.sidebar.currentRowChanged.connect(self.display_widget)
        
        # Connect unit_changed_signal from SettingsWindow to ItemWidget's load_units_to_combo
        self.settings_window.unit_changed_signal.connect(self.widgets["Items"].load_units_to_combo)
        # Connect unit_changed_signal from SettingsWindow to POSMainWindow's sales_page and returns_page refresh_units_data
        self.settings_window.unit_changed_signal.connect(self.pos_main_window.sales_page.refresh_units_data)
        self.settings_window.unit_changed_signal.connect(self.pos_main_window.returns_page.refresh_units_data)

    def init_services(self):
        self.account_service = AccountService()
        self.journal_service = JournalService()
        self.arap_service = ARAPService()
        self.inventory_service = InventoryService()
        self.sales_purchase_service = SalesPurchaseService()
        self.cash_bank_service = CashBankService()
        self.fixed_asset_service = FixedAssetService()
        self.tax_service = TaxService()
        self.iam_service = IAMService()
        self.company_service = CompanyService()
        self.branch_service = BranchService()
        self.fiscal_period_service = FiscalPeriodService()
        self.cost_center_project_service = CostCenterProjectService()
        self.payroll_service = PayrollService()
        self.notifications_workflows_service = NotificationsWorkflowsService()
        self.reporting_service = ReportingService(self.account_service, self.journal_service, self.arap_service)
        self.general_configuration_service = GeneralConfigurationService()
        # New services for Settings Module
        self.unit_service = UnitService()
        self.currency_service = CurrencyService()
        self.payment_method_service = PaymentMethodService()
        self.coupon_service = CouponService() # New service instantiation
        self.shift_service = ShiftService() # New: ShiftService instantiation
        self.loyalty_program_service = LoyaltyProgramService() # New: LoyaltyProgramService instantiation
        self.gift_card_service = GiftCardService() # New: GiftCardService instantiation
        self.warehouse_service = WarehouseService() # New: WarehouseService instantiation

        # Initialize Sales & Purchase Backend
        from app.sales_purchase_module.sales_purchase_backend import SalesPurchaseBackend
        self.sales_purchase_backend = SalesPurchaseBackend()
        self.sales_purchase_backend.set_services(
            arap_service=self.arap_service,
            inventory_service=self.inventory_service,
            unit_service=self.unit_service,
            payment_method_service=self.payment_method_service,
            branch_service=self.branch_service,
            company_service=self.company_service,
            currency_service=self.currency_service,
            warehouse_service=self.warehouse_service
        )

        # Initialize Inventory Backend
        from app.inventory_module.inventory_backend import InventoryBackend
        self.inventory_backend = InventoryBackend()
        self.inventory_backend.set_services(
            inventory_service=self.inventory_service,
            warehouse_service=self.warehouse_service,
            unit_service=self.unit_service
        )

        self.pos_backend = POSBackend() # Initialize POSBackend here
        self.pos_backend.set_services(self.arap_service, self.inventory_service,
                                     self.unit_service, self.payment_method_service, self.branch_service,
                                     self.company_service, self.currency_service, self.coupon_service, 
                                     self.shift_service, self.loyalty_program_service, self.gift_card_service) # Set services for POSBackend including loyalty_program_service and gift_card_service
        # Instantiate the main POS window and show it
        self.pos_main_window = POSMainWindow(self.pos_backend, self.arap_service, self.inventory_service,
                                             self.unit_service, self.payment_method_service, self.branch_service,
                                             self.company_service, self.currency_service, 
                                             self.coupon_service, self.shift_service, self.loyalty_program_service,
                                             self.gift_card_service, self.warehouse_service) # Pass warehouse_service
        
        # Instantiate the Settings window
        # self.settings_window = SettingsWindow(self.current_company_id, self.unit_service, self.currency_service, self.payment_method_service, self.loyalty_program_service) # Moved instantiation

        # Connect POSBackend signals to MainWindow slots for cross-module communication
        self.pos_backend.sales_invoice_created.connect(self._handle_invoice_event)
        self.pos_backend.return_invoice_created.connect(self._handle_invoice_event)

    def init_widgets(self):
        # Create Language Settings Widget
        print("[init_widgets] Creating Language Settings...")
        self.language_settings_widget = LanguageSettingsWidget()
        self.language_settings_widget.language_changed.connect(self.on_language_changed)
        
        print("[init_widgets] Creating widgets dictionary...")
        self.widgets = {
            "Accounts": AccountsWidget(self.account_service),
            "Journals": JournalsWidget(self.journal_service),
            "Customers": CustomerWidget(self.arap_service),
            "Suppliers": SupplierWidget(self.arap_service),
            "Items": ItemWidget(self.inventory_service, self.unit_service),
        }
        
        print("[init_widgets] Creating Sales & Purchase window...")
        try:
            sales_purchase_window = SalesPurchaseMainWindow(
                self.sales_purchase_backend,
                self.arap_service,
                self.inventory_service,
                self.unit_service,
                self.payment_method_service,
                self.branch_service,
                self.company_service,
                self.currency_service,
                self.warehouse_service
            )
            print("[init_widgets] Sales & Purchase window created successfully")
            self.widgets["Sales & Purchases"] = sales_purchase_window
        except Exception as e:
            print(f"[init_widgets] ERROR creating Sales & Purchase window: {e}")
            import traceback
            traceback.print_exc()
        
        print("[init_widgets] Creating Inventory window...")
        try:
            inventory_window = InventoryMainWindow(
                self.inventory_backend,
                self.inventory_service,
                self.warehouse_service,
                self.unit_service,
                self.branch_service
            )
            print("[init_widgets] Inventory window created successfully")
            self.widgets["Inventory"] = inventory_window
        except Exception as e:
            print(f"[init_widgets] ERROR creating Inventory window: {e}")
            import traceback
            traceback.print_exc()
        
        self.widgets.update({
            "Cash & Bank": CashBankWidget(self.cash_bank_service, self.company_service, self.branch_service),
            "Fixed Assets": FixedAssetsWidget(self.fixed_asset_service),
            "Tax Compliance": TaxComplianceWidget(self.tax_service),
            "IAM": IAMWidget(self.iam_service),
            "Company": CompanyWidget(self.company_service, self.currency_service),
            "Branch": BranchWidget(self.company_service, self.branch_service),
            "Fiscal Periods": FiscalPeriodWidget(self.fiscal_period_service, self.company_service),
            "Cost Centers & Projects": CostCenterProjectWidget(self.cost_center_project_service),
            "Employees": EmployeeWidget(self.payroll_service, self.company_service, self.branch_service),
            "Payroll": PayrollWidget(self.payroll_service),
            "Notifications & Workflows": NotificationsWorkflowsWidget(self.notifications_workflows_service),
            "Reporting": ReportingWidget(self.reporting_service, self.account_service, self.journal_service, self.arap_service),
            "General Configuration": GeneralConfigurationWidget(self.general_configuration_service, self.company_service),
            tr('settings.language_settings'): self.language_settings_widget,
            # "Settings": SettingsMainWidget(self.current_company_id, self.unit_service, self.currency_service, self.payment_method_service), # Removed from here
            # "POS": POSMainWindow(self.pos_backend, self.arap_service, self.inventory_service), # Removed from here
        })
        
        print("[init_widgets] Adding widgets to stacked widget...")
        for name, widget in self.widgets.items():
            self.stacked_widget.addWidget(widget)
        print("[init_widgets] All widgets added successfully")
    
    def on_language_changed(self, language):
        """Handle language change event and update UI"""
        print(f"Language changed to: {language}")
        
        # Apply layout direction to application and all widgets
        if language == 'ar':
            QApplication.instance().setLayoutDirection(Qt.RightToLeft)
            self.setLayoutDirection(Qt.RightToLeft)
        else:
            QApplication.instance().setLayoutDirection(Qt.LeftToRight)
            self.setLayoutDirection(Qt.LeftToRight)
        
        # Update window title
        self.setWindowTitle(tr('windows.main_window'))
        
        # Update menu bar
        self.menuBar().clear()
        self.create_menu()
        
        # Update sidebar
        self.populate_sidebar()
        
        # Refresh all widgets
        self.refresh_all_widgets()
    
    def refresh_all_widgets(self):
        """Refresh translations for all widgets"""
        for widget_name, widget in self.widgets.items():
            if hasattr(widget, 'refresh_translations'):
                try:
                    widget.refresh_translations()
                except Exception as e:
                    print(f"Error refreshing {widget_name}: {e}")
        
        # Refresh current widget display
        current_widget = self.stacked_widget.currentWidget()
        if current_widget:
            self.stacked_widget.setCurrentWidget(current_widget)

    def populate_sidebar(self):
        """Populate sidebar with module names"""
        self.sidebar.clear()
        
        # Store mapping between display names and widget keys
        self.sidebar_mapping = {}
        
        # Define module names with translations
        module_names = {
            "Accounts": tr('modules.accounts'),
            "Journals": tr('modules.journals'),
            "Customers": tr('modules.customers'),
            "Suppliers": tr('modules.suppliers'),
            "Items": tr('modules.items'),
            "Sales & Purchases": tr('modules.sales') + " & " + tr('modules.purchases'),
            "Inventory": tr('modules.inventory'),
            "Cash & Bank": tr('modules.cash_bank'),
            "Fixed Assets": tr('modules.fixed_assets'),
            "Tax Compliance": tr('modules.tax_compliance'),
            "IAM": tr('modules.iam'),
            "Company": tr('modules.company'),
            "Branch": tr('modules.branch'),
            "Fiscal Periods": tr('modules.fiscal_periods'),
            "Cost Centers & Projects": tr('modules.cost_centers') + " & " + tr('modules.projects'),
            "Employees": tr('modules.employees'),
            "Payroll": tr('modules.payroll'),
            "Notifications & Workflows": tr('modules.notifications') + " & " + tr('modules.workflows'),
            "Reporting": tr('modules.reports'),
            "General Configuration": tr('modules.general_config'),
            tr('settings.language_settings'): tr('settings.language_settings'),
        }
        
        for key in self.widgets.keys():
            display_name = module_names.get(key, key)
            self.sidebar.addItem(display_name)
            # Store mapping from display name to widget key
            self.sidebar_mapping[display_name] = key
        self.sidebar.addItem("POS") # Add POS explicitly to sidebar
        self.sidebar.addItem(tr('modules.settings')) # Add Settings explicitly to sidebar

    def display_widget(self, index):
        display_name = self.sidebar.currentItem().text()
        
        # Get the actual widget key from mapping
        widget_key = self.sidebar_mapping.get(display_name, display_name)
        
        if widget_key == "POS": # If POS is selected, open in new window
            self.pos_main_window.showMaximized() # Show the pre-instantiated POS window
        elif widget_key == "Settings" or display_name == tr('modules.settings'): # If Settings is selected, open in new window
            self.settings_window.show() # Show the pre-instantiated Settings window
        else:
            widget = self.widgets.get(widget_key)
            if widget:
                self.stacked_widget.setCurrentWidget(widget)

    def create_menu(self):
        from app.i18n.translations import tr, set_language, get_language
        
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu(tr('menu.file'))
        exit_action = file_menu.addAction(tr('menu.exit'))
        exit_action.triggered.connect(self.close)

        # Modules Menu
        modules_menu = menu_bar.addMenu("&Modules")
        for name in self.widgets.keys():
            action = modules_menu.addAction(name)
            action.triggered.connect(lambda checked, n=name: self.show_widget(n))
        # Add POS to modules menu explicitly
        pos_action = modules_menu.addAction("POS")
        pos_action.triggered.connect(lambda: self.show_widget("POS"))
        # Add Settings to modules menu explicitly
        settings_action = modules_menu.addAction("Settings")
        settings_action.triggered.connect(lambda: self.show_widget("Settings"))
        
        # Language Menu
        language_menu = menu_bar.addMenu(tr('menu.language'))
        
        # Arabic Action
        arabic_action = language_menu.addAction(tr('menu.arabic'))
        arabic_action.triggered.connect(lambda: self.change_language('ar'))
        
        # English Action
        english_action = language_menu.addAction(tr('menu.english'))
        english_action.triggered.connect(lambda: self.change_language('en'))
        
        # Help Menu
        help_menu = menu_bar.addMenu(tr('menu.help'))
        about_action = help_menu.addAction(tr('menu.about'))
        about_action.triggered.connect(self.show_about)
    
    def change_language(self, language):
        """Change application language"""
        from app.i18n.translations import set_language
        from PySide6.QtWidgets import QMessageBox
        
        set_language(language)
        
        # Show message
        if language == 'ar':
            QMessageBox.information(self, "تغيير اللغة", "تم تغيير اللغة إلى العربية.\nيرجى إعادة تشغيل التطبيق لتطبيق التغييرات.")
        else:
            QMessageBox.information(self, "Language Change", "Language changed to English.\nPlease restart the application to apply changes.")
    
    def show_about(self):
        """Show about dialog"""
        from PySide6.QtWidgets import QMessageBox
        from app.i18n.translations import get_language
        
        if get_language() == 'ar':
            QMessageBox.about(self, "حول النظام", 
                            "Labeeb ERP - لبيب\n"
                            "الإصدار 1.0.0\n\n"
                            "نظام محاسبي وإداري ذكي ومتكامل\n"
                            "© 2024 جميع الحقوق محفوظة")
        else:
            QMessageBox.about(self, "About System",
                            "Labeeb ERP\n"
                            "Version 1.0.0\n\n"
                            "Smart & Integrated Accounting System\n"
                            "© 2024 All Rights Reserved")

    def show_widget(self, name):
        if name == "POS":
            self.pos_main_window.showMaximized() # Show the pre-instantiated POS window
        elif name == "Settings":
            # if self.settings_window is None: # Removed conditional creation
            #    self.settings_window = SettingsWindow(self.current_company_id, self.unit_service, self.currency_service, self.payment_method_service, self.loyalty_program_service, self.gift_card_service, self.company_service) # Pass company_service
            self.settings_window.show() # Show the pre-instantiated Settings window
        else:
            widget = self.widgets.get(name)
            if widget:
                self.stacked_widget.setCurrentWidget(widget)

    def _handle_invoice_event(self, invoice_data: dict):
        """ A slot to handle invoice creation events from POSBackend.
        This triggers the creation of accounting entries.
        """
        print(f"[MainWindow] Received invoice event: {invoice_data.get('invoice_no', 'N/A')}")
        invoice_type = invoice_data.get("invoice_type") # 0 for Sales, 1 for Return

        company_id = invoice_data.get("company_id", 1) # Default to 1
        branch_id = invoice_data.get("branch_id", 1)   # Default to 1
        invoice_date_str = invoice_data.get("invoice_date", date.today().isoformat())
        entry_date = date.fromisoformat(invoice_date_str) if isinstance(invoice_date_str, str) else invoice_date_str
        
        payment_method = invoice_data.get("payment_method")
        total_amount = Decimal(str(invoice_data.get("total_amount", 0.0)))
        discount_percentage = Decimal(str(invoice_data.get("discount_percentage", 0.0)))
        charges = Decimal(str(invoice_data.get("charges", 0.0)))
        coupon_discount_amount = Decimal(str(invoice_data.get("coupon_discount", 0.0))) # New: Get coupon discount
        loyalty_discount_amount = Decimal(str(invoice_data.get("loyalty_discount_amount", 0.0))) # New: Get loyalty discount
        customer_id = invoice_data.get("customer_id")
        supplier_id = invoice_data.get("supplier_id")
        invoice_no = invoice_data.get("invoice_no", "N/A")
        
        created_by = invoice_data.get("created_by", 1) # Assuming a default user ID
        current_period = f"{entry_date.year}-{entry_date.month:02d}" # Simple period format

        journal_lines = []
        
        # Calculate net sales amount (before COGS)
        # total_amount from invoice_data is already after line item discounts and overall discount and charges
        # We need to reverse calculate gross sales and the actual discount amount for accounting entries.
        # This assumes total_amount is inclusive of charges and net of discount.
        # Gross sales before any discounts or charges at the item level
        gross_items_amount = sum(Decimal(str(line['quantity'])) * Decimal(str(line['price'])) for line in invoice_data.get('lines', []))
        
        # Total discount amount (from percentage)
        overall_discount_amount = gross_items_amount * (discount_percentage / 100)

        # Add coupon and loyalty discount to overall_discount_amount for accounting purposes
        overall_discount_amount += coupon_discount_amount
        overall_discount_amount += loyalty_discount_amount

        # Sales Revenue (Credit) - Gross sales before overall discount, but after item-level discounts
        # If total_amount includes charges, we should credit sales revenue with (total_amount - charges + overall_discount_amount)
        # This is a critical point: how `total_amount` is calculated and what it represents.
        # Assuming `total_amount` is the final amount paid/owed by customer, it includes charges and is net of discount.
        # So, Sales Revenue = (total_amount - charges) + overall_discount_amount
        sales_revenue_credit = (total_amount - charges) + overall_discount_amount
        
        if invoice_type == 0: # Sales Invoice
            print(f"[MainWindow] Creating accounting entries for Sales Invoice {invoice_no}")
            
            # 1. Debit: Cash / Accounts Receivable / Accounts Payable (Supplier)
            debit_account_id = None
            # Iterate through payment_details for split payments
            if "payments" in invoice_data and invoice_data["payments"]:
                for payment_detail in invoice_data["payments"]:
                    payment_method_name = payment_detail.get("payment_method_name")
                    payment_amount = Decimal(str(payment_detail.get("amount", 0.0)))
                    
                    if payment_method_name == "نقدي" or payment_method_name == "شبكة" or payment_method_name == "شيك" or payment_method_name == "تحويل":
                        debit_account_id = self.CASH_ACCOUNT_ID # Assuming Cash Account for all immediate payments
                    elif payment_method_name == "آجل": # On Credit
                        debit_account_id = self.ACCOUNTS_RECEIVABLE_ID
                    elif payment_method_name == "إلى حساب": # To Supplier's Account
                        debit_account_id = self.ACCOUNTS_PAYABLE_ID 
                    elif payment_method_name == "بطاقة هدية": # Gift Card payment
                        # In a real scenario, this might debit a Gift Card Liability account
                        # For simplicity, we'll treat it like cash for now for the debit side of the invoice total
                        debit_account_id = self.CASH_ACCOUNT_ID 

                    if debit_account_id:
                        journal_lines.append({
                            "account_id": debit_account_id,
                            "debit": payment_amount,
                            "credit": Decimal(0),
                            "memo": f"Sales Invoice {invoice_no} - {payment_method_name}"
                        })
            else: # Fallback if no payment_details (shouldn't happen with SplitPaymentDialog)
                if payment_method == "cash" or payment_method == "network" or payment_method == "cheque" or payment_method == "transfer" or payment_method == "coupon":
                    debit_account_id = self.CASH_ACCOUNT_ID # Assuming Cash Account for all immediate payments
                elif payment_method == "اجل": # On Credit
                    debit_account_id = self.ACCOUNTS_RECEIVABLE_ID
                elif payment_method == "الى حساب": # To Supplier's Account
                    debit_account_id = self.ACCOUNTS_PAYABLE_ID 
                
                if debit_account_id:
                    journal_lines.append({
                        "account_id": debit_account_id,
                        "debit": total_amount,
                        "credit": Decimal(0),
                        "memo": f"Sales Invoice {invoice_no} - {payment_method}"
                    })
            
            # 2. Credit: Sales Revenue
            if sales_revenue_credit > 0:
                journal_lines.append({
                    "account_id": self.SALES_REVENUE_ACCOUNT_ID,
                    "debit": Decimal(0),
                    "credit": sales_revenue_credit,
                    "memo": f"Sales Revenue for Invoice {invoice_no}"
                })
            
            # 3. Debit: Sales Discount (if any) - This now includes coupon and loyalty discounts
            if overall_discount_amount > 0:
                journal_lines.append({
                    "account_id": self.SALES_DISCOUNT_ACCOUNT_ID,
                    "debit": overall_discount_amount,
                    "credit": Decimal(0),
                    "memo": f"Sales Discount for Invoice {invoice_no}"
                })

            # 4. Credit: Sales Charges Revenue (if any)
            if charges > 0:
                journal_lines.append({
                    "account_id": self.SALES_CHARGES_REVENUE_ACCOUNT_ID,
                    "debit": Decimal(0),
                    "credit": charges,
                    "memo": f"Sales Charges for Invoice {invoice_no}"
                })

            # 5. Cost of Goods Sold Entry (Debit: COGS, Credit: Inventory)
            total_cogs = Decimal(0)
            for line in invoice_data.get('lines', []):
                item_cost = Decimal(str(line.get('cost_price', 0.0)))
                item_quantity = Decimal(str(line.get('quantity', 0)))
                total_cogs += item_cost * item_quantity
            
            if total_cogs > 0:
                journal_lines.append({
                    "account_id": self.COGS_ACCOUNT_ID,
                    "debit": total_cogs,
                    "credit": Decimal(0),
                    "memo": f"COGS for Sales Invoice {invoice_no}"
                })
                journal_lines.append({
                    "account_id": self.INVENTORY_ACCOUNT_ID,
                    "debit": Decimal(0),
                    "credit": total_cogs,
                    "memo": f"Inventory reduction for Sales Invoice {invoice_no}"
                })

        elif invoice_type == 1: # Return Invoice
            print(f"[MainWindow] Creating accounting entries for Return Invoice {invoice_no}")

            # 1. Debit: Sales Returns
            if total_amount > 0: # Total amount for returns is effectively the credit to customer, so debit sales returns
                journal_lines.append({
                    "account_id": self.SALES_RETURNS_ACCOUNT_ID,
                    "debit": total_amount,
                    "credit": Decimal(0),
                    "memo": f"Sales Return for Invoice {invoice_no}"
                })
            
            # 2. Credit: Cash / Accounts Receivable / Accounts Payable (Supplier)
            credit_account_id = None
            # Iterate through payment_details for split payments
            if "payments" in invoice_data and invoice_data["payments"]:
                for payment_detail in invoice_data["payments"]:
                    payment_method_name = payment_detail.get("payment_method_name")
                    payment_amount = Decimal(str(payment_detail.get("amount", 0.0)))

                    if payment_method_name == "نقدي" or payment_method_name == "شبكة" or payment_method_name == "شيك" or payment_method_name == "تحويل":
                        credit_account_id = self.CASH_ACCOUNT_ID # Assuming Cash Account for all immediate payments
                    elif payment_method_name == "آجل": # On Credit
                        credit_account_id = self.ACCOUNTS_RECEIVABLE_ID
                    elif payment_method_name == "إلى حساب": # To Supplier's Account (as a credit, increasing our liability to them or reducing their balance)
                        credit_account_id = self.ACCOUNTS_PAYABLE_ID
                    elif payment_method_name == "بطاقة هدية": # Gift Card payment
                        # For simplicity, we'll treat it like cash for now for the credit side of the invoice total
                        credit_account_id = self.CASH_ACCOUNT_ID 

                    if credit_account_id:
                        journal_lines.append({
                            "account_id": credit_account_id,
                            "debit": Decimal(0),
                            "credit": payment_amount,
                            "memo": f"Return Payment for Invoice {invoice_no} - {payment_method_name}"
                        })
            else: # Fallback if no payment_details
                if payment_method == "cash" or payment_method == "network" or payment_method == "cheque" or payment_method == "transfer" or payment_method == "coupon":
                    credit_account_id = self.CASH_ACCOUNT_ID # Assuming Cash Account for all immediate payments
                elif payment_method == "اجل": # On Credit
                    credit_account_id = self.ACCOUNTS_RECEIVABLE_ID
                elif payment_method == "الى حساب": # To Supplier's Account (as a credit, increasing our liability to them or reducing their balance)
                    credit_account_id = self.ACCOUNTS_PAYABLE_ID
                
                if credit_account_id:
                    journal_lines.append({
                        "account_id": credit_account_id,
                        "debit": Decimal(0),
                        "credit": total_amount,
                        "memo": f"Return Payment for Invoice {invoice_no} - {payment_method}"
                    })
            
            # 3. Debit: Inventory (for returned items)
            # 4. Credit: COGS (reverse of sales COGS)
            total_cogs_returned = Decimal(0)
            for line in invoice_data.get('lines', []):
                item_cost = Decimal(str(line.get('cost_price', 0.0)))
                item_quantity = Decimal(str(line.get('quantity', 0)))
                total_cogs_returned += item_cost * item_quantity
            
            if total_cogs_returned > 0:
                journal_lines.append({
                    "account_id": self.INVENTORY_ACCOUNT_ID,
                    "debit": total_cogs_returned,
                    "credit": Decimal(0),
                    "memo": f"Inventory increase for Return Invoice {invoice_no}"
                })
                journal_lines.append({
                    "account_id": self.COGS_ACCOUNT_ID,
                    "debit": Decimal(0),
                    "credit": total_cogs_returned,
                    "memo": f"COGS reversal for Return Invoice {invoice_no}"
                })
            
            # 5. Handle return charges (if applicable, usually as an expense)
            if charges > 0:
                journal_lines.append({
                    "account_id": self.RETURN_CHARGES_EXPENSE_ACCOUNT_ID,
                    "debit": charges,
                    "credit": Decimal(0),
                    "memo": f"Return Charges for Invoice {invoice_no}"
                })

        try:
            if journal_lines:
                ref_no = f"POS-{invoice_no}"
                self.journal_service.create_journal_entry(
                    company_id=company_id,
                    branch_id=branch_id,
                    entry_date=entry_date,
                    period=current_period,
                    ref_no=ref_no,
                    created_by=created_by,
                    lines_data=journal_lines
                )
                print(f"[MainWindow] Accounting entries successfully created for Invoice {invoice_no}.")
            else:
                print(f"[MainWindow] No journal lines generated for Invoice {invoice_no}. Skipping journal entry creation.")
        except ValueError as e:
            print(f"[MainWindow] Error creating journal entry for Invoice {invoice_no}: {e}")
        except Exception as e:
            print(f"[MainWindow] An unexpected error occurred while creating journal entry for Invoice {invoice_no}: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set initial layout direction based on current language
    from app.i18n.translations import get_language
    current_lang = get_language()
    if current_lang == 'ar':
        app.setLayoutDirection(Qt.RightToLeft)
    else:
        app.setLayoutDirection(Qt.LeftToRight)
    
    # Removed QML path settings as we are using QtWidgets
    
    # Check if a company exists, if not, run the setup wizard
    with SessionLocal() as db:
        company_service = CompanyService()
        companies = company_service.get_all_companies()
        if not companies:
            print("No companies found. Creating default company, user, branch, and warehouse...")
            
            # Create default currencies if they don't exist
            currency_service = CurrencyService()
            sar_currency = currency_service.get_currency_by_code("SAR")
            if not sar_currency:
                sar_currency = currency_service.create_currency(
                    name_ar="الريال السعودي", name_en="Saudi Riyal", code="SAR", symbol="SR", exchange_rate=Decimal(1.0)
                )
            
            # You can add more default currencies here if needed
            # usd_currency = currency_service.get_currency_by_code("USD")
            # if not usd_currency:
            #     usd_currency = currency_service.create_currency(
            #         name_ar="الدولار الأمريكي", name_en="US Dollar", code="USD", symbol="$", exchange_rate=Decimal(3.75)
            #     )

            # Create a default company
            company_service = CompanyService()
            new_company = company_service.create_company(
                name_ar="الشركة الافتراضية",
                name_en="Default Company",
                base_currency_id=sar_currency.id,  # Use the ID of the SAR currency
                # secondary_currency_id=usd_currency.id, # Optional secondary currency
                address="الرياض",
                phone_number="0500000000",
                email="admin@default.com",
                admin_username="admin",
                admin_password_hash=generate_password_hash("adminpass"),
                created_by=None # Will be updated after user creation
            )
            print(f"Default Company created with ID: {new_company.id}")

            # Create a default admin user for the company
            iam_service = IAMService()
            admin_user = iam_service.create_user(
                username="admin",
                password="adminpass",
                email="admin@default.com",
                company_id=new_company.id,
                full_name_ar="مدير النظام",
                full_name_en="System Admin"
            )
            print(f"Default Admin User created with ID: {admin_user.id}")

            # Update the company's created_by field with the admin user's ID
            company_service.update_company_created_by(new_company.id, admin_user.id)
            print(f"Company {new_company.id} created_by updated to user {admin_user.id}")

            # Create a default branch for the company
            branch_service = BranchService()
            new_branch = branch_service.create_branch(
                company_id=new_company.id,
                name_ar="الفرع الرئيسي",
                name_en="Main Branch",
                address="الرياض، شارع العليا",
                phone_number="0511111111",
                base_currency_id=sar_currency.id, # Link branch to SAR currency
                created_by=admin_user.id
            )
            print(f"Default Branch created with ID: {new_branch.id}")

            # Create a default warehouse for the branch
            warehouse_service = WarehouseService()
            new_warehouse = warehouse_service.create_warehouse(
                company_id=new_company.id,
                branch_id=new_branch.id,
                name_ar="المستودع الرئيسي",
                name_en="Main Warehouse",
                location="الرياض، المنطقة الصناعية",
                base_currency_id=sar_currency.id, # Link warehouse to SAR currency
                created_by=admin_user.id
            )
            print(f"Default Warehouse created with ID: {new_warehouse.id}")

            print("Default company, user, branch, and warehouse created. Starting main application.")
        # else: # Removed the else block for setup wizard
        #    print("Companies found. Starting main application.")

    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
