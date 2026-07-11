from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


class Lead(Base):
    """Represents a prospect or customer lead."""

    __tablename__ = "leads"

    lead_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    company_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    industry: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    contact_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    lead_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    interactions: Mapped[list["SalesInteraction"]] = relationship(
        back_populates="lead",
        cascade="all, delete-orphan",
    )

    insights: Mapped[list["CompanyInsight"]] = relationship(
        back_populates="lead",
        cascade="all, delete-orphan",
    )


class SalesInteraction(Base):
    """Represents an engagement record associated with a lead."""

    __tablename__ = "sales_interactions"

    interaction_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    lead_id: Mapped[int] = mapped_column(
        ForeignKey("leads.lead_id", ondelete="CASCADE"),
        nullable=False,
    )

    interaction_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    action_items: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    interaction_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    lead: Mapped["Lead"] = relationship(
        back_populates="interactions",
    )


class CompanyInsight(Base):
    """AI-generated lead intelligence produced by Module 2."""

    __tablename__ = "company_insights"

    insight_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    lead_id: Mapped[int] = mapped_column(
        ForeignKey("leads.lead_id", ondelete="CASCADE"),
        nullable=False,
    )

    business_needs: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    opportunities: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    industry_analysis: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    qualification_score: Mapped[int] = mapped_column(
        nullable=False,
    )

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    lead: Mapped["Lead"] = relationship(
        back_populates="insights",
    )
