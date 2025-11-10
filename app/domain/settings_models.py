from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, func, TIMESTAMP, Numeric, Text
from sqlalchemy.orm import relationship
from app.infrastructure.database import Base
import datetime

class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    name_ar = Column(String, index=True)
    name_en = Column(String, index=True)
    base_quantity = Column(Float, default=1.0) # e.g., 1 carton = 12 pieces, base_quantity for carton is 12
    is_active = Column(Boolean, default=True)
    code = Column(String(50), unique=True, nullable=False)
    created_by = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=func.now())

    # Relationships - Company can have multiple units. Unit belongs to one company
    # company = relationship("Company", back_populates="units") # Removed: Units are not directly linked to Company

    def __repr__(self):
        return f"<Unit(code='{self.code}', name_ar='{self.name_ar}')>"

# --- Currency Model (was in domain/models.py) ---
class Currency(Base):
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True)
    code = Column(String(3), unique=True, nullable=False) # e.g., SAR, USD, EUR
    name_ar = Column(Text, nullable=False)
    name_en = Column(Text)
    symbol = Column(String(10), nullable=False)
    exchange_rate = Column(Numeric(18,6), default=1.0) # Exchange rate to a base currency (e.g., USD)
    is_active = Column(Boolean, default=True)
    # company_id = Column(Integer, ForeignKey("company.id"), nullable=True) # Removed: Currencies are not directly linked to Company
    created_by = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=func.now())

    # Relationships
    # company = relationship("Company", back_populates="currencies", foreign_keys="[Currency.company_id]") # Removed
    companies_as_base = relationship("Company", foreign_keys="[Company.base_currency_id]", back_populates="base_currency") # New: Companies using this as base currency
    companies_as_secondary = relationship("Company", foreign_keys="[Company.secondary_currency_id]", back_populates="secondary_currency") # New: Companies using this as secondary currency
    branches_as_base = relationship("Branch", foreign_keys="[Branch.base_currency_id]", back_populates="base_currency") # New: Branches using this as base currency
    warehouses_as_base = relationship("Warehouse", foreign_keys="[Warehouse.base_currency_id]", back_populates="base_currency") # New: Warehouses using this as base currency

    def __repr__(self):
        return f"<Currency(code='{self.code}', name_ar='{self.name_ar}')>"

# --- PaymentMethod Model ---
class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=True)
    name_ar = Column(String, index=True)
    name_en = Column(String, index=True)
    is_active = Column(Boolean, default=True)

    # company = relationship("Company", back_populates="payment_methods") # Removed this line

    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, name_ar='{self.name_ar}')>"

class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name_ar = Column(String)
    name_en = Column(String)
    discount_type = Column(String, nullable=False) # e.g., "percentage", "fixed_amount"
    discount_value = Column(Float, nullable=False)
    min_purchase_amount = Column(Float, default=0.0)
    valid_from = Column(DateTime, default=datetime.datetime.now)
    valid_until = Column(DateTime)
    is_active = Column(Boolean, default=True)

    company = relationship("Company") # Removed back_populates="coupons"

    def __repr__(self):
        return f"<Coupon(id={self.id}, code='{self.code}', discount_value={self.discount_value}, is_active={self.is_active})>"

class GiftCard(Base):
    __tablename__ = "gift_cards"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=True)
    card_number = Column(String(50), unique=True, nullable=False)
    balance = Column(Float, default=0.0)
    issue_date = Column(DateTime, default=datetime.datetime.now)
    expiry_date = Column(DateTime)
    is_active = Column(Boolean, default=True)

    company = relationship("Company")

    def __repr__(self):
        return f"<GiftCard(id={self.id}, card_number='{self.card_number}', balance={self.balance})>"

class LoyaltyProgram(Base):
    __tablename__ = "loyalty_programs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=True)
    name_ar = Column(String, index=True, nullable=False)
    name_en = Column(String, index=True)
    type = Column(String, nullable=False, default="points") # New: Type of loyalty program (e.g., 'points', 'cashback', 'tiers', 'vouchers')
    points_per_amount = Column(Float, default=1.0) # e.g., 1 point per $1 spent (for 'points' type)
    point_value = Column(Float, default=0.01) # e.g., 1 point = $0.01 discount (for 'points' type)
    min_redemption_points = Column(Integer, default=100) # Minimum points required to redeem (for 'points' type)
    cashback_percentage = Column(Float, default=0.0) # New: Percentage of cashback (for 'cashback' type)
    min_purchase_amount_for_cashback = Column(Float, default=0.0) # New: Minimum purchase amount for cashback (for 'cashback' type)
    is_active = Column(Boolean, default=True)

    company = relationship("Company")

    def __repr__(self):
        return f"<LoyaltyProgram(id={self.id}, name_ar='{self.name_ar}', points_per_amount={self.points_per_amount})>"

