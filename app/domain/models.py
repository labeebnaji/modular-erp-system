from sqlalchemy import Column, Integer, String, Boolean, SmallInteger, Numeric, ForeignKey, Text, Date, TIMESTAMP, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
import enum
from sqlalchemy.schema import Sequence # Import Sequence
import datetime
from app.domain.settings_models import Unit, Currency, PaymentMethod
from app.infrastructure.database import Base # Import Base from database.py

class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    name_ar = Column(Text, nullable=False)
    name_en = Column(Text)
    type = Column(SmallInteger, nullable=False)
    level = Column(SmallInteger, nullable=False)
    parent_id = Column(Integer, ForeignKey("account.id"))
    currency = Column(String(3), nullable=False)
    is_postable = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    parent = relationship("Account", remote_side=[id])

    def __repr__(self):
        return f"<Account(code='{self.code}', name_ar='{self.name_ar}')>"

class JournalEntry(Base):
    __tablename__ = "journal_entry"

    id = Column(BigInteger, primary_key=True)
    company_id = Column(Integer, nullable=True) # Changed to nullable=True
    branch_id = Column(Integer)
    date = Column(Date, nullable=False)
    period = Column(String(10), nullable=False)
    ref_no = Column(String(50))
    status = Column(SmallInteger, nullable=False, default=0)    # 0:Draft 1:Approved 2:Posted 3:Voided
    created_by = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=func.now())
    posted_by = Column(Integer)
    posted_at = Column(TIMESTAMP)
    row_version = Column(BigInteger, nullable=False, default=0)

    lines = relationship("JournalLine", back_populates="journal_entry", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<JournalEntry(id={self.id}, date='{self.date}', status={self.status})>"

class JournalLine(Base):
    __tablename__ = "journal_line"

    id = Column(BigInteger, primary_key=True)
    entry_id = Column(BigInteger, ForeignKey("journal_entry.id", ondelete="CASCADE"))
    account_id = Column(Integer, ForeignKey("account.id"))
    debit = Column(Numeric(18,3), default=0)
    credit = Column(Numeric(18,3), default=0)
    currency = Column(String(3), nullable=False)
    fx_rate = Column(Numeric(12,6), default=1)
    cost_center_id = Column(Integer)
    project_id = Column(Integer)
    memo = Column(Text)

    journal_entry = relationship("JournalEntry", back_populates="lines")
    account = relationship("Account")

    def __repr__(self):
        return f"<JournalLine(id={self.id}, account_id={self.account_id}, debit={self.debit}, credit={self.credit})>"

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(BigInteger, primary_key=True)
    entity = Column(Text)
    entity_id = Column(Text)
    action = Column(Text)        # create/update/delete/post/approve
    user_id = Column(Integer)
    at = Column(TIMESTAMP, default=func.now())
    before = Column(JSONB)
    after = Column(JSONB)

    def __repr__(self):
        return f"<AuditLog(entity='{self.entity}', entity_id='{self.entity_id}', action='{self.action}')>"

class Customer(Base):
    __tablename__ = "customer"

    id = Column(Integer, primary_key=True)
    name_ar = Column(Text, nullable=False)
    name_en = Column(Text)
    code = Column(Integer, Sequence('customer_code_seq', start=1), nullable=False, server_default=Sequence('customer_code_seq').next_value())
    credit_limit = Column(Numeric(18,3), default=0)
    payment_terms = Column(Text)
    is_active = Column(Boolean, default=True)

    address = Column(Text)
    phone_number = Column(String(50))
    customer_group = Column(String(50))
    type = Column(SmallInteger, default=0) # 0: Retail, 1: Wholesale
    email = Column(String(100)) # Added email column
    created_at = Column(TIMESTAMP, default=func.now()) # Added created_at column

    def __repr__(self):
        return f"<Customer(code='{self.code}', name_ar='{self.name_ar}')>"

class Supplier(Base): # Renamed from Vendor
    __tablename__ = "supplier" # Renamed from vendor

    id = Column(Integer, primary_key=True)
    name_ar = Column(Text, nullable=False)
    name_en = Column(Text)
    code = Column(Integer, Sequence('supplier_code_seq', start=1), nullable=False, server_default=Sequence('supplier_code_seq').next_value())
    credit_limit = Column(Numeric(18,3), default=0)
    payment_terms = Column(Text)
    is_active = Column(Boolean, default=True)

    # New fields for Supplier based on common ERP needs
    address = Column(Text)
    phone_number = Column(String(50))
    contact_person = Column(Text)
    email = Column(String(100))
    tax_id = Column(String(50))
    supplier_group = Column(String(50))

    def __repr__(self):
        return f"<Supplier(code='{self.code}', name_ar='{self.name_ar}')>"

class Invoice(Base):
    __tablename__ = "invoice"

    id = Column(BigInteger, primary_key=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False) # Changed to nullable=False
    branch_id = Column(Integer, ForeignKey("branch.id"), nullable=False) # Changed to nullable=False
    customer_id = Column(Integer, ForeignKey("customer.id"))
    supplier_id = Column(Integer, ForeignKey("supplier.id")) # Changed from vendor_id
    invoice_type = Column(SmallInteger, nullable=False) # 0: Sales, 1: Purchase, 2: Sales Return, 3: Purchase Return
    invoice_no = Column(String(50), unique=True, nullable=False)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date)
    total_amount = Column(Numeric(18,3), default=0)
    total_tax = Column(Numeric(18,3), default=0)
    currency = Column(String(3), nullable=False)
    status = Column(SmallInteger, default=0) # 0: Draft, 1: Issued, 2: Paid, 3: Cancelled
    created_by = Column(Integer, nullable=True) # Changed to nullable=True
    created_at = Column(TIMESTAMP, default=func.now())

    customer = relationship("Customer")
    supplier = relationship("Supplier") # Changed from vendor
    branch = relationship("Branch", backref="invoices", lazy='joined') # New: Relationship to Branch model
    company = relationship("Company", back_populates="invoices") # New: Relationship to Company model
    lines = relationship("InvoiceLine", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("InvoicePayment", back_populates="invoice", cascade="all, delete-orphan") # New relationship

    def __repr__(self):
        return f"<Invoice(invoice_no='{self.invoice_no}', type={self.invoice_type}, total={self.total_amount})>"

class Payment(Base):
    __tablename__ = "payment"

    id = Column(BigInteger, primary_key=True)
    company_id = Column(Integer, nullable=False)
    branch_id = Column(Integer)
    invoice_id = Column(BigInteger, ForeignKey("invoice.id"))
    payment_date = Column(Date, nullable=False)
    amount = Column(Numeric(18,3), nullable=False)
    currency = Column(String(3), nullable=False)
    payment_method = Column(Text)
    ref_no = Column(String(50))
    created_by = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())

    invoice = relationship("Invoice")

    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, date='{self.payment_date}')>"

