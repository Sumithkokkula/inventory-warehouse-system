from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/sales-orders", tags=["Sales Orders"])


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


@router.post("/", response_model=schemas.SalesOrderResponse)
def create_sales_order(order: schemas.SalesOrderCreate, db: Session = Depends(get_db)):
    if not order.items:
        raise HTTPException(status_code=400, detail="Sales order must have items")

    for item in order.items:
        inventory = get_or_create_inventory(db, item.product_id, order.warehouse_id)
        if inventory.quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product {item.product_id}",
            )

    sales_order = models.SalesOrder(
        customer_name=order.customer_name,
        warehouse_id=order.warehouse_id,
        status="confirmed",
    )
    db.add(sales_order)
    db.flush()

    for item in order.items:
        db.add(models.SalesOrderItem(
            sales_order_id=sales_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
        ))

    db.commit()
    db.refresh(sales_order)
    return sales_order


@router.get("/")
def get_sales_orders(db: Session = Depends(get_db)):
    return db.query(models.SalesOrder).all()


@router.post("/{order_id}/ship")
def ship_sales_order(order_id: int, db: Session = Depends(get_db)):
    sales_order = db.query(models.SalesOrder).filter_by(id=order_id).first()

    if sales_order is None:
        raise HTTPException(status_code=404, detail="Sales order not found")
    if sales_order.status == "shipped":
        raise HTTPException(status_code=400, detail="Sales order already shipped")

    items = db.query(models.SalesOrderItem).filter_by(sales_order_id=order_id).all()

    for item in items:
        inventory = get_or_create_inventory(db, item.product_id, sales_order.warehouse_id)
        if inventory.quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product {item.product_id}",
            )

    for item in items:
        inventory = get_or_create_inventory(db, item.product_id, sales_order.warehouse_id)
        inventory.quantity -= item.quantity
        db.add(models.StockMovement(
            product_id=item.product_id,
            warehouse_id=sales_order.warehouse_id,
            movement_type="sale_shipped",
            quantity=-item.quantity,
            note=f"Sales order #{sales_order.id} shipped",
        ))

    sales_order.status = "shipped"
    db.commit()

    return {"message": "Sales order shipped successfully"}

