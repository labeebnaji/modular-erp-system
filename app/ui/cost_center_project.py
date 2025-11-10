from PySide6.QtWidgets import QWidget
#from PySide6.QtWidgets import QVBoxLayout, QTabWidget, QMessageBox
from app.application.services import CostCenterProjectService
#from app.infrastructure.database import get_db # No longer needed
#from app.ui.cost_center_widget import CostCenterWidget
#from app.ui.project_widget import ProjectWidget

class CostCenterProjectWidget(QWidget):
    def __init__(self, cost_center_project_service, parent=None):
        super().__init__(parent)
        self.cost_center_project_service = cost_center_project_service
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Cost Centers and Projects")
        # Removed fixed geometry

        # Previously, this contained a QTabWidget and its sub-widgets.
        # Now, sub-widgets are directly managed by main.py's QStackedWidget.
        pass
