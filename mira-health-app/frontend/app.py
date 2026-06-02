import streamlit as st
import requests
from datetime import date
import pandas as pd

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="MIRA Health", page_icon="🏥", layout="wide")
st.title("🏥 MIRA — Medical Intelligence Robotic Automation")

menu = st.sidebar.selectbox("Menu", ["View Patients", "Add Patient", "Update Patient", "Delete Patient"])


# ─── HELPER FUNCTIONS ─────────────────────────────────────
def fetch_patients():
    res = requests.get(f"{API}/patients")
    if res.status_code == 200:
        return res.json()
    return []

def filter_patients(patients, search_term):
    if not search_term:
        return patients
    search_term = search_term.lower()
    return [
        p for p in patients
        if search_term in p["full_name"].lower()
        or search_term in p["email"].lower()
        or search_term in p["id"].lower()
    ]


# ─── VIEW ALL PATIENTS ────────────────────────────────────
if menu == "View Patients":
    st.subheader("All Patients")

    search = st.text_input("🔍 Search by Name, Email or UUID")
    patients = fetch_patients()
    patients = filter_patients(patients, search)

    if patients:
        display_cols = ["id", "full_name", "dob", "email", "glucose", "haemoglobin", "cholesterol", "created_at", "remarks"]
        df = pd.DataFrame(patients)[display_cols]

        st.caption("Select a row to view patient details.")
        ROW_HEIGHT = 38   # approximate px per row
        HEADER_HEIGHT = 38

        dynamic_height = HEADER_HEIGHT + (ROW_HEIGHT * len(df))
        selection = st.dataframe(
            df,
            use_container_width=False,
            column_config={
                "id"         : st.column_config.TextColumn("UUID"),
                "full_name"  : st.column_config.TextColumn("Full Name"),
                "dob"        : st.column_config.TextColumn("DOB"),
                "email"      : st.column_config.TextColumn("Email"),
                "glucose"    : st.column_config.NumberColumn("Glucose"),
                "haemoglobin": st.column_config.NumberColumn("Haemoglobin"),
                "cholesterol": st.column_config.NumberColumn("Cholesterol"),
                "created_at" : st.column_config.TextColumn("Created At"),
                "remarks"    : st.column_config.TextColumn("AI Remarks", width="large"),
            },
            hide_index=True,
            height=dynamic_height,
            on_select="rerun",        # ← row click pe rerun
            selection_mode="single-row",  # ← ek baar mein ek hi row
        )

        st.caption(f"Total records: {len(patients)}")

        # ─── Row select hone par dialog kholo ─────────────────
        selected_rows = selection.selection.rows
        if selected_rows:
            selected = patients[selected_rows[0]]  # selected patient dict

            @st.dialog(f"🏥 {selected['full_name']}", width="large")
            def show_patient_dialog():
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Patient Info**")
                    st.write(f"**Name:** {selected['full_name']}")
                    st.write(f"**DOB:** {selected['dob']}")
                    st.write(f"**Email:** {selected['email']}")
                    st.write(f"**Created:** {selected.get('created_at', 'N/A')}")
                    st.write(f"**UUID:** `{selected['id']}`")
                with col2:
                    st.markdown("**Blood Test Values**")
                    st.metric("Glucose",     f"{selected['glucose']} mg/dL")
                    st.metric("Haemoglobin", f"{selected['haemoglobin']} g/dL")
                    st.metric("Cholesterol", f"{selected['cholesterol']} mg/dL")
                st.divider()
                st.markdown("**🤖 Full AI Remarks**")
                st.info(selected.get('remarks') or "No remarks available.")

            show_patient_dialog()

    else:
        st.info("No patients found.")

# ─── ADD PATIENT ──────────────────────────────────────────
elif menu == "Add Patient":
    st.subheader("Add New Patient")

    # Fix 4 — form clear hoga submit ke baad using session state
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False

    if st.session_state.form_submitted:
        st.session_state.form_submitted = False
        st.rerun()

    with st.form(key="add_patient_form", clear_on_submit=True):
        full_name   = st.text_input("Full Name")
        dob         = st.date_input("Date of Birth", min_value=date(1900, 1, 1), max_value=date.today())
        email       = st.text_input("Email Address")
        glucose     = st.number_input("Glucose (mg/dL)",     min_value=0.0, step=0.1)
        haemoglobin = st.number_input("Haemoglobin (g/dL)",  min_value=0.0, step=0.1)
        cholesterol = st.number_input("Cholesterol (mg/dL)", min_value=0.0, step=0.1)

        submitted = st.form_submit_button("💾 Save Patient & Get AI Prediction")

    if submitted:
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
                st.success("✅ Patient saved successfully!")
                st.info(f"🤖 AI Prediction: {data['remarks']}")
                st.session_state.form_submitted = True
            else:
                st.error(f"Error: {res.json()['detail']}")


