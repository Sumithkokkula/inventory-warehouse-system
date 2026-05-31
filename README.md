# Inventory & Warehouse Management System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/>
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black"/>
</p>

> A full-stack system to manage products, warehouses, suppliers, and order workflows with a live dashboard showing real-time KPIs, stock alerts, and movement tracking across **3,200+ inventory records**.

---

## 🚨 The Problem

Businesses managing multiple warehouses and suppliers often rely on spreadsheets that don't update in real time, can't trigger alerts, and make it impossible to track stock movement or forecast demand. This system replaces that with a structured, API-driven backend and a live dashboard.

---

## Features

-  **Product & warehouse management** -track stock levels, warehouse capacity, and supplier info
- **Order workflow**-create, process, and fulfill orders with status tracking
- **Low-stock alerts**-automatic notifications when inventory drops below threshold
- **Live KPI dashboard** -stock movement, fulfillment rates, and performance metrics
- **Demand forecasting** — analyze 3,200+ records to surface reorder signals
- **REST API** - Full CRUD for inventory, orders, warehouses, and suppliers
- **Inventory sync** -converts raw dataset entries into structured operational data

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + Uvicorn |
| Database | SQLite + SQLAlchemy ORM |
| Frontend Dashboard | HTML, CSS, JavaScript |
| Data Processing | Python (Pandas, NumPy) |
| API Style | RESTful |

---

## 📁 Project Structure

```
inventory-warehouse-system/
├── backend/
│   ├── main.py           # FastAPI app + all API routes
│   ├── models.py         # SQLAlchemy ORM models
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── database.py       # DB connection & session setup
│   ├── crud.py           # Database operations (Create/Read/Update/Delete)
│   └── data_loader.py    # Loads & syncs the 3,200+ record dataset
└── frontend/
    ├── index.html        # Dashboard UI
    ├── app.js            # API calls & dynamic rendering
    └── styles.css        # Dashboard styling
```

---

📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/products` | List all products with stock levels |
| `POST` | `/products` | Add a new product |
| `PUT` | `/products/{id}` | Update product details or stock |
| `GET` | `/warehouses` | List warehouses and capacity |
| `GET` | `/suppliers` | List suppliers |
| `POST` | `/orders` | Create a new order |
| `PUT` | `/orders/{id}/fulfill` | Mark order as fulfilled |
| `GET` | `/dashboard/stats` | KPIs — stock summary, alerts, fulfillment rate |
| `GET` | `/alerts/low-stock` | Products below reorder threshold |

---

## 🚀 Run Locally

```bash
git clone https://github.com/Sumithkokkula/inventory-warehouse-system.git
cd inventory-warehouse-system/backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open `frontend/index.html` in your browser, or serve it with:

```bash
cd ../frontend
python3 -m http.server 3000
```

Open `http://localhost:3000`

---

## 📊 Dataset

- **3,200+ inventory records** covering products, stock levels, supplier data, and order history
- Data loaded via `data_loader.py` which syncs raw CSV entries into structured SQLite tables
- Used to power demand forecasting signals and low-stock alert thresholds

---

## 🔮 Future Improvements

- [ ] Add user authentication (JWT)
- [ ] Barcode/QR code scanning for stock updates
- [ ] Migrate to PostgreSQL for multi-user production use
- [ ] Add email notifications for low-stock alerts
- [ ] Export reports as PDF / Excel

---

## 👤 Author

**Sumith Kokkula** · [LinkedIn](https://www.linkedin.com/in/sumith-kokkula-6a240b329) · [GitHub](https://github.com/Sumithkokkula)
