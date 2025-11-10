from sqlalchemy.orm import Session
from app.infrastructure.repositories import AccountRepository, JournalEntryRepository, JournalLineRepository, CustomerRepository, SupplierRepository, InvoiceRepository, PaymentRepository, ItemRepository, StockMovementRepository, SalesOrderRepository, PurchaseOrderRepository, BankTransactionRepository, BankReconciliationRepository, FixedAssetRepository, DepreciationRepository, TaxSettingRepository, TaxReportRepository, UserRepository, RoleRepository, PermissionRepository, CompanyRepository, BranchRepository, FiscalPeriodRepository, CostCenterRepository, ProjectRepository, EmployeeRepository, PayrunRepository, NotificationRepository, WorkflowRepository, UnitRepository, CurrencyRepository, PaymentMethodRepository, WarehouseRepository, CouponRepository, ShiftRepository, ShiftMovementRepository, GiftCardRepository, LoyaltyProgramRepository # Added new repositories and GiftCardRepository, LoyaltyProgramRepository
from app.domain import models # Import models module as a whole
from app.domain.settings_models import Unit, Currency, PaymentMethod, GiftCard, LoyaltyProgram # Import new settings models and GiftCard and LoyaltyProgram
from datetime import date, datetime
from decimal import Decimal
from app.infrastructure.database import get_session
from sqlalchemy.exc import IntegrityError # Import IntegrityError
from sqlalchemy import func # Import func for max()

# For password hashing
from werkzeug.security import generate_password_hash, check_password_hash

class AccountService:
    def __init__(self):
        pass

    def get_all_accounts(self):
        with get_session() as db:
            return AccountRepository(db).get_all_accounts()

    def get_account_by_id(self, account_id: int):
        with get_session() as db:
            return AccountRepository(db).get_account_by_id(account_id)

    def create_account(self, code: str, name_ar: str, name_en: str, type: int, level: int, parent_id: int, currency: str, is_postable: bool, is_active: bool):
        with get_session() as db:
            account = models.Account(
                code=code,
                name_ar=name_ar,
                name_en=name_en,
                type=type,
                level=level,
                parent_id=parent_id,
                currency=currency,
                is_postable=is_postable,
                is_active=is_active
            )
            return AccountRepository(db).create_account(account)

    def update_account(self, account_id: int, **kwargs):
        with get_session() as db:
            return AccountRepository(db).update_account(account_id, kwargs)

    def delete_account(self, account_id: int):
        with get_session() as db:
            return AccountRepository(db).delete_account(account_id)

class JournalService:
    def __init__(self):
        pass

    def get_all_journal_entries(self):
        with get_session() as db:
            return JournalEntryRepository(db).get_all_journal_entries()

    def get_journal_entry_with_lines(self, entry_id: int):
        with get_session() as db:
            journal_entry_repo = JournalEntryRepository(db)
            journal_line_repo = JournalLineRepository(db)
            journal_entry = journal_entry_repo.get_journal_entry_by_id(entry_id)
            if journal_entry:
                journal_entry.lines = journal_line_repo.get_lines_by_entry_id(entry_id)
            return journal_entry

    def create_journal_entry(self, company_id: int, branch_id: int, entry_date: date, period: str, ref_no: str, created_by: int, lines_data: list):
        with get_session() as db:
            journal_entry_repo = JournalEntryRepository(db)
            journal_line_repo = JournalLineRepository(db)
            account_repo = AccountRepository(db)

            total_debit = Decimal(0)
            total_credit = Decimal(0)

            for line in lines_data:
                total_debit += Decimal(line.get('debit', 0))
                total_credit += Decimal(line.get('credit', 0))

            if total_debit != total_credit:
                raise ValueError("Debit and Credit totals must be equal.")

            journal_entry = models.JournalEntry(
                company_id=company_id,
                branch_id=branch_id,
                date=entry_date,
                period=period,
                ref_no=ref_no,
                created_by=created_by,
                status=0 # Draft
            )
            created_entry = journal_entry_repo.create_journal_entry(journal_entry)

            for line_data in lines_data:
                account = account_repo.get_account_by_id(line_data['account_id'])
                if not account:
                    raise ValueError(f"Account with ID {line_data['account_id']} not found.")

                journal_line = models.JournalLine(
                    entry_id=created_entry.id,
                    account_id=line_data['account_id'],
                    debit=Decimal(line_data.get('debit', 0)),
                    credit=Decimal(line_data.get('credit', 0)),
                    currency=line_data.get('currency', 'USD'), # Default currency for now
                    fx_rate=Decimal(line_data.get('fx_rate', 1)),
                    cost_center_id=line_data.get('cost_center_id'),
                    project_id=line_data.get('project_id'),
                    memo=line_data.get('memo')
                )
                journal_line_repo.create_journal_line(journal_line)

            return created_entry

    def update_journal_entry(self, entry_id: int, **kwargs):
        with get_session() as db:
            return JournalEntryRepository(db).update_journal_entry(entry_id, kwargs)

    def approve_journal_entry(self, entry_id: int, approved_by: int):
        with get_session() as db:
            return JournalEntryRepository(db).update_journal_entry(entry_id, {'status': 1, 'posted_by': approved_by}) # 1: Approved

    def post_journal_entry(self, entry_id: int, posted_by: int):
        with get_session() as db:
            from datetime import datetime
            return JournalEntryRepository(db).update_journal_entry(entry_id, {'status': 2, 'posted_by': posted_by, 'posted_at': datetime.now()}) # 2: Posted

    def void_journal_entry(self, entry_id: int):
        with get_session() as db:
            return JournalEntryRepository(db).update_journal_entry(entry_id, {'status': 3}) # 3: Voided

