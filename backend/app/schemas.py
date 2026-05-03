from pydantic import BaseModel


class ProductCreate(BaseModel):
    sku: str
    name: str
    category: str | None = None
    cost_price: float = 0
    selling_price: float = 0
    min_stock_level: int = 0


class ProductResponse(ProductCreate):
    id: int

    class Config:
        from_attributes = True


class WarehouseCreate(BaseModel):
    name: str
    location: str | None = None


class WarehouseResponse(WarehouseCreate):
    id: int

    class Config:
        from_attributes = True


class SupplierCreate(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None


class SupplierResponse(SupplierCreate):
    id: int

    class Config:
        from_attributes = True


class InventoryAdjust(BaseModel):
    product_id: int
    warehouse_id: int
    quantity: int
    note: str | None = None


class InventoryTransfer(BaseModel):
    product_id: int
    from_warehouse_id: int
    to_warehouse_id: int
    quantity: int
    note: str | None = None


class PurchaseOrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_cost: float = 0


class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    warehouse_id: int
    items: list[PurchaseOrderItemCreate]


class PurchaseOrderResponse(BaseModel):
    id: int
    supplier_id: int
    warehouse_id: int
    status: str

    class Config:
        from_attributes = True


class SalesOrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: float = 0


class SalesOrderCreate(BaseModel):
    customer_name: str
    warehouse_id: int
    items: list[SalesOrderItemCreate]


class SalesOrderResponse(BaseModel):
    id: int
    customer_name: str
    warehouse_id: int
    status: str

    class Config:
        from_attributes = True