class InvoicePayment(Base): # New InvoicePayment Model for split payments
    __tablename__ = "invoice_payment"

    id = Column(BigInteger, primary_key=True)
    invoice_id = Column(BigInteger, ForeignKey("invoice.id"), nullable=False)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=False)
    amount = Column(Numeric(18, 3), nullable=False)
    transaction_details = Column(Text) # Optional: e.g., credit card last 4 digits, bank ref
    created_at = Column(TIMESTAMP, default=func.now())

    invoice = relationship("Invoice", back_populates="payments")
    payment_method = relationship("PaymentMethod")

    def __repr__(self):
        return f"<InvoicePayment(id={self.id}, invoice_id={self.invoice_id}, amount={self.amount})>"

class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False) # Added company_id
    warehouse_id = Column(Integer, ForeignKey("warehouse.id"), nullable=False) # New: Link item to a warehouse
    code = Column(Integer, Sequence('item_code_seq', start=1), nullable=False, server_default=Sequence('item_code_seq').next_value())
    name_ar = Column(Text, nullable=False)
    name_en = Column(Text)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False) # Changed to unit_id as ForeignKey
    barcode = Column(String(50))
    sale_price = Column(Numeric(18,3), default=0)
    min_sale_price = Column(Numeric(18,3), default=0)
    cost_price = Column(Numeric(18,3), default=0) # Added cost_price
    reorder_level = Column(Numeric(18,3), default=0)
    free_quantity_level = Column(Numeric(18,3), default=0) # Added free_quantity_level
    costing_method = Column(SmallInteger, default=0) # 0: FIFO, 1: Weighted Average, 2: Specific
    is_active = Column(Boolean, default=True)

    unit = relationship("Unit", lazy='joined') # Relationship to Unit model
    warehouse = relationship("Warehouse", backref="items", lazy='joined') # New: Relationship to Warehouse model
    company = relationship("Company", back_populates="items") # New: Relationship to Company model

    def __repr__(self):
        return f"<Item(code='{self.code}', name_ar='{self.name_ar}')>"

