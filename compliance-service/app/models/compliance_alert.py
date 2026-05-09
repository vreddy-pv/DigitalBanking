import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text, Integer
from app.database import Base


class ComplianceAlert(Base):
    __tablename__ = "compliance_alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String, nullable=False, index=True)
    account_id = Column(String, nullable=False, index=True)
    customer_name = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)  # DEPOSIT, WITHDRAWAL, TRANSFER

    # AML fields
    alert_type = Column(String, nullable=False)     # HIGH_VALUE, FREQUENT_TX, LARGE_WITHDRAWAL, etc.
    severity = Column(String, nullable=False)        # LOW, MEDIUM, HIGH, CRITICAL
    description = Column(Text, nullable=False)

    # Review workflow
    status = Column(String, nullable=False, default="PENDING")  # PENDING, REVIEWED, CLEARED, ESCALATED
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CustomerRiskProfile(Base):
    __tablename__ = "customer_risk_profiles"

    customer_id = Column(String, primary_key=True)   # ACCOUNT_ID used as customer identifier
    risk_score = Column(Integer, default=0)           # 0-100
    risk_level = Column(String, default="LOW")        # LOW, MEDIUM, HIGH, CRITICAL
    alert_count = Column(Integer, default=0)
    high_alert_count = Column(Integer, default=0)
    last_assessed_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
