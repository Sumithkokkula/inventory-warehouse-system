from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/inventory", tags=["Inventory"])


def get_or_create_inventory(db: Session, product_id: int, warehouse_id: int):
    inventory = db.query(models.Inventory).filter_by(
        product_id=product_id,
        warehouse_id=warehouse_id,
    ).first()

    if inventory is None:
        inventory = models.Inventory(
            product_id=product_id,
            warehouse_id=warehouse_id,
            quantity=0,
        )
        db.add(inventory)
        db.flush()

    return inventory


@router.post("/adjust")
def adjust_stock(data: schemas.InventoryAdjust, db: Session = Depends(get_db)):
    inventory = get_or_create_inventory(db, data.product_id, data.warehouse_id)

    inventory.quantity += data.quantity

    if inventory.quantity < 0:
        raise HTTPException(status_code=400, detail="Stock cannot be negative")

    movement = models.StockMovement(
        product_id=data.product_id,
        warehouse_id=data.warehouse_id,
        movement_type="manual_adjustment",
        quantity=data.quantity,
        note=data.note,
    )

    db.add(movement)
    db.commit()
    db.refresh(inventory)

    return {"message": "Stock adjusted successfully", "quantity": inventory.quantity}


@router.post("/transfer")
def transfer_stock(data: schemas.InventoryTransfer, db: Session = Depends(get_db)):
    if data.quantity <= 0:
        raise HTTPException(status_code=400, detail="Transfer quantity must be positive")

    source = get_or_create_inventory(db, data.product_id, data.from_warehouse_id)
    destination = get_or_create_inventory(db, data.product_id, data.to_warehouse_id)

    if source.quantity < data.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock to transfer")

    source.quantity -= data.quantity
    destination.quantity += data.quantity

    db.add(models.StockMovement(
        product_id=data.product_id,
        warehouse_id=data.from_warehouse_id,
        movement_type="transfer_out",
        quantity=-data.quantity,
        note=data.note,
    ))
    db.add(models.StockMovement(
        product_id=data.product_id,
        warehouse_id=data.to_warehouse_id,
        movement_type="transfer_in",
        quantity=data.quantity,
        note=data.note,
    ))
    db.commit()

    return {"message": "Stock transferred successfully"}


@router.get("/")
def get_inventory(db: Session = Depends(get_db)):
    return db.query(models.Inventory).all()


@router.get("/movements")
def get_stock_movements(db: Session = Depends(get_db)):
    return db.query(models.StockMovement).order_by(models.StockMovement.created_at.desc()).all()


@router.get("/low-stock")
def get_low_stock(db: Session = Depends(get_db)):
    results = (
        db.query(models.Product, models.Inventory)
        .join(models.Inventory, models.Product.id == models.Inventory.product_id)
        .filter(models.Inventory.quantity <= models.Product.min_stock_level)
        .all()
    )

    return [
        {
            "product_id": product.id,
            "sku": product.sku,
            "name": product.name,
            "quantity": inventory.quantity,
            "min_stock_level": product.min_stock_level,
        }
        for product, inventory in results
    ]


@router.get("/report")
def inventory_report(db: Session = Depends(get_db)):
    rows = (
        db.query(models.Product, models.Warehouse, models.Inventory)
        .join(models.Inventory, models.Product.id == models.Inventory.product_id)
        .join(models.Warehouse, models.Warehouse.id == models.Inventory.warehouse_id)
        .all()
    )

    return [
        {
            "sku": product.sku,
            "product": product.name,
            "warehouse": warehouse.name,
            "quantity": inventory.quantity,
            "stock_value": round(inventory.quantity * product.cost_price, 2),
        }
        for product, warehouse, inventory in rows
    ]
