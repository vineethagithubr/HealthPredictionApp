import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import re
import google.generativeai as genai
import os

# Database Connection
conn = sqlite3.connect("health.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS patients(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
dob TEXT,
email TEXT,
glucose REAL,
haemoglobin REAL,
cholesterol REAL,
remarks TEXT
)
""")
conn.commit()

# -----------------------------
# GEMINI AI CONFIG (SECURE WAY)
# -----------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def predict(glucose, haemoglobin, cholesterol):

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = f"""
        Patient Health Data:

        Glucose: {glucose}
        Haemoglobin: {haemoglobin}
        Cholesterol: {cholesterol}

        Give ONE short sentence in 3 words predicting health risk.
        """

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        # Fallback logic if Gemini fails
        if glucose > 140:
            return "High Diabetes Risk"
        elif cholesterol > 240:
            return "Heart Disease Risk"
        elif haemoglobin < 12:
            return "Possible Anaemia"
        else:
            return "Healthy"
        
st.title("Health Prediction Application")

# Input Fields
name = st.text_input("Full Name")
dob = st.date_input("Date of Birth")
email = st.text_input("Email Address")

glucose = st.number_input("Glucose")
haemoglobin = st.number_input("Haemoglobin")
cholesterol = st.number_input("Cholesterol")

# Create Record
if st.button("Save Record"):

    if "@" not in email or "." not in email:
        st.error("Invalid Email")
    elif dob > date.today():
        st.error("Future DOB not allowed")
    else:
        remarks = predict(glucose, haemoglobin, cholesterol)

        cursor.execute("""
        INSERT INTO patients
        (name,dob,email,glucose,haemoglobin,cholesterol,remarks)
        VALUES(?,?,?,?,?,?,?)
        """,
        (
            name,
            str(dob),
            email,
            glucose,
            haemoglobin,
            cholesterol,
            remarks
        ))

        conn.commit()
        st.success("Record Saved")

# Display Records
st.subheader("Patient Records")

df = pd.read_sql_query("SELECT * FROM patients", conn)

st.dataframe(df)

st.subheader("Update Record")

update_id = st.number_input(
    "Enter ID to Update",
    min_value=1,
    key="update_id"
)

update_name = st.text_input(
    "New Name",
    key="update_name"
)

update_email = st.text_input(
    "New Email",
    key="update_email"
)

update_glucose = st.number_input(
    "New Glucose",
    key="update_glucose"
)

update_haemoglobin = st.number_input(
    "New Haemoglobin",
    key="update_haemoglobin"
)

update_cholesterol = st.number_input(
    "New Cholesterol",
    key="update_cholesterol"
)

if st.button("Update Record"):

    remarks = predict(
        update_glucose,
        update_haemoglobin,
        update_cholesterol
    )

    cursor.execute("""
    UPDATE patients
    SET
        name=?,
        email=?,
        glucose=?,
        haemoglobin=?,
        cholesterol=?,
        remarks=?
    WHERE id=?
    """,
    (
        update_name,
        update_email,
        update_glucose,
        update_haemoglobin,
        update_cholesterol,
        remarks,
        update_id
    ))

    conn.commit()

    st.success("Record Updated Successfully")

# Delete Record
st.subheader("Delete Record")

delete_id = st.number_input("Enter ID to Delete", min_value=1)

if st.button("Delete"):
    cursor.execute(
        "DELETE FROM patients WHERE id=?",
        (delete_id,)
    )
    conn.commit()
    st.success("Record Deleted")