class ARAPService:
    def __init__(self):
        pass

    # Customer Operations
    def get_all_customers(self):
        with get_session() as db:
            return CustomerRepository(db).get_all_customers()

    def get_customer_by_id(self, customer_id: int):
        with get_session() as db:
            return CustomerRepository(db).get_customer_by_id(customer_id)

    def create_customer(self, name_ar: str, name_en: str, credit_limit: Decimal = Decimal(0), payment_terms: str = None, is_active: bool = True, address: str = None, phone_number: str = None, customer_group: str = None, type: int = 0, email: str = None): # Removed code parameter
        with get_session() as db:
            try:
                customer = models.Customer(
                    name_ar=name_ar,
                    name_en=name_en,
                    credit_limit=credit_limit,
                    payment_terms=payment_terms,
                    is_active=is_active,
                    address=address,
                    phone_number=phone_number,
                    # mobile_number=mobile_number, # Removed from here
                    customer_group=customer_group,
                    type=type,
                    email=email # Pass email to the model
                )
                return CustomerRepository(db).create_customer(customer)
            except IntegrityError as e: # Catch IntegrityError for unique constraint violations
                db.rollback()
                if "unique_code" in str(e): # Assuming a unique constraint named 'unique_code' on customer code
                    raise ValueError("رقم العميل هذا موجود بالفعل. يرجى إدخال رقم فريد.")
                elif "unique_email" in str(e): # Assuming a unique constraint on email
                    raise ValueError("البريد الإلكتروني هذا مستخدم بالفعل. يرجى إدخال بريد إلكتروني فريد.")
                else:
                    raise ValueError(f"فشل إنشاء العميل: {e}")
            except Exception as e:
                db.rollback() # Rollback the transaction on any other error
                raise ValueError(f"فشل إنشاء العميل بسبب خطأ غير متوقع: {e}")

    def update_customer(self, customer_id: int, **kwargs):
        with get_session() as db:
            return CustomerRepository(db).update_customer(customer_id, kwargs)

    def delete_customer(self, customer_id: int):
        with get_session() as db:
            return CustomerRepository(db).delete_customer(customer_id)

    def get_next_customer_code(self) -> int:
        with get_session() as db:
            max_code = db.query(func.max(models.Customer.code)).scalar()
            next_code = (max_code or 0) + 1
            return next_code

    # Supplier Operations
    def get_all_suppliers(self):
        with get_session() as db:
            return SupplierRepository(db).get_all_suppliers()

    def get_supplier_by_id(self, supplier_id: int):
        with get_session() as db:
            return SupplierRepository(db).get_supplier_by_id(supplier_id)

    def create_supplier(self, name_ar: str, name_en: str, credit_limit: Decimal = Decimal(0), payment_terms: str = None, is_active: bool = True, address: str = None, phone_number: str = None, contact_person: str = None, email: str = None, tax_id: str = None, supplier_group: str = None):
        with get_session() as db:
            try:
                supplier = models.Supplier(
                    name_ar=name_ar,
                    name_en=name_en,
                    credit_limit=credit_limit,
                    payment_terms=payment_terms,
                    is_active=is_active,
                    address=address,
                    phone_number=phone_number,
                    contact_person=contact_person,
                    email=email,
                    tax_id=tax_id,
                    supplier_group=supplier_group
                )
                return SupplierRepository(db).create_supplier(supplier)
            except IntegrityError as e:
                db.rollback()
                if "unique_code" in str(e): # Assuming a unique constraint named 'unique_code' on supplier code
                    raise ValueError("رقم المورد هذا موجود بالفعل. يرجى إدخال رقم فريد.")
                elif "unique_email" in str(e): # Assuming a unique constraint on email
                    raise ValueError("البريد الإلكتروني هذا مستخدم بالفعل. يرجى إدخال بريد إلكتروني فريد.")
                else:
                    raise ValueError(f"فشل إنشاء المورد: {e}")
            except Exception as e:
                db.rollback()
                raise ValueError(f"فشل إنشاء المورد بسبب خطأ غير متوقع: {e}")

    def update_supplier(self, supplier_id: int, **kwargs):
        with get_session() as db:
            return SupplierRepository(db).update_supplier(supplier_id, kwargs)

    def delete_supplier(self, supplier_id: int):
        with get_session() as db:
            return SupplierRepository(db).delete_supplier(supplier_id)

    def get_next_supplier_code(self) -> int:
        with get_session() as db:
            max_code = db.query(func.max(models.Supplier.code)).scalar()
            next_code = (max_code or 0) + 1
            return next_code

    # Invoice Operations
    def get_all_invoices(self):
        with get_session() as db:
            return InvoiceRepository(db).get_all_invoices()

    def get_invoice_by_id(self, invoice_id: int):
        with get_session() as db:
            return InvoiceRepository(db).get_invoice_by_id(invoice_id)

    def create_invoice(self, company_id: int, branch_id: int, invoice_type: int, invoice_no: str, invoice_date: date, total_amount: Decimal, total_tax: Decimal, currency: str, customer_id: int = None, supplier_id: int = None, due_date: date = None, created_by: int = 1):
        with get_session() as db:
            if invoice_type == 0 and not customer_id: # Sales Invoice
                raise ValueError("Customer ID is required for sales invoices.")
            if invoice_type == 1 and not supplier_id: # Purchase Invoice
                raise ValueError("Supplier ID is required for purchase invoices.")
            if not company_id: # Ensure company_id is not None
                raise ValueError("Company ID is required for invoices.")
            if not branch_id: # Ensure branch_id is not None
                raise ValueError("Branch ID is required for invoices.")

            invoice = models.Invoice(
                company_id=company_id,
                branch_id=branch_id,
                customer_id=customer_id,
                supplier_id=supplier_id,
                invoice_type=invoice_type,
                invoice_no=invoice_no,
                invoice_date=invoice_date,
                due_date=due_date,
                total_amount=total_amount,
                total_tax=total_tax,
                currency=currency,
                status=0, # Draft
                created_by=created_by
            )
            return InvoiceRepository(db).create_invoice(invoice)

    def update_invoice(self, invoice_id: int, **kwargs):
        with get_session() as db:
            return InvoiceRepository(db).update_invoice(invoice_id, kwargs)

    def delete_invoice(self, invoice_id: int):
        with get_session() as db:
            return InvoiceRepository(db).delete_invoice(invoice_id)

    # Payment Operations
    def get_all_payments(self):
        with get_session() as db:
            return PaymentRepository(db).get_all_payments()

    def get_payment_by_id(self, payment_id: int):
        with get_session() as db:
            return PaymentRepository(db).get_payment_by_id(payment_id)

    def record_payment(self, company_id: int, branch_id: int, invoice_id: int, payment_date: date, amount: Decimal, currency: str, payment_method: str, ref_no: str = None, created_by: int = 1):
        with get_session() as db:
            payment_repo = PaymentRepository(db)
            invoice_repo = InvoiceRepository(db)

            payment = models.Payment(
                company_id=company_id,
                branch_id=branch_id,
                invoice_id=invoice_id,
                payment_date=payment_date,
                amount=amount,
                currency=currency,
                payment_method=payment_method,
                ref_no=ref_no,
                created_by=created_by
            )
            recorded_payment = payment_repo.create_payment(payment)

            # Update invoice status to 'Paid' if the total amount is covered
            invoice = invoice_repo.get_invoice_by_id(invoice_id)
            if invoice:
                total_paid = sum([p.amount for p in invoice.payments]) if invoice.payments else Decimal(0)
                if total_paid >= invoice.total_amount: # Simple check, can be more complex with partial payments
                    invoice_repo.update_invoice(invoice_id, {'status': 2}) # 2: Paid

            return recorded_payment

    def update_payment(self, payment_id: int, **kwargs):
        with get_session() as db:
            return PaymentRepository(db).update_payment(payment_id, kwargs)

    def delete_payment(self, payment_id: int):
        with get_session() as db:
            return PaymentRepository(db).delete_payment(payment_id)

class InventoryService:
    def __init__(self):
        pass

    # Item Operations
    def get_all_items(self):
        with get_session() as db:
            return ItemRepository(db).get_all_items()

    def get_item_by_id(self, item_id: int):
        with get_session() as db:
            return ItemRepository(db).get_item_by_id(item_id)

    def create_item(self, company_id: int, warehouse_id: int, name_ar: str, name_en: str = None, unit_id: int = None, barcode: str = None, sale_price: Decimal = Decimal(0), min_sale_price: Decimal = Decimal(0), cost_price: Decimal = Decimal(0), reorder_level: Decimal = Decimal(0), free_quantity_level: Decimal = Decimal(0), costing_method: int = 0, is_active: bool = True):
        with get_session() as db:
            item = models.Item(
                company_id=company_id,
                warehouse_id=warehouse_id, # New: Link item to a warehouse
                name_ar=name_ar,
                name_en=name_en,
                unit_id=unit_id,
                barcode=barcode,
                sale_price=sale_price,
                min_sale_price=min_sale_price,
                cost_price=cost_price,
                reorder_level=reorder_level,
                free_quantity_level=free_quantity_level,
                costing_method=costing_method,
                is_active=is_active
            )
            return ItemRepository(db).create_item(item)

    def update_item(self, item_id: int, **kwargs):
        with get_session() as db:
            return ItemRepository(db).update_item(item_id, kwargs)

    def delete_item(self, item_id: int):
        with get_session() as db:
            return ItemRepository(db).delete_item(item_id)

    def get_next_item_code(self) -> int:
        with get_session() as db:
            max_code = db.query(func.max(models.Item.code)).scalar()
            next_code = (max_code or 0) + 1
            return next_code

    # Removed Warehouse Operations from InventoryService

    # Stock Movement Operations
    def get_all_stock_movements(self):
        with get_session() as db:
            return StockMovementRepository(db).get_all_stock_movements()

    def record_stock_movement(self, company_id: int, branch_id: int, item_id: int, movement_type: int, quantity: Decimal, cost: Decimal = Decimal(0), movement_date: date = None, ref_no: str = None, created_by: int = 1):
        with get_session() as db:
            if not movement_date:
                movement_date = date.today()

            stock_movement = models.StockMovement(
                company_id=company_id,
                branch_id=branch_id,
                item_id=item_id,
                movement_type=movement_type,
                quantity=quantity,
                cost=cost,
                movement_date=movement_date,
                ref_no=ref_no,
                created_by=created_by
            )
            return StockMovementRepository(db).create_stock_movement(stock_movement)

    def get_stock_movements_by_item(self, item_id: int):
        with get_session() as db:
            return StockMovementRepository(db).db.query(models.StockMovement).filter(models.StockMovement.item_id == item_id).all()

    def get_item_stock_level(self, item_id: int, warehouse_id: int) -> float:
        with get_session() as db:
            # Calculate total 'in' movements (received items)
            total_in = db.query(func.sum(models.StockMovement.quantity)).filter(
                models.StockMovement.item_id == item_id,
                models.StockMovement.warehouse_id == warehouse_id,
                models.StockMovement.movement_type == 0  # Assuming 0 is 'in' movement type
            ).scalar() or 0.0

            # Calculate total 'out' movements (sold/returned items)
            total_out = db.query(func.sum(models.StockMovement.quantity)).filter(
                models.StockMovement.item_id == item_id,
                models.StockMovement.warehouse_id == warehouse_id,
                (models.StockMovement.movement_type == 1) | (models.StockMovement.movement_type == 3) # Assuming 1 is 'out' (sales) and 3 is 'returns'
            ).scalar() or 0.0

            current_stock = total_in - total_out
            return float(current_stock)

    def update_stock_movement(self, movement_id: int, **kwargs):
        with get_session() as db:
            return StockMovementRepository(db).update_stock_movement(movement_id, kwargs)

    def delete_stock_movement(self, movement_id: int):
        with get_session() as db:
            return StockMovementRepository(db).delete_stock_movement(movement_id)

class SalesPurchaseService:
    def __init__(self):
        pass

    # Sales Order Operations
    def get_all_sales_orders(self):
        with get_session() as db:
            return SalesOrderRepository(db).get_all_sales_orders()

    def get_sales_order_by_id(self, order_id: int):
        with get_session() as db:
            return SalesOrderRepository(db).get_sales_order_by_id(order_id)

    def create_sales_order(self, company_id: int, branch_id: int, customer_id: int, order_no: str, order_date: date, total_amount: Decimal, total_tax: Decimal, currency: str, created_by: int = 1):
        with get_session() as db:
            sales_order = models.SalesOrder(
                company_id=company_id,
                branch_id=branch_id,
                customer_id=customer_id,
                order_no=order_no,
                order_date=order_date,
                total_amount=total_amount,
                total_tax=total_tax,
                currency=currency,
                status=0, # Draft
                created_by=created_by
            )
            return SalesOrderRepository(db).create_sales_order(sales_order)

    def update_sales_order(self, order_id: int, **kwargs):
        with get_session() as db:
            return SalesOrderRepository(db).update_sales_order(order_id, kwargs)

    def delete_sales_order(self, order_id: int):
        with get_session() as db:
            return SalesOrderRepository(db).delete_sales_order(order_id)

    # Purchase Order Operations
    def get_all_purchase_orders(self):
        with get_session() as db:
            return PurchaseOrderRepository(db).get_all_purchase_orders()

    def get_purchase_order_by_id(self, order_id: int):
        with get_session() as db:
            return PurchaseOrderRepository(db).get_purchase_order_by_id(order_id)

    def create_purchase_order(self, company_id: int, branch_id: int, supplier_id: int, order_no: str, order_date: date, total_amount: Decimal, total_tax: Decimal, currency: str, created_by: int = 1):
        with get_session() as db:
            purchase_order = models.PurchaseOrder(
                company_id=company_id,
                branch_id=branch_id,
                supplier_id=supplier_id,
                order_no=order_no,
                order_date=order_date,
                total_amount=total_amount,
                total_tax=total_tax,
                currency=currency,
                status=0, # Draft
                created_by=created_by
            )
            return PurchaseOrderRepository(db).create_purchase_order(purchase_order)

    def update_purchase_order(self, order_id: int, **kwargs):
        with get_session() as db:
            return PurchaseOrderRepository(db).update_purchase_order(order_id, kwargs)

    def delete_purchase_order(self, order_id: int):
        with get_session() as db:
            return PurchaseOrderRepository(db).delete_purchase_order(order_id)

