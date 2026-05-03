import csv
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db

router = APIRouter(prefix="/logistics", tags=["Kaggle Logistics Dataset"])

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "logistics_dataset.csv"


def to_int(value):
    return int(float(value or 0))


def to_float(value):
    return float(value or 0)


@router.post("/import")
def import_logistics_dataset(db: Session = Depends(get_db)):
    if not DATA_FILE.exists():
        raise HTTPException(status_code=404, detail=f"CSV not found at {DATA_FILE}")

    imported = 0
    skipped = 0

    with DATA_FILE.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            exists = db.query(models.LogisticsItem).filter_by(item_id=row["item_id"]).first()
            if exists:
                skipped += 1
                continue

            db.add(models.LogisticsItem(
                item_id=row["item_id"],
                category=row["category"],
                stock_level=to_int(row["stock_level"]),
                reorder_point=to_int(row["reorder_point"]),
                reorder_frequency_days=to_int(row["reorder_frequency_days"]),
                lead_time_days=to_int(row["lead_time_days"]),
                daily_demand=to_float(row["daily_demand"]),
                demand_std_dev=to_float(row["demand_std_dev"]),
                item_popularity_score=to_float(row["item_popularity_score"]),
                storage_location_id=row["storage_location_id"],
                zone=row["zone"],
                picking_time_seconds=to_int(row["picking_time_seconds"]),
                handling_cost_per_unit=to_float(row["handling_cost_per_unit"]),
                unit_price=to_float(row["unit_price"]),
                holding_cost_per_unit_day=to_float(row["holding_cost_per_unit_day"]),
                stockout_count_last_month=to_int(row["stockout_count_last_month"]),
                order_fulfillment_rate=to_float(row["order_fulfillment_rate"]),
                total_orders_last_month=to_int(row["total_orders_last_month"]),
                turnover_ratio=to_float(row["turnover_ratio"]),
                layout_efficiency_score=to_float(row["layout_efficiency_score"]),
                last_restock_date=row["last_restock_date"],
                forecasted_demand_next_7d=to_float(row["forecasted_demand_next_7d"]),
                kpi_score=to_float(row["KPI_score"]),
            ))
            imported += 1

    db.commit()

    return {
        "message": "Logistics dataset imported",
        "imported": imported,
        "skipped": skipped,
    }


@router.get("/items")
def get_logistics_items(
    limit: int = Query(default=50, ge=1, le=500),
    category: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.LogisticsItem)

    if category:
        query = query.filter(models.LogisticsItem.category == category)

    return query.order_by(models.LogisticsItem.kpi_score.desc()).limit(limit).all()


@router.get("/summary")
def get_logistics_summary(db: Session = Depends(get_db)):
    total_items = db.query(models.LogisticsItem).count()
    low_stock_items = (
        db.query(models.LogisticsItem)
        .filter(models.LogisticsItem.stock_level <= models.LogisticsItem.reorder_point)
        .count()
    )

    totals = db.query(
        func.coalesce(func.sum(models.LogisticsItem.stock_level), 0),
        func.coalesce(func.avg(models.LogisticsItem.order_fulfillment_rate), 0),
        func.coalesce(func.avg(models.LogisticsItem.kpi_score), 0),
        func.coalesce(func.sum(models.LogisticsItem.forecasted_demand_next_7d), 0),
    ).first()

    category_rows = (
        db.query(
            models.LogisticsItem.category,
            func.count(models.LogisticsItem.id),
            func.coalesce(func.avg(models.LogisticsItem.kpi_score), 0),
        )
        .group_by(models.LogisticsItem.category)
        .order_by(func.count(models.LogisticsItem.id).desc())
        .all()
    )

    return {
        "total_items": total_items,
        "low_stock_items": low_stock_items,
        "total_stock": totals[0],
        "avg_fulfillment_rate": round(totals[1], 3),
        "avg_kpi_score": round(totals[2], 3),
        "forecasted_demand_next_7d": round(totals[3], 2),
        "categories": [
            {
                "category": row[0],
                "items": row[1],
                "avg_kpi_score": round(row[2], 3),
            }
            for row in category_rows
        ],
    }


@router.post("/sync-products")
def sync_logistics_to_inventory(db: Session = Depends(get_db)):
    logistics_items = db.query(models.LogisticsItem).all()

    if not logistics_items:
        raise HTTPException(status_code=400, detail="Import logistics dataset first")

    warehouse_by_zone = {}
    products_created = 0
    products_updated = 0
    warehouses_created = 0
    inventory_rows_synced = 0

    for item in logistics_items:
        warehouse_name = f"Zone {item.zone} Warehouse"
        warehouse = warehouse_by_zone.get(item.zone)

        if warehouse is None:
            warehouse = db.query(models.Warehouse).filter_by(name=warehouse_name).first()

            if warehouse is None:
                warehouse = models.Warehouse(
                    name=warehouse_name,
                    location=f"Storage zone {item.zone}",
                )
                db.add(warehouse)
                db.flush()
                warehouses_created += 1

            warehouse_by_zone[item.zone] = warehouse

        product = db.query(models.Product).filter_by(sku=item.item_id).first()

        if product is None:
            product = models.Product(
                sku=item.item_id,
                name=f"{item.category} Item {item.item_id}",
                category=item.category,
                cost_price=item.handling_cost_per_unit,
                selling_price=item.unit_price,
                min_stock_level=item.reorder_point,
            )
            db.add(product)
            db.flush()
            products_created += 1
        else:
            product.name = f"{item.category} Item {item.item_id}"
            product.category = item.category
            product.cost_price = item.handling_cost_per_unit
            product.selling_price = item.unit_price
            product.min_stock_level = item.reorder_point
            products_updated += 1

        inventory = db.query(models.Inventory).filter_by(
            product_id=product.id,
            warehouse_id=warehouse.id,
        ).first()

        if inventory is None:
            inventory = models.Inventory(
                product_id=product.id,
                warehouse_id=warehouse.id,
                quantity=item.stock_level,
            )
            db.add(inventory)
        else:
            inventory.quantity = item.stock_level

        inventory_rows_synced += 1

    db.commit()

    return {
        "message": "Logistics dataset synced to products and inventory",
        "products_created": products_created,
        "products_updated": products_updated,
        "warehouses_created": warehouses_created,
        "inventory_rows_synced": inventory_rows_synced,
    }
