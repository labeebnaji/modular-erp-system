"""
Complete Notifications and Workflows Management System
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                               QTableWidget, QTableWidgetItem, QPushButton, QLabel,
                               QLineEdit, QComboBox, QMessageBox, QGroupBox, 
                               QFormLayout, QHeaderView, QTextEdit, QCheckBox)
from PySide6.QtCore import Qt, QDate, QTimer
from datetime import datetime

from app.application.services import NotificationsWorkflowsService, IAMService, CompanyService
from app.ui.styles import BUTTON_STYLE, TABLE_STYLE, GROUPBOX_STYLE
from app.i18n.translations import tr


class NotificationsWidget(QWidget):
    """Widget for managing notifications"""
    
    def __init__(self, notifications_workflows_service, iam_service, company_service, parent=None):
        super().__init__(parent)
        self.notifications_workflows_service = notifications_workflows_service
        self.iam_service = iam_service
        self.company_service = company_service
        self.init_ui()
        self.load_notifications()
        
        # Auto-refresh every 30 seconds
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_notifications)
        self.refresh_timer.start(30000)  # 30 seconds
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Filter section
        filter_layout = QHBoxLayout()
        
        self.user_combo = QComboBox()
        self.load_users()
        filter_layout.addWidget(QLabel("User:"))
        filter_layout.addWidget(self.user_combo)
        
        self.status_combo = QComboBox()
        self.status_combo.addItem("All", None)
        self.status_combo.addItem("Unread", False)
        self.status_combo.addItem("Read", True)
        filter_layout.addWidget(QLabel(tr('common.status') + ":"))
        filter_layout.addWidget(self.status_combo)
        
        self.refresh_button = QPushButton(tr('common.refresh'))
        self.refresh_button.setStyleSheet(BUTTON_STYLE)
        self.refresh_button.clicked.connect(self.load_notifications)
        filter_layout.addWidget(self.refresh_button)
        
        self.mark_read_button = QPushButton("Mark as Read")
        self.mark_read_button.setStyleSheet(BUTTON_STYLE)
        self.mark_read_button.clicked.connect(self.mark_as_read)
        filter_layout.addWidget(self.mark_read_button)
        
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)
        
        # Notifications table
        self.notifications_table = QTableWidget()
        self.notifications_table.setColumnCount(6)
        self.notifications_table.setHorizontalHeaderLabels([
            "ID", "User", "Message", "Status", "Created At", "Action"
        ])
        self.notifications_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.notifications_table.setStyleSheet(TABLE_STYLE)
        self.notifications_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.notifications_table)
        
        # Create notification section
        create_group = QGroupBox("Create Notification")
        create_group.setStyleSheet(GROUPBOX_STYLE)
        create_layout = QFormLayout()
        
        self.target_user_combo = QComboBox()
        self.load_users_for_create()
        create_layout.addRow(QLabel("Target User:"), self.target_user_combo)
        
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(100)
        self.message_input.setPlaceholderText("Enter notification message...")
        create_layout.addRow(QLabel("Message:"), self.message_input)
        
        self.send_button = QPushButton("Send Notification")
        self.send_button.setStyleSheet(BUTTON_STYLE)
        self.send_button.clicked.connect(self.send_notification)
        create_layout.addRow(self.send_button)
        
        create_group.setLayout(create_layout)
        main_layout.addWidget(create_group)
    
    def load_users(self):
        """Load all users for filter"""
        self.user_combo.clear()
        self.user_combo.addItem("All Users", None)
        users = self.iam_service.get_all_users()
        for user in users:
            self.user_combo.addItem(user.username, user.id)
    
    def load_users_for_create(self):
        """Load all users for notification creation"""
        self.target_user_combo.clear()
        users = self.iam_service.get_all_users()
        for user in users:
            self.target_user_combo.addItem(user.username, user.id)
    
    def load_notifications(self):
        """Load all notifications"""
        self.notifications_table.setRowCount(0)
        
        user_id = self.user_combo.currentData()
        is_read = self.status_combo.currentData()
        
        # Get all notifications
        notifications = self.notifications_workflows_service.get_all_notifications()
        
        # Filter
        filtered = []
        for notif in notifications:
            if user_id and notif.user_id != user_id:
                continue
            if is_read is not None and notif.is_read != is_read:
                continue
            filtered.append(notif)
        
        self.notifications_table.setRowCount(len(filtered))
        for row, notif in enumerate(filtered):
            user = self.iam_service.get_user_by_id(notif.user_id)
            username = user.username if user else "Unknown"
            
            status = "Read" if notif.is_read else "Unread"
            
            self.notifications_table.setItem(row, 0, QTableWidgetItem(str(notif.id)))
            self.notifications_table.setItem(row, 1, QTableWidgetItem(username))
            self.notifications_table.setItem(row, 2, QTableWidgetItem(notif.message))
            self.notifications_table.setItem(row, 3, QTableWidgetItem(status))
            self.notifications_table.setItem(row, 4, QTableWidgetItem(str(notif.created_at)))
            
            # Delete button
            delete_btn = QPushButton(tr('common.delete'))
            delete_btn.setStyleSheet(BUTTON_STYLE)
            delete_btn.clicked.connect(lambda checked, nid=notif.id: self.delete_notification(nid))
            self.notifications_table.setCellWidget(row, 5, delete_btn)
    
    def mark_as_read(self):
        """Mark selected notifications as read"""
        selected_rows = self.notifications_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, tr('common.warning'), "Please select notifications to mark as read")
            return
        
        for index in selected_rows:
            notif_id = int(self.notifications_table.item(index.row(), 0).text())
            try:
                self.notifications_workflows_service.mark_notification_as_read(notif_id)
            except Exception as e:
                print(f"Error marking notification {notif_id} as read: {e}")
        
        QMessageBox.information(self, tr('common.success'), "Notifications marked as read")
        self.load_notifications()
    
    def send_notification(self):
        """Send new notification"""
        user_id = self.target_user_combo.currentData()
        message = self.message_input.toPlainText().strip()
        
        if not user_id or not message:
            QMessageBox.warning(self, tr('common.warning'), "Please select user and enter message")
            return
        
        try:
            user = self.iam_service.get_user_by_id(user_id)
            company_id = user.company_id if user else 1
            
            self.notifications_workflows_service.create_notification(
                user_id=user_id,
                company_id=company_id,
                message=message
            )
            
            QMessageBox.information(self, tr('common.success'), "Notification sent successfully")
            self.message_input.clear()
            self.load_notifications()
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error: {str(e)}")
    
    def delete_notification(self, notif_id):
        """Delete notification"""
        reply = QMessageBox.question(self, tr('common.confirm'), 
                                    tr('messages.confirm_delete'),
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.notifications_workflows_service.delete_notification(notif_id)
                QMessageBox.information(self, tr('common.success'), tr('messages.delete_success'))
                self.load_notifications()
            except Exception as e:
                QMessageBox.critical(self, tr('common.error'), f"Error: {str(e)}")


class WorkflowsWidget(QWidget):
    """Widget for managing workflows"""
    
    def __init__(self, notifications_workflows_service, company_service, parent=None):
        super().__init__(parent)
        self.notifications_workflows_service = notifications_workflows_service
        self.company_service = company_service
        self.selected_workflow_id = None
        self.init_ui()
        self.load_workflows()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Workflow Form
        form_group = QGroupBox("Workflow Details")
        form_group.setStyleSheet(GROUPBOX_STYLE)
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Workflow Name")
        form_layout.addRow(QLabel(tr('common.name') + ":"), self.name_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("Workflow Description")
        form_layout.addRow(QLabel(tr('common.description') + ":"), self.description_input)
        
        self.trigger_event_combo = QComboBox()
        self.trigger_event_combo.addItem("Invoice Created", "InvoiceCreated")
        self.trigger_event_combo.addItem("Payment Received", "PaymentReceived")
        self.trigger_event_combo.addItem("Order Confirmed", "OrderConfirmed")
        self.trigger_event_combo.addItem("Stock Low", "StockLow")
        self.trigger_event_combo.addItem("Employee Hired", "EmployeeHired")
        form_layout.addRow(QLabel("Trigger Event:"), self.trigger_event_combo)
        
        self.actions_input = QTextEdit()
        self.actions_input.setMaximumHeight(100)
        self.actions_input.setPlaceholderText("Actions (JSON format)\nExample: {\"action\": \"send_email\", \"to\": \"admin@company.com\"}")
        form_layout.addRow(QLabel("Actions:"), self.actions_input)
        
        self.is_active_checkbox = QCheckBox(tr('common.active'))
        self.is_active_checkbox.setChecked(True)
        form_layout.addRow(QLabel(tr('common.status') + ":"), self.is_active_checkbox)
        
        self.company_combo = QComboBox()
        self.load_companies()
        form_layout.addRow(QLabel("Company:"), self.company_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton(tr('common.save'))
        self.save_button.setStyleSheet(BUTTON_STYLE)
        self.save_button.clicked.connect(self.save_workflow)
        
        self.new_button = QPushButton(tr('common.new'))
        self.new_button.setStyleSheet(BUTTON_STYLE)
        self.new_button.clicked.connect(self.clear_form)
        
        self.delete_button = QPushButton(tr('common.delete'))
        self.delete_button.setStyleSheet(BUTTON_STYLE)
        self.delete_button.clicked.connect(self.delete_workflow)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        
        form_layout.addRow(button_layout)
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        # Workflows Table
        self.workflows_table = QTableWidget()
        self.workflows_table.setColumnCount(6)
        self.workflows_table.setHorizontalHeaderLabels([
            "ID", tr('common.name'), "Trigger Event", 
            tr('common.description'), tr('common.status'), "Company"
        ])
        self.workflows_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.workflows_table.setStyleSheet(TABLE_STYLE)
        self.workflows_table.setAlternatingRowColors(True)
        self.workflows_table.cellClicked.connect(self.load_workflow_details)
        
        main_layout.addWidget(self.workflows_table)
    
    def load_companies(self):
        """Load all companies"""
        self.company_combo.clear()
        companies = self.company_service.get_all_companies()
        for company in companies:
            self.company_combo.addItem(f"{company.name_en} ({company.code})", company.id)
    
    def load_workflows(self):
        """Load all workflows"""
        self.workflows_table.setRowCount(0)
        workflows = self.notifications_workflows_service.get_all_workflows()
        
        self.workflows_table.setRowCount(len(workflows))
        for row, workflow in enumerate(workflows):
            company = self.company_service.get_company_by_id(workflow.company_id)
            company_name = company.name_en if company else "Unknown"
            
            status = tr('common.active') if workflow.is_active else tr('common.inactive')
            
            self.workflows_table.setItem(row, 0, QTableWidgetItem(str(workflow.id)))
            self.workflows_table.setItem(row, 1, QTableWidgetItem(workflow.name))
            self.workflows_table.setItem(row, 2, QTableWidgetItem(workflow.trigger_event))
            self.workflows_table.setItem(row, 3, QTableWidgetItem(workflow.description or ""))
            self.workflows_table.setItem(row, 4, QTableWidgetItem(status))
            self.workflows_table.setItem(row, 5, QTableWidgetItem(company_name))
    
    def load_workflow_details(self, row, col):
        """Load workflow details when clicked"""
        workflow_id = int(self.workflows_table.item(row, 0).text())
        workflow = self.notifications_workflows_service.get_workflow_by_id(workflow_id)
        
        if workflow:
            self.selected_workflow_id = workflow.id
            self.name_input.setText(workflow.name)
            self.description_input.setPlainText(workflow.description or "")
            
            # Set trigger event
            index = self.trigger_event_combo.findData(workflow.trigger_event)
            if index >= 0:
                self.trigger_event_combo.setCurrentIndex(index)
            
            self.actions_input.setPlainText(workflow.actions or "")
            self.is_active_checkbox.setChecked(workflow.is_active)
            
            # Set company
            comp_index = self.company_combo.findData(workflow.company_id)
            if comp_index >= 0:
                self.company_combo.setCurrentIndex(comp_index)
    
    def save_workflow(self):
        """Save workflow"""
        name = self.name_input.text().strip()
        description = self.description_input.toPlainText().strip()
        trigger_event = self.trigger_event_combo.currentData()
        actions = self.actions_input.toPlainText().strip()
        is_active = self.is_active_checkbox.isChecked()
        company_id = self.company_combo.currentData()
        
        if not name or not trigger_event:
            QMessageBox.warning(self, tr('common.warning'), "Please enter workflow name and select trigger event")
            return
        
        try:
            if self.selected_workflow_id:
                # Update existing workflow
                self.notifications_workflows_service.update_workflow(
                    self.selected_workflow_id,
                    name=name,
                    description=description,
                    trigger_event=trigger_event,
                    actions=actions,
                    is_active=is_active
                )
                QMessageBox.information(self, tr('common.success'), tr('messages.update_success'))
            else:
                # Create new workflow
                self.notifications_workflows_service.create_workflow(
                    company_id=company_id,
                    name=name,
                    description=description,
                    trigger_event=trigger_event,
                    actions=actions,
                    is_active=is_active,
                    created_by=1
                )
                QMessageBox.information(self, tr('common.success'), tr('messages.save_success'))
            
            self.clear_form()
            self.load_workflows()
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error: {str(e)}")
    
    def delete_workflow(self):
        """Delete selected workflow"""
        if not self.selected_workflow_id:
            QMessageBox.warning(self, tr('common.warning'), "Please select a workflow to delete")
            return
        
        reply = QMessageBox.question(self, tr('common.confirm'), 
                                    tr('messages.confirm_delete'),
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.notifications_workflows_service.delete_workflow(self.selected_workflow_id)
                QMessageBox.information(self, tr('common.success'), tr('messages.delete_success'))
                self.clear_form()
                self.load_workflows()
            except Exception as e:
                QMessageBox.critical(self, tr('common.error'), f"Error: {str(e)}")
    
    def clear_form(self):
        """Clear all form fields"""
        self.selected_workflow_id = None
        self.name_input.clear()
        self.description_input.clear()
        self.trigger_event_combo.setCurrentIndex(0)
        self.actions_input.clear()
        self.is_active_checkbox.setChecked(True)
        self.company_combo.setCurrentIndex(0)


class NotificationsWorkflowsManagementWidget(QWidget):
    """Main notifications and workflows management widget with tabs"""
    
    def __init__(self, notifications_workflows_service, iam_service, company_service, parent=None):
        super().__init__(parent)
        self.notifications_workflows_service = notifications_workflows_service
        self.iam_service = iam_service
        self.company_service = company_service
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Notifications & Workflows Management")
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.notifications_widget = NotificationsWidget(
            self.notifications_workflows_service,
            self.iam_service,
            self.company_service
        )
        self.workflows_widget = WorkflowsWidget(
            self.notifications_workflows_service,
            self.company_service
        )
        
        self.tab_widget.addTab(self.notifications_widget, "Notifications")
        self.tab_widget.addTab(self.workflows_widget, "Workflows")
        
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
