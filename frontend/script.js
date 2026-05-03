const API_URL = "http://127.0.0.1:8000";

const state = {
  products: [],
  warehouses: [],
  suppliers: [],
  purchaseOrders: [],
  salesOrders: [],
  logisticsItems: [],
};

const statusEl = document.querySelector("#status");
const pageTitle = document.querySelector("#page-title");

function showStatus(message) {
  statusEl.textContent = message;
  setTimeout(() => {
    statusEl.textContent = "";
  }, 3500);
}

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Request failed");
  }

  return response.json();
}

function getFormData(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function toNumbers(data, fields) {
  for (const field of fields) {
    data[field] = Number(data[field] || 0);
  }
  return data;
}

function emptyRow(columns, message) {
  return `<tr><td class="empty" colspan="${columns}">${message}</td></tr>`;
}

async function loadDashboard() {
  const dashboard = await request("/reports/dashboard");
  const warehouseStock = await request("/reports/warehouse-stock");

  const metrics = [
    ["Products", dashboard.total_products],
    ["Warehouses", dashboard.total_warehouses],
    ["Suppliers", dashboard.total_suppliers],
    ["Stock Units", dashboard.total_stock_units],
    ["Stock Value", `$${dashboard.inventory_value}`],
    ["Low Stock", dashboard.low_stock_count],
  ];

  document.querySelector("#metrics").innerHTML = metrics
    .map(([label, value]) => `<article class="metric"><strong>${value}</strong><span>${label}</span></article>`)
    .join("");

  document.querySelector("#movement-rows").innerHTML = dashboard.recent_movements.length
    ? dashboard.recent_movements.map((item) => `
        <tr>
          <td>${item.movement_type}</td>
          <td>${item.product_id}</td>
          <td>${item.warehouse_id}</td>
          <td>${item.quantity}</td>
          <td>${item.note || ""}</td>
        </tr>
      `).join("")
    : emptyRow(5, "No stock movements yet");

  document.querySelector("#warehouse-stock-list").innerHTML = warehouseStock.length
    ? warehouseStock.map((item) => `
        <article class="card">
          <strong>${item.warehouse}</strong>
          <p>${item.quantity} units in stock</p>
        </article>
      `).join("")
    : `<p class="empty">No warehouses yet</p>`;
}

async function loadProducts() {
  state.products = await request("/products/");

  document.querySelector("#product-rows").innerHTML = state.products.length
    ? state.products.map((product) => `
        <tr>
          <td>${product.id}</td>
          <td>${product.sku}</td>
          <td>${product.name}</td>
          <td>${product.category || ""}</td>
          <td>${product.cost_price}</td>
          <td>${product.selling_price}</td>
          <td>${product.min_stock_level}</td>
        </tr>
      `).join("")
    : emptyRow(7, "No products yet");
}

async function loadWarehouses() {
  state.warehouses = await request("/warehouses/");

  document.querySelector("#warehouse-list").innerHTML = state.warehouses.length
    ? state.warehouses.map((warehouse) => `
        <article class="card">
          <strong>#${warehouse.id} ${warehouse.name}</strong>
          <p>${warehouse.location || "No location"}</p>
        </article>
      `).join("")
    : `<p class="empty">No warehouses yet</p>`;
}

async function loadSuppliers() {
  state.suppliers = await request("/suppliers/");

  document.querySelector("#supplier-list").innerHTML = state.suppliers.length
    ? state.suppliers.map((supplier) => `
        <article class="card">
          <strong>#${supplier.id} ${supplier.name}</strong>
          <p>${supplier.email || ""} ${supplier.phone || ""}</p>
          <p>${supplier.address || ""}</p>
        </article>
      `).join("")
    : `<p class="empty">No suppliers yet</p>`;
}

async function loadLowStock() {
  const rows = await request("/inventory/low-stock");

  document.querySelector("#low-stock-rows").innerHTML = rows.length
    ? rows.map((row) => `
        <tr>
          <td>${row.sku}</td>
          <td>${row.name}</td>
          <td>${row.quantity}</td>
          <td>${row.min_stock_level}</td>
        </tr>
      `).join("")
    : emptyRow(4, "No low-stock products");
}

async function loadOrders() {
  state.purchaseOrders = await request("/purchase-orders/");
  state.salesOrders = await request("/sales-orders/");

  document.querySelector("#purchase-list").innerHTML = state.purchaseOrders.length
    ? state.purchaseOrders.map((order) => `
        <article class="card">
          <strong>PO #${order.id}</strong>
          <p>Supplier ${order.supplier_id} · Warehouse ${order.warehouse_id} · ${order.status}</p>
          <div class="order-actions">
            <button class="receive" data-po="${order.id}">Receive</button>
          </div>
        </article>
      `).join("")
    : `<p class="empty">No purchase orders yet</p>`;

  document.querySelector("#sales-list").innerHTML = state.salesOrders.length
    ? state.salesOrders.map((order) => `
        <article class="card">
          <strong>SO #${order.id}</strong>
          <p>${order.customer_name} · Warehouse ${order.warehouse_id} · ${order.status}</p>
          <div class="order-actions">
            <button class="ship" data-so="${order.id}">Ship</button>
          </div>
        </article>
      `).join("")
    : `<p class="empty">No sales orders yet</p>`;
}

async function importLogisticsDataset() {
  const result = await request("/logistics/import", { method: "POST" });
  const sync = await request("/logistics/sync-products", { method: "POST" });
  showStatus(`${result.imported} imported, ${sync.products_created} products created`);
  await refreshAll();
}

async function syncLogisticsToProducts() {
  const sync = await request("/logistics/sync-products", { method: "POST" });
  showStatus(`${sync.inventory_rows_synced} inventory rows synced`);
  await refreshAll();
}

async function loadLogistics() {
  const summary = await request("/logistics/summary");

  if (summary.total_items === 0) {
    document.querySelector("#logistics-metrics").innerHTML = `
      <article class="metric"><strong>0</strong><span>Rows imported</span></article>
    `;
    document.querySelector("#category-list").innerHTML = `<p class="empty">Click Import CSV to load the Kaggle dataset.</p>`;
    document.querySelector("#logistics-rows").innerHTML = emptyRow(8, "No logistics data imported yet");
    return;
  }

  state.logisticsItems = await request("/logistics/items?limit=50");

  const metrics = [
    ["Dataset Items", summary.total_items],
    ["Low Stock", summary.low_stock_items],
    ["Total Stock", summary.total_stock],
    ["Avg Fulfillment", `${Math.round(summary.avg_fulfillment_rate * 100)}%`],
    ["Avg KPI", summary.avg_kpi_score],
    ["7d Demand", summary.forecasted_demand_next_7d],
  ];

  document.querySelector("#logistics-metrics").innerHTML = metrics
    .map(([label, value]) => `<article class="metric"><strong>${value}</strong><span>${label}</span></article>`)
    .join("");

  document.querySelector("#category-list").innerHTML = summary.categories
    .map((item) => `
      <article class="card">
        <strong>${item.category}</strong>
        <p>${item.items} items · avg KPI ${item.avg_kpi_score}</p>
      </article>
    `)
    .join("");

  document.querySelector("#logistics-rows").innerHTML = state.logisticsItems
    .map((item) => `
      <tr>
        <td>${item.item_id}</td>
        <td>${item.category}</td>
        <td>${item.stock_level}</td>
        <td>${item.reorder_point}</td>
        <td>${item.zone}</td>
        <td>${Math.round(item.order_fulfillment_rate * 100)}%</td>
        <td>${item.total_orders_last_month}</td>
        <td>${item.kpi_score}</td>
      </tr>
    `)
    .join("");
}

async function refreshAll() {
  await Promise.all([
    loadDashboard(),
    loadProducts(),
    loadWarehouses(),
    loadSuppliers(),
    loadLowStock(),
    loadOrders(),
    loadLogistics(),
  ]);
}

function setActiveView(viewName) {
  document.querySelectorAll(".nav-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === viewName);
  });
  document.querySelectorAll(".view").forEach((view) => {
    view.classList.toggle("active", view.id === viewName);
  });
  pageTitle.textContent = viewName.charAt(0).toUpperCase() + viewName.slice(1);
}

