from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])


def get_or_create_inventory(db: Session, product_id: int, warehouse_id: int):
    inventory = db.query(models.Inventory).filter_by(
        product_id=product_id,
        warehouse_id=warehouse_id,
    ).first()

    if inventory is None:
        inventory = models.Inventory(product_id=product_id, warehouse_id=warehouse_id, quantity=0)
        db.add(inventory)
        db.flush()

    return inventory


@router.post("/", response_model=schemas.PurchaseOrderResponse)
def create_purchase_order(order: schemas.PurchaseOrderCreate, db: Session = Depends(get_db)):
    if not order.items:
        raise HTTPException(status_code=400, detail="Purchase order must have items")

    purchase_order = models.PurchaseOrder(
        supplier_id=order.supplier_id,
        warehouse_id=order.warehouse_id,
        status="draft",
    )
    db.add(purchase_order)
    db.flush()

    for item in order.items:
        db.add(models.PurchaseOrderItem(
            purchase_order_id=purchase_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_cost=item.unit_cost,
        ))

    db.commit()
    db.refresh(purchase_order)
    return purchase_order


@router.get("/")
def get_purchase_orders(db: Session = Depends(get_db)):
    return db.query(models.PurchaseOrder).all()


@router.post("/{order_id}/receive")
def receive_purchase_order(order_id: int, db: Session = Depends(get_db)):
    purchase_order = db.query(models.PurchaseOrder).filter_by(id=order_id).first()

    if purchase_order is None:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    if purchase_order.status == "received":
        raise HTTPException(status_code=400, detail="Purchase order already received")

    items = db.query(models.PurchaseOrderItem).filter_by(purchase_order_id=order_id).all()

    for item in items:
        inventory = get_or_create_inventory(db, item.product_id, purchase_order.warehouse_id)
        inventory.quantity += item.quantity
        db.add(models.StockMovement(
            product_id=item.product_id,
            warehouse_id=purchase_order.warehouse_id,
            movement_type="purchase_received",
            quantity=item.quantity,
            note=f"Purchase order #{purchase_order.id} received",
        ))

    purchase_order.status = "received"
    db.commit()

    return {"message": "Purchase order received successfully"}

