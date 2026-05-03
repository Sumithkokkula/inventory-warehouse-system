from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.post("/", response_model=schemas.WarehouseResponse)
def create_warehouse(warehouse: schemas.WarehouseCreate, db: Session = Depends(get_db)):
    new_warehouse = models.Warehouse(**warehouse.model_dump())
    db.add(new_warehouse)
    db.commit()
    db.refresh(new_warehouse)
    return new_warehouse


@router.get("/", response_model=list[schemas.WarehouseResponse])
def get_warehouses(db: Session = Depends(get_db)):
    return db.query(models.Warehouse).all()