class CashBankService:
    def __init__(self):
        pass

    # Bank Transaction Operations
    def get_all_bank_transactions(self):
        with get_session() as db:
            return BankTransactionRepository(db).get_all_bank_transactions()

    def get_bank_transaction_by_id(self, transaction_id: int):
        with get_session() as db:
            return BankTransactionRepository(db).get_bank_transaction_by_id(transaction_id)

    def create_bank_transaction(self, company_id: int, branch_id: int, bank_account_id: int, transaction_type: int, amount: Decimal, currency: str, transaction_date: date, ref_no: str = None, description: str = None, created_by: int = 1):
        with get_session() as db:
            bank_transaction = models.BankTransaction(
                company_id=company_id,
                branch_id=branch_id,
                bank_account_id=bank_account_id,
                transaction_type=transaction_type,
                amount=amount,
                currency=currency,
                transaction_date=transaction_date,
                ref_no=ref_no,
                description=description,
                created_by=created_by
            )
            return BankTransactionRepository(db).create_bank_transaction(bank_transaction)

    def update_bank_transaction(self, transaction_id: int, **kwargs):
        with get_session() as db:
            return BankTransactionRepository(db).update_bank_transaction(transaction_id, kwargs)

    def delete_bank_transaction(self, transaction_id: int):
        with get_session() as db:
            return BankTransactionRepository(db).delete_bank_transaction(transaction_id)

    # Bank Reconciliation Operations
    def get_all_bank_reconciliations(self):
        with get_session() as db:
            return BankReconciliationRepository(db).get_all_bank_reconciliations()

    def get_bank_reconciliation_by_id(self, reconciliation_id: int):
        with get_session() as db:
            return BankReconciliationRepository(db).get_bank_reconciliation_by_id(reconciliation_id)

    def create_bank_reconciliation(self, company_id: int, branch_id: int, bank_account_id: int, reconciliation_date: date, statement_balance: Decimal, book_balance: Decimal, created_by: int = 1):
        with get_session() as db:
            difference = statement_balance - book_balance
            bank_reconciliation = models.BankReconciliation(
                company_id=company_id,
                branch_id=branch_id,
                bank_account_id=bank_account_id,
                reconciliation_date=reconciliation_date,
                statement_balance=statement_balance,
                book_balance=book_balance,
                difference=difference,
                is_reconciled=(difference == 0),
                created_by=created_by
            )
            return BankReconciliationRepository(db).create_bank_reconciliation(bank_reconciliation)

    def update_bank_reconciliation(self, reconciliation_id: int, **kwargs):
        with get_session() as db:
            return BankReconciliationRepository(db).update_reconciliation(reconciliation_id, kwargs)

    def delete_bank_reconciliation(self, reconciliation_id: int):
        with get_session() as db:
            return BankReconciliationRepository(db).delete_reconciliation(reconciliation_id)

    def get_all_cash_bank_entries(self):
        with get_session() as db:
            transactions = BankTransactionRepository(db).get_all_bank_transactions()
            reconciliations = BankReconciliationRepository(db).get_all_bank_reconciliations()

            combined_entries = []
            for t in transactions:
                combined_entries.append({
                    "id": t.id,
                    "company_id": t.company_id,
                    "branch_id": t.branch_id,
                    "account_id": t.bank_account_id,
                    "type": "Transaction",
                    "amount": t.amount,
                    "date": t.transaction_date,
                    "description": t.description,
                    "ref_no": t.ref_no
                })
            for r in reconciliations:
                combined_entries.append({
                    "id": r.id,
                    "company_id": r.company_id,
                    "branch_id": r.branch_id,
                    "account_id": r.bank_account_id,
                    "type": "Reconciliation",
                    "amount": r.statement_balance, # Or difference, depending on what's desired
                    "date": r.reconciliation_date,
                    "description": "Bank Reconciliation",
                    "ref_no": None
                })
            # Sort by date, most recent first
            combined_entries.sort(key=lambda x: x['date'], reverse=True)
            return combined_entries

class FixedAssetService:
    def __init__(self):
        pass

    # Fixed Asset Operations
    def get_all_fixed_assets(self):
        with get_session() as db:
            return FixedAssetRepository(db).get_all_fixed_assets()

    def get_fixed_asset_by_id(self, asset_id: int):
        with get_session() as db:
            return FixedAssetRepository(db).get_fixed_asset_by_id(asset_id)

    def create_fixed_asset(self, company_id: int, branch_id: int, code: str, name_ar: str, name_en: str, asset_category: str, acquisition_date: date, cost: Decimal, salvage_value: Decimal, useful_life_years: int, depreciation_method: int, created_by: int = 1):
        with get_session() as db:
            fixed_asset = models.FixedAsset(
                company_id=company_id,
                branch_id=branch_id,
                code=code,
                name_ar=name_ar,
                name_en=name_en,
                asset_category=asset_category,
                acquisition_date=acquisition_date,
                cost=cost,
                salvage_value=salvage_value,
                useful_life_years=useful_life_years,
                depreciation_method=depreciation_method,
                created_by=created_by
            )
            return FixedAssetRepository(db).create_fixed_asset(fixed_asset)

    def update_fixed_asset(self, asset_id: int, **kwargs):
        with get_session() as db:
            return FixedAssetRepository(db).update_fixed_asset(asset_id, kwargs)

    def delete_fixed_asset(self, asset_id: int):
        with get_session() as db:
            return FixedAssetRepository(db).delete_fixed_asset(asset_id)

    # Depreciation Operations (simplified for now)
    def get_all_depreciations(self):
        with get_session() as db:
            return DepreciationRepository(db).get_all_depreciations()

    def record_depreciation(self, company_id: int, branch_id: int, asset_id: int, depreciation_date: date, amount: Decimal, created_by: int = 1):
        with get_session() as db:
            depreciation = models.Depreciation(
                company_id=company_id,
                branch_id=branch_id,
                asset_id=asset_id,
                depreciation_date=depreciation_date,
                amount=amount,
                created_by=created_by
            )
            return DepreciationRepository(db).create_depreciation(depreciation)

    def get_depreciations_by_asset(self, asset_id: int):
        with get_session() as db:
            return DepreciationRepository(db).db.query(models.Depreciation).filter(models.Depreciation.asset_id == asset_id).all()

class TaxService:
    def __init__(self):
        pass

    # Tax Setting Operations
    def get_all_tax_settings(self):
        with get_session() as db:
            return TaxSettingRepository(db).get_all_tax_settings()

    def get_tax_setting_by_id(self, setting_id: int):
        with get_session() as db:
            return TaxSettingRepository(db).get_tax_setting_by_id(setting_id)

    def create_tax_setting(self, company_id: int, country_code: str, tax_name_ar: str, tax_name_en: str, tax_rate: Decimal, is_active: bool = True, created_by: int = 1):
        with get_session() as db:
            tax_setting = models.TaxSetting(
                company_id=company_id,
                country_code=country_code,
                tax_name_ar=tax_name_ar,
                tax_name_en=name_en,
                tax_rate=tax_rate,
                is_active=is_active,
                created_by=created_by
            )
            return TaxSettingRepository(db).create_tax_setting(tax_setting)

    def update_tax_setting(self, setting_id: int, **kwargs):
        with get_session() as db:
            return TaxSettingRepository(db).update_tax_setting(setting_id, kwargs)

    def delete_tax_setting(self, setting_id: int):
        with get_session() as db:
            return TaxSettingRepository(db).delete_tax_setting(setting_id)

    # Tax Report Operations (simplified for now)
    def get_all_tax_reports(self):
        with get_session() as db:
            return TaxReportRepository(db).get_all_tax_reports()

    def get_tax_report_by_id(self, report_id: int):
        with get_session() as db:
            return TaxReportRepository(db).get_tax_report_by_id(report_id)

    def create_tax_report(self, company_id: int, branch_id: int, tax_setting_id: int, report_period: str, start_date: date, end_date: date, total_sales_tax: Decimal, total_purchase_tax: Decimal, created_by: int = 1):
        with get_session() as db:
            net_tax_payable = total_sales_tax - total_purchase_tax
            tax_report = models.TaxReport(
                company_id=company_id,
                branch_id=branch_id,
                tax_setting_id=tax_setting_id,
                report_period=report_period,
                start_date=start_date,
                end_date=end_date,
                total_sales_tax=total_sales_tax,
                total_purchase_tax=total_purchase_tax,
                net_tax_payable=net_tax_payable,
                status=0, # Draft
                created_by=created_by
            )
            return TaxReportRepository(db).create_tax_report(tax_report)

    def update_tax_report(self, report_id: int, **kwargs):
        with get_session() as db:
            return TaxReportRepository(db).update_tax_report(report_id, kwargs)

    def delete_tax_report(self, report_id: int):
        with get_session() as db:
            return TaxReportRepository(db).delete_tax_report(report_id)