class InvoiceLine(Base):
    __tablename__ = "invoice_line"

    id = Column(BigInteger, primary_key=True)
    invoice_id = Column(BigInteger, ForeignKey("invoice.id", ondelete="CASCADE"))
    item_id = Column(Integer, ForeignKey("item.id"))
    quantity = Column(Numeric(18,3), nullable=False)
    unit_price = Column(Numeric(18,3), nullable=False)
    discount_percentage = Column(Numeric(5,2), default=0)
    total_line_amount = Column(Numeric(18,3), nullable=False)
    memo = Column(Text)

    invoice = relationship("Invoice", back_populates="lines")
    item = relationship("Item")

    def __repr__(self):
        return f"<InvoiceLine(invoice_id={self.invoice_id}, item_id={self.item_id}, quantity={self.quantity}, total={self.total_line_amount})>"

class StockMovement(Base):
    __tablename__ = "stock_movement"

    id = Column(BigInteger, primary_key=True)
    company_id = Column(Integer, nullable=True) # Changed to nullable=True
    branch_id = Column(Integer)
    item_id = Column(Integer, ForeignKey("item.id"), nullable=False)
    movement_type = Column(SmallInteger, nullable=False) # 0: In, 1: Out, 2: Transfer, 3: Adjustment, 4: Waste
    quantity = Column(Numeric(18,3), nullable=False)
    cost = Column(Numeric(18,3), default=0)
    movement_date = Column(Date, nullable=False)
    ref_no = Column(String(50))
    created_by = Column(Integer, nullable=True) # Changed to nullable=True
    created_at = Column(TIMESTAMP, default=func.now())

    item = relationship("Item")

    def __repr__(self):
        return f"<StockMovement(item_id={self.item_id}, type={self.movement_type}, quantity={self.quantity})>"

class SalesOrder(Base):
    __tablename__ = "sales_order"

    id = Column(BigInteger, primary_key=True)
    company_id = Column(Integer, nullable=True) # Changed to nullable=True
    branch_id = Column(Integer)
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    order_no = Column(String(50), unique=True, nullable=False)
    order_date = Column(Date, nullable=False)
    total_amount = Column(Numeric(18,3), default=0)
    total_tax = Column(Numeric(18,3), default=0)
    currency = Column(String(3), nullable=False)
    status = Column(SmallInteger, default=0) # 0: Draft, 1: Confirmed, 2: Fulfilled, 3: Cancelled
    created_by = Column(Integer, nullable=True) # Changed to nullable=True
    created_at = Column(TIMESTAMP, default=func.now())

    customer = relationship("Customer")

    def __repr__(self):
        return f"<SalesOrder(order_no='{self.order_no}', total={self.total_amount})>"

class PurchaseOrder(Base):
    __tablename__ = "purchase_order"

    id = Column(BigInteger, primary_key=True)
    company_id = Column(Integer, nullable=True) # Changed to nullable=True
    branch_id = Column(Integer)
    supplier_id = Column(Integer, ForeignKey("supplier.id"), nullable=False) # Changed from vendor_id
    order_no = Column(String(50), unique=True, nullable=False)
    order_date = Column(Date, nullable=False)
    total_amount = Column(Numeric(18,3), default=0)
    total_tax = Column(Numeric(18,3), default=0)
    currency = Column(String(3), nullable=False)
    status = Column(SmallInteger, default=0) # 0: Draft, 1: Confirmed, 2: Received, 3: Cancelled
    created_by = Column(Integer, nullable=True) # Changed to nullable=True
    created_at = Column(TIMESTAMP, default=func.now())

    supplier = relationship("Supplier") # Changed from vendor

    def __repr__(self):
        return f"<PurchaseOrder(order_no='{self.order_no}', total={self.total_amount})>"

