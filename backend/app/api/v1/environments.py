"""Environment CRUD API endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tenant import Environment, Customer
from app.schemas.tenant import EnvironmentCreate, EnvironmentUpdate, EnvironmentResponse

router = APIRouter()


@router.post("/", response_model=EnvironmentResponse, status_code=status.HTTP_201_CREATED)
def create_environment(payload: EnvironmentCreate, db: Session = Depends(get_db)):
    """Create a new environment for a customer."""
    customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")
    env = Environment(**payload.model_dump())
    db.add(env)
    db.commit()
    db.refresh(env)
    return env


@router.get("/", response_model=List[EnvironmentResponse])
def list_environments(
    customer_id: UUID = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List environments, optionally filtered by customer."""
    query = db.query(Environment)
    if customer_id:
        query = query.filter(Environment.customer_id == customer_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{env_id}", response_model=EnvironmentResponse)
def get_environment(env_id: UUID, db: Session = Depends(get_db)):
    """Get a single environment by ID."""
    env = db.query(Environment).filter(Environment.id == env_id).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found.")
    return env


@router.patch("/{env_id}", response_model=EnvironmentResponse)
def update_environment(env_id: UUID, payload: EnvironmentUpdate, db: Session = Depends(get_db)):
    """Partially update an environment."""
    env = db.query(Environment).filter(Environment.id == env_id).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found.")
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(env, field, value)
    db.commit()
    db.refresh(env)
    return env


@router.delete("/{env_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_environment(env_id: UUID, db: Session = Depends(get_db)):
    """Delete an environment."""
    env = db.query(Environment).filter(Environment.id == env_id).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found.")
    db.delete(env)
    db.commit()
    return None
