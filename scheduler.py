import schedule
import time
from email_service import send_email
import sqlite3

def send_reminders():
    conn = sqlite3.connect("suppliers.db")
    cursor = conn.cursor()

    suppliers = cursor.execute("""
    SELECT supplier_name, email
    FROM suppliers
    WHERE iso_received = 0
    """).fetchall()

    for name, email in suppliers:
        send_email(email, name)

schedule.every(90).days.do(send_reminders)

while True:
    schedule.run_pending()
    time.sleep(1)
