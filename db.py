import sqlite3


# -----------------------------
# Create DB Connection
# -----------------------------
def create_connection():
    conn = sqlite3.connect("suppliers.db")
    return conn


# -----------------------------
# Create Table
# -----------------------------
def create_table():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        supplier_number TEXT PRIMARY KEY,
        supplier_name TEXT,
        email TEXT,
        phone TEXT,
        iso_received INTEGER DEFAULT 0,
        expiry_date TEXT,
        days_to_expiry INTEGER,
        status TEXT,
        uploaded_to_rbsrm INTEGER DEFAULT 0,
        last_updated TEXT
    )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# Insert Supplier
# -----------------------------
def insert_supplier(data):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO suppliers
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    conn.close()
