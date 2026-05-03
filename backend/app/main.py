from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routes import products, warehouses, suppliers, inventory, purchase_orders, sales_orders, reports, logistics

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory Warehouse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://[::]:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(warehouses.router)
app.include_router(suppliers.router)
app.include_router(inventory.router)
app.include_router(purchase_orders.router)
app.include_router(sales_orders.router)
app.include_router(reports.router)
app.include_router(logistics.router)

@app.get("/")
def root():
    return {"message": "Inventory Warehouse API is running"}