class BankTransaction(Base):
    __tablename__ = "bank_transaction"

    id = Column(BigInteger, primary_key=True)
    company_id = Column(Integer, nullable=False)
    branch_id = Column(Integer)
    bank_account_id = Column(Integer, nullable=False) # Assuming an Account with type Bank
    transaction_type = Column(SmallInteger, nullable=False) # 0: Deposit, 1: Withdrawal, 2: Transfer In, 3: Transfer Out
    amount = Column(Numeric(18,3), nullable=False)
    currency = Column(String(3), nullable=False)
    transaction_date = Column(Date, nullable=False)
    ref_no = Column(String(50))
    description = Column(Text)
    created_by = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())

    def __repr__(self):
        return f"<BankTransaction(id={self.id}, amount={self.amount}, type={self.transaction_type})>"

class BankReconciliation(Base):
    __tablename__ = "bank_reconciliation"

    id = Column(BigInteger, primary_key=True)
    company_id = Column(Integer, nullable=False)
    branch_id = Column(Integer)
    bank_account_id = Column(Integer, nullable=False) # Assuming an Account with type Bank
    reconciliation_date = Column(Date, nullable=False)
    statement_balance = Column(Numeric(18,3), nullable=False)
    book_balance = Column(Numeric(18,3), nullable=False)
    difference = Column(Numeric(18,3), default=0)
    is_reconciled = Column(Boolean, default=False)
    created_by = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())

    def __repr__(self):
        return f"<BankReconciliation(id={self.id}, date='{self.reconciliation_date}', reconciled={self.is_reconciled})>"

class FixedAsset(Base):
    __tablename__ = "fixed_asset"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, nullable=False)
    branch_id = Column(Integer)
    code = Column(String(50), unique=True, nullable=False)
    name_ar = Column(Text, nullable=False)
    name_en = Column(Text)
    asset_category = Column(Text)
    acquisition_date = Column(Date, nullable=False)
    cost = Column(Numeric(18,3), nullable=False)
    salvage_value = Column(Numeric(18,3), default=0)
    useful_life_years = Column(Integer, nullable=False)
    depreciation_method = Column(SmallInteger, default=0) # 0: Straight-Line, 1: Declining Balance
    current_book_value = Column(Numeric(18,3), default=0)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())

    def __repr__(self):
        return f"<FixedAsset(code='{self.code}', name_ar='{self.name_ar}')>"

class Depreciation(Base):
    __tablename__ = "depreciation"

    id = Column(BigInteger, primary_key=True)
    company_id = Column(Integer, nullable=False)
    branch_id = Column(Integer)
    asset_id = Column(Integer, ForeignKey("fixed_asset.id"), nullable=False)
    depreciation_date = Column(Date, nullable=False)
    amount = Column(Numeric(18,3), nullable=False)
    created_by = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())

    fixed_asset = relationship("FixedAsset")

    def __repr__(self):
        return f"<Depreciation(id={self.id}, asset_id={self.asset_id}, amount={self.amount})>"

class TaxSetting(Base):
    __tablename__ = "tax_setting"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, nullable=False)
    country_code = Column(String(3), nullable=False)
    tax_name_ar = Column(Text, nullable=False)
    tax_name_en = Column(Text)
    tax_rate = Column(Numeric(5,4), nullable=False) # e.g., 0.15 for 15%
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())

    def __repr__(self):
        return f"<TaxSetting(country='{self.country_code}', name='{self.tax_name_ar}', rate={self.tax_rate})>"

class TaxReport(Base):
    __tablename__ = "tax_report"

    id = Column(BigInteger, primary_key=True)
    company_id = Column(Integer, nullable=False)
    branch_id = Column(Integer)
    tax_setting_id = Column(Integer, ForeignKey("tax_setting.id"), nullable=False)
    report_period = Column(String(10), nullable=False) # YYYY-MM or YYYY-Qn
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_sales_tax = Column(Numeric(18,3), default=0)
    total_purchase_tax = Column(Numeric(18,3), default=0)
    net_tax_payable = Column(Numeric(18,3), default=0)
    status = Column(SmallInteger, default=0) # 0: Draft, 1: Submitted
    created_by = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())

    tax_setting = relationship("TaxSetting")

    def __repr__(self):
        return f"<TaxReport(id={self.id}, period='{self.report_period}', net_tax={self.net_tax_payable})>"

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False) # New: Link user to a company
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    full_name_ar = Column(Text)
    full_name_en = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=func.now())
    last_login_at = Column(TIMESTAMP)

    # relationships
    roles = relationship("UserRole", back_populates="user")
    company = relationship("Company", foreign_keys=[company_id], back_populates="users") # Explicitly define foreign_keys

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)

    # relationships
    permissions = relationship("RolePermission", back_populates="role")

    def __repr__(self):
        return f"<Role(name='{self.name}')>"

