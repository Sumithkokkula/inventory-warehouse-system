from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.post("/", response_model=schemas.SupplierResponse)
def create_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(get_db)):
    new_supplier = models.Supplier(**supplier.model_dump())
    db.add(new_supplier)
    db.commit()
    db.refresh(new_supplier)
    return new_supplier


@router.get("/", response_model=list[schemas.SupplierResponse])
def get_suppliers(db: Session = Depends(get_db)):
    return db.query(models.Supplier).all()
