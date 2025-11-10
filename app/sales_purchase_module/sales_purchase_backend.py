"""
Labeeb ERP - Sales & Purchase Backend
Backend logic for sales and purchase operations
"""

from PySide6.QtCore import QObject, Signal, Slot
from sqlalchemy.orm import joinedload
from sqlalchemy import func, and_, or_
from decimal import Decimal
from datetime import datetime, date
from typing import List, Dict, Optional

from app.infrastructure.database import get_session
from app.infrastructure.repositories import (
    InvoiceRepository, InvoiceLineRepository, StockMovementRepository,
    CustomerRepository, SupplierRepository, ItemRepository,
    InvoicePaymentRepository, SalesOrderRepository, PurchaseOrderRepository
)
from app.domain.models import (
    Invoice, InvoiceLine, StockMovement, Customer, Supplier, Item,
    InvoicePayment, SalesOrder, PurchaseOrder
)


class SalesPurchaseBackend(QObject):
    """Backend for sales and purchase operations"""
    
    # Signals
    sales_invoice_created = Signal(dict)
    purchase_invoice_created = Signal(dict)
    sales_order_created = Signal(dict)
    purchase_order_created = Signal(dict)
    invoice_updated = Signal(dict)
    invoice_deleted = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.services = {}
    
    def set_services(self, **services):
        """Set required services"""
        self.services = services
    
    # ==================== Sales Invoices ====================
    
    @Slot(dict, result=bool)
    def create_sales_invoice(self, invoice_data: dict) -> bool:
        """Create a new sales invoice"""
        try:
            with get_session() as db:
                invoice_repo = InvoiceRepository(db)
                stock_repo = StockMovementRepository(db)
                payment_repo = InvoicePaymentRepository(db)
                
                # Create invoice
                invoice = Invoice(
                    invoice_no=invoice_data['invoice_no'],
                    invoice_date=invoice_data['invoice_date'],
                    invoice_type=0,  # Sales
                    customer_id=invoice_data.get('customer_id'),
                    currency=invoice_data.get('currency', 'SAR'),
                    total_amount=Decimal(str(invoice_data['total'])),
                    discount_percentage=Decimal(str(invoice_data.get('discount', 0))),
                    charges=Decimal(str(invoice_data.get('charges', 0))),
                    memo=invoice_data.get('notes', ''),
                    company_id=invoice_data.get('company_id', 1),
                    branch_id=invoice_data.get('branch_id', 1),
                    warehouse_id=invoice_data.get('warehouse_id'),
                    created_by=invoice_data.get('user_id', 1)
                )
                
                # Add invoice lines
                for item_data in invoice_data['items']:
                    line = InvoiceLine(
                        item_id=item_data['item_id'],
                        quantity=Decimal(str(item_data['quantity'])),
                        unit_price=Decimal(str(item_data['price'])),
                        discount_percentage=Decimal(str(item_data.get('discount', 0))),
                        total_line_amount=Decimal(str(item_data['total'])),
                        memo=item_data.get('notes', '')
                    )
                    invoice.lines.append(line)
                    
                    # Create stock movement (out)
                    stock_movement = StockMovement(
                        item_id=item_data['item_id'],
                        movement_type=1,  # Out
                        quantity=Decimal(str(item_data['quantity'])),
                        movement_date=invoice_data['invoice_date'],
                        memo=f"Sales Invoice {invoice_data['invoice_no']}",
                        company_id=invoice_data.get('company_id', 1),
                        branch_id=invoice_data.get('branch_id', 1),
                        warehouse_id=invoice_data.get('warehouse_id')
                    )
                    stock_repo.create_stock_movement(stock_movement)
                
                # Save invoice
                created_invoice = invoice_repo.create_invoice(invoice)
                
                # Add payments
                if 'payments' in invoice_data:
                    for payment_data in invoice_data['payments']:
                        payment = InvoicePayment(
                            invoice_id=created_invoice.id,
                            payment_method_id=payment_data['payment_method_id'],
                            amount=Decimal(str(payment_data['amount'])),
                            transaction_details=payment_data.get('transaction_details')
                        )
                        payment_repo.create_invoice_payment(payment)
                
                db.commit()
                
                # Emit signal
                self.sales_invoice_created.emit(self._format_invoice(created_invoice))
                return True
                
        except Exception as e:
            print(f"Error creating sales invoice: {e}")
            return False
    
    @Slot(dict, result=bool)
    def update_sales_invoice(self, invoice_data: dict) -> bool:
        """Update existing sales invoice"""
        try:
            with get_session() as db:
                invoice_repo = InvoiceRepository(db)
                invoice = invoice_repo.get_invoice_by_id(invoice_data['id'])
                
                if not invoice:
                    return False
                
                # Update invoice fields
                invoice.customer_id = invoice_data.get('customer_id')
                invoice.total_amount = Decimal(str(invoice_data['total']))
                invoice.discount_percentage = Decimal(str(invoice_data.get('discount', 0)))
                invoice.memo = invoice_data.get('notes', '')
                
                # Update lines (simplified - in production, handle additions/deletions)
                # For now, we'll clear and recreate
                invoice.lines.clear()
                for item_data in invoice_data['items']:
                    line = InvoiceLine(
                        item_id=item_data['item_id'],
                        quantity=Decimal(str(item_data['quantity'])),
                        unit_price=Decimal(str(item_data['price'])),
                        total_line_amount=Decimal(str(item_data['total']))
                    )
                    invoice.lines.append(line)
                
                db.commit()
                self.invoice_updated.emit(self._format_invoice(invoice))
                return True
                
        except Exception as e:
            print(f"Error updating sales invoice: {e}")
            return False
    
    @Slot(int, result=bool)
    def delete_sales_invoice(self, invoice_id: int) -> bool:
        """Delete sales invoice"""
        try:
            with get_session() as db:
                invoice_repo = InvoiceRepository(db)
                invoice_repo.delete_invoice(invoice_id)
                db.commit()
                self.invoice_deleted.emit(invoice_id)
                return True
        except Exception as e:
            print(f"Error deleting invoice: {e}")
            return False
    
    @Slot(result=list)
    def get_all_sales_invoices(self) -> List[Dict]:
        """Get all sales invoices"""
        try:
            with get_session() as db:
                invoice_repo = InvoiceRepository(db)
                invoices = db.query(Invoice).options(
                    joinedload(Invoice.customer),
                    joinedload(Invoice.lines).joinedload(InvoiceLine.item),
                    joinedload(Invoice.payments)
                ).filter(Invoice.invoice_type == 0).order_by(Invoice.invoice_date.desc()).all()
                
                return [self._format_invoice(inv) for inv in invoices]
        except Exception as e:
            print(f"Error getting sales invoices: {e}")
            return []
    
    @Slot(int, result=dict)
    def get_sales_invoice_by_id(self, invoice_id: int) -> Optional[Dict]:
        """Get sales invoice by ID"""
        try:
            with get_session() as db:
                invoice = db.query(Invoice).options(
                    joinedload(Invoice.customer),
                    joinedload(Invoice.lines).joinedload(InvoiceLine.item),
                    joinedload(Invoice.payments).joinedload(InvoicePayment.payment_method)
                ).filter(Invoice.id == invoice_id, Invoice.invoice_type == 0).first()
                
                return self._format_invoice(invoice) if invoice else None
        except Exception as e:
            print(f"Error getting invoice: {e}")
            return None
    
    # ==================== Purchase Invoices ====================
    
    @Slot(dict, result=bool)
    def create_purchase_invoice(self, invoice_data: dict) -> bool:
        """Create a new purchase invoice"""
        try:
            with get_session() as db:
                invoice_repo = InvoiceRepository(db)
                stock_repo = StockMovementRepository(db)
                payment_repo = InvoicePaymentRepository(db)
                
                # Create invoice
                invoice = Invoice(
                    invoice_no=invoice_data['invoice_no'],
                    invoice_date=invoice_data['invoice_date'],
                    invoice_type=2,  # Purchase
                    supplier_id=invoice_data.get('supplier_id'),
                    currency=invoice_data.get('currency', 'SAR'),
                    total_amount=Decimal(str(invoice_data['total'])),
                    discount_percentage=Decimal(str(invoice_data.get('discount', 0))),
                    charges=Decimal(str(invoice_data.get('charges', 0))),
                    memo=invoice_data.get('notes', ''),
                    company_id=invoice_data.get('company_id', 1),
                    branch_id=invoice_data.get('branch_id', 1),
                    warehouse_id=invoice_data.get('warehouse_id'),
                    created_by=invoice_data.get('user_id', 1)
                )
                
                # Add invoice lines
                for item_data in invoice_data['items']:
                    line = InvoiceLine(
                        item_id=item_data['item_id'],
                        quantity=Decimal(str(item_data['quantity'])),
                        unit_price=Decimal(str(item_data['price'])),
                        discount_percentage=Decimal(str(item_data.get('discount', 0))),
                        total_line_amount=Decimal(str(item_data['total'])),
                        memo=item_data.get('notes', '')
                    )
                    invoice.lines.append(line)
                    
                    # Create stock movement (in)
                    stock_movement = StockMovement(
                        item_id=item_data['item_id'],
                        movement_type=0,  # In
                        quantity=Decimal(str(item_data['quantity'])),
                        movement_date=invoice_data['invoice_date'],
                        memo=f"Purchase Invoice {invoice_data['invoice_no']}",
                        company_id=invoice_data.get('company_id', 1),
                        branch_id=invoice_data.get('branch_id', 1),
                        warehouse_id=invoice_data.get('warehouse_id')
                    )
                    stock_repo.create_stock_movement(stock_movement)
                
                # Save invoice
                created_invoice = invoice_repo.create_invoice(invoice)
                
                # Add payments
                if 'payments' in invoice_data:
                    for payment_data in invoice_data['payments']:
                        payment = InvoicePayment(
                            invoice_id=created_invoice.id,
                            payment_method_id=payment_data['payment_method_id'],
                            amount=Decimal(str(payment_data['amount'])),
                            transaction_details=payment_data.get('transaction_details')
                        )
                        payment_repo.create_invoice_payment(payment)
                
                db.commit()
                
                # Emit signal
                self.purchase_invoice_created.emit(self._format_invoice(created_invoice))
                return True
                
        except Exception as e:
            print(f"Error creating purchase invoice: {e}")
            return False
    
    @Slot(result=list)
    def get_all_purchase_invoices(self) -> List[Dict]:
        """Get all purchase invoices"""
        try:
            with get_session() as db:
                invoices = db.query(Invoice).options(
                    joinedload(Invoice.supplier),
                    joinedload(Invoice.lines).joinedload(InvoiceLine.item),
                    joinedload(Invoice.payments)
                ).filter(Invoice.invoice_type == 2).order_by(Invoice.invoice_date.desc()).all()
                
                return [self._format_invoice(inv) for inv in invoices]
        except Exception as e:
            print(f"Error getting purchase invoices: {e}")
            return []
    
    # ==================== Helper Methods ====================
    
    def _format_invoice(self, invoice: Invoice) -> Dict:
        """Format invoice for display"""
        if not invoice:
            return {}
        
        customer_name = ""
        if invoice.customer:
            customer_name = invoice.customer.name_ar or invoice.customer.name_en
        elif invoice.supplier:
            customer_name = invoice.supplier.name_ar or invoice.supplier.name_en
        
        items = []
        for line in invoice.lines:
            item_name = line.item.name_ar if line.item else "Unknown"
            items.append({
                'item_id': line.item_id,
                'item_name': item_name,
                'quantity': float(line.quantity),
                'price': float(line.unit_price),
                'discount': float(line.discount_percentage),
                'total': float(line.total_line_amount),
                'notes': line.memo
            })
        
        payments = []
        for payment in invoice.payments:
            payment_method_name = payment.payment_method.name_ar if payment.payment_method else "Unknown"
            payments.append({
                'payment_method_id': payment.payment_method_id,
                'payment_method_name': payment_method_name,
                'amount': float(payment.amount),
                'transaction_details': payment.transaction_details
            })
        
        return {
            'id': invoice.id,
            'invoice_no': invoice.invoice_no,
            'invoice_date': invoice.invoice_date.strftime('%Y-%m-%d'),
            'invoice_type': invoice.invoice_type,
            'customer_id': invoice.customer_id,
            'supplier_id': invoice.supplier_id,
            'customer_name': customer_name,
            'currency': invoice.currency,
            'subtotal': float(sum(line.total_line_amount for line in invoice.lines)),
            'discount': float(invoice.discount_percentage),
            'charges': float(invoice.charges),
            'total': float(invoice.total_amount),
            'notes': invoice.memo,
            'items': items,
            'payments': payments,
            'branch_id': invoice.branch_id,
            'warehouse_id': invoice.warehouse_id
        }
    
    @Slot(str, result=str)
    def generate_invoice_number(self, invoice_type: str) -> str:
        """Generate next invoice number"""
        prefix = "SI" if invoice_type == "sales" else "PI"
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{prefix}-{timestamp}"
