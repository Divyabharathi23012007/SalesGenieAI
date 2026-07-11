from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Lead, SalesInteraction

router = APIRouter(prefix="/leads", tags=["Lead Management"])

DatabaseSession = Annotated[Session, Depends(get_db)]


class LeadPayload(BaseModel):
    """Defines the required data for a lead."""

    company_name: str = Field(min_length=1, max_length=255)
    industry: str = Field(min_length=1, max_length=100)
    contact_name: str = Field(min_length=1, max_length=255)
    email: str = Field(
        min_length=3,
        max_length=255,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )
    phone: str = Field(min_length=1, max_length=20)
    lead_status: str = Field(min_length=1, max_length=50)


class LeadCreate(LeadPayload):
    """Defines data required to create a lead."""


class LeadUpdate(LeadPayload):
    """Defines data required to update a lead."""


class LeadRead(LeadPayload):
    """Defines the lead response structure."""

    model_config = ConfigDict(from_attributes=True)

    lead_id: int
    created_at: datetime
    updated_at: datetime


class SalesInteractionPayload(BaseModel):
    """Defines the required data for a sales interaction."""

    interaction_type: str = Field(min_length=1, max_length=100)
    summary: str = Field(min_length=1)
    action_items: str = Field(min_length=1)
    interaction_date: datetime | None = None


class SalesInteractionCreate(SalesInteractionPayload):
    """Defines data required to create a sales interaction."""


class SalesInteractionUpdate(SalesInteractionPayload):
    """Defines data required to update a sales interaction."""


class SalesInteractionRead(SalesInteractionPayload):
    """Defines the sales interaction response structure."""

    model_config = ConfigDict(from_attributes=True)

    interaction_id: int
    lead_id: int
    interaction_date: datetime


def get_lead_or_404(lead_id: int, db: Session) -> Lead:
    """Return a lead or raise a 404 error."""
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found.",
        )
    return lead


def get_interaction_or_404(
    interaction_id: int,
    db: Session,
) -> SalesInteraction:
    """Return a sales interaction or raise a 404 error."""
    interaction = db.get(SalesInteraction, interaction_id)
    if interaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales interaction not found.",
        )
    return interaction


@router.post(
    "",
    response_model=LeadRead,
    status_code=status.HTTP_201_CREATED,
)
def create_lead(lead_data: LeadCreate, db: DatabaseSession) -> Lead:
    """Create and return a new lead."""
    lead = Lead(**lead_data.model_dump())
    db.add(lead)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A lead with this email already exists.",
        ) from error

    db.refresh(lead)
    return lead


@router.get("", response_model=list[LeadRead])
def get_leads(db: DatabaseSession) -> list[Lead]:
    """Return all leads."""
    statement = select(Lead).order_by(Lead.created_at.desc())
    return list(db.scalars(statement).all())


@router.get("/{lead_id}", response_model=LeadRead)
def get_lead(lead_id: int, db: DatabaseSession) -> Lead:
    """Return a single lead by its ID."""
    return get_lead_or_404(lead_id, db)


@router.put("/{lead_id}", response_model=LeadRead)
def update_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    db: DatabaseSession,
) -> Lead:
    """Update and return an existing lead."""
    lead = get_lead_or_404(lead_id, db)

    for field_name, value in lead_data.model_dump().items():
        setattr(lead, field_name, value)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A lead with this email already exists.",
        ) from error

    db.refresh(lead)
    return lead


@router.delete(
    "/{lead_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_lead(lead_id: int, db: DatabaseSession) -> Response:
    """Delete an existing lead."""
    lead = get_lead_or_404(lead_id, db)
    db.delete(lead)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{lead_id}/interactions",
    response_model=SalesInteractionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_sales_interaction(
    lead_id: int,
    interaction_data: SalesInteractionCreate,
    db: DatabaseSession,
) -> SalesInteraction:
    """Create and return a sales interaction for a lead."""
    get_lead_or_404(lead_id, db)

    interaction_values = interaction_data.model_dump(exclude_none=True)
    interaction = SalesInteraction(
        lead_id=lead_id,
        **interaction_values,
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


@router.get(
    "/{lead_id}/interactions",
    response_model=list[SalesInteractionRead],
)
def get_sales_interactions(
    lead_id: int,
    db: DatabaseSession,
) -> list[SalesInteraction]:
    """Return all sales interactions for a lead."""
    get_lead_or_404(lead_id, db)

    statement = (
        select(SalesInteraction)
        .where(SalesInteraction.lead_id == lead_id)
        .order_by(SalesInteraction.interaction_date.desc())
    )
    return list(db.scalars(statement).all())


@router.put(
    "/interactions/{interaction_id}",
    response_model=SalesInteractionRead,
)
def update_sales_interaction(
    interaction_id: int,
    interaction_data: SalesInteractionUpdate,
    db: DatabaseSession,
) -> SalesInteraction:
    """Update and return an existing sales interaction."""
    interaction = get_interaction_or_404(interaction_id, db)

    for field_name, value in interaction_data.model_dump(
        exclude_none=True,
    ).items():
        setattr(interaction, field_name, value)

    db.commit()
    db.refresh(interaction)
    return interaction


@router.delete(
    "/interactions/{interaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_sales_interaction(
    interaction_id: int,
    db: DatabaseSession,
) -> Response:
    """Delete an existing sales interaction."""
    interaction = get_interaction_or_404(interaction_id, db)
    db.delete(interaction)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
