from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QFormLayout, QGroupBox, QHeaderView, QCheckBox
from PySide6.QtCore import QDate
from app.application.services import NotificationsWorkflowsService, CompanyService # Added CompanyService
#from app.infrastructure.database import get_db # No longer needed

class NotificationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notifications_workflows_service = NotificationsWorkflowsService()
        self.company_service = CompanyService() # Initialize CompanyService
        self.init_ui()
        self.load_notifications()

    def init_ui(self):
        self.setWindowTitle("Notification Management")

        main_layout = QVBoxLayout(self)

        # Notification form
        form_group_box = QGroupBox("Notification Details")
        form_layout = QFormLayout()

        self.company_id_input = QComboBox()
        self.load_companies_to_combobox(self.company_id_input)
        form_layout.addRow(QLabel("Company:"), self.company_id_input)

        self.branch_id_input = QComboBox()
        self.load_branches_to_combobox(self.branch_id_input, self.company_id_input.currentData())
        form_layout.addRow(QLabel("Branch:"), self.branch_id_input)

        self.recipient_input = QLineEdit()
        self.recipient_input.setPlaceholderText("Recipient (e.g., user ID or email)")
        # Icon placeholder: self.recipient_input.addAction(QIcon("path/to/recipient_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Recipient:"), self.recipient_input)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Notification Message")
        # Icon placeholder: self.message_input.addAction(QIcon("path/to/message_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Message:"), self.message_input)

        self.notification_type_input = QComboBox()
        self.notification_type_input.addItems(["Email", "SMS", "In-App"])
        form_layout.addRow(QLabel("Type:"), self.notification_type_input)

        self.status_input = QComboBox()
        self.status_input.addItems(["Pending", "Sent", "Failed"])
        form_layout.addRow(QLabel("Status:"), self.status_input)

        add_button = QPushButton("Add Notification")
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        add_button.clicked.connect(self.add_notification)
        form_layout.addRow(add_button)

        form_group_box.setLayout(form_layout)
        main_layout.addWidget(form_group_box)

        # Notification table
        self.notifications_table = QTableWidget()
        self.notifications_table.setColumnCount(7) # Increased column count
        self.notifications_table.setHorizontalHeaderLabels(["ID", "Company", "Branch", "Recipient", "Message", "Type", "Status"])
        self.notifications_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        main_layout.addWidget(self.notifications_table)

        main_layout.addStretch(1) # Add stretch to push content upwards and fill remaining space

        self.setLayout(main_layout)

    def load_companies_to_combobox(self, combobox):
        combobox.clear()
        companies = self.company_service.get_all_companies()
        combobox.addItem("Select Company", 0) # Default empty item
        for company in companies:
            combobox.addItem(f"{company.name_en} ({company.code})", company.id)

    def load_branches_to_combobox(self, combobox, company_id):
        combobox.clear()
        branches = self.company_service.get_all_branches()
        combobox.addItem("Select Branch", 0)
        for branch in branches:
            if branch.company_id == company_id: # Basic filtering
                combobox.addItem(f"{branch.name_en} ({branch.code})", branch.id)

    def load_notifications(self):
        self.notifications_table.setRowCount(0)
        # Placeholder logic: In a real scenario, this would fetch actual notification data.
        # For now, we'll use dummy data.
        dummy_data = [
            (1, 1, 1, "user@example.com", "Your invoice #123 is due.", "Email", "Pending"),
            (2, 1, 1, "admin@example.com", "New sales order #456 created.", "In-App", "Sent"),
        ]

        self.notifications_table.setRowCount(len(dummy_data))
        for row, (id, company_id, branch_id, recipient, message, type, status) in enumerate(dummy_data):
            company = self.company_service.get_company_by_id(company_id)
            company_name = company.name_en if company else "Unknown Company"
            branch = self.company_service.get_branch_by_id(branch_id)
            branch_name = branch.name_en if branch else "Unknown Branch"

            self.notifications_table.setItem(row, 0, QTableWidgetItem(str(id)))
            self.notifications_table.setItem(row, 1, QTableWidgetItem(company_name))
            self.notifications_table.setItem(row, 2, QTableWidgetItem(branch_name))
            self.notifications_table.setItem(row, 3, QTableWidgetItem(recipient))
            self.notifications_table.setItem(row, 4, QTableWidgetItem(message))
            self.notifications_table.setItem(row, 5, QTableWidgetItem(type))
            self.notifications_table.setItem(row, 6, QTableWidgetItem(status))

    def add_notification(self):
        try:
            company_id = self.company_id_input.currentData()
            branch_id = self.branch_id_input.currentData()
            recipient = self.recipient_input.text()
            message = self.message_input.text()
            notification_type = self.notification_type_input.currentText()
            status = self.status_input.currentText()

            if not company_id or not branch_id or not recipient or not message or not notification_type or not status:
                QMessageBox.warning(self, "Input Error", "Company, Branch, Recipient, Message, Type, and Status are required.")
                return

            # self.notifications_workflows_service.create_notification(
            #     company_id=company_id,
            #     branch_id=branch_id,
            #     recipient=recipient,
            #     message=message,
            #     notification_type=notification_type,
            #     status=status
            # )
            self.clear_form()
            self.load_notifications()
            QMessageBox.information(self, "Success", "Notification added successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.company_id_input.setCurrentIndex(0)
        self.branch_id_input.setCurrentIndex(0)
        self.recipient_input.clear()
        self.message_input.clear()
        self.notification_type_input.setCurrentIndex(0)
        self.status_input.setCurrentIndex(0)
