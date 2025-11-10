from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QFormLayout, QGroupBox, QHeaderView, QCheckBox
from PySide6.QtCore import QDate
from app.application.services import NotificationsWorkflowsService, CompanyService # Added CompanyService
#from app.infrastructure.database import get_db # No longer needed

class WorkflowWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notifications_workflows_service = NotificationsWorkflowsService()
        self.company_service = CompanyService() # Initialize CompanyService
        self.init_ui()
        self.load_workflows()

    def init_ui(self):
        self.setWindowTitle("Workflow Management")

        main_layout = QVBoxLayout(self)

        # Workflow form
        form_group_box = QGroupBox("Workflow Details")
        form_layout = QFormLayout()

        self.company_id_input = QComboBox()
        self.load_companies_to_combobox(self.company_id_input)
        form_layout.addRow(QLabel("Company:"), self.company_id_input)

        self.branch_id_input = QComboBox()
        self.load_branches_to_combobox(self.branch_id_input, self.company_id_input.currentData())
        form_layout.addRow(QLabel("Branch:"), self.branch_id_input)

        self.workflow_name_input = QLineEdit()
        self.workflow_name_input.setPlaceholderText("Workflow Name (e.g., Invoice Approval)")
        # Icon placeholder: self.workflow_name_input.addAction(QIcon("path/to/workflow_name_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Workflow Name:"), self.workflow_name_input)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Description")
        # Icon placeholder: self.description_input.addAction(QIcon("path/to/description_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Description:"), self.description_input)

        self.trigger_event_input = QLineEdit()
        self.trigger_event_input.setPlaceholderText("Trigger Event (e.g., Invoice Created)")
        # Icon placeholder: self.trigger_event_input.addAction(QIcon("path/to/trigger_event_icon.png"), QLineEdit.LeadingPosition)
        form_layout.addRow(QLabel("Trigger Event:"), self.trigger_event_input)

        self.status_input = QComboBox()
        self.status_input.addItems(["Active", "Inactive"])
        form_layout.addRow(QLabel("Status:"), self.status_input)

        add_button = QPushButton("Add Workflow")
        # Icon placeholder: add_button.setIcon(QIcon("path/to/add_icon.png"))
        add_button.clicked.connect(self.add_workflow)
        form_layout.addRow(add_button)

        form_group_box.setLayout(form_layout)
        main_layout.addWidget(form_group_box)

        # Workflow table
        self.workflows_table = QTableWidget()
        self.workflows_table.setColumnCount(7) # Increased column count
        self.workflows_table.setHorizontalHeaderLabels(["ID", "Company", "Branch", "Workflow Name", "Description", "Trigger Event", "Status"])
        self.workflows_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        main_layout.addWidget(self.workflows_table)

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

    def load_workflows(self):
        self.workflows_table.setRowCount(0)
        # Placeholder logic: In a real scenario, this would fetch actual workflow data.
        # For now, we'll use dummy data.
        dummy_data = [
            (1, 1, 1, "Invoice Approval", "Workflow for approving invoices", "Invoice Created", "Active"),
            (2, 1, 1, "Leave Request", "Workflow for employee leave requests", "Leave Request Submitted", "Active"),
        ]

        self.workflows_table.setRowCount(len(dummy_data))
        for row, (id, company_id, branch_id, name, description, trigger_event, status) in enumerate(dummy_data):
            company = self.company_service.get_company_by_id(company_id)
            company_name = company.name_en if company else "Unknown Company"
            branch = self.company_service.get_branch_by_id(branch_id)
            branch_name = branch.name_en if branch else "Unknown Branch"

            self.workflows_table.setItem(row, 0, QTableWidgetItem(str(id)))
            self.workflows_table.setItem(row, 1, QTableWidgetItem(company_name))
            self.workflows_table.setItem(row, 2, QTableWidgetItem(branch_name))
            self.workflows_table.setItem(row, 3, QTableWidgetItem(name))
            self.workflows_table.setItem(row, 4, QTableWidgetItem(description))
            self.workflows_table.setItem(row, 5, QTableWidgetItem(trigger_event))
            self.workflows_table.setItem(row, 6, QTableWidgetItem(status))

    def add_workflow(self):
        try:
            company_id = self.company_id_input.currentData()
            branch_id = self.branch_id_input.currentData()
            workflow_name = self.workflow_name_input.text()
            description = self.description_input.text()
            trigger_event = self.trigger_event_input.text()
            status = self.status_input.currentText()

            if not company_id or not branch_id or not workflow_name or not trigger_event or not status:
                QMessageBox.warning(self, "Input Error", "Company, Branch, Workflow Name, Trigger Event, and Status are required.")
                return

            # self.notifications_workflows_service.create_workflow(
            #     company_id=company_id,
            #     branch_id=branch_id,
            #     workflow_name=workflow_name,
            #     description=description,
            #     trigger_event=trigger_event,
            #     status=status
            # )
            self.clear_form()
            self.load_workflows()
            QMessageBox.information(self, "Success", "Workflow added successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_form(self):
        self.company_id_input.setCurrentIndex(0)
        self.branch_id_input.setCurrentIndex(0)
        self.workflow_name_input.clear()
        self.description_input.clear()
        self.trigger_event_input.clear()
        self.status_input.setCurrentIndex(0)
