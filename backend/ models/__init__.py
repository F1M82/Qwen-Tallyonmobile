# FILE: backend/models/__init__.py

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text, DECIMAL, Date, JSON
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from decimal import Decimal as PyDecimal
import uuid

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    gstin = Column(String(15))
    pan = Column(String(10))
    financial_year_start = Column(Date)
    accounting_source = Column(String(50))  # tally, zoho, standalone
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ledgers = relationship("Ledger", back_populates="company")
    vouchers = relationship("Voucher", back_populates="company")
    recon_sessions = relationship("ReconciliationSession", back_populates="company")

class Ledger(Base):
    __tablename__ = "ledgers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("companies.id"))
    name = Column(String(255), nullable=False)
    group_name = Column(String(100))
    opening_balance = Column(DECIMAL(15, 2), default=0)
    balance_type = Column(String(2))  # Dr, Cr
    gstin = Column(String(15))
    pan = Column(String(10))
    phone = Column(String(15))
    email = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    company = relationship("Company", back_populates="ledgers")
    entries = relationship("LedgerEntry", back_populates="ledger")

class Voucher(Base):
    __tablename__ = "vouchers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("companies.id"))
    voucher_type = Column(String(50))  # Receipt, Payment, Sales, Purchase
    voucher_number = Column(String(50))
    date = Column(Date)
    narration = Column(Text)
    reference = Column(String(100))
    total_amount = Column(DECIMAL(15, 2))
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="posted")  # draft, posted, cancelled
    source = Column(String(20))  # voice, photo, manual, sms, email
    
    company = relationship("Company", back_populates="vouchers")
    entries = relationship("LedgerEntry", back_populates="voucher")

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    voucher_id = Column(String, ForeignKey("vouchers.id"))
    ledger_id = Column(String, ForeignKey("ledgers.id"))
    amount = Column(DECIMAL(15, 2), nullable=False)
    entry_type = Column(String(2))  # Dr, Cr
    gst_rate = Column(DECIMAL(5, 2))
    cgst = Column(DECIMAL(15, 2))
    sgst = Column(DECIMAL(15, 2))
    igst = Column(DECIMAL(15, 2))
    tds_amount = Column(DECIMAL(15, 2))
    tds_section = Column(String(10))
    
    voucher = relationship("Voucher", back_populates="entries")
    ledger = relationship("Ledger", back_populates="entries")

class ReconciliationSession(Base):
    __tablename__ = "recon_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("companies.id"))
    party_id = Column(String)
    period_from = Column(Date)
    period_to = Column(Date)
    status = Column(String(20), default="processing")
    your_balance = Column(DECIMAL(15, 2))
    party_balance = Column(DECIMAL(15, 2))
    difference = Column(DECIMAL(15, 2))
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    company = relationship("Company", back_populates="recon_sessions")
    matches = relationship("ReconciliationMatch", back_populates="recon_session")

class ReconciliationMatch(Base):
    __tablename__ = "recon_matches"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    recon_session_id = Column(String, ForeignKey("recon_sessions.id"))
    your_voucher_id = Column(String)
    party_voucher_id = Column(String)
    match_type = Column(String(20))  # exact, fuzzy, amount_only
    confidence_score = Column(Float)
    status = Column(String(20))  # auto_matched, user_confirmed, disputed
    difference = Column(DECIMAL(15, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    recon_session = relationship("ReconciliationSession", back_populates="matches")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String)
    user_id = Column(String)
    action = Column(String(50))
    entity_type = Column(String(50))
    entity_id = Column(String)
    old_value = Column(JSON)
    new_value = Column(JSON)
    ip_address = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_ca = Column(Boolean, default=False)
    firm_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
