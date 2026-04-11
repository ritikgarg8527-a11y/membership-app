import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import datetime

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Membership System", layout="wide")

# ---------- CUSTOM UI (FIXED DARK MODE) ----------
st.markdown("""
<style>
.main {
    background-color: #0e1117;
}

/* CARD */
.card {
    padding: 20px;
    border-radius: 12px;
    background: #1e1e1e;
    color: #ffffff;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    margin-bottom: 15px;
}

/* TEXT */
.card h3, .card h4 {
    color: #ffffff;
    margin-bottom: 5px;
}

.card p {
    color: #d1d5db;
    font-size: 14px;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #111827;
}
</style>
""", unsafe_allow_html=True)

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

    col1, col2, col3 = st.columns(3)

    total = len(df)
    primary = len(df[df["Type"] == "Primary"])
    family = len(df[df["Type"] == "Family"])

    col1.markdown(f"<div class='card'>📊 <h2>{total}</h2>Total Members</div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'>👤 <h2>{primary}</h2>Primary Members</div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card'>👨‍👩‍👧 <h2>{family}</h2>Family Members</div>", unsafe_allow_html=True)

    st.dataframe(df)

# ---------- ADD ----------
elif menu == "Add":
    st.subheader("➕ Add Member")

    member_type = st.selectbox("Primary / Family Member *", ["Primary", "Family"])

    col1, col2 = st.columns(2)

    with col1:
        id_ = st.text_input("Id *" if member_type == "Primary" else "Id")
        user_id = st.text_input("User ID *" if member_type == "Primary" else "User ID")
        membership = st.text_input("Membership No *" if member_type == "Primary" else "Membership No")

        fname = st.text_input("First Name *")
        mname = st.text_input("Middle Name")
        sname = st.text_input("Surname *")

        relation = st.text_input("Relation *" if member_type == "Primary" else "Relation")

    with col2:
        dob = st.date_input(
            "Date of Birth *" if member_type == "Primary" else "Date of Birth",
            min_value=datetime.date(1950, 1, 1),
            max_value=datetime.date.today()
        )

        blood = st.text_input("Blood Group *" if member_type == "Primary" else "Blood Group")
        occupation = st.text_input("Occupation *" if member_type == "Primary" else "Occupation")

        email = st.text_input("Email *" if member_type == "Primary" else "Email")
        box = st.text_input("Box No.")

        phone1 = st.text_input("Phone No.1 *")
        phone2 = st.text_input("Phone No.2")
        phone3 = st.text_input("Phone No.3")

        location = st.text_input("Location *")
        remarks = st.text_input("Remarks")

    if st.button("Add Member"):

        if member_type == "Primary":
            if not all([id_, user_id, membership, fname, sname, relation,
                        blood, occupation, email, phone1, location]):
                st.error("❌ Fill all required Primary fields")
                st.stop()
        else:
            if not all([fname, sname, phone1, location]):
                st.error("❌ Fill required Family fields")
                st.stop()

        sheet.append_row([
            id_, user_id, membership, member_type,
            fname, mname, sname, relation,
            str(dob), blood, occupation, email,
            box, phone1, phone2, phone3, location, remarks
        ])

        st.success("✅ Member Added Successfully")
        st.rerun()

# ---------- SEARCH ----------
elif menu == "Search / Edit / Delete":
    st.subheader("🔍 Search Member")

    m = st.text_input("Enter Membership No")

    if m:
        group = df[df["MemberShip No"].astype(str) == m]

        if not group.empty:
            st.success("Records Found ✅")

            primary = group[group["Type"] == "Primary"]
            if not primary.empty:
                p = primary.iloc[0]

                st.markdown(f"""
                <div class='card'>
                <h3>👤 {p['First Name']} {p['Surname']}</h3>
                <p>☎️ {p['Phone No.1']}</p>
                <p>📌 {p['LOCATION']}</p>
                </div>
                """, unsafe_allow_html=True)

            family = group[group["Type"] == "Family"]

            for i in range(len(family)):
                f = family.iloc[i]

                st.markdown(f"""
                <div class='card'>
                <h4>👤 {f['First Name']} {f['Surname']}</h4>
                <p>Relation: {f['Relation']}</p>
                <p>☎️ {f['Phone No.1']}</p>
                </div>
                """, unsafe_allow_html=True)

            st.dataframe(group)

        else:
            st.error("Not found")

# ---------- EDIT ----------
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
        st.rerun()