class IAMService:
    def __init__(self):
        pass

    # User Operations
    def get_all_users(self):
        with get_session() as db:
            return UserRepository(db).get_all_users()

    def get_user_by_id(self, user_id: int):
        with get_session() as db:
            return UserRepository(db).get_user_by_id(user_id)

    def create_user(self, username: str, password: str, email: str, company_id: int, full_name_ar: str = None, full_name_en: str = None, is_active: bool = True):
        with get_session() as db:
            hashed_password = generate_password_hash(password)
            user = models.User(
                username=username,
                password_hash=hashed_password,
                email=email,
                full_name_ar=full_name_ar,
                full_name_en=full_name_en,
                is_active=is_active,
                company_id=company_id # New: Link user to a company
            )
            return UserRepository(db).create_user(user)

    def authenticate_user(self, username: str, password: str):
        with get_session() as db:
            user = UserRepository(db).db.query(models.User).filter(models.User.username == username).first()
            if user and check_password_hash(user.password_hash, password):
                return user
            return None

    def update_user(self, user_id: int, **kwargs):
        with get_session() as db:
            if 'password' in kwargs:
                kwargs['password_hash'] = generate_password_hash(kwargs['password'])
                del kwargs['password']
            return UserRepository(db).update_user(user_id, kwargs)

    def delete_user(self, user_id: int):
        with get_session() as db:
            return UserRepository(db).delete_user(user_id)

    # Role Operations
    def get_all_roles(self):
        with get_session() as db:
            return RoleRepository(db).get_all_roles()

    def get_role_by_id(self, role_id: int):
        with get_session() as db:
            return RoleRepository(db).get_role_by_id(role_id)

    def create_role(self, name: str, description: str = None, is_active: bool = True):
        with get_session() as db:
            role = models.Role(
                name=name,
                description=description,
                is_active=is_active
            )
            return RoleRepository(db).create_role(role)

    def update_role(self, role_id: int, **kwargs):
        with get_session() as db:
            return RoleRepository(db).update_role(role_id, kwargs)

    def delete_role(self, role_id: int):
        with get_session() as db:
            return RoleRepository(db).delete_role(role_id)

    # Permission Operations
    def get_all_permissions(self):
        with get_session() as db:
            return PermissionRepository(db).get_all_permissions()

    def get_permission_by_id(self, permission_id: int):
        with get_session() as db:
            return PermissionRepository(db).get_permission_by_id(permission_id)

    def create_permission(self, name: str, description: str = None):
        with get_session() as db:
            permission = models.Permission(
                name=name,
                description=description
            )
            return PermissionRepository(db).create_permission(permission)

    def update_permission(self, permission_id: int, **kwargs):
        with get_session() as db:
            return PermissionRepository(db).update_permission(permission_id, kwargs)

    def delete_permission(self, permission_id: int):
        with get_session() as db:
            return PermissionRepository(db).delete_permission(permission_id)

    # User-Role Management (Simplified for now)
    def assign_role_to_user(self, user_id: int, role_id: int):
        with get_session() as db:
            user_role = models.UserRole(user_id=user_id, role_id=role_id)
            db.add(user_role)
            db.commit()
            return user_role

    def remove_role_from_user(self, user_id: int, role_id: int):
        with get_session() as db:
            user_role = db.query(models.UserRole).filter_by(user_id=user_id, role_id=role_id).first()
            if user_role:
                db.delete(user_role)
                db.commit()
                return True
            return False

    # Role-Permission Management (Simplified for now)
    def assign_permission_to_role(self, role_id: int, permission_id: int):
        with get_session() as db:
            role_permission = models.RolePermission(role_id=role_id, permission_id=permission_id)
            db.add(role_permission)
            db.commit()
            return role_permission

    def remove_permission_from_role(self, role_id: int, permission_id: int):
        with get_session() as db:
            role_permission = db.query(models.RolePermission).filter_by(role_id=role_id, permission_id=permission_id).first()
            if role_permission:
                db.delete(role_permission)
                db.commit()
                return True
            return False

class CompanyService:
    def __init__(self):
        pass

    # Company Operations
    def get_all_companies(self):
        with get_session() as db:
            return CompanyRepository(db).get_all_companies()

    def get_company_by_id(self, company_id: int):
        with get_session() as db:
            return CompanyRepository(db).get_company_by_id(company_id)

    def create_company(self, name_ar: str, name_en: str = None, base_currency_id: int = None, secondary_currency_id: int = None, address: str = None, phone_number: str = None, email: str = None, is_active: bool = True, admin_username: str = None, admin_password_hash: str = None, created_by: int = 1):
        with get_session() as db:
            try:
                company = models.Company(
                    name_ar=name_ar,
                    name_en=name_en,
                    base_currency_id=base_currency_id,
                    secondary_currency_id=secondary_currency_id,
                    address=address,
                    phone_number=phone_number,
                    email=email,
                    is_active=is_active,
                    admin_username=admin_username, # New
                    admin_password_hash=admin_password_hash, # New
                    created_by=created_by
                )
                new_company = CompanyRepository(db).create_company(company)

                # Removed default branch creation here. It will be handled in SetupWizard.

                return new_company
            except IntegrityError as e:
                db.rollback() # Rollback the transaction on integrity error
                if "unique_code" in str(e): # Assuming a unique constraint named 'unique_code' on company code
                    raise ValueError("رقم الشركة هذا موجود بالفعل. يرجى إدخال رقم فريد.")
                elif "unique_email" in str(e): # Assuming a unique constraint on email
                    raise ValueError("البريد الإلكتروني هذا مستخدم بالفعل. يرجى إدخال بريد إلكتروني فريد.")
                else:
                    raise ValueError(f"فشل إنشاء الشركة: {e}")
            except Exception as e:
                db.rollback() # Rollback the transaction on any other error
                raise ValueError(f"فشل إنشاء الشركة بسبب خطأ غير متوقع: {e}")

    def update_company(self, company_id: int, **kwargs):
        with get_session() as db:
            if 'base_currency' in kwargs:
                kwargs['base_currency_id'] = kwargs.pop('base_currency')
            if 'secondary_currency' in kwargs:
                kwargs['secondary_currency_id'] = kwargs.pop('secondary_currency')
            return CompanyRepository(db).update_company(company_id, kwargs)

    def update_company_loyalty_status(self, company_id: int, is_enabled: bool):
        """ Updates the loyalty program enabled status for a company. """
        with get_session() as db:
            return CompanyRepository(db).update_company(company_id, {'is_loyalty_enabled': is_enabled})

    def update_company_created_by(self, company_id: int, created_by_user_id: int):
        """ Updates the created_by field for a company. """
        with get_session() as db:
            return CompanyRepository(db).update_company(company_id, {'created_by': created_by_user_id})

    def delete_company(self, company_id: int):
        with get_session() as db:
            return CompanyRepository(db).delete_company(company_id)

    def get_next_company_code(self) -> int:
        with get_session() as db:
            max_code = db.query(func.max(models.Company.code)).scalar()
            next_code = (max_code or 0) + 1
            return next_code


class BranchService:
    def __init__(self):
        pass

    # Branch Operations
    def get_all_branches(self):
        with get_session() as db:
            return BranchRepository(db).get_all_branches()

    def get_branch_by_id(self, branch_id: int):
        with get_session() as db:
            return BranchRepository(db).get_branch_by_id(branch_id)

    def create_branch(self, company_id: int, name_ar: str, name_en: str = None, address: str = None, phone_number: str = None, base_currency_id: int = None, is_active: bool = True, created_by: int = 1):
        with get_session() as db:
            try:
                branch = models.Branch(
                    company_id=company_id,
                    name_ar=name_ar,
                    name_en=name_en,
                    address=address,
                    phone_number=phone_number,
                    # Removed email from Branch model creation
                    base_currency_id=base_currency_id, # New: Pass base_currency_id to the model
                    is_active=is_active,
                    created_by=created_by
                )
                return BranchRepository(db).create_branch(branch)
            except IntegrityError as e: # Catch IntegrityError for unique constraint violations
                db.rollback()
                if "unique_code" in str(e): # Assuming a unique constraint named 'unique_code' on branch code
                    raise ValueError("رقم الفرع هذا موجود بالفعل. يرجى إدخال رقم فريد.")
                else:
                    raise ValueError(f"فشل إنشاء الفرع: {e}")
            except Exception as e:
                db.rollback() # Rollback the transaction on any other error
                raise ValueError(f"فشل إنشاء الفرع بسبب خطأ غير متوقع: {e}")

    def update_branch(self, branch_id: int, **kwargs):
        with get_session() as db:
            return BranchRepository(db).update_branch(branch_id, kwargs)

    def delete_branch(self, branch_id: int):
        with get_session() as db:
            return BranchRepository(db).delete_branch(branch_id)

    def get_next_branch_code(self) -> int:
        with get_session() as db:
            max_code = db.query(func.max(models.Branch.code)).scalar()
            next_code = (max_code or 0) + 1
            return next_code

