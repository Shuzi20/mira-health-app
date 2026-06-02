import streamlit as st
import requests
from datetime import date

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="MIRA Health", page_icon="🏥", layout="wide")
st.title("🏥 MIRA — Medical Intelligence Robotic Automation")

menu = st.sidebar.selectbox("Menu", ["View Patients", "Add Patient", "Update Patient", "Delete Patient"])


# ─── VIEW ALL PATIENTS ────────────────────────────────────
if menu == "View Patients":
    st.subheader("All Patients")
    response = requests.get(f"{API}/patients")
    if response.status_code == 200:
        patients = response.json()
        if patients:
            st.dataframe(patients, use_container_width=True)
        else:
            st.info("No patients found. Add one from the menu.")
    else:
        st.error("Could not fetch patients.")


# ─── ADD PATIENT ──────────────────────────────────────────
elif menu == "Add Patient":
    st.subheader("Add New Patient")

    full_name   = st.text_input("Full Name")
    dob         = st.date_input("Date of Birth", min_value=date(1900, 1, 1), max_value=date.today())
    email       = st.text_input("Email Address")
    glucose     = st.number_input("Glucose (mg/dL)",     min_value=0.0, step=0.1)
    haemoglobin = st.number_input("Haemoglobin (g/dL)",  min_value=0.0, step=0.1)
    cholesterol = st.number_input("Cholesterol (mg/dL)", min_value=0.0, step=0.1)

    if st.button("Save Patient & Get AI Prediction"):
        if not full_name or not email:
            st.warning("Please fill in all fields.")
        else:
            payload = {
                "full_name"   : full_name,
                "dob"         : str(dob),
                "email"       : email,
                "glucose"     : glucose,
                "haemoglobin" : haemoglobin,
                "cholesterol" : cholesterol,
            }
            with st.spinner("Saving patient and generating AI prediction..."):
                res = requests.post(f"{API}/patients", json=payload)
            if res.status_code == 200:
                data = res.json()
                st.success("Patient saved successfully!")
                st.info(f"🤖 AI Prediction: {data['remarks']}")
            else:
                st.error(f"Error: {res.json()['detail']}")


# ─── UPDATE PATIENT ───────────────────────────────────────
elif menu == "Update Patient":
    st.subheader("Update Patient Record")

    patient_id  = st.number_input("Enter Patient ID to update", min_value=1, step=1)
    glucose     = st.number_input("New Glucose (mg/dL)",     min_value=0.0, step=0.1)
    haemoglobin = st.number_input("New Haemoglobin (g/dL)",  min_value=0.0, step=0.1)
    cholesterol = st.number_input("New Cholesterol (mg/dL)", min_value=0.0, step=0.1)

    if st.button("Update Patient"):
        payload = {
            "glucose"     : glucose,
            "haemoglobin" : haemoglobin,
            "cholesterol" : cholesterol,
        }
        res = requests.put(f"{API}/patients/{int(patient_id)}", json=payload)
        if res.status_code == 200:
            st.success("Patient updated successfully!")
            st.json(res.json())
        else:
            st.error(f"Error: {res.json()['detail']}")


# ─── DELETE PATIENT ───────────────────────────────────────
elif menu == "Delete Patient":
    st.subheader("Delete Patient Record")

    patient_id = st.number_input("Enter Patient ID to delete", min_value=1, step=1)

    if st.button("Delete Patient"):
        res = requests.delete(f"{API}/patients/{int(patient_id)}")
        if res.status_code == 200:
            st.success(res.json()["message"])
        else:
            st.error(f"Error: {res.json()['detail']}")