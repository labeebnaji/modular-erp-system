from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QCheckBox, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import Signal # Import Signal

from app.settings_module.ui_widgets.units_settings_widget import UnitsSettingsWidget
from app.settings_module.ui_widgets.currency_settings_widget import CurrencySettingsWidget
from app.settings_module.ui_widgets.payment_method_settings_widget import PaymentMethodSettingsWidget
from app.settings_module.ui_widgets.loyalty_program_settings_widget import LoyaltyProgramSettingsWidget

from app.application.services import UnitService, CurrencyService, PaymentMethodService, LoyaltyProgramService, CompanyService

class SettingsMainWidget(QWidget):
    unit_changed_signal = Signal() # New signal to propagate unit changes

    def __init__(self, company_id: int, unit_service: UnitService, currency_service: CurrencyService, 
                 payment_method_service: PaymentMethodService, loyalty_program_service: LoyaltyProgramService,
                 gift_card_service, company_service: CompanyService, parent=None):
        super().__init__(parent)
        self.company_id = company_id
        self.unit_service = unit_service
        self.currency_service = currency_service
        self.payment_method_service = payment_method_service
        self.loyalty_program_service = loyalty_program_service
        self.gift_card_service = gift_card_service # New: Store GiftCardService
        self.company_service = company_service
        self.is_loading = True  # Flag to prevent message during initial load
        self.init_ui()
        self._load_general_settings()
        self.is_loading = False  # Enable messages after initial load

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()

        # General Settings Tab (New)
        self.general_settings_tab = QWidget()
        general_settings_layout = QVBoxLayout(self.general_settings_tab)
        
        self.loyalty_program_checkbox = QCheckBox("تمكين برنامج الولاء")
        self.loyalty_program_checkbox.stateChanged.connect(self._toggle_loyalty_program_status)
        general_settings_layout.addWidget(self.loyalty_program_checkbox)

        general_settings_layout.addStretch(1) # Add stretch to push checkbox to top
        self.tab_widget.addTab(self.general_settings_tab, "General Settings")

        # Units Settings Tab
        self.units_settings_widget = UnitsSettingsWidget(self.company_id, self.unit_service)
        self.units_settings_widget.unit_updated.connect(self.unit_changed_signal.emit) # Connect to propagate signal
        self.tab_widget.addTab(self.units_settings_widget, "Item Units")

        # Currency Settings Tab
        self.currency_settings_widget = CurrencySettingsWidget(self.company_id, self.currency_service)
        self.tab_widget.addTab(self.currency_settings_widget, "Currencies")

        # Payment Method Settings Tab
        self.payment_method_settings_widget = PaymentMethodSettingsWidget(self.company_id, self.payment_method_service)
        self.tab_widget.addTab(self.payment_method_settings_widget, "Payment Methods")

        # Loyalty Program Settings Tab (New)
        self.loyalty_program_settings_widget = LoyaltyProgramSettingsWidget(self.company_id, self.loyalty_program_service)
        self.tab_widget.addTab(self.loyalty_program_settings_widget, "Loyalty Programs")

        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

    def _load_general_settings(self):
        company = self.company_service.get_company_by_id(self.company_id)
        if company:
            self.loyalty_program_checkbox.setChecked(company.is_loyalty_enabled)

    def _toggle_loyalty_program_status(self, state):
        is_enabled = bool(state)
        self.company_service.update_company_loyalty_status(self.company_id, is_enabled)
        # Only show message if not during initial loading
        if not self.is_loading:
            QMessageBox.information(self, "برنامج الولاء", f"تم {'' if is_enabled else 'إلغاء'} تفعيل برنامج الولاء للشركة.")