class FiscalPeriodService:
    def __init__(self):
        pass

    # Fiscal Period Operations
    def get_all_fiscal_periods(self):
        with get_session() as db:
            return FiscalPeriodRepository(db).get_all_fiscal_periods()

    def get_fiscal_period_by_id(self, period_id: int):
        with get_session() as db:
            return FiscalPeriodRepository(db).get_fiscal_period_by_id(period_id)

    def create_fiscal_period(self, company_id: int, year: int, start_date: date, end_date: date, is_open: bool = True, created_by: int = 1):
        with get_session() as db:
            fiscal_period = models.FiscalPeriod(
                company_id=company_id,
                year=year,
                start_date=start_date,
                end_date=end_date,
                is_open=is_open,
                created_by=created_by
            )
            return FiscalPeriodRepository(db).create_fiscal_period(fiscal_period)

    def update_fiscal_period(self, period_id: int, **kwargs):
        with get_session() as db:
            return FiscalPeriodRepository(db).update_fiscal_period(period_id, kwargs)

    def close_fiscal_period(self, period_id: int):
        with get_session() as db:
            return FiscalPeriodRepository(db).update_fiscal_period(period_id, {'is_open': False})

    def delete_fiscal_period(self, period_id: int):
        with get_session() as db:
            return FiscalPeriodRepository(db).delete_fiscal_period(period_id)

class CostCenterProjectService:
    def __init__(self):
        pass

    # Cost Center Operations
    def get_all_cost_centers(self):
        with get_session() as db:
            return CostCenterRepository(db).get_all_cost_centers()

    def get_cost_center_by_id(self, cost_center_id: int):
        with get_session() as db:
            return CostCenterRepository(db).get_cost_center_by_id(cost_center_id)

    def create_cost_center(self, company_id: int, name_ar: str, name_en: str, is_active: bool = True, created_by: int = 1):
        with get_session() as db:
            try:
                cost_center = models.CostCenter(
                    company_id=company_id,
                    name_ar=name_ar,
                    name_en=name_en,
                    is_active=is_active,
                    created_by=created_by
                )
                return CostCenterRepository(db).create_cost_center(cost_center)
            except IntegrityError as e: # Catch IntegrityError for unique constraint violations
                db.rollback()
                if "unique_code" in str(e): # Assuming a unique constraint named 'unique_code' on cost center code
                    raise ValueError("رقم مركز التكلفة هذا موجود بالفعل. يرجى إدخال رقم فريد.")
                else:
                    raise ValueError(f"فشل إنشاء مركز التكلفة: {e}")
            except Exception as e:
                db.rollback() # Rollback the transaction on any other error
                raise ValueError(f"فشل إنشاء مركز التكلفة بسبب خطأ غير متوقع: {e}")

    def update_cost_center(self, cost_center_id: int, **kwargs):
        with get_session() as db:
            return CostCenterRepository(db).update_cost_center(cost_center_id, kwargs)

    def delete_cost_center(self, cost_center_id: int):
        with get_session() as db:
            return CostCenterRepository(db).delete_cost_center(cost_center_id)

    def get_next_cost_center_code(self) -> int:
        with get_session() as db:
            max_code = db.query(func.max(models.CostCenter.code)).scalar()
            next_code = (max_code or 0) + 1
            return next_code

    # Project Operations
    def get_all_projects(self):
        with get_session() as db:
            return ProjectRepository(db).get_all_projects()

    def get_project_by_id(self, project_id: int):
        with get_session() as db:
            return ProjectRepository(db).get_project_by_id(project_id)

    def create_project(self, company_id: int, name_ar: str, name_en: str, start_date: date = None, end_date: date = None, is_active: bool = True, created_by: int = 1):
        with get_session() as db:
            try:
                project = models.Project(
                    company_id=company_id,
                    name_ar=name_ar,
                    name_en=name_en,
                    start_date=start_date,
                    end_date=end_date,
                    is_active=is_active,
                    created_by=created_by
                )
                return ProjectRepository(db).create_project(project)
            except IntegrityError as e: # Catch IntegrityError for unique constraint violations
                db.rollback()
                if "unique_code" in str(e): # Assuming a unique constraint named 'unique_code' on project code
                    raise ValueError("رقم المشروع هذا موجود بالفعل. يرجى إدخال رقم فريد.")
                else:
                    raise ValueError(f"فشل إنشاء المشروع: {e}")
            except Exception as e:
                db.rollback() # Rollback the transaction on any other error
                raise ValueError(f"فشل إنشاء المشروع بسبب خطأ غير متوقع: {e}")

    def update_project(self, project_id: int, **kwargs):
        with get_session() as db:
            return ProjectRepository(db).update_project(project_id, kwargs)

    def delete_project(self, project_id: int):
        with get_session() as db:
            return ProjectRepository(db).delete_project(project_id)

    def get_next_project_code(self) -> int:
        with get_session() as db:
            max_code = db.query(func.max(models.Project.code)).scalar()
            next_code = (max_code or 0) + 1
            return next_code

class PayrollService:
    def __init__(self):
        pass

    # Employee Operations
    def get_all_employees(self):
        with get_session() as db:
            return EmployeeRepository(db).get_all_employees()

    def get_employee_by_id(self, employee_id: int):
        with get_session() as db:
            return EmployeeRepository(db).get_employee_by_id(employee_id)

    def create_employee(self, company_id: int, branch_id: int, first_name_ar: str, last_name_ar: str, first_name_en: str, last_name_en: str, position: str, hire_date: date, salary: Decimal, is_active: bool = True, created_by: int = 1):
        with get_session() as db:
            employee = models.Employee(
                company_id=company_id,
                branch_id=branch_id,
                first_name_ar=first_name_ar,
                last_name_ar=last_name_ar,
                first_name_en=first_name_en,
                last_name_en=last_name_en,
                position=position,
                hire_date=hire_date,
                salary=salary,
                is_active=is_active,
                created_by=created_by
            )
            return EmployeeRepository(db).create_employee(employee)

    def update_employee(self, employee_id: int, **kwargs):
        with get_session() as db:
            return EmployeeRepository(db).update_employee(employee_id, kwargs)

    def delete_employee(self, employee_id: int):
        with get_session() as db:
            return EmployeeRepository(db).delete_employee(employee_id)

    # Payrun Operations
    def get_all_payruns(self):
        with get_session() as db:
            return PayrunRepository(db).get_all_payruns()

    def get_payrun_by_id(self, payrun_id: int):
        with get_session() as db:
            return PayrunRepository(db).get_payrun_by_id(payrun_id)

    def create_payrun(self, company_id: int, branch_id: int, start_date: date, end_date: date, pay_date: date, total_gross_pay: Decimal, total_net_pay: Decimal, status: int, created_by: int = 1):
        with get_session() as db:
            payrun = models.Payrun(
                company_id=company_id,
                branch_id=branch_id,
                start_date=start_date,
                end_date=end_date,
                pay_date=pay_date,
                total_gross_pay=total_gross_pay,
                total_net_pay=total_net_pay,
                status=status,
                created_by=created_by
            )
            return PayrunRepository(db).create_payrun(payrun)

    def update_payrun(self, payrun_id: int, **kwargs):
        with get_session() as db:
            return PayrunRepository(db).update_payrun(payrun_id, kwargs)

    def delete_payrun(self, payrun_id: int):
        with get_session() as db:
            return PayrunRepository(db).delete_payrun(payrun_id)

class NotificationsWorkflowsService:
    def __init__(self):
        pass

    # Notification Operations
    def get_all_notifications(self):
        with get_session() as db:
            return NotificationRepository(db).get_all_notifications()

    def get_notification_by_id(self, notification_id: int):
        with get_session() as db:
            return NotificationRepository(db).get_notification_by_id(notification_id)

    def create_notification(self, user_id: int, company_id: int, message: str, is_read: bool = False):
        with get_session() as db:
            notification = models.Notification(
                user_id=user_id,
                company_id=company_id,
                message=message,
                is_read=is_read
            )
            return NotificationRepository(db).create_notification(notification)

    def update_notification(self, notification_id: int, **kwargs):
        with get_session() as db:
            return NotificationRepository(db).update_notification(notification_id, kwargs)

    def delete_notification(self, notification_id: int):
        with get_session() as db:
            return NotificationRepository(db).delete_notification(notification_id)

    # Workflow Operations
    def get_all_workflows(self):
        with get_session() as db:
            return WorkflowRepository(db).get_all_workflows()

    def get_workflow_by_id(self, workflow_id: int):
        with get_session() as db:
            return WorkflowRepository(db).get_workflow_by_id(workflow_id)

    def create_workflow(self, company_id: int, name: str, description: str, trigger_event: str, actions: dict, is_active: bool = True, created_by: int = 1):
        with get_session() as db:
            workflow = models.Workflow(
                company_id=company_id,
                name=name,
                description=description,
                trigger_event=trigger_event,
                actions=actions,
                is_active=is_active,
                created_by=created_by
            )
            return WorkflowRepository(db).create_workflow(workflow)

    def update_workflow(self, workflow_id: int, **kwargs):
        with get_session() as db:
            return WorkflowRepository(db).update_workflow(workflow_id, kwargs)

    def delete_workflow(self, workflow_id: int):
        with get_session() as db:
            return WorkflowRepository(db).delete_workflow(workflow_id)

class ReportingService:
    def __init__(self, account_service, journal_service, arap_service):
        self.account_service = account_service
        self.journal_service = journal_service
        self.arap_service = arap_service

    def get_trial_balance(self, company_id: int, branch_id: int = None, period: str = None, as_of_date: date = None):
        # Simplified for now
        with get_session() as db:
            # Example: Fetch all accounts
            accounts = AccountRepository(db).get_all_accounts()
            return [{
                "account_code": a.code,
                "account_name": a.name_ar,
                "debit": 0.0, # Placeholder
                "credit": 0.0 # Placeholder
            } for a in accounts]

