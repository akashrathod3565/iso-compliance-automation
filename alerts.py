import sqlite3
from email_service import send_email


def check_and_send_alerts():

    conn = sqlite3.connect("suppliers.db")
    cursor = conn.cursor()

    suppliers = cursor.execute("""
    SELECT supplier_name, email, status, days_to_expiry
    FROM suppliers
    """).fetchall()

    for name, email, status, days_left in suppliers:

        if status == "Red":
            send_email(email, name, status, days_left)

        elif status == "Amber" and days_left <= 30:
            send_email(email, name, status, days_left)

    conn.close()
