import csv
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    new_product = models.Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.get("/", response_model=list[schemas.ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()


@router.post("/import-csv")
def import_products_csv(csv_text: str, db: Session = Depends(get_db)):
    reader = csv.DictReader(StringIO(csv_text))
    required_columns = {"sku", "name"}

    if not required_columns.issubset(set(reader.fieldnames or [])):
        raise HTTPException(status_code=400, detail="CSV must include sku and name columns")

    imported = 0

    for row in reader:
        existing = db.query(models.Product).filter_by(sku=row["sku"]).first()
        if existing is not None:
            continue

        db.add(models.Product(
            sku=row["sku"],
            name=row["name"],
            category=row.get("category"),
            cost_price=float(row.get("cost_price") or 0),
            selling_price=float(row.get("selling_price") or 0),
            min_stock_level=int(row.get("min_stock_level") or 0),
        ))
        imported += 1

    db.commit()

    return {"message": "Products imported successfully", "imported": imported}


@router.get("/export-csv")
def export_products_csv(db: Session = Depends(get_db)):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "sku", "name", "category", "cost_price", "selling_price", "min_stock_level"])

    for product in db.query(models.Product).all():
        writer.writerow([
            product.id,
            product.sku,
            product.name,
            product.category,
            product.cost_price,
            product.selling_price,
            product.min_stock_level,
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=products.csv"},
    )


@router.get("/{product_id}/qr")
def get_product_qr_payload(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter_by(id=product_id).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "label": product.name,
        "qr_payload": f"SKU:{product.sku}|PRODUCT_ID:{product.id}",
        "scan_url": f"/products/{product.id}",
    }