class GeneralConfigurationService:
    def __init__(self):
        pass

    def get_all_companies(self):
        with get_session() as db:
            return CompanyRepository(db).get_all_companies()

    def get_all_branches(self):
        with get_session() as db:
            return BranchRepository(db).get_all_branches()

    def get_all_fiscal_periods(self):
        with get_session() as db:
            return FiscalPeriodRepository(db).get_all_fiscal_periods()

class UnitService:
    def __init__(self):
        pass

    def get_all_units(self):
        with get_session() as db:
            return UnitRepository(db).db.query(Unit).all()

    def get_unit_by_id(self, unit_id: int):
        with get_session() as db:
            return UnitRepository(db).get_unit_by_id(unit_id)

    def get_units_for_item(self, item_id: int):
        with get_session() as db:
            # For now, return all units as they are no longer tied to company_id directly
            return UnitRepository(db).db.query(Unit).all()

    def create_unit(self, name_ar: str, name_en: str = None, code: str = None, base_quantity: Decimal = Decimal(1.0), is_active: bool = True):
        with get_session() as db:
            try:
                unit = Unit(
                    name_ar=name_ar,
                    name_en=name_en,
                    code=code, # New: Pass code to the model
                    base_quantity=base_quantity,
                    is_active=is_active
                )
                return UnitRepository(db).create_unit(unit)
            except IntegrityError as e:
                db.rollback()
                if "unit_name_ar_key" in str(e) or "unit_name_en_key" in str(e) or "units_code_key" in str(e): # Assuming unique constraints
                    raise ValueError("اسم الوحدة أو رمزها موجود بالفعل. يرجى إدخال اسم ورمز فريدين.")
                else:
                    raise ValueError(f"فشل إنشاء الوحدة: {e}")
            except Exception as e:
                db.rollback()
                raise ValueError(f"فشل إنشاء الوحدة بسبب خطأ غير متوقع: {e}")

    def update_unit(self, unit_id: int, name_ar: str = None, name_en: str = None, code: str = None, base_quantity: Decimal = None, is_active: bool = None):
        with get_session() as db:
            try:
                update_data = {}
                if name_ar is not None: update_data['name_ar'] = name_ar
                if name_en is not None: update_data['name_en'] = name_en
                if code is not None: update_data['code'] = code
                if base_quantity is not None: update_data['base_quantity'] = base_quantity
                if is_active is not None: update_data['is_active'] = is_active
                
                return UnitRepository(db).update_unit(unit_id, update_data)
            except IntegrityError as e:
                db.rollback()
                if "unit_name_ar_key" in str(e) or "unit_name_en_key" in str(e) or "units_code_key" in str(e):
                    raise ValueError("اسم الوحدة أو رمزها موجود بالفعل. يرجى إدخال اسم ورمز فريدين.")
                else:
                    raise ValueError(f"فشل تحديث الوحدة: {e}")
            except Exception as e:
                db.rollback()
                raise ValueError(f"فشل تحديث الوحدة بسبب خطأ غير متوقع: {e}")

    def delete_unit(self, unit_id: int):
        with get_session() as db:
            return UnitRepository(db).delete_unit(unit_id)

class CurrencyService:
    def __init__(self):
        pass

    def get_all_currencies(self):
        with get_session() as db:
            return CurrencyRepository(db).db.query(Currency).all()

    def get_currency_by_id(self, currency_id: int):
        with get_session() as db:
            return CurrencyRepository(db).get_currency_by_id(currency_id)

    def get_currency_by_code(self, code: str):
        with get_session() as db:
            return CurrencyRepository(db).db.query(Currency).filter(Currency.code == code).first()

    def create_currency(self, name_ar: str, name_en: str = None, code: str = None, symbol: str = None, exchange_rate: Decimal = Decimal(1.0), is_active: bool = True):
        with get_session() as db:
            try:
                currency = Currency(
                    name_ar=name_ar,
                    name_en=name_en,
                    code=code,
                    symbol=symbol,
                    exchange_rate=exchange_rate,
                    is_active=is_active
                )
                return CurrencyRepository(db).create_currency(currency)
            except IntegrityError as e:
                db.rollback()
                if "currencies_code_key" in str(e): # Assuming unique constraint on currency code
                    raise ValueError("رمز العملة موجود بالفعل. يرجى إدخال رمز فريد.")
                else:
                    raise ValueError(f"فشل إنشاء العملة: {e}")
            except Exception as e:
                db.rollback()
                raise ValueError(f"فشل إنشاء العملة بسبب خطأ غير متوقع: {e}")

    def update_currency(self, currency_id: int, name_ar: str = None, name_en: str = None, code: str = None, symbol: str = None, exchange_rate: Decimal = None, is_active: bool = None):
        with get_session() as db:
            try:
                update_data = {}
                if name_ar is not None: update_data['name_ar'] = name_ar
                if name_en is not None: update_data['name_en'] = name_en
                if code is not None: update_data['code'] = code
                if symbol is not None: update_data['symbol'] = symbol
                if exchange_rate is not None: update_data['exchange_rate'] = exchange_rate
                if is_active is not None: update_data['is_active'] = is_active
                
                return CurrencyRepository(db).update_currency(currency_id, update_data)
            except IntegrityError as e:
                db.rollback()
                if "currencies_code_key" in str(e):
                    raise ValueError("رمز العملة موجود بالفعل. يرجى إدخال رمز فريد.")
                else:
                    raise ValueError(f"فشل تحديث العملة: {e}")
            except ValueError as ve:
                db.rollback()
                raise ve # Re-raise custom validation errors
            except Exception as e:
                db.rollback()
                raise ValueError(f"فشل تحديث العملة بسبب خطأ غير متوقع: {e}")

    def delete_currency(self, currency_id: int):
        with get_session() as db:
            return CurrencyRepository(db).delete_currency(currency_id)

class PaymentMethodService:
    def __init__(self):
        pass

    def get_all_payment_methods(self, company_id: int):
        with get_session() as db:
            return PaymentMethodRepository(db).db.query(models.PaymentMethod).filter(models.PaymentMethod.company_id == company_id).all()

    def get_payment_method_by_id(self, method_id: int):
        with get_session() as db:
            return PaymentMethodRepository(db).get_payment_method_by_id(method_id)

    def create_payment_method(self, company_id: int, name_ar: str, name_en: str = None, type: str = 'Cash', is_active: bool = True):
        with get_session() as db:
            try:
                payment_method = models.PaymentMethod(
                    company_id=company_id,
                    name_ar=name_ar,
                    name_en=name_en,
                    type=type,
                    is_active=is_active
                )
                return PaymentMethodRepository(db).create_payment_method(payment_method)
            except IntegrityError as e:
                db.rollback()
                if "payment_method_name_ar_key" in str(e) or "payment_method_name_en_key" in str(e): # Assuming unique constraints
                    raise ValueError("اسم طريقة الدفع موجود بالفعل. يرجى إدخال اسم فريد.")
                else:
                    raise ValueError(f"فشل إنشاء طريقة الدفع: {e}")
            except Exception as e:
                db.rollback()
                raise ValueError(f"فشل إنشاء طريقة الدفع بسبب خطأ غير متوقع: {e}")

    def update_payment_method(self, method_id: int, **kwargs):
        with get_session() as db:
            try:
                return PaymentMethodRepository(db).update_payment_method(method_id, kwargs)
            except IntegrityError as e:
                db.rollback()
                if "payment_method_name_ar_key" in str(e) or "payment_method_name_en_key" in str(e):
                    raise ValueError("اسم طريقة الدفع موجود بالفعل. يرجى إدخال اسم فريد.")
                else:
                    raise ValueError(f"فشل تحديث طريقة الدفع: {e}")
            except Exception as e:
                db.rollback()
                raise ValueError(f"فشل تحديث طريقة الدفع بسبب خطأ غير متوقع: {e}")

    def delete_payment_method(self, method_id: int):
        with get_session() as db:
            return PaymentMethodRepository(db).delete_payment_method(method_id)

