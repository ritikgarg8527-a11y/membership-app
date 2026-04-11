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

st.title("📊 Membership Management System")

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
    mname = st.text_input("Middle Name")
    sname = st.text_input("Surname")
    relation = st.text_input("Relation")

    dob = st.date_input(
        "Date of Birth",
        min_value=datetime.date(1950, 1, 1),
        max_value=datetime.date.today()
    )

    phone = st.text_input("Phone No.1")
    location = st.text_input("Location")

    if st.button("Add"):
        sheet.append_row([
            "", "", membership, "Primary", fname, mname, sname,
            relation, str(dob), "", "", "",
            "", phone, "", "", location, ""
        ])
        st.success("Added Successfully")

# ---------- SEARCH / EDIT / DELETE ----------
elif menu == "Search / Edit / Delete":
    st.subheader("🔍 Search Member")

    m = st.text_input("Enter Membership No")

    if m:
        result = df[df["MemberShip No"].astype(str) == m]
        result = result.reset_index()

        if not result.empty:
            st.success("Records Found ✅")

            # FULL TABLE
            st.dataframe(result.drop(columns=["index"]))

            st.divider()

            for i in range(len(result)):
                row = result.loc[i]

                st.markdown(f"### 👤 {row['First Name']} {row['Surname']}")

                col1, col2 = st.columns(2)

                # DELETE (FIXED)
                if col1.button(f"🗑 Delete {i}"):
                    sheet.delete_rows(int(row["index"]) + 2)
                    st.success("Deleted")
                    st.experimental_rerun()

                # EDIT (FIXED)
                if col2.button(f"✏️ Edit {i}"):
                    st.session_state.edit_row = row
                    st.session_state.edit_index = int(row["index"])
                    st.session_state.edit_mode = True

        else:
            st.error("Not found")

# ---------- FULL EDIT FORM ----------
if "edit_mode" in st.session_state and st.session_state.edit_mode:

    row = st.session_state.edit_row
    index = int(st.session_state.edit_index) + 2

    st.subheader("✏️ Edit Full Member")

    id_ = st.text_input("Id", row["Id"])
    user_id = st.text_input("User ID", row["user_id"])
    membership = st.text_input("Membership No", row["MemberShip No"])
    type_ = st.text_input("Type", row["Type"])

    fname = st.text_input("First Name", row["First Name"])
    mname = st.text_input("Middle Name", row["MiddleName"])
    sname = st.text_input("Surname", row["Surname"])
    relation = st.text_input("Relation", row["Relation"])

    dob = st.text_input("Date of Birth", row["DateOfBirth"])
    blood = st.text_input("Blood Group", row["Blood Group"])
    occupation = st.text_input("Occupation", row["Occupation"])

    email = st.text_input("Email", row["E-mail"])
    box = st.text_input("Box No.", row["Box No."])

    phone1 = st.text_input("Phone No.1", row["Phone No.1"])
    phone2 = st.text_input("Phone No.2", row["Phone No.2"])
    phone3 = st.text_input("Phone No.3", row["Phone No.3"])

    location = st.text_input("Location", row["LOCATION"])
    remarks = st.text_input("Remarks", row["Remarks"])

    if st.button("Update All Data"):

        sheet.update(f"A{index}", id_)
        sheet.update(f"B{index}", user_id)
        sheet.update(f"C{index}", membership)
        sheet.update(f"D{index}", type_)
        sheet.update(f"E{index}", fname)
        sheet.update(f"F{index}", mname)
        sheet.update(f"G{index}", sname)
        sheet.update(f"H{index}", relation)
        sheet.update(f"I{index}", dob)
        sheet.update(f"J{index}", blood)
        sheet.update(f"K{index}", occupation)
        sheet.update(f"L{index}", email)
        sheet.update(f"M{index}", box)
        sheet.update(f"N{index}", phone1)
        sheet.update(f"O{index}", phone2)
        sheet.update(f"P{index}", phone3)
        sheet.update(f"Q{index}", location)
        sheet.update(f"R{index}", remarks)

        st.success("✅ Fully Updated")
        st.session_state.edit_mode = False
        st.experimental_rerun()
