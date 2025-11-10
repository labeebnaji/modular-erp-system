from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSize, Signal # Import Signal

from app.settings_module.ui_widgets.settings_main_widget import SettingsMainWidget
from app.application.services import UnitService, CurrencyService, PaymentMethodService, LoyaltyProgramService, CompanyService

class SettingsWindow(QMainWindow):
    unit_changed_signal = Signal() # New signal to propagate unit changes

    def __init__(self, company_id: int, unit_service: UnitService, currency_service: CurrencyService, 
                 payment_method_service: PaymentMethodService, loyalty_program_service: LoyaltyProgramService,
                 gift_card_service, company_service: CompanyService, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Settings")
        self.setGeometry(150, 150, 1000, 700) # Adjust size and position as needed

        self.company_id = company_id
        self.unit_service = unit_service
        self.currency_service = currency_service
        self.payment_method_service = payment_method_service
        self.loyalty_program_service = loyalty_program_service # Store the new service
        self.gift_card_service = gift_card_service # New: Store GiftCardService
        self.company_service = company_service # Store the new service

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.settings_main_widget = SettingsMainWidget(
            self.company_id,
            self.unit_service,
            self.currency_service,
            self.payment_method_service,
            self.loyalty_program_service,
            self.gift_card_service, # Pass the new service
            self.company_service # Pass the new service
        )
        self.settings_main_widget.unit_changed_signal.connect(self.unit_changed_signal.emit) # Connect to propagate signal
        main_layout.addWidget(self.settings_main_widget)

        # Apply some basic styling for consistency
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                background-color: white;
            }
            QTabBar::tab {
                background: #e0e0e0;
                border: 1px solid #ccc;
                border-bottom-color: #c2c2c2; /* Separator color */
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 8ex;
                padding: 5px;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background: #d0d0d0;
            }
            QTabBar::tab:selected {
                border-color: #999;
                border-bottom-color: #f0f0f0; /* Same as pane color */
            }
        """)
