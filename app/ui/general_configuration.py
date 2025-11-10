from PySide6.QtWidgets import QWidget
#from PySide6.QtWidgets import QVBoxLayout, QTabWidget, QMessageBox
from app.application.services import CompanyService
#from app.infrastructure.database import get_db # No longer needed
#from app.ui.company_widget import CompanyWidget
#from app.ui.branch_widget import BranchWidget
#from app.ui.fiscal_period_widget import FiscalPeriodWidget

class GeneralConfigurationWidget(QWidget):
    def __init__(self, general_configuration_service, company_service, parent=None):
        super().__init__(parent)
        self.general_configuration_service = general_configuration_service
        self.company_service = company_service
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("General Configuration")
        # Removed fixed geometry

        # Previously, this contained a QTabWidget and its sub-widgets.
        # Now, sub-widgets are directly managed by main.py's QStackedWidget.
        pass