document.querySelectorAll(".nav-button").forEach((button) => {
  button.addEventListener("click", () => setActiveView(button.dataset.view));
});

document.querySelector("#refresh-button").addEventListener("click", async () => {
  await refreshAll();
  showStatus("Dashboard refreshed");
});

document.querySelector("#import-logistics-button").addEventListener("click", importLogisticsDataset);
document.querySelector("#sync-logistics-button").addEventListener("click", syncLogisticsToProducts);

document.querySelector("#product-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = toNumbers(getFormData(event.target), ["cost_price", "selling_price", "min_stock_level"]);
  await request("/products/", { method: "POST", body: JSON.stringify(data) });
  event.target.reset();
  await refreshAll();
  showStatus("Product added");
});

document.querySelector("#warehouse-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  await request("/warehouses/", { method: "POST", body: JSON.stringify(getFormData(event.target)) });
  event.target.reset();
  await refreshAll();
  showStatus("Warehouse added");
});

document.querySelector("#supplier-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  await request("/suppliers/", { method: "POST", body: JSON.stringify(getFormData(event.target)) });
  event.target.reset();
  await refreshAll();
  showStatus("Supplier added");
});

document.querySelector("#inventory-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = toNumbers(getFormData(event.target), ["product_id", "warehouse_id", "quantity"]);
  await request("/inventory/adjust", { method: "POST", body: JSON.stringify(data) });
  event.target.reset();
  await refreshAll();
  showStatus("Stock adjusted");
});

document.querySelector("#purchase-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = toNumbers(getFormData(event.target), ["supplier_id", "warehouse_id", "product_id", "quantity", "unit_cost"]);
  await request("/purchase-orders/", {
    method: "POST",
    body: JSON.stringify({
      supplier_id: data.supplier_id,
      warehouse_id: data.warehouse_id,
      items: [{ product_id: data.product_id, quantity: data.quantity, unit_cost: data.unit_cost }],
    }),
  });
  event.target.reset();
  await refreshAll();
  showStatus("Purchase order created");
});

document.querySelector("#sales-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = toNumbers(getFormData(event.target), ["warehouse_id", "product_id", "quantity", "unit_price"]);
  await request("/sales-orders/", {
    method: "POST",
    body: JSON.stringify({
      customer_name: data.customer_name,
      warehouse_id: data.warehouse_id,
      items: [{ product_id: data.product_id, quantity: data.quantity, unit_price: data.unit_price }],
    }),
  });
  event.target.reset();
  await refreshAll();
  showStatus("Sales order created");
});

document.addEventListener("click", async (event) => {
  const purchaseId = event.target.dataset.po;
  const salesId = event.target.dataset.so;

  if (purchaseId) {
    await request(`/purchase-orders/${purchaseId}/receive`, { method: "POST" });
    await refreshAll();
    showStatus(`Purchase order #${purchaseId} received`);
  }

  if (salesId) {
    await request(`/sales-orders/${salesId}/ship`, { method: "POST" });
    await refreshAll();
    showStatus(`Sales order #${salesId} shipped`);
  }
});

refreshAll().catch((error) => showStatus(error.message));
