from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from .database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String)
    cost_price = Column(Float, default=0)
    selling_price = Column(Float, default=0)
    min_stock_level = Column(Integer, default=0)


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String)


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    address = Column(String)


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    quantity = Column(Integer, default=0)


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    movement_type = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    note = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    status = Column(String, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Float, default=0)


class SalesOrder(Base):
    __tablename__ = "sales_orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    status = Column(String, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)


class SalesOrderItem(Base):
    __tablename__ = "sales_order_items"

    id = Column(Integer, primary_key=True, index=True)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, default=0)


class LogisticsItem(Base):
    __tablename__ = "logistics_items"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(String, unique=True, index=True, nullable=False)
    category = Column(String)
    stock_level = Column(Integer, default=0)
    reorder_point = Column(Integer, default=0)
    reorder_frequency_days = Column(Integer, default=0)
    lead_time_days = Column(Integer, default=0)
    daily_demand = Column(Float, default=0)
    demand_std_dev = Column(Float, default=0)
    item_popularity_score = Column(Float, default=0)
    storage_location_id = Column(String)
    zone = Column(String)
    picking_time_seconds = Column(Integer, default=0)
    handling_cost_per_unit = Column(Float, default=0)
    unit_price = Column(Float, default=0)
    holding_cost_per_unit_day = Column(Float, default=0)
    stockout_count_last_month = Column(Integer, default=0)
    order_fulfillment_rate = Column(Float, default=0)
    total_orders_last_month = Column(Integer, default=0)
    turnover_ratio = Column(Float, default=0)
    layout_efficiency_score = Column(Float, default=0)
    last_restock_date = Column(String)
    forecasted_demand_next_7d = Column(Float, default=0)
    kpi_score = Column(Float, default=0)