class Permission(Base):
    __tablename__ = "permission"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    def __repr__(self):
        return f"<Permission(name='{self.name}')>"

class UserRole(Base):
    __tablename__ = "user_role"
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("role.id"), primary_key=True)

    user = relationship("User", back_populates="roles")
    role = relationship("Role")

class RolePermission(Base):
    __tablename__ = "role_permission"
    role_id = Column(Integer, ForeignKey("role.id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permission.id"), primary_key=True)

    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission")

class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(Integer, Sequence('company_code_seq', start=1), nullable=False, server_default=Sequence('company_code_seq').next_value()) # Restored Sequence
    name_ar = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_loyalty_enabled = Column(Boolean, default=False)
    admin_username = Column(String(50), nullable=True) # New: Store admin username for the company
    admin_password_hash = Column(Text, nullable=True) # New: Store hashed admin password
    
    # Restored direct currency link for base_currency_id, made nullable=False
    base_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False) # Not Null
    secondary_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=True) # Allow NULL

    created_by = Column(Integer, ForeignKey("user.id"), nullable=True)
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    # Relationships
    users = relationship("User", primaryjoin="Company.id == User.company_id", back_populates="company") # Explicitly define primaryjoin
    base_currency = relationship("Currency", foreign_keys=[base_currency_id], lazy='joined', post_update=True) # New relationship to Currency
    secondary_currency = relationship("Currency", foreign_keys=[secondary_currency_id], lazy='joined', post_update=True) # New relationship to Currency
    branches = relationship("Branch", back_populates="company", cascade="all, delete-orphan")
    warehouses = relationship("Warehouse", back_populates="company", cascade="all, delete-orphan")
    items = relationship("Item", back_populates="company", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Company(code='{self.code}', name_ar='{self.name_ar}')>"

class Branch(Base):
    __tablename__ = "branch"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)
    code = Column(Integer, Sequence('branch_code_seq', start=1), nullable=False, server_default=Sequence('branch_code_seq').next_value())
    name_ar = Column(Text, nullable=False)
    name_en = Column(Text)
    address = Column(Text)
    phone_number = Column(String(50)) # Added phone_number column
    email = Column(String(100)) # Added email column
    base_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False) # New: Link branch to a base currency
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=func.now())

    company = relationship("Company", back_populates="branches") # Changed from backref
    base_currency = relationship("Currency", foreign_keys=[base_currency_id], back_populates="branches_as_base", lazy='joined') # New: Relationship to Currency model

    def __repr__(self):
        return f"<Branch(code='{self.code}', name_ar='{self.name_ar}')>"

class Warehouse(Base): # New Warehouse Model
    __tablename__ = "warehouse"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branch.id"), nullable=False) # Changed to nullable=False
    name_ar = Column(Text, nullable=False)
    name_en = Column(Text)
    location = Column(Text)
    base_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False) # New: Link warehouse to a base currency
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=func.now())

    company = relationship("Company", back_populates="warehouses") # Changed from backref
    branch = relationship("Branch", backref="warehouses")
    base_currency = relationship("Currency", foreign_keys=[base_currency_id], back_populates="warehouses_as_base", lazy='joined') # New: Relationship to Currency model

    def __repr__(self):
        return f"<Warehouse(id={self.id}, name_ar='{self.name_ar}')>"

class FiscalPeriod(Base):
    __tablename__ = "fiscal_period"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)
    year = Column(SmallInteger, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_open = Column(Boolean, default=True)
    created_by = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=func.now())

    company = relationship("Company", backref="fiscal_periods")

    def __repr__(self):
        return f"<FiscalPeriod(year={self.year}, is_open={self.is_open})>"

