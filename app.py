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

# ✅ FIXED (WORKS ONLINE)
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

st.title("📊 Membership Management System")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Add", "Search / Edit / Delete"])

# ---------- DASHBOARD ----------
if menu == "Dashboard":
    st.subheader("📊 Statistics")

    total = len(df)
    primary = len(df[df["Type"] == "Primary"])
    family = len(df[df["Type"] == "Family"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Members", total)
    col2.metric("Primary Members", primary)
    col3.metric("Family Members", family)

    st.dataframe(df)

# ---------- ADD ----------
elif menu == "Add":
    st.subheader("➕ Add Member")

    type_ = st.selectbox("Type", ["Primary", "Family"])

    membership = st.text_input("Membership No *")
    fname = st.text_input("First Name *")
    mname = st.text_input("Middle Name")
    sname = st.text_input("Surname *")
    relation = st.text_input("Relation *")

    dob = st.date_input(
        "Date of Birth",
        min_value=datetime.date(1950, 1, 1),
        max_value=datetime.date.today()
    )

    phone = st.text_input("Phone No.1 *")
    email = st.text_input("Email")
    location = st.text_input("Location *")

    if st.button("Add"):
        if not all([membership, fname, sname, relation, phone, location]):
            st.error("Fill required fields")
        else:
            sheet.append_row([
                "", "", membership, type_, fname, mname, sname,
                relation, str(dob), "", "", email,
                "", phone, "", "", location, ""
            ])
            st.success("Added Successfully")

# ---------- SEARCH ----------
elif menu == "Search / Edit / Delete":
    st.subheader("🔍 Search Member")

    m = st.text_input("Enter Membership No")

    if m:
        result = df[df["MemberShip No"].astype(str) == m]
        result = result.reset_index()

        if not result.empty:
            st.success("Records Found ✅")

            st.dataframe(result.drop(columns=["index"]))

        else:
            st.error("Not Found ❌")
