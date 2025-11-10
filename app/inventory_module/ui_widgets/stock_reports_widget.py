"""
Labeeb ERP - Stock Reports Widget
واجهة تقارير المخزون
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QDateEdit, QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QMessageBox, QHeaderView, QTextEdit, QComboBox
)
from PySide6.QtCore import Qt, QDate

from app.ui.base_widget import TranslatableWidget
from app.i18n.translations import tr


class StockReportsWidget(TranslatableWidget):
    """واجهة تقارير المخزون"""
    
    def __init__(self, backend, inventory_service, parent=None):
        super().__init__(parent)
        
        self.backend = backend
        self.inventory_service = inventory_service
        
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        filter_group = QGroupBox(tr('inventory.report_filters'))
        filter_layout = QFormLayout()
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            tr('inventory.stock_summary'),
            tr('inventory.stock_movements_report'),
            tr('inventory.low_stock_report'),
            tr('inventory.stock_valuation')
        ])
        filter_layout.addRow(tr('common.type') + ":", self.report_type_combo)
        
        self.from_date_input = QDateEdit(QDate.currentDate().addMonths(-1))
        self.from_date_input.setCalendarPopup(True)
        filter_layout.addRow(tr('common.from_date') + ":", self.from_date_input)
        
        self.to_date_input = QDateEdit(QDate.currentDate())
        self.to_date_input.setCalendarPopup(True)
        filter_layout.addRow(tr('common.to_date') + ":", self.to_date_input)
        
        button_layout = QHBoxLayout()
        
        self.generate_button = QPushButton(tr('common.generate'))
        self.generate_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;")
        self.generate_button.clicked.connect(self.generate_report)
        
        self.export_button = QPushButton(tr('common.export'))
        self.export_button.setStyleSheet("background-color: #2196F3; color: white; padding: 10px;")
        self.export_button.clicked.connect(self.export_report)
        
        self.print_button = QPushButton(tr('common.print'))
        self.print_button.setStyleSheet("background-color: #FF9800; color: white; padding: 10px;")
        self.print_button.clicked.connect(self.print_report)
        
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.print_button)
        filter_layout.addRow(button_layout)
        
        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group)
        
        report_group = QGroupBox(tr('inventory.report_results'))
        report_layout = QVBoxLayout()
        
        self.report_table = QTableWidget()
        self.report_table.setAlternatingRowColors(True)
        report_layout.addWidget(self.report_table)
        
        self.summary_text = QTextEdit()
        self.summary_text.setMaximumHeight(100)
        self.summary_text.setReadOnly(True)
        report_layout.addWidget(self.summary_text)
        
        report_group.setLayout(report_layout)
        main_layout.addWidget(report_group)
    
    def generate_report(self):
        try:
            report_type = self.report_type_combo.currentIndex()
            from_date = self.from_date_input.date().toString("yyyy-MM-dd")
            to_date = self.to_date_input.date().toString("yyyy-MM-dd")
            
            if report_type == 0:
                self.generate_stock_summary()
            elif report_type == 1:
                self.generate_movements_report(from_date, to_date)
            elif report_type == 2:
                self.generate_low_stock_report()
            elif report_type == 3:
                self.generate_valuation_report()
                
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error generating report: {str(e)}")
    
    def generate_stock_summary(self):
        try:
            self.report_table.clear()
            self.report_table.setColumnCount(5)
            self.report_table.setHorizontalHeaderLabels([
                tr('common.code'),
                tr('common.name'),
                tr('common.quantity'),
                tr('inventory.reorder_level'),
                tr('common.status')
            ])
            self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            stock_levels = self.backend.get_all_stock_levels()
            self.report_table.setRowCount(len(stock_levels))
            
            total_items = len(stock_levels)
            low_stock = sum(1 for s in stock_levels if s.get('needs_reorder', False))
            
            for row, stock in enumerate(stock_levels):
                item = self.inventory_service.get_item_by_id(stock['item_id'])
                if not item:
                    continue
                
                self.report_table.setItem(row, 0, QTableWidgetItem(str(item.code)))
                self.report_table.setItem(row, 1, QTableWidgetItem(stock['item_name']))
                self.report_table.setItem(row, 2, QTableWidgetItem(f"{stock['current_stock']:.2f}"))
                self.report_table.setItem(row, 3, QTableWidgetItem(f"{stock['reorder_level']:.2f}"))
                
                status = tr('inventory.in_stock') if not stock['needs_reorder'] else tr('inventory.low_stock')
                self.report_table.setItem(row, 4, QTableWidgetItem(status))
            
            summary = f"""
{tr('inventory.stock_summary_report')}
{tr('inventory.total_items')}: {total_items}
{tr('inventory.low_stock_items')}: {low_stock}
            """
            self.summary_text.setPlainText(summary.strip())
            
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error: {str(e)}")
    
    def generate_movements_report(self, from_date, to_date):
        try:
            report_data = self.backend.get_stock_report(from_date, to_date)
            
            self.report_table.clear()
            self.report_table.setColumnCount(6)
            self.report_table.setHorizontalHeaderLabels([
                tr('common.name'),
                tr('common.type'),
                tr('common.quantity'),
                tr('common.date'),
                tr('common.code'),
                tr('common.description')
            ])
            self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            movements = self.backend.get_all_stock_movements()
            filtered_movements = [
                m for m in movements 
                if from_date <= m['movement_date'] <= to_date
            ]
            
            self.report_table.setRowCount(len(filtered_movements))
            
            for row, movement in enumerate(filtered_movements):
                self.report_table.setItem(row, 0, QTableWidgetItem(movement['item_name']))
                self.report_table.setItem(row, 1, QTableWidgetItem(movement['movement_type_name']))
                self.report_table.setItem(row, 2, QTableWidgetItem(f"{movement['quantity']:.2f}"))
                self.report_table.setItem(row, 3, QTableWidgetItem(movement['movement_date']))
                self.report_table.setItem(row, 4, QTableWidgetItem(movement['ref_no'] or ""))
                self.report_table.setItem(row, 5, QTableWidgetItem(movement['memo'] or ""))
            
            summary = f"""
{tr('inventory.stock_movements_report')}
{tr('common.from_date')}: {from_date}
{tr('common.to_date')}: {to_date}
{tr('inventory.total_movements')}: {report_data.get('total_movements', 0)}
{tr('inventory.total_in')}: {report_data.get('total_in', 0):.2f}
{tr('inventory.total_out')}: {report_data.get('total_out', 0):.2f}
{tr('inventory.net_change')}: {report_data.get('net_change', 0):.2f}
            """
            self.summary_text.setPlainText(summary.strip())
            
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error: {str(e)}")
    
    def generate_low_stock_report(self):
        try:
            self.report_table.clear()
            self.report_table.setColumnCount(4)
            self.report_table.setHorizontalHeaderLabels([
                tr('common.code'),
                tr('common.name'),
                tr('common.quantity'),
                tr('inventory.reorder_level')
            ])
            self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            low_stock_items = self.backend.get_low_stock_items()
            self.report_table.setRowCount(len(low_stock_items))
            
            for row, stock in enumerate(low_stock_items):
                item = self.inventory_service.get_item_by_id(stock['item_id'])
                if not item:
                    continue
                
                self.report_table.setItem(row, 0, QTableWidgetItem(str(item.code)))
                self.report_table.setItem(row, 1, QTableWidgetItem(stock['item_name']))
                self.report_table.setItem(row, 2, QTableWidgetItem(f"{stock['current_stock']:.2f}"))
                self.report_table.setItem(row, 3, QTableWidgetItem(f"{stock['reorder_level']:.2f}"))
            
            summary = f"""
{tr('inventory.low_stock_report')}
{tr('inventory.items_need_reorder')}: {len(low_stock_items)}
            """
            self.summary_text.setPlainText(summary.strip())
            
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error: {str(e)}")
    
    def generate_valuation_report(self):
        try:
            self.report_table.clear()
            self.report_table.setColumnCount(5)
            self.report_table.setHorizontalHeaderLabels([
                tr('common.code'),
                tr('common.name'),
                tr('common.quantity'),
                tr('common.price'),
                tr('inventory.total_value')
            ])
            self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            stock_levels = self.backend.get_all_stock_levels()
            self.report_table.setRowCount(len(stock_levels))
            
            total_value = 0
            
            for row, stock in enumerate(stock_levels):
                item = self.inventory_service.get_item_by_id(stock['item_id'])
                if not item:
                    continue
                
                quantity = stock['current_stock']
                price = float(item.cost_price)
                value = quantity * price
                total_value += value
                
                self.report_table.setItem(row, 0, QTableWidgetItem(str(item.code)))
                self.report_table.setItem(row, 1, QTableWidgetItem(stock['item_name']))
                self.report_table.setItem(row, 2, QTableWidgetItem(f"{quantity:.2f}"))
                self.report_table.setItem(row, 3, QTableWidgetItem(f"{price:.2f}"))
                self.report_table.setItem(row, 4, QTableWidgetItem(f"{value:.2f}"))
            
            summary = f"""
{tr('inventory.stock_valuation_report')}
{tr('inventory.total_items')}: {len(stock_levels)}
{tr('inventory.total_stock_value')}: {total_value:.2f}
            """
            self.summary_text.setPlainText(summary.strip())
            
        except Exception as e:
            QMessageBox.critical(self, tr('common.error'), f"Error: {str(e)}")
    
    def export_report(self):
        QMessageBox.information(self, tr('common.info'), tr('common.feature_coming_soon'))
    
    def print_report(self):
        QMessageBox.information(self, tr('common.info'), tr('common.feature_coming_soon'))
    
    def refresh_data(self):
        self.generate_report()
    
    def refresh_translations(self):
        super().refresh_translations()
