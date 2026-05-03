from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/dashboard")
def dashboard_report(db: Session = Depends(get_db)):
    total_products = db.query(models.Product).count()
    total_warehouses = db.query(models.Warehouse).count()
    total_suppliers = db.query(models.Supplier).count()
    total_stock_units = db.query(func.coalesce(func.sum(models.Inventory.quantity), 0)).scalar()

    inventory_value = (
        db.query(func.coalesce(func.sum(models.Inventory.quantity * models.Product.cost_price), 0))
        .join(models.Product, models.Product.id == models.Inventory.product_id)
        .scalar()
    )

    low_stock_count = (
        db.query(models.Inventory)
        .join(models.Product, models.Product.id == models.Inventory.product_id)
        .filter(models.Inventory.quantity <= models.Product.min_stock_level)
        .count()
    )

    recent_movements = (
        db.query(models.StockMovement)
        .order_by(models.StockMovement.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "total_products": total_products,
        "total_warehouses": total_warehouses,
        "total_suppliers": total_suppliers,
        "total_stock_units": total_stock_units,
        "inventory_value": round(inventory_value, 2),
        "low_stock_count": low_stock_count,
        "recent_movements": recent_movements,
    }


@router.get("/warehouse-stock")
def warehouse_stock_report(db: Session = Depends(get_db)):
    rows = (
        db.query(
            models.Warehouse.id,
            models.Warehouse.name,
            func.coalesce(func.sum(models.Inventory.quantity), 0).label("quantity"),
        )
        .outerjoin(models.Inventory, models.Inventory.warehouse_id == models.Warehouse.id)
        .group_by(models.Warehouse.id, models.Warehouse.name)
        .all()
    )

    return [
        {
            "warehouse_id": row.id,
            "warehouse": row.name,
            "quantity": row.quantity,
        }
        for row in rows
    ]
    