# ─── UPDATE PATIENT ───────────────────────────────────────
elif menu == "Update Patient":
    st.subheader("Update Patient Record")

    patients = fetch_patients()

    if not patients:
        st.info("No patients found. Add one first.")
    else:
        search = st.text_input("🔍 Search by Name, Email or UUID")
        filtered = filter_patients(patients, search)

        if not filtered:
            st.warning("No patients match your search.")
        else:
            st.markdown("#### Select a patient from the table:")

            display_cols = ["id", "full_name", "dob", "email", "glucose", "haemoglobin", "cholesterol", "created_at"]
            df = pd.DataFrame(filtered)[display_cols].copy()
            df.insert(0, "Select", False)

            edited_df = st.data_editor(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Select": st.column_config.CheckboxColumn("Select", default=False),
                    "id": st.column_config.TextColumn("UUID", width="medium"),
                },
                disabled=["id", "full_name", "dob", "email", "glucose", "haemoglobin", "cholesterol", "created_at"],
            )

            selected_rows = edited_df[edited_df["Select"] == True]

            if len(selected_rows) == 0:
                st.info("☝️ Select a patient from the table above to edit.")

            elif len(selected_rows) > 1:
                st.warning("Please select only one patient to update.")

            else:
                selected_id = selected_rows.iloc[0]["id"]
                selected_patient = next(p for p in filtered if p["id"] == selected_id)

                st.divider()
                st.markdown(f"#### ✏️ Editing: **{selected_patient['full_name']}**")

                # Show current remarks before editing
                with st.expander("📋 Current AI Remarks", expanded=False):
                    st.info(selected_patient.get("remarks") or "No remarks available.")

                col1, col2 = st.columns(2)

                with col1:
                    new_name  = st.text_input("Full Name",     value=selected_patient["full_name"])
                    new_email = st.text_input("Email Address", value=selected_patient["email"])
                    new_dob   = st.date_input(
                        "Date of Birth",
                        value=date.fromisoformat(selected_patient["dob"]),
                        min_value=date(1900, 1, 1),
                        max_value=date.today()
                    )

                with col2:
                    new_glucose     = st.number_input("Glucose (mg/dL)",     value=float(selected_patient["glucose"]),     min_value=0.0, step=0.1)
                    new_haemoglobin = st.number_input("Haemoglobin (g/dL)",  value=float(selected_patient["haemoglobin"]), min_value=0.0, step=0.1)
                    new_cholesterol = st.number_input("Cholesterol (mg/dL)", value=float(selected_patient["cholesterol"]), min_value=0.0, step=0.1)

                st.divider()

                if st.button("💾 Save Changes & Regenerate AI Prediction"):
                    payload = {
                        "full_name"   : new_name,
                        "email"       : new_email,
                        "dob"         : str(new_dob),
                        "glucose"     : new_glucose,
                        "haemoglobin" : new_haemoglobin,
                        "cholesterol" : new_cholesterol,
                    }
                    with st.spinner("Updating and regenerating AI prediction..."):
                        res = requests.put(f"{API}/patients/{selected_patient['id']}", json=payload)

                    if res.status_code == 200:
                        updated = res.json()
                        st.success(f"✅ {updated['full_name']} updated successfully!")
                        st.info(f"🤖 New AI Prediction: {updated['remarks']}")
                    else:
                        st.error(f"Error: {res.json()['detail']}")


# ─── DELETE PATIENT — Gmail style ─────────────────────────
elif menu == "Delete Patient":
    st.subheader("Delete Patients")

    patients = fetch_patients()

    if not patients:
        st.info("No patients found.")
    else:
        search = st.text_input("🔍 Search by Name, Email or UUID")
        filtered = filter_patients(patients, search)

        if not filtered:
            st.warning("No patients match your search.")
        else:
            st.markdown("#### Select patients to delete:")

            display_cols = ["id", "full_name", "dob", "email", "glucose", "haemoglobin", "cholesterol", "created_at"]
            df = pd.DataFrame(filtered)[display_cols].copy()
            df.insert(0, "Select", False)

            edited_df = st.data_editor(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Select": st.column_config.CheckboxColumn("Select", default=False),
                    "id": st.column_config.TextColumn("UUID", width="large"),
                },
                disabled=["id", "full_name", "dob", "email", "glucose", "haemoglobin", "cholesterol", "created_at"],
            )

            selected_ids = edited_df[edited_df["Select"] == True]["id"].tolist()

            st.divider()

            if selected_ids:
                st.warning(f"⚠️ {len(selected_ids)} patient(s) selected for deletion.")

                # Fix 3 — Delete confirmation
                st.error("🚨 Are you sure you want to delete the selected patient(s)? This action cannot be undone.")

                col1, col2 = st.columns([1, 5])

                with col1:
                    if st.button("Yes, Delete"):
                        res = requests.delete(
                            f"{API}/patients",
                            json={"ids": selected_ids}
                        )
                        if res.status_code == 200:
                            st.success(res.json()["message"])
                            st.rerun()
                        else:
                            st.error("Error deleting patients.")

                with col2:
                    if st.button("❌ Cancel"):
                        st.rerun()
            else:
                st.info("Select patients from the table above to delete.")