class CouponService:
    def __init__(self):
        pass

    def get_all_coupons(self, company_id: int):
        with get_session() as db:
            return CouponRepository(db).get_all_coupons(company_id)

    def get_coupon_by_id(self, coupon_id: int):
        with get_session() as db:
            return CouponRepository(db).get_coupon_by_id(coupon_id)

    def get_coupon_by_code(self, company_id: int, code: str):
        with get_session() as db:
            return CouponRepository(db).get_coupon_by_code(company_id, code)

    def create_coupon(self, company_id: int, code: str, name_ar: str, name_en: str = None, discount_type: str = "percentage", discount_value: float = 0.0, min_purchase_amount: float = 0.0, valid_from: datetime = None, valid_until: datetime = None, is_active: bool = True):
        with get_session() as db:
            try:
                if valid_from is None: valid_from = datetime.now()

                coupon = models.Coupon(
                    company_id=company_id,
                    code=code,
                    name_ar=name_ar,
                    name_en=name_en,
                    discount_type=discount_type,
                    discount_value=discount_value,
                    min_purchase_amount=min_purchase_amount,
                    valid_from=valid_from,
                    valid_until=valid_until,
                    is_active=is_active
                )
                return CouponRepository(db).create_coupon(coupon)
            except IntegrityError as e:
                db.rollback()
                if "coupons_code_key" in str(e): # Assuming unique constraint on coupon code
                    raise ValueError("كود الكوبون موجود بالفعل. يرجى إدخال كود فريد.")
                else:
                    raise ValueError(f"فشل إنشاء الكوبون: {e}")
            except Exception as e:
                db.rollback()
                raise ValueError(f"فشل إنشاء الكوبون بسبب خطأ غير متوقع: {e}")

    def update_coupon(self, coupon_id: int, **kwargs):
        with get_session() as db:
            try:
                return CouponRepository(db).update_coupon(coupon_id, kwargs)
            except IntegrityError as e:
                db.rollback()
                if "coupons_code_key" in str(e):
                    raise ValueError("كود الكوبون موجود بالفعل. يرجى إدخال كود فريد.")
                else:
                    raise ValueError(f"فشل تحديث الكوبون: {e}")
            except Exception as e:
                db.rollback()
                raise ValueError(f"فشل تحديث الكوبون بسبب خطأ غير متوقع: {e}")

    def delete_coupon(self, coupon_id: int):
        with get_session() as db:
            return CouponRepository(db).delete_coupon(coupon_id)

    def apply_coupon(self, company_id: int, coupon_code: str, total_amount: float) -> float:
        with get_session() as db:
            coupon = self.get_coupon_by_code(company_id, coupon_code)
            if not coupon or not coupon.is_active:
                raise ValueError("الكوبون غير صالح أو غير نشط.")

            if coupon.valid_until and coupon.valid_until < datetime.now():
                raise ValueError("الكوبون منتهي الصلاحية.")

            if total_amount < coupon.min_purchase_amount:
                raise ValueError(f"الحد الأدنى للشراء لتطبيق هذا الكوبون هو {coupon.min_purchase_amount:.2f}.")

            discount_amount = 0.0
            if coupon.discount_type == "percentage":
                discount_amount = total_amount * (coupon.discount_value / 100)
            elif coupon.discount_type == "fixed_amount":
                discount_amount = coupon.discount_value
            else:
                raise ValueError("نوع الخصم غير مدعوم.")

            return max(0.0, total_amount - discount_amount)

class ShiftService:
    def __init__(self):
        pass

    def open_shift(self, company_id: int, branch_id: int, user_id: int, starting_cash: Decimal = Decimal(0.0)):
        with get_session() as db:
            shift_repo = ShiftRepository(db)
            # Check for existing open shift for this user, branch, company
            existing_shift = shift_repo.get_open_shift(company_id, branch_id, user_id)
            if existing_shift:
                raise ValueError("يوجد وردية مفتوحة بالفعل لهذا المستخدم في هذا الفرع والشركة.")

            shift = models.Shift(
                company_id=company_id,
                branch_id=branch_id,
                user_id=user_id,
                starting_cash=starting_cash,
                status=0 # Open
            )
            return shift_repo.create_shift(shift)

    def close_shift(self, shift_id: int, ending_cash: Decimal):
        with get_session() as db:
            shift_repo = ShiftRepository(db)
            shift = shift_repo.get_shift_by_id(shift_id)
            if not shift:
                raise ValueError("الوردية غير موجودة.")
            if shift.status != 0: # Only close open shifts
                raise ValueError("لا يمكن إغلاق وردية غير مفتوحة.")

            # Calculate totals (simplified for now, actual totals would come from transactions)
            # For now, let's assume total_sales and total_returns are updated by other processes
            # or passed in if this method is called after aggregation
            total_sales = Decimal(0.0) # Placeholder
            total_returns = Decimal(0.0) # Placeholder
            
            # Recalculate based on shift movements
            movement_repo = ShiftMovementRepository(db)
            movements = movement_repo.get_movements_by_shift_id(shift_id)
            for move in movements:
                if move.movement_type == 2: # Sale
                    total_sales += move.amount
                elif move.movement_type == 3: # Return
                    total_returns += move.amount

            # Retrieve starting_cash from the shift object
            starting_cash = shift.starting_cash
            
            net_cash = (starting_cash + total_sales) - total_returns - ending_cash # Simplified

            # Update shift details
            new_data = {
                "end_time": datetime.now(),
                "ending_cash": ending_cash,
                "total_sales": total_sales,
                "total_returns": total_returns,
                "net_cash": net_cash, # This should be the difference between expected and actual cash
                "status": 1 # Closed
            }
            return shift_repo.update_shift(shift_id, new_data)

    def get_shift_by_id(self, shift_id: int):
        with get_session() as db:
            return ShiftRepository(db).get_shift_by_id(shift_id)

    def get_open_shift(self, company_id: int, branch_id: int, user_id: int):
        with get_session() as db:
            return ShiftRepository(db).get_open_shift(company_id, branch_id, user_id)

    def record_shift_movement(self, shift_id: int, movement_type: int, amount: Decimal, notes: str = None, sales_invoice_id: int = None, return_invoice_id: int = None):
        with get_session() as db:
            shift_repo = ShiftRepository(db)
            shift = shift_repo.get_shift_by_id(shift_id)
            if not shift or shift.status != 0:
                raise ValueError("لا يمكن تسجيل حركة على وردية غير موجودة أو مغلقة.")
            
            movement = models.ShiftMovement(
                shift_id=shift_id,
                movement_type=movement_type,
                amount=amount,
                notes=notes,
                sales_invoice_id=sales_invoice_id,
                return_invoice_id=return_invoice_id
            )
            return ShiftMovementRepository(db).create_shift_movement(movement)

    def get_shift_closeout_report(self, shift_id: int):
        with get_session() as db:
            shift_repo = ShiftRepository(db)
            movement_repo = ShiftMovementRepository(db)
            shift = shift_repo.get_shift_by_id(shift_id)
            if not shift:
                raise ValueError("الوردية غير موجودة.")

            movements = movement_repo.get_movements_by_shift_id(shift_id)

            # Aggregate data for the report
            total_cash_in = Decimal(0.0)
            total_cash_out = Decimal(0.0)
            total_sales_amount = Decimal(0.0)
            total_returns_amount = Decimal(0.0)
            num_sales_invoices = 0
            num_return_invoices = 0

            for move in movements:
                if move.movement_type == 0: # Cash In
                    total_cash_in += move.amount
                elif move.movement_type == 1: # Cash Out
                    total_cash_out += move.amount
                elif move.movement_type == 2: # Sale
                    total_sales_amount += move.amount
                    num_sales_invoices += 1
                elif move.movement_type == 3: # Return
                    total_returns_amount += move.amount
                    num_return_invoices += 1
            
            expected_cash_at_close = shift.starting_cash + total_cash_in - total_cash_out + total_sales_amount - total_returns_amount
            cash_difference = shift.ending_cash - expected_cash_at_close if shift.ending_cash is not None else Decimal(0.0)

            report_data = {
                "shift_id": shift.id,
                "user_id": shift.user_id,
                "start_time": shift.start_time,
                "end_time": shift.end_time,
                "starting_cash": shift.starting_cash,
                "ending_cash": shift.ending_cash,
                "total_sales": total_sales_amount,
                "total_returns": total_returns_amount,
                "total_cash_in": total_cash_in,
                "total_cash_out": total_cash_out,
                "expected_cash_at_close": expected_cash_at_close,
                "cash_difference": cash_difference,
                "net_cash_from_shift": shift.net_cash, # This is the recorded net_cash after close_shift
                "num_sales_invoices": num_sales_invoices,
                "num_return_invoices": num_return_invoices,
                "status": shift.status
            }
            return report_data

class GiftCardService:
    def __init__(self):
        pass

    def get_gift_card_by_number(self, card_number: str, company_id: int):
        with get_session() as db:
            return GiftCardRepository(db).get_gift_card_by_number(card_number, company_id)

    def create_gift_card(self, company_id: int, card_number: str, balance: Decimal, expiry_date: datetime = None, is_active: bool = True):
        with get_session() as db:
            try:
                gift_card = GiftCard(
                    company_id=company_id,
                    card_number=card_number,
                    balance=balance,
                    expiry_date=expiry_date,
                    is_active=is_active
                )
                return GiftCardRepository(db).create_gift_card(gift_card)
            except IntegrityError as e:
                db.rollback()
                if "gift_cards_card_number_key" in str(e): # Assuming unique constraint on card number
                    raise ValueError("رقم بطاقة الهدية موجود بالفعل. يرجى إدخال رقم فريد.")
                else:
                    raise ValueError(f"فشل إنشاء بطاقة الهدية: {e}")
            except Exception as e:
                db.rollback()
                raise ValueError(f"فشل إنشاء بطاقة الهدية بسبب خطأ غير متوقع: {e}")

    def top_up_gift_card(self, card_number: str, company_id: int, amount: Decimal):
        with get_session() as db:
            gift_card = self.get_gift_card_by_number(card_number, company_id)
            if not gift_card:
                raise ValueError("بطاقة الهدية غير موجودة أو غير نشطة.")
            if not gift_card.is_active:
                raise ValueError("بطاقة الهدية غير نشطة.")
            if gift_card.expiry_date and gift_card.expiry_date < datetime.now():
                raise ValueError("بطاقة الهدية منتهية الصلاحية.")
            
            new_balance = gift_card.balance + amount
            return GiftCardRepository(db).update_gift_card(gift_card.id, {"balance": new_balance})

    def redeem_gift_card(self, card_number: str, company_id: int, amount: Decimal):
        with get_session() as db:
            gift_card = self.get_gift_card_by_number(card_number, company_id)
            if not gift_card:
                raise ValueError("بطاقة الهدية غير موجودة أو غير نشطة.")
            if not gift_card.is_active:
                raise ValueError("بطاقة الهدية غير نشطة.")
            if gift_card.expiry_date and gift_card.expiry_date < datetime.now():
                raise ValueError("بطاقة الهدية منتهية الصلاحية.")
            if gift_card.balance < amount:
                raise ValueError(f"رصيد بطاقة الهدية غير كافٍ. الرصيد المتاح: {gift_card.balance:.2f}")

            new_balance = gift_card.balance - amount
            return GiftCardRepository(db).update_gift_card(gift_card.id, {"balance": new_balance})

