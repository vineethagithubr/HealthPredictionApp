import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import re
import google.generativeai as genai
from dotenv import load_dotenv
import os


# GEMINI API CONFIGURATION

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)


# DATABASE CONNECTION

conn = sqlite3.connect(
    "health.db",
    check_same_thread=False
)

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


# HEALTH PREDICTION FUNCTION

def predict(glucose, haemoglobin, cholesterol):

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        Patient Health Data:

        Glucose: {glucose}
        Haemoglobin: {haemoglobin}
        Cholesterol: {cholesterol}

        Give ONLY a 3-word health prediction.
        """

        response = model.generate_content(prompt)

        return response.text.strip()

    except Exception:

        # Fallback Prediction Logic

        if glucose > 180:
            return "Severe Diabetes Risk"

        elif glucose > 140:
            return "High Diabetes Risk"

        elif glucose < 70:
            return "Low Sugar Risk"

        elif cholesterol > 240:
            return "High Heart Risk"

        elif cholesterol < 120:
            return "Low Cholesterol Risk"

        elif haemoglobin < 12:
            return "Anaemia Risk"

        elif haemoglobin > 18:
            return "Thick Blood Risk"

        else:
            return "Normal Health Status"


# STREAMLIT UI

st.set_page_config(
    page_title="Health Prediction App",
    layout="wide"
)

st.title("AI Health Prediction System")

st.sidebar.title("Navigation")
st.sidebar.write("Patient Management System")

# CREATE RECORD

st.header("Add Patient Record")

name = st.text_input("Full Name")

dob = st.date_input("Date of Birth")

email = st.text_input("Email Address")

glucose = st.number_input(
    "Glucose",
    min_value=0.0
)

haemoglobin = st.number_input(
    "Haemoglobin",
    min_value=0.0
)

cholesterol = st.number_input(
    "Cholesterol",
    min_value=0.0
)

if st.button("Save Record"):

    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    if name.strip() == "":
        st.error("Name cannot be empty")

    elif not re.match(email_pattern, email):
        st.error("Invalid Email Format")

    elif dob > date.today():
        st.error("Future DOB not allowed")

    else:

        remarks = predict(
            glucose,
            haemoglobin,
            cholesterol
        )

        cursor.execute("""
        INSERT INTO patients
        (
            name,
            dob,
            email,
            glucose,
            haemoglobin,
            cholesterol,
            remarks
        )
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

        st.success("Record Saved Successfully")

# DISPLAY RECORDS

st.header("Patient Records")

df = pd.read_sql_query(
    "SELECT * FROM patients",
    conn
)

st.metric(
    "Total Patients",
    len(df)
)

search = st.text_input("Search Patient Name")

if search:

    filtered_df = df[
        df["name"].str.contains(
            search,
            case=False,
            na=False
        )
    ]

    st.dataframe(filtered_df)

else:
    st.dataframe(df)

# UPDATE RECORD

st.header("Update Record")

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
    min_value=0.0,
    key="update_glucose"
)

update_haemoglobin = st.number_input(
    "New Haemoglobin",
    min_value=0.0,
    key="update_haemoglobin"
)

update_cholesterol = st.number_input(
    "New Cholesterol",
    min_value=0.0,
    key="update_cholesterol"
)

if st.button("Update Record"):

    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    if update_name.strip() == "":
        st.error("Name required")

    elif not re.match(email_pattern, update_email):
        st.error("Invalid Email")

    else:

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

# DELETE RECORD

st.header("Delete Record")

delete_id = st.number_input(
    "Enter ID to Delete",
    min_value=1,
    key="delete_id"
)

confirm_delete = st.checkbox(
    "Confirm Delete"
)

if st.button("Delete Record"):

    if confirm_delete:

        cursor.execute(
            "DELETE FROM patients WHERE id=?",
            (delete_id,)
        )

        conn.commit()

        st.success("Record Deleted Successfully")

    else:
        st.warning("Please confirm delete")


conn.close()