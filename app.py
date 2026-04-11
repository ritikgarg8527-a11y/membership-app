import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import datetime

# ---------- LOGIN ----------
USERNAME = "admin"
PASSWORD = "1234"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Admin Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == USERNAME and p == PASSWORD:
            st.session_state.logged_in = True
        else:
            st.error("Invalid login")

    st.stop()

# ---------- GOOGLE SHEETS ----------
scope = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

sheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1CWKJgqVShCbatUJoUWHl6w2VCiL9Xy0LXZzXBL1npRs"
).sheet1

data = sheet.get_all_records()
df = pd.DataFrame(data)
df.columns = df.columns.str.strip()

st.title("📊 Membership System")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Add", "Search / Edit / Delete"])

# ---------- DASHBOARD ----------
if menu == "Dashboard":
    st.subheader("📊 Dashboard")

    st.metric("Total Members", len(df))
    st.dataframe(df)

# ---------- ADD ----------
elif menu == "Add":
    st.subheader("➕ Add Member")

    membership = st.text_input("Membership No")
    fname = st.text_input("First Name")
    sname = st.text_input("Surname")
    phone = st.text_input("Phone")
    location = st.text_input("Location")

    if st.button("Add"):
        sheet.append_row(["", "", membership, "Primary", fname, "", sname,
                          "", "", "", "", "", "", phone, "", "", location, ""])
        st.success("Added")

# ---------- SEARCH / EDIT / DELETE ----------
elif menu == "Search / Edit / Delete":
    st.subheader("🔍 Search Member")

    m = st.text_input("Enter Membership No")

    if m:
        result = df[df["MemberShip No"].astype(str) == m]
        result = result.reset_index()

        if not result.empty:

            for i in range(len(result)):
                row = result.loc[i]

                st.markdown("---")
                st.write("👤 Name:", row["First Name"], row["Surname"])
                st.write("📞 Phone:", row["Phone No.1"])
                st.write("📍 Location:", row["LOCATION"])

                col1, col2 = st.columns(2)

                # ---------- DELETE ----------
                if col1.button(f"🗑 Delete {i}"):
                    sheet.delete_rows(row["index"] + 2)
                    st.success("Deleted")
                    st.experimental_rerun()

                # ---------- EDIT ----------
                if col2.button(f"✏️ Edit {i}"):
                    st.session_state.edit_index = row["index"]
                    st.session_state.edit_mode = True

        else:
            st.error("Not found")

# ---------- EDIT FORM ----------
if "edit_mode" in st.session_state and st.session_state.edit_mode:
    st.subheader("✏️ Edit Member")

    index = st.session_state.edit_index + 2

    fname = st.text_input("First Name")
    sname = st.text_input("Surname")
    phone = st.text_input("Phone")
    location = st.text_input("Location")

    if st.button("Update"):
        sheet.update(f"E{index}", fname)
        sheet.update(f"G{index}", sname)
        sheet.update(f"N{index}", phone)
        sheet.update(f"Q{index}", location)

        st.success("Updated")
        st.session_state.edit_mode = False
        st.experimental_rerun()