class CostCenter(Base):
    __tablename__ = "cost_center"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)
    code = Column(Integer, Sequence('cost_center_code_seq', start=1), nullable=False, server_default=Sequence('cost_center_code_seq').next_value())
    name_ar = Column(Text, nullable=False)
    name_en = Column(Text)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=func.now())

    company = relationship("Company", backref="cost_centers")

    def __repr__(self):
        return f"<CostCenter(code='{self.code}', name_ar='{self.name_ar}')>"

class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)
    code = Column(Integer, Sequence('project_code_seq', start=1), nullable=False, server_default=Sequence('project_code_seq').next_value())
    name_ar = Column(Text, nullable=False)
    name_en = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=func.now())

    company = relationship("Company", backref="projects")

    def __repr__(self):
        return f"<Project(code='{self.code}', name_ar='{self.name_ar}')>"

class Employee(Base):
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branch.id"))
    first_name_ar = Column(Text, nullable=False)
    last_name_ar = Column(Text, nullable=False)
    first_name_en = Column(Text)
    last_name_en = Column(Text)
    position = Column(String(50))
    hire_date = Column(Date)
    salary = Column(Numeric(18,3), default=0)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=func.now())

    branch = relationship("Branch", backref="employees")

    def __repr__(self):
        return f"<Employee(id={self.id}, name_ar={self.first_name_ar} {self.last_name_ar})>"

class Payrun(Base):
    __tablename__ = "payrun"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branch.id"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    pay_date = Column(Date, nullable=False)
    total_gross_pay = Column(Numeric(18,3), default=0)
    total_net_pay = Column(Numeric(18,3), default=0)
    status = Column(SmallInteger, default=0) # 0: Draft, 1: Processed, 2: Paid
    created_by = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=func.now())

    branch = relationship("Branch", backref="payruns")

    def __repr__(self):
        return f"<Payrun(id={self.id}, period={self.start_date}-{self.end_date})>"

class Notification(Base):
    __tablename__ = "notification"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=func.now())
    
    user = relationship("User", backref="notifications")
    company = relationship("Company", backref="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, message='{self.message[:20]}...')>"

class Workflow(Base):
    __tablename__ = "workflow"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    trigger_event = Column(String(50), nullable=False) # e.g., 'InvoiceCreated', 'PaymentReceived'
    actions = Column(Text) # JSON field for actions to be taken, stored as text
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=func.now())

    company = relationship("Company", backref="workflows")

    def __repr__(self):
        return f"<Workflow(name='{self.name}', trigger='{self.trigger_event}')>"

class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branch.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    start_time = Column(TIMESTAMP, nullable=False, default=func.now())
    end_time = Column(TIMESTAMP)
    starting_cash = Column(Numeric(18, 3), default=0.0)
    ending_cash = Column(Numeric(18, 3), default=0.0)
    total_sales = Column(Numeric(18, 3), default=0.0)
    total_returns = Column(Numeric(18, 3), default=0.0)
    net_cash = Column(Numeric(18, 3), default=0.0)
    status = Column(SmallInteger, default=0)  # 0: Open, 1: Closed, 2: Reconciled

    company = relationship("Company", backref="shifts")
    branch = relationship("Branch", backref="shifts")
    user = relationship("User", backref="shifts")
    movements = relationship("ShiftMovement", back_populates="shift", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Shift(id={self.id}, user_id={self.user_id}, status={self.status})>"

class ShiftMovement(Base):
    __tablename__ = "shift_movements"

    id = Column(Integer, primary_key=True)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)
    movement_type = Column(SmallInteger, nullable=False) # 0: Cash In, 1: Cash Out, 2: Sale, 3: Return
    amount = Column(Numeric(18, 3), nullable=False)
    notes = Column(Text)
    transaction_time = Column(TIMESTAMP, nullable=False, default=func.now())
    sales_invoice_id = Column(BigInteger, ForeignKey("invoice.id"), nullable=True)
    return_invoice_id = Column(BigInteger, ForeignKey("invoice.id"), nullable=True)

    shift = relationship("Shift", back_populates="movements")
    sales_invoice = relationship("Invoice", foreign_keys=[sales_invoice_id])
    return_invoice = relationship("Invoice", foreign_keys=[return_invoice_id])

    def __repr__(self):
        return f"<ShiftMovement(id={self.id}, shift_id={self.shift_id}, type={self.movement_type}, amount={self.amount})>"
