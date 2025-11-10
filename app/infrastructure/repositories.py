from sqlalchemy.orm import Session, joinedload
from app.domain.models import Account, JournalEntry, JournalLine, Customer, Supplier, Invoice, Payment, Item, StockMovement, SalesOrder, PurchaseOrder, BankTransaction, BankReconciliation, FixedAsset, Depreciation, TaxSetting, TaxReport, User, Role, Permission, UserRole, RolePermission, Company, Branch, FiscalPeriod, CostCenter, Project, Employee, Payrun, Notification, Workflow, InvoiceLine, Warehouse, Shift, ShiftMovement, InvoicePayment # Added Warehouse model
from app.domain.settings_models import Unit, Currency, PaymentMethod, Coupon, GiftCard, LoyaltyProgram # Import new settings models and GiftCard and LoyaltyProgram

class AccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_accounts(self):
        return self.db.query(Account).all()

    def get_account_by_id(self, account_id: int):
        return self.db.query(Account).filter(Account.id == account_id).first()

    def create_account(self, account: Account):
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def update_account(self, account_id: int, new_data: dict):
        db_account = self.get_account_by_id(account_id)
        if db_account:
            for key, value in new_data.items():
                setattr(db_account, key, value)
            self.db.commit()
            self.db.refresh(db_account)
        return db_account

    def delete_account(self, account_id: int):
        db_account = self.get_account_by_id(account_id)
        if db_account:
            self.db.delete(db_account)
            self.db.commit()
        return db_account

class JournalEntryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_journal_entries(self):
        return self.db.query(JournalEntry).all()

    def get_journal_entry_by_id(self, entry_id: int):
        return self.db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()

    def create_journal_entry(self, journal_entry: JournalEntry):
        self.db.add(journal_entry)
        self.db.commit()
        self.db.refresh(journal_entry)
        return journal_entry

    def update_journal_entry(self, entry_id: int, new_data: dict):
        db_entry = self.get_journal_entry_by_id(entry_id)
        if db_entry:
            for key, value in new_data.items():
                setattr(db_entry, key, value)
            self.db.commit()
            self.db.refresh(db_entry)
        return db_entry

    def delete_journal_entry(self, entry_id: int):
        db_entry = self.get_journal_entry_by_id(entry_id)
        if db_entry:
            self.db.delete(db_entry)
            self.db.commit()
        return db_entry

class JournalLineRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_lines_by_entry_id(self, entry_id: int):
        return self.db.query(JournalLine).filter(JournalLine.entry_id == entry_id).all()

    def create_journal_line(self, journal_line: JournalLine):
        self.db.add(journal_line)
        self.db.commit()
        self.db.refresh(journal_line)
        return journal_line

    def update_journal_line(self, line_id: int, new_data: dict):
        db_line = self.db.query(JournalLine).filter(JournalLine.id == line_id).first()
        if db_line:
            for key, value in new_data.items():
                setattr(db_line, key, value)
            self.db.commit()
            self.db.refresh(db_line)
        return db_line

    def delete_journal_line(self, line_id: int):
        db_line = self.db.query(JournalLine).filter(JournalLine.id == line_id).first()
        if db_line:
            self.db.delete(db_line)
            self.db.commit()
        return db_line

class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_customers(self):
        return self.db.query(Customer).all()

    def get_customer_by_id(self, customer_id: int):
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def create_customer(self, customer: Customer):
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def update_customer(self, customer_id: int, new_data: dict):
        db_customer = self.get_customer_by_id(customer_id)
        if db_customer:
            for key, value in new_data.items():
                setattr(db_customer, key, value)
            self.db.commit()
            self.db.refresh(db_customer)
        return db_customer

    def delete_customer(self, customer_id: int):
        db_customer = self.get_customer_by_id(customer_id)
        if db_customer:
            self.db.delete(db_customer)
            self.db.commit()
        return db_customer

class SupplierRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_suppliers(self):
        return self.db.query(Supplier).all()

    def get_supplier_by_id(self, supplier_id: int):
        return self.db.query(Supplier).filter(Supplier.id == supplier_id).first()

    def create_supplier(self, supplier: Supplier):
        self.db.add(supplier)
        self.db.commit()
        self.db.refresh(supplier)
        return supplier

    def update_supplier(self, supplier_id: int, new_data: dict):
        db_supplier = self.get_supplier_by_id(supplier_id)
        if db_supplier:
            for key, value in new_data.items():
                setattr(db_supplier, key, value)
            self.db.commit()
            self.db.refresh(db_supplier)
        return db_supplier

    def delete_supplier(self, supplier_id: int):
        db_supplier = self.get_supplier_by_id(supplier_id)
        if db_supplier:
            self.db.delete(db_supplier)
            self.db.commit()
        return db_supplier

class InvoiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_invoices(self):
        return self.db.query(Invoice).all()

    def get_invoice_by_id(self, invoice_id: int):
        return self.db.query(Invoice).filter(Invoice.id == invoice_id).options(joinedload(Invoice.lines), joinedload(Invoice.customer), joinedload(Invoice.supplier)).first()

    def create_invoice(self, invoice: Invoice):
        self.db.add(invoice)
        self.db.flush() # Flush to get invoice.id before committing lines
        for line in invoice.lines:
            line.invoice_id = invoice.id
            self.db.add(line)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def update_invoice(self, invoice_id: int, new_data: dict):
        db_invoice = self.get_invoice_by_id(invoice_id)
        if db_invoice:
            for key, value in new_data.items():
                if key == 'lines':
                    # Handle lines update separately if needed, for now assuming they are managed via invoice relationship
                    continue
                setattr(db_invoice, key, value)
            self.db.commit()
            self.db.refresh(db_invoice)
        return db_invoice

    def delete_invoice(self, invoice_id: int):
        db_invoice = self.get_invoice_by_id(invoice_id)
        if db_invoice:
            self.db.delete(db_invoice)
            self.db.commit()
        return db_invoice

class InvoiceLineRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_line_by_id(self, line_id: int):
        return self.db.query(InvoiceLine).filter(InvoiceLine.id == line_id).first()

    def get_lines_by_invoice_id(self, invoice_id: int):
        return self.db.query(InvoiceLine).filter(InvoiceLine.invoice_id == invoice_id).all()

    def create_invoice_line(self, invoice_line: InvoiceLine):
        self.db.add(invoice_line)
        self.db.commit()
        self.db.refresh(invoice_line)
        return invoice_line

    def update_invoice_line(self, line_id: int, new_data: dict):
        db_line = self.get_line_by_id(line_id)
        if db_line:
            for key, value in new_data.items():
                setattr(db_line, key, value)
            self.db.commit()
            self.db.refresh(db_line)
        return db_line

    def delete_invoice_line(self, line_id: int):
        db_line = self.get_line_by_id(line_id)
        if db_line:
            self.db.delete(db_line)
            self.db.commit()
        return db_line

class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_payments(self):
        return self.db.query(Payment).all()

    def get_payment_by_id(self, payment_id: int):
        return self.db.query(Payment).filter(Payment.id == payment_id).first()

    def create_payment(self, payment: Payment):
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def update_payment(self, payment_id: int, new_data: dict):
        db_payment = self.get_payment_by_id(payment_id)
        if db_payment:
            for key, value in new_data.items():
                setattr(db_payment, key, value)
            self.db.commit()
            self.db.refresh(db_payment)
        return db_payment

    def delete_payment(self, payment_id: int):
        db_payment = self.get_payment_by_id(payment_id)
        if db_payment:
            self.db.delete(db_payment)
            self.db.commit()
        return db_payment

class ItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_items(self):
        return self.db.query(Item).all()

    def get_item_by_id(self, item_id: int):
        return self.db.query(Item).filter(Item.id == item_id).first()

    def get_item_by_barcode(self, barcode: str):
        return self.db.query(Item).filter(Item.barcode == barcode).first()

    def create_item(self, item: Item):
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_item(self, item_id: int, new_data: dict):
        db_item = self.get_item_by_id(item_id)
        if db_item:
            for key, value in new_data.items():
                setattr(db_item, key, value)
            self.db.commit()
            self.db.refresh(db_item)
        return db_item

    def delete_item(self, item_id: int):
        db_item = self.get_item_by_id(item_id)
        if db_item:
            self.db.delete(db_item)
            self.db.commit()
        return db_item

class StockMovementRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_stock_movements(self):
        return self.db.query(StockMovement).all()

    def get_stock_movement_by_id(self, movement_id: int):
        return self.db.query(StockMovement).filter(StockMovement.id == movement_id).first()

    def create_stock_movement(self, stock_movement: StockMovement):
        self.db.add(stock_movement)
        self.db.commit()
        self.db.refresh(stock_movement)
        return stock_movement

    def update_stock_movement(self, movement_id: int, new_data: dict):
        db_movement = self.get_stock_movement_by_id(movement_id)
        if db_movement:
            for key, value in new_data.items():
                setattr(db_movement, key, value)
            self.db.commit()
            self.db.refresh(db_movement)
        return db_movement

    def delete_stock_movement(self, movement_id: int):
        db_movement = self.get_stock_movement_by_id(movement_id)
        if db_movement:
            self.db.delete(db_movement)
            self.db.commit()
        return db_movement

class SalesOrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_sales_orders(self):
        return self.db.query(SalesOrder).all()

    def get_sales_order_by_id(self, order_id: int):
        return self.db.query(SalesOrder).filter(SalesOrder.id == order_id).first()

    def create_sales_order(self, sales_order: SalesOrder):
        self.db.add(sales_order)
        self.db.commit()
        self.db.refresh(sales_order)
        return sales_order

    def update_sales_order(self, order_id: int, new_data: dict):
        db_order = self.get_sales_order_by_id(order_id)
        if db_order:
            for key, value in new_data.items():
                setattr(db_order, key, value)
            self.db.commit()
            self.db.refresh(db_order)
        return db_order

    def delete_sales_order(self, order_id: int):
        db_order = self.get_sales_order_by_id(order_id)
        if db_order:
            self.db.delete(db_order)
            self.db.commit()
        return db_order

class PurchaseOrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_purchase_orders(self):
        return self.db.query(PurchaseOrder).options(joinedload(PurchaseOrder.supplier)).all()

    def get_purchase_order_by_id(self, order_id: int):
        return self.db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).options(joinedload(PurchaseOrder.supplier)).first()

    def create_purchase_order(self, purchase_order: PurchaseOrder):
        self.db.add(purchase_order)
        self.db.commit()
        self.db.refresh(purchase_order)
        return purchase_order

    def update_purchase_order(self, order_id: int, new_data: dict):
        db_order = self.get_purchase_order_by_id(order_id)
        if db_order:
            for key, value in new_data.items():
                setattr(db_order, key, value)
            self.db.commit()
            self.db.refresh(db_order)
        return db_order

    def delete_purchase_order(self, order_id: int):
        db_order = self.get_purchase_order_by_id(order_id)
        if db_order:
            self.db.delete(db_order)
            self.db.commit()
        return db_order

class BankTransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_bank_transactions(self):
        return self.db.query(BankTransaction).all()

    def get_bank_transaction_by_id(self, transaction_id: int):
        return self.db.query(BankTransaction).filter(BankTransaction.id == transaction_id).first()

    def create_bank_transaction(self, bank_transaction: BankTransaction):
        self.db.add(bank_transaction)
        self.db.commit()
        self.db.refresh(bank_transaction)
        return bank_transaction

    def update_bank_transaction(self, transaction_id: int, new_data: dict):
        db_transaction = self.get_bank_transaction_by_id(transaction_id)
        if db_transaction:
            for key, value in new_data.items():
                setattr(db_transaction, key, value)
            self.db.commit()
            self.db.refresh(db_transaction)
        return db_transaction

    def delete_bank_transaction(self, transaction_id: int):
        db_transaction = self.get_bank_transaction_by_id(transaction_id)
        if db_transaction:
            self.db.delete(db_transaction)
            self.db.commit()
        return db_transaction

class BankReconciliationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_bank_reconciliations(self):
        return self.db.query(BankReconciliation).all()

    def get_bank_reconciliation_by_id(self, reconciliation_id: int):
        return self.db.query(BankReconciliation).filter(BankReconciliation.id == reconciliation_id).first()

    def create_bank_reconciliation(self, bank_reconciliation: BankReconciliation):
        self.db.add(bank_reconciliation)
        self.db.commit()
        self.db.refresh(bank_reconciliation)
        return bank_reconciliation

    def update_bank_reconciliation(self, reconciliation_id: int, new_data: dict):
        db_reconciliation = self.get_bank_reconciliation_by_id(reconciliation_id)
        if db_reconciliation:
            for key, value in new_data.items():
                setattr(db_reconciliation, key, value)
            self.db.commit()
            self.db.refresh(db_reconciliation)
        return db_reconciliation

    def delete_bank_reconciliation(self, reconciliation_id: int):
        db_reconciliation = self.get_bank_reconciliation_by_id(reconciliation_id)
        if db_reconciliation:
            self.db.delete(db_reconciliation)
            self.db.commit()
        return db_reconciliation

class FixedAssetRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_fixed_assets(self):
        return self.db.query(FixedAsset).all()

    def get_fixed_asset_by_id(self, asset_id: int):
        return self.db.query(FixedAsset).filter(FixedAsset.id == asset_id).first()

    def create_fixed_asset(self, fixed_asset: FixedAsset):
        self.db.add(fixed_asset)
        self.db.commit()
        self.db.refresh(fixed_asset)
        return fixed_asset

    def update_fixed_asset(self, asset_id: int, new_data: dict):
        db_asset = self.get_fixed_asset_by_id(asset_id)
        if db_asset:
            for key, value in new_data.items():
                setattr(db_asset, key, value)
            self.db.commit()
            self.db.refresh(db_asset)
        return db_asset

    def delete_fixed_asset(self, asset_id: int):
        db_asset = self.get_fixed_asset_by_id(asset_id)
        if db_asset:
            self.db.delete(db_asset)
            self.db.commit()
        return db_asset

class DepreciationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_depreciations(self):
        return self.db.query(Depreciation).all()

    def get_depreciation_by_id(self, depreciation_id: int):
        return self.db.query(Depreciation).filter(Depreciation.id == depreciation_id).first()

    def create_depreciation(self, depreciation: Depreciation):
        self.db.add(depreciation)
        self.db.commit()
        self.db.refresh(depreciation)
        return depreciation

    def update_depreciation(self, depreciation_id: int, new_data: dict):
        db_depreciation = self.get_depreciation_by_id(depreciation_id)
        if db_depreciation:
            for key, value in new_data.items():
                setattr(db_depreciation, key, value)
            self.db.commit()
            self.db.refresh(db_depreciation)
        return db_depreciation

    def delete_depreciation(self, depreciation_id: int):
        db_depreciation = self.get_depreciation_by_id(depreciation_id)
        if db_depreciation:
            self.db.delete(db_depreciation)
            self.db.commit()
        return db_depreciation

class TaxSettingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_tax_settings(self):
        return self.db.query(TaxSetting).all()

    def get_tax_setting_by_id(self, setting_id: int):
        return self.db.query(TaxSetting).filter(TaxSetting.id == setting_id).first()

    def create_tax_setting(self, tax_setting: TaxSetting):
        self.db.add(tax_setting)
        self.db.commit()
        self.db.refresh(tax_setting)
        return tax_setting

    def update_tax_setting(self, setting_id: int, new_data: dict):
        db_setting = self.get_tax_setting_by_id(setting_id)
        if db_setting:
            for key, value in new_data.items():
                setattr(db_setting, key, value)
            self.db.commit()
            self.db.refresh(db_setting)
        return db_setting

    def delete_tax_setting(self, setting_id: int):
        db_setting = self.get_tax_setting_by_id(setting_id)
        if db_setting:
            self.db.delete(db_setting)
            self.db.commit()
        return db_setting

class TaxReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_tax_reports(self):
        return self.db.query(TaxReport).all()

    def get_tax_report_by_id(self, report_id: int):
        return self.db.query(TaxReport).filter(TaxReport.id == report_id).first()

    def create_tax_report(self, tax_report: TaxReport):
        self.db.add(tax_report)
        self.db.commit()
        self.db.refresh(tax_report)
        return tax_report

    def update_tax_report(self, report_id: int, new_data: dict):
        db_report = self.get_tax_report_by_id(report_id)
        if db_report:
            for key, value in new_data.items():
                setattr(db_report, key, value)
            self.db.commit()
            self.db.refresh(db_report)
        return db_report

    def delete_tax_report(self, report_id: int):
        db_report = self.get_tax_report_by_id(report_id)
        if db_report:
            self.db.delete(db_report)
            self.db.commit()
        return db_report

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_users(self):
        return self.db.query(User).all()

    def get_user_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user: User):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user_id: int, new_data: dict):
        db_user = self.get_user_by_id(user_id)
        if db_user:
            for key, value in new_data.items():
                setattr(db_user, key, value)
            self.db.commit()
            self.db.refresh(db_user)
        return db_user

    def delete_user(self, user_id: int):
        db_user = self.get_user_by_id(user_id)
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
        return db_user

