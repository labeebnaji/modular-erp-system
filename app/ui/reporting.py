from PySide6.QtWidgets import QWidget
#from PySide6.QtWidgets import QVBoxLayout, QTabWidget
from app.application.services import AccountService, JournalService, ARAPService # Add other services as needed
#from app.infrastructure.database import get_db # No longer needed
#from app.ui.trial_balance_widget import TrialBalanceWidget
#from app.ui.income_statement_widget import IncomeStatementWidget
#from app.ui.balance_sheet_widget import BalanceSheetWidget
#from app.ui.cash_flow_statement_widget import CashFlowStatementWidget

class ReportingWidget(QWidget):
    def __init__(self, reporting_service, account_service, journal_service, arap_service, parent=None):
        super().__init__(parent)
        # Initialize services here, without passing db
        self.reporting_service = reporting_service
        self.account_service = account_service
        self.journal_service = journal_service
        self.arap_service = arap_service
        # self.inventory_service = InventoryService()
        # self.sales_purchase_service = SalesPurchaseService()
        # self.cash_bank_service = CashBankService()
        # self.fixed_asset_service = FixedAssetService()
        # self.tax_service = TaxService()
        # self.company_service = CompanyService()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Reporting and Financial Statements")
        # Removed fixed geometry

        # Previously, this contained a QTabWidget and its sub-widgets.
        # Now, sub-widgets are directly managed by main.py's QStackedWidget.
        pass
