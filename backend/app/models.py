from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    complaint_source: Mapped[str | None] = mapped_column(String(100))
    customer_name: Mapped[str | None] = mapped_column(String(255))
    product_name: Mapped[str | None] = mapped_column(String(255))
    product_strength: Mapped[str | None] = mapped_column(String(100))
    batch_number: Mapped[str | None] = mapped_column(String(100), index=True)
    affected_quantity: Mapped[str | None] = mapped_column(String(100))
    manufacturing_date: Mapped[str | None] = mapped_column(String(100))
    expiry_date: Mapped[str | None] = mapped_column(String(100))
    originating_site: Mapped[str | None] = mapped_column(String(255))
    impacted_material: Mapped[str | None] = mapped_column(String(255))
    complaint_category: Mapped[str | None] = mapped_column(String(255))
    complaint_description: Mapped[str | None] = mapped_column(Text)
    severity: Mapped[str | None] = mapped_column(String(50))
    suggested_action: Mapped[str | None] = mapped_column(Text)
    risk_assessment: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="Pending Triage")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

