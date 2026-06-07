CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    phone_tail TEXT NOT NULL,
    status TEXT NOT NULL,
    paid_at TEXT NOT NULL,
    shipped_at TEXT,
    carrier TEXT,
    tracking_no TEXT,
    refund_status TEXT NOT NULL,
    refund_requested_at TEXT,
    refund_amount REAL NOT NULL,
    invoice_status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY,
    order_id TEXT NOT NULL,
    product_name TEXT NOT NULL,
    sku TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    warranty_status TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
