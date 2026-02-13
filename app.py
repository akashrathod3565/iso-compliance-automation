import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

from db import create_table, insert_supplier
from validation import validate_iso_certificate
from alerts import check_and_send_alerts


# -----------------------------
# Initial Setup
# -----------------------------
st.set_page_config(page_title="ISO Compliance System", layout="wide")

create_table()

conn = sqlite3.connect("suppliers.db", check_same_thread=False)
cursor = conn.cursor()

if not os.path.exists("uploads"):
    os.makedirs("uploads")


# -----------------------------
# Sidebar Menu
# -----------------------------
st.sidebar.title("Navigation")
menu = st.sidebar.selectbox("Select Menu", ["Dashboard", "Upload Certificate"])


# ============================================================
# ======================== DASHBOARD =========================
# ============================================================

if menu == "Dashboard":

    st.title("ISO 9001 Compliance Dashboard")

    # -----------------------------
    # Load Suppliers from Excel
    # -----------------------------
    st.subheader("Upload Supplier Excel")

    uploaded_excel = st.file_uploader(
        "Upload Supplier Excel File",
        type=["xlsx"],
        key="supplier_excel_upload"
        )

    if uploaded_excel:

        df_excel = pd.read_excel(uploaded_excel)

        required_columns = [
                "Supplier Number",
                "Supplier Name",
                "Email",
                "Phone"
            ]

        if not all(col in df_excel.columns for col in required_columns):
            st.error("Excel must contain required columns.")
        else:
            for _, row in df_excel.iterrows():
                insert_supplier((
                        row["Supplier Number"],
                        row["Supplier Name"],
                        row["Email"],
                        row["Phone"],
                        0,
                        None,
                        None,
                        "Pending",
                        0,
                        None
                    ))

            st.success("Suppliers Loaded Successfully!")
        

        for _, row in df_excel.iterrows():
            insert_supplier((
                row["Supplier Number"],
                row["Supplier Name"],
                row["Email"],
                row["Phone"],
                0,
                None,
                None,
                "Pending",
                0,
                None
            ))

        st.success("Suppliers Loaded Successfully!")

    # -----------------------------
    # Load Data from DB
    # -----------------------------
    df = pd.read_sql_query("SELECT * FROM suppliers", conn)

    if df.empty:
        st.warning("No supplier data found. Load suppliers from Excel first.")
        st.stop()

    # -----------------------------
    # KPI Metrics
    # -----------------------------
    total = len(df)
    compliant = len(df[df["status"] == "Green"])
    expiring = len(df[df["status"] == "Amber"])
    expired = len(df[df["status"] == "Red"])
    pending = len(df[df["status"] == "Pending"])

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Suppliers", total)
    col2.metric("Compliant", compliant)
    col3.metric("Expiring Soon", expiring)
    col4.metric("Expired", expired)
    col5.metric("Pending", pending)

    st.divider()

    # -----------------------------
    # Compliance Pie Chart
    # -----------------------------
    st.subheader("Compliance Distribution")

    status_counts = df["status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]

    fig1 = px.pie(
        status_counts,
        names="Status",
        values="Count",
        color="Status",
        color_discrete_map={
            "Green": "green",
            "Amber": "orange",
            "Red": "red",
            "Pending": "gray"
        },
        title="ISO Compliance Status"
    )

    st.plotly_chart(fig1, use_container_width=True)

    # -----------------------------
    # ISO Received Bar Chart
    # -----------------------------
    st.subheader("ISO Submission Overview")

    submission_counts = df["iso_received"].value_counts().reset_index()
    submission_counts.columns = ["ISO Received", "Count"]

    submission_counts["ISO Received"] = submission_counts["ISO Received"].map({
        1: "Received",
        0: "Not Received"
    })

    fig2 = px.bar(
        submission_counts,
        x="ISO Received",
        y="Count",
        color="ISO Received",
        title="Certificate Submission Status"
    )

    st.plotly_chart(fig2, use_container_width=True)

    # -----------------------------
    # Expiry Histogram
    # -----------------------------
    st.subheader("Days to Expiry Distribution")

    valid_df = df[df["days_to_expiry"].notnull()]

    if not valid_df.empty:
        fig3 = px.histogram(
            valid_df,
            x="days_to_expiry",
            nbins=20,
            title="Expiry Timeline"
        )
        st.plotly_chart(fig3, use_container_width=True)

    # -----------------------------
    # Top Risk Suppliers
    # -----------------------------
    st.subheader("Top 10 Expiring Soon")

    risk_df = df[df["days_to_expiry"].notnull()] \
        .sort_values("days_to_expiry") \
        .head(10)

    st.dataframe(risk_df, use_container_width=True)

    # -----------------------------
    # Alert Button
    # -----------------------------
    if st.button("Run Compliance Alert Check"):
        check_and_send_alerts()
        st.success("Alert Emails Sent Successfully!")


# ============================================================
# ======================== UPLOAD ============================
# ============================================================

if menu == "Upload Certificate":

    st.title("Upload ISO 9001 Certificate")

    supplier_number = st.text_input(
        "Supplier Number",
        key="upload_supplier_number"
    )

    if supplier_number:

        supplier = cursor.execute(
            "SELECT * FROM suppliers WHERE supplier_number=?",
            (supplier_number,)
        ).fetchone()

        if supplier is None:
            st.error("Supplier not found in database.")
        else:
            st.success(f"Supplier Found: {supplier[1]}")
            uploaded_file = st.file_uploader(
                "Upload ISO Certificate (PDF only for cloud)",
                type=["pdf"],
                key="upload_file"
            )


            if uploaded_file:

                file_path = os.path.join("uploads", uploaded_file.name)

                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                valid, expiry, days_left, status = validate_iso_certificate(file_path)

                if valid:
                    cursor.execute("""
                        UPDATE suppliers
                        SET iso_received = 1,
                            expiry_date = ?,
                            days_to_expiry = ?,
                            status = ?,
                            last_updated = ?
                        WHERE supplier_number = ?
                    """, (
                        expiry,
                        days_left,
                        status,
                        datetime.today().strftime("%Y-%m-%d"),
                        supplier_number
                    ))

                    conn.commit()

                    st.success(f"Certificate Valid ✅ Status: {status}")
                    st.write(f"Days to Expiry: {days_left}")
                else:
                    st.error("Invalid ISO Certificate ❌")