class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_roles(self):
        return self.db.query(Role).all()

    def get_role_by_id(self, role_id: int):
        return self.db.query(Role).filter(Role.id == role_id).first()

    def create_role(self, role: Role):
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def update_role(self, role_id: int, new_data: dict):
        db_role = self.get_role_by_id(role_id)
        if db_role:
            for key, value in new_data.items():
                setattr(db_role, key, value)
            self.db.commit()
            self.db.refresh(db_role)
        return db_role

    def delete_role(self, role_id: int):
        db_role = self.get_role_by_id(role_id)
        if db_role:
            self.db.delete(db_role)
            self.db.commit()
        return db_role

class PermissionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_permissions(self):
        return self.db.query(Permission).all()

    def get_permission_by_id(self, permission_id: int):
        return self.db.query(Permission).filter(Permission.id == permission_id).first()

    def create_permission(self, permission: Permission):
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        return permission

    def update_permission(self, permission_id: int, new_data: dict):
        db_permission = self.get_permission_by_id(permission_id)
        if db_permission:
            for key, value in new_data.items():
                setattr(db_permission, key, value)
            self.db.commit()
            self.db.refresh(db_permission)
        return db_permission

    def delete_permission(self, permission_id: int):
        db_permission = self.get_permission_by_id(permission_id)
        if db_permission:
            self.db.delete(db_permission)
            self.db.commit()
        return db_permission

class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_companies(self):
        return self.db.query(Company).all()

    def get_company_by_id(self, company_id: int):
        return self.db.query(Company).filter(Company.id == company_id).first()

    def create_company(self, company: Company):
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def update_company(self, company_id: int, new_data: dict):
        db_company = self.get_company_by_id(company_id)
        if db_company:
            for key, value in new_data.items():
                setattr(db_company, key, value)
            self.db.commit()
            self.db.refresh(db_company)
        return db_company

    def delete_company(self, company_id: int):
        db_company = self.get_company_by_id(company_id)
        if db_company:
            self.db.delete(db_company)
            self.db.commit()
        return db_company

class BranchRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_branches(self):
        return self.db.query(Branch).all()

    def get_branch_by_id(self, branch_id: int):
        return self.db.query(Branch).filter(Branch.id == branch_id).first()

    def create_branch(self, branch: Branch):
        self.db.add(branch)
        self.db.commit()
        self.db.refresh(branch)
        return branch

    def update_branch(self, branch_id: int, new_data: dict):
        db_branch = self.get_branch_by_id(branch_id)
        if db_branch:
            for key, value in new_data.items():
                setattr(db_branch, key, value)
            self.db.commit()
            self.db.refresh(db_branch)
        return db_branch

    def delete_branch(self, branch_id: int):
        db_branch = self.get_branch_by_id(branch_id)
        if db_branch:
            self.db.delete(db_branch)
            self.db.commit()
        return db_branch

class FiscalPeriodRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_fiscal_periods(self):
        return self.db.query(FiscalPeriod).all()

    def get_fiscal_period_by_id(self, period_id: int):
        return self.db.query(FiscalPeriod).filter(FiscalPeriod.id == period_id).first()

    def create_fiscal_period(self, fiscal_period: FiscalPeriod):
        self.db.add(fiscal_period)
        self.db.commit()
        self.db.refresh(fiscal_period)
        return fiscal_period

    def update_fiscal_period(self, period_id: int, new_data: dict):
        db_period = self.get_fiscal_period_by_id(period_id)
        if db_period:
            for key, value in new_data.items():
                setattr(db_period, key, value)
            self.db.commit()
            self.db.refresh(db_period)
        return db_period

    def delete_fiscal_period(self, period_id: int):
        db_period = self.get_fiscal_period_by_id(period_id)
        if db_period:
            self.db.delete(db_period)
            self.db.commit()
        return db_period

class WarehouseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_warehouses(self):
        return self.db.query(Warehouse).all()

    def get_warehouse_by_id(self, warehouse_id: int):
        return self.db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()

    def create_warehouse(self, warehouse: Warehouse):
        self.db.add(warehouse)
        self.db.commit()
        self.db.refresh(warehouse)
        return warehouse

    def update_warehouse(self, warehouse_id: int, new_data: dict):
        db_warehouse = self.get_warehouse_by_id(warehouse_id)
        if db_warehouse:
            for key, value in new_data.items():
                setattr(db_warehouse, key, value)
            self.db.commit()
            self.db.refresh(db_warehouse)
        return db_warehouse

    def delete_warehouse(self, warehouse_id: int):
        db_warehouse = self.get_warehouse_by_id(warehouse_id)
        if db_warehouse:
            self.db.delete(db_warehouse)
            self.db.commit()
        return db_warehouse

class CostCenterRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_cost_centers(self):
        return self.db.query(CostCenter).all()

    def get_cost_center_by_id(self, cost_center_id: int):
        return self.db.query(CostCenter).filter(CostCenter.id == cost_center_id).first()

    def create_cost_center(self, cost_center: CostCenter):
        self.db.add(cost_center)
        self.db.commit()
        self.db.refresh(cost_center)
        return cost_center

    def update_cost_center(self, cost_center_id: int, new_data: dict):
        db_cost_center = self.get_cost_center_by_id(cost_center_id)
        if db_cost_center:
            for key, value in new_data.items():
                setattr(db_cost_center, key, value)
            self.db.commit()
            self.db.refresh(db_cost_center)
        return db_cost_center

    def delete_cost_center(self, cost_center_id: int):
        db_cost_center = self.get_cost_center_by_id(cost_center_id)
        if db_cost_center:
            self.db.delete(db_cost_center)
            self.db.commit()
        return db_cost_center

class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_projects(self):
        return self.db.query(Project).all()

    def get_project_by_id(self, project_id: int):
        return self.db.query(Project).filter(Project.id == project_id).first()

    def create_project(self, project: Project):
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update_project(self, project_id: int, new_data: dict):
        db_project = self.get_project_by_id(project_id)
        if db_project:
            for key, value in new_data.items():
                setattr(db_project, key, value)
            self.db.commit()
            self.db.refresh(db_project)
        return db_project

    def delete_project(self, project_id: int):
        db_project = self.get_project_by_id(project_id)
        if db_project:
            self.db.delete(db_project)
            self.db.commit()
        return db_project

class EmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_employees(self):
        return self.db.query(Employee).all()

    def get_employee_by_id(self, employee_id: int):
        return self.db.query(Employee).filter(Employee.id == employee_id).first()

    def create_employee(self, employee: Employee):
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)
        return employee

    def update_employee(self, employee_id: int, new_data: dict):
        db_employee = self.get_employee_by_id(employee_id)
        if db_employee:
            for key, value in new_data.items():
                setattr(db_employee, key, value)
            self.db.commit()
            self.db.refresh(db_employee)
        return db_employee

    def delete_employee(self, employee_id: int):
        db_employee = self.get_employee_by_id(employee_id)
        if db_employee:
            self.db.delete(db_employee)
            self.db.commit()
        return db_employee

class PayrunRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_payruns(self):
        return self.db.query(Payrun).all()

    def get_payrun_by_id(self, payrun_id: int):
        return self.db.query(Payrun).filter(Payrun.id == payrun_id).first()

    def create_payrun(self, payrun: Payrun):
        self.db.add(payrun)
        self.db.commit()
        self.db.refresh(payrun)
        return payrun

    def update_payrun(self, payrun_id: int, new_data: dict):
        db_payrun = self.get_payrun_by_id(payrun_id)
        if db_payrun:
            for key, value in new_data.items():
                setattr(db_payrun, key, value)
            self.db.commit()
            self.db.refresh(db_payrun)
        return db_payrun

    def delete_payrun(self, payrun_id: int):
        db_payrun = self.get_payrun_by_id(payrun_id)
        if db_payrun:
            self.db.delete(db_payrun)
            self.db.commit()
        return db_payrun

class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_notifications(self):
        return self.db.query(Notification).all()

    def get_notification_by_id(self, notification_id: int):
        return self.db.query(Notification).filter(Notification.id == notification_id).first()

    def create_notification(self, notification: Notification):
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def update_notification(self, notification_id: int, new_data: dict):
        db_notification = self.get_notification_by_id(notification_id)
        if db_notification:
            for key, value in new_data.items():
                setattr(db_notification, key, value)
            self.db.commit()
            self.db.refresh(db_notification)
        return db_notification

    def delete_notification(self, notification_id: int):
        db_notification = self.get_notification_by_id(notification_id)
        if db_notification:
            self.db.delete(db_notification)
            self.db.commit()
        return db_notification

class WorkflowRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_workflows(self):
        return self.db.query(Workflow).all()

    def get_workflow_by_id(self, workflow_id: int):
        return self.db.query(Workflow).filter(Workflow.id == workflow_id).first()

    def create_workflow(self, workflow: Workflow):
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        return workflow

    def update_workflow(self, workflow_id: int, new_data: dict):
        db_workflow = self.get_workflow_by_id(workflow_id)
        if db_workflow:
            for key, value in new_data.items():
                setattr(db_workflow, key, value)
            self.db.commit()
            self.db.refresh(db_workflow)
        return db_workflow

    def delete_workflow(self, workflow_id: int):
        db_workflow = self.get_workflow_by_id(workflow_id)
        if db_workflow:
            self.db.delete(db_workflow)
            self.db.commit()
        return db_workflow

class UnitRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_units(self):
        return self.db.query(Unit).all()

    def get_unit_by_id(self, unit_id: int):
        return self.db.query(Unit).filter(Unit.id == unit_id).first()

    def create_unit(self, unit: Unit):
        self.db.add(unit)
        self.db.commit()
        self.db.refresh(unit)
        return unit

    def update_unit(self, unit_id: int, new_data: dict):
        db_unit = self.get_unit_by_id(unit_id)
        if db_unit:
            for key, value in new_data.items():
                setattr(db_unit, key, value)
            self.db.commit()
            self.db.refresh(db_unit)
        return db_unit

    def delete_unit(self, unit_id: int):
        db_unit = self.get_unit_by_id(unit_id)
        if db_unit:
            self.db.delete(db_unit)
            self.db.commit()
        return db_unit

class CurrencyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_currencies(self):
        return self.db.query(Currency).all()

    def get_currency_by_id(self, currency_id: int):
        return self.db.query(Currency).filter(Currency.id == currency_id).first()

    def create_currency(self, currency: Currency):
        self.db.add(currency)
        self.db.commit()
        self.db.refresh(currency)
        return currency

    def update_currency(self, currency_id: int, new_data: dict):
        db_currency = self.get_currency_by_id(currency_id)
        if db_currency:
            for key, value in new_data.items():
                setattr(db_currency, key, value)
            self.db.commit()
            self.db.refresh(db_currency)
        return db_currency

    def delete_currency(self, currency_id: int):
        db_currency = self.get_currency_by_id(currency_id)
        if db_currency:
            self.db.delete(db_currency)
            self.db.commit()
        return db_currency

class PaymentMethodRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_payment_methods(self, company_id: int):
        return self.db.query(PaymentMethod).filter(PaymentMethod.company_id == company_id, PaymentMethod.is_active == True).all()

    def get_payment_method_by_id(self, method_id: int):
        return self.db.query(PaymentMethod).filter(PaymentMethod.id == method_id).first()

    def create_payment_method(self, payment_method: PaymentMethod):
        self.db.add(payment_method)
        self.db.commit()
        self.db.refresh(payment_method)
        return payment_method

    def update_payment_method(self, method_id: int, new_data: dict):
        db_method = self.get_payment_method_by_id(method_id)
        if db_method:
            for key, value in new_data.items():
                setattr(db_method, key, value)
            self.db.commit()
            self.db.refresh(db_method)
        return db_method

    def delete_payment_method(self, method_id: int):
        db_method = self.get_payment_method_by_id(method_id)
        if db_method:
            self.db.delete(db_method)
            self.db.commit()
        return db_method

class CouponRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_coupons(self, company_id: int):
        return self.db.query(Coupon).filter(Coupon.company_id == company_id, Coupon.is_active == True).all()

    def get_coupon_by_id(self, coupon_id: int):
        return self.db.query(Coupon).filter(Coupon.id == coupon_id).first()

    def get_coupon_by_code(self, company_id: int, code: str):
        return self.db.query(Coupon).filter(Coupon.company_id == company_id, Coupon.code == code, Coupon.is_active == True).first()

    def create_coupon(self, coupon: Coupon):
        self.db.add(coupon)
        self.db.commit()
        self.db.refresh(coupon)
        return coupon

    def update_coupon(self, coupon_id: int, new_data: dict):
        db_coupon = self.get_coupon_by_id(coupon_id)
        if db_coupon:
            for key, value in new_data.items():
                setattr(db_coupon, key, value)
            self.db.commit()
            self.db.refresh(db_coupon)
        return db_coupon

    def delete_coupon(self, coupon_id: int):
        db_coupon = self.get_coupon_by_id(coupon_id)
        if db_coupon:
            self.db.delete(db_coupon)
            self.db.commit()
        return db_coupon

class ShiftRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_shift_by_id(self, shift_id: int):
        return self.db.query(Shift).filter(Shift.id == shift_id).first()

    def get_open_shift(self, company_id: int, branch_id: int, user_id: int):
        return self.db.query(Shift).filter(Shift.company_id == company_id, Shift.branch_id == branch_id, Shift.user_id == user_id, Shift.status == 0).first()

    def create_shift(self, shift: Shift):
        self.db.add(shift)
        self.db.commit()
        self.db.refresh(shift)
        return shift

    def update_shift(self, shift_id: int, new_data: dict):
        db_shift = self.get_shift_by_id(shift_id)
        if db_shift:
            for key, value in new_data.items():
                setattr(db_shift, key, value)
            self.db.commit()
            self.db.refresh(db_shift)
        return db_shift

class ShiftMovementRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_shift_movement(self, movement: ShiftMovement):
        self.db.add(movement)
        self.db.commit()
        self.db.refresh(movement)
        return movement

    def get_movements_by_shift_id(self, shift_id: int):
        return self.db.query(ShiftMovement).filter(ShiftMovement.shift_id == shift_id).all()

class InvoicePaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_invoice_payment(self, invoice_payment: InvoicePayment):
        self.db.add(invoice_payment)
        self.db.commit()
        self.db.refresh(invoice_payment)
        return invoice_payment

    def get_payments_by_invoice_id(self, invoice_id: int):
        return self.db.query(InvoicePayment).filter(InvoicePayment.invoice_id == invoice_id).options(joinedload(InvoicePayment.payment_method)).all()

    def delete_invoice_payments_by_invoice_id(self, invoice_id: int):
        self.db.query(InvoicePayment).filter(InvoicePayment.invoice_id == invoice_id).delete()
        self.db.commit()

class GiftCardRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_gift_card_by_number(self, card_number: str, company_id: int):
        return self.db.query(GiftCard).filter(GiftCard.card_number == card_number, GiftCard.company_id == company_id, GiftCard.is_active == True).first()

    def create_gift_card(self, gift_card: GiftCard):
        self.db.add(gift_card)
        self.db.commit()
        self.db.refresh(gift_card)
        return gift_card

    def update_gift_card(self, gift_card_id: int, new_data: dict):
        db_gift_card = self.db.query(GiftCard).filter(GiftCard.id == gift_card_id).first()
        if db_gift_card:
            for key, value in new_data.items():
                setattr(db_gift_card, key, value)
            self.db.commit()
            self.db.refresh(db_gift_card)
        return db_gift_card

    def deactivate_gift_card(self, gift_card_id: int):
        db_gift_card = self.db.query(GiftCard).filter(GiftCard.id == gift_card_id).first()
        if db_gift_card:
            db_gift_card.is_active = False
            self.db.commit()
            self.db.refresh(db_gift_card)
        return db_gift_card

class LoyaltyProgramRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_loyalty_programs(self, company_id: int):
        return self.db.query(LoyaltyProgram).filter(LoyaltyProgram.company_id == company_id, LoyaltyProgram.is_active == True).all()

    def get_loyalty_program_by_id(self, program_id: int):
        return self.db.query(LoyaltyProgram).filter(LoyaltyProgram.id == program_id).first()

    def create_loyalty_program(self, program: LoyaltyProgram):
        self.db.add(program)
        self.db.commit()
        self.db.refresh(program)
        return program

    def update_loyalty_program(self, program_id: int, new_data: dict):
        db_program = self.get_loyalty_program_by_id(program_id)
        if db_program:
            for key, value in new_data.items():
                setattr(db_program, key, value)
            self.db.commit()
            self.db.refresh(db_program)
        return db_program

    def deactivate_loyalty_program(self, program_id: int):
        db_program = self.get_loyalty_program_by_id(program_id)
        if db_program:
            db_program.is_active = False
            self.db.commit()
            self.db.refresh(db_program)
        return db_program