class LoyaltyProgramService:
    def __init__(self):
        pass

    def get_all_loyalty_programs(self, company_id: int):
        with get_session() as db:
            return LoyaltyProgramRepository(db).get_all_loyalty_programs(company_id)

    def get_loyalty_program_by_id(self, program_id: int):
        with get_session() as db:
            return LoyaltyProgramRepository(db).get_loyalty_program_by_id(program_id)

    def create_loyalty_program(self, company_id: int, name_ar: str, name_en: str = None, type: str = "points", points_per_amount: float = 0.0, point_value: float = 0.0, min_redemption_points: int = 0, cashback_percentage: float = 0.0, min_purchase_amount_for_cashback: float = 0.0, is_active: bool = True):
        with get_session() as db:
            try:
                if type == "points":
                    if not (points_per_amount > 0 and point_value > 0 and min_redemption_points >= 0):
                        raise ValueError("لبرنامج النقاط، يجب أن تكون قيمة النقاط لكل مبلغ وقيمة النقطة أكبر من صفر، والحد الأدنى للاسترداد أكبر من أو يساوي صفر.")
                elif type == "cashback":
                    if not (0 <= cashback_percentage <= 100 and min_purchase_amount_for_cashback >= 0):
                        raise ValueError("لبرنامج استرداد النقود، يجب أن تكون نسبة الاسترداد بين 0 و 100%، والحد الأدنى للشراء أكبر من أو يساوي صفر.")
                # Add checks for other types if implemented (tiers, vouchers)
                else:
                    raise ValueError("نوع برنامج الولاء غير مدعوم.")

                loyalty_program = LoyaltyProgram(
                    company_id=company_id,
                    name_ar=name_ar,
                    name_en=name_en,
                    type=type,
                    points_per_amount=points_per_amount,
                    point_value=point_value,
                    min_redemption_points=min_redemption_points,
                    cashback_percentage=cashback_percentage,
                    min_purchase_amount_for_cashback=min_purchase_amount_for_cashback,
                    is_active=is_active
                )
                return LoyaltyProgramRepository(db).create_loyalty_program(loyalty_program)
            except IntegrityError as e:
                db.rollback()
                if "loyalty_programs_name_ar_key" in str(e) or "loyalty_programs_name_en_key" in str(e): # Assuming unique constraints
                    raise ValueError("اسم برنامج الولاء موجود بالفعل. يرجى إدخال اسم فريد.")
                else:
                    raise ValueError(f"فشل إنشاء برنامج الولاء: {e}")
            except Exception as e:
                db.rollback()
                raise ValueError(f"فشل إنشاء برنامج الولاء بسبب خطأ غير متوقع: {e}")

    def update_loyalty_program(self, program_id: int, **kwargs):
        with get_session() as db:
            try:
                # Retrieve existing program to validate updates against its type
                existing_program = self.get_loyalty_program_by_id(program_id)
                if not existing_program:
                    raise ValueError("برنامج الولاء غير موجود.")

                updated_type = kwargs.get('type', existing_program.type)

                if updated_type == "points":
                    points_per_amount = kwargs.get('points_per_amount', existing_program.points_per_amount)
                    point_value = kwargs.get('point_value', existing_program.point_value)
                    min_redemption_points = kwargs.get('min_redemption_points', existing_program.min_redemption_points)
                    if not (points_per_amount > 0 and point_value > 0 and min_redemption_points >= 0):
                        raise ValueError("لبرنامج النقاط، يجب أن تكون قيمة النقاط لكل مبلغ وقيمة النقطة أكبر من صفر، والحد الأدنى للاسترداد أكبر من أو يساوي صفر.")
                elif updated_type == "cashback":
                    cashback_percentage = kwargs.get('cashback_percentage', existing_program.cashback_percentage)
                    min_purchase_amount_for_cashback = kwargs.get('min_purchase_amount_for_cashback', existing_program.min_purchase_amount_for_cashback)
                    if not (0 <= cashback_percentage <= 100 and min_purchase_amount_for_cashback >= 0):
                        raise ValueError("لبرنامج استرداد النقود، يجب أن تكون نسبة الاسترداد بين 0 و 100%، والحد الأدنى للشراء أكبر من أو يساوي صفر.")
                # Add checks for other types if implemented (tiers, vouchers)
                elif updated_type not in ["points", "cashback"]:
                    raise ValueError("نوع برنامج الولاء غير مدعوم.")

                return LoyaltyProgramRepository(db).update_loyalty_program(program_id, kwargs)
            except IntegrityError as e:
                db.rollback()
                if "loyalty_programs_name_ar_key" in str(e) or "loyalty_programs_name_en_key" in str(e):
                    raise ValueError("اسم برنامج الولاء موجود بالفعل. يرجى إدخال اسم فريد.")
                else:
                    raise ValueError(f"فشل تحديث برنامج الولاء: {e}")
            except Exception as e:
                db.rollback()
                raise ValueError(f"فشل تحديث برنامج الولاء بسبب خطأ غير متوقع: {e}")

    def deactivate_loyalty_program(self, program_id: int):
        with get_session() as db:
            return LoyaltyProgramRepository(db).deactivate_loyalty_program(program_id)

class WarehouseService:
    def __init__(self):
        pass

    def get_all_warehouses(self, company_id: int):
        with get_session() as db:
            return WarehouseRepository(db).db.query(models.Warehouse).filter(models.Warehouse.company_id == company_id).all()

    def get_warehouse_by_id(self, warehouse_id: int):
        with get_session() as db:
            return WarehouseRepository(db).get_warehouse_by_id(warehouse_id)

    def create_warehouse(self, company_id: int, branch_id: int, name_ar: str, name_en: str = None, location: str = None, base_currency_id: int = None, is_active: bool = True, created_by: int = 1):
        with get_session() as db:
            try:
                warehouse = models.Warehouse(
                    company_id=company_id,
                    branch_id=branch_id,
                    name_ar=name_ar,
                    name_en=name_en,
                    location=location,
                    base_currency_id=base_currency_id,
                    is_active=is_active,
                    created_by=created_by
                )
                return WarehouseRepository(db).create_warehouse(warehouse)
            except IntegrityError as e:
                db.rollback()
                if "unique_name_ar" in str(e) or "unique_name_en" in str(e):
                    raise ValueError("اسم المخزن موجود بالفعل. يرجى إدخال اسم فريد.")
                else:
                    raise ValueError(f"فشل إنشاء المخزن: {e}")
            except Exception as e:
                db.rollback()
                raise ValueError(f"فشل إنشاء المخزن بسبب خطأ غير متوقع: {e}")

    def update_warehouse(self, warehouse_id: int, **kwargs):
        with get_session() as db:
            return WarehouseRepository(db).update_warehouse(warehouse_id, kwargs)

    def delete_warehouse(self, warehouse_id: int):
        with get_session() as db:
            return WarehouseRepository(db).delete_warehouse(warehouse_id)

    # Stock Movement Operations
    def get_all_stock_movements(self):
        with get_session() as db:
            return StockMovementRepository(db).get_all_stock_movements()

    def record_stock_movement(self, company_id: int, branch_id: int, item_id: int, movement_type: int, quantity: Decimal, cost: Decimal = Decimal(0), movement_date: date = None, ref_no: str = None, created_by: int = 1):
        with get_session() as db:
            if not movement_date:
                movement_date = date.today()

            stock_movement = models.StockMovement(
                company_id=company_id,
                branch_id=branch_id,
                item_id=item_id,
                movement_type=movement_type,
                quantity=quantity,
                cost=cost,
                movement_date=movement_date,
                ref_no=ref_no,
                created_by=created_by
            )
            return StockMovementRepository(db).create_stock_movement(stock_movement)

    def get_stock_movements_by_item(self, item_id: int):
        with get_session() as db:
            return StockMovementRepository(db).db.query(models.StockMovement).filter(models.StockMovement.item_id == item_id).all()

    def get_item_stock_level(self, item_id: int, warehouse_id: int) -> float:
        with get_session() as db:
            # Calculate total 'in' movements (received items)
            total_in = db.query(func.sum(models.StockMovement.quantity)).filter(
                models.StockMovement.item_id == item_id,
                models.StockMovement.warehouse_id == warehouse_id,
                models.StockMovement.movement_type == 0  # Assuming 0 is 'in' movement type
            ).scalar() or 0.0

            # Calculate total 'out' movements (sold/returned items)
            total_out = db.query(func.sum(models.StockMovement.quantity)).filter(
                models.StockMovement.item_id == item_id,
                models.StockMovement.warehouse_id == warehouse_id,
                (models.StockMovement.movement_type == 1) | (models.StockMovement.movement_type == 3) # Assuming 1 is 'out' (sales) and 3 is 'returns'
            ).scalar() or 0.0

            current_stock = total_in - total_out
            return float(current_stock)

    def update_stock_movement(self, movement_id: int, **kwargs):
        with get_session() as db:
            return StockMovementRepository(db).update_stock_movement(movement_id, kwargs)

    def delete_stock_movement(self, movement_id: int):
        with get_session() as db:
            return StockMovementRepository(db).delete_stock_movement(movement_id)
