import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import datetime

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Membership System", layout="wide")

# ---------- PROFESSIONAL LIGHT UI ----------
st.markdown("""
<style>

/* LIGHT CLEAN BACKGROUND */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #f8fafc !important;
    color: #1e293b !important;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #ffffff !important;
}

/* CARD */
.card {
    padding: 20px;
    border-radius: 12px;
    background-color: #ffffff !important;
    color: #111827 !important;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
    margin-bottom: 12px;
}

/* TEXT */
.card h3, .card h4 {
    color: #111827 !important;
}

.card p {
    color: #475569 !important;
    font-size: 14px;
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

st.title("🏢 Membership Management System")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Add", "Search / Edit / Delete"])

# ---------- DASHBOARD ----------
if menu == "Dashboard":
    st.subheader("📊 Dashboard")

    col1, col2, col3 = st.columns(3)

    total = len(df)
    primary = len(df[df["Type"] == "Primary"])
    family = len(df[df["Type"] == "Family"])

    col1.markdown(f"<div class='card'><h3>📊 Total</h3><h2>{total}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'><h3>👤 Primary</h3><h2>{primary}</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card'><h3>👨‍👩‍👧 Family</h3><h2>{family}</h2></div>", unsafe_allow_html=True)

    st.dataframe(df)

# ---------- ADD ----------
elif menu == "Add":
    st.subheader("➕ Add Member")

    member_type = st.selectbox("Primary / Family Member *", ["Primary", "Family"])

    col1, col2 = st.columns(2)

    with col1:
        id_ = st.text_input("Id")
        user_id = st.text_input("User ID")
        membership = st.text_input("Membership No *")

        fname = st.text_input("First Name *")
        mname = st.text_input("Middle Name")
        sname = st.text_input("Surname *")

        relation = st.text_input("Relation")

    with col2:
        dob = st.date_input("Date of Birth")
        blood = st.text_input("Blood Group")
        occupation = st.text_input("Occupation")

        email = st.text_input("Email")
        box = st.text_input("Box No.")

        phone1 = st.text_input("Phone No.1 *")
        phone2 = st.text_input("Phone No.2")
        phone3 = st.text_input("Phone No.3")

        location = st.text_input("Location *")
        remarks = st.text_input("Remarks")

    if st.button("Add Member"):
        if not all([fname, sname, phone1, location]):
            st.error("Required fields missing")
        else:
            sheet.append_row([
                id_, user_id, membership, member_type,
                fname, mname, sname, relation,
                str(dob), blood, occupation, email,
                box, phone1, phone2, phone3, location, remarks
            ])
            st.success("✅ Added")
            st.rerun()

# ---------- SEARCH ----------
elif menu == "Search / Edit / Delete":
    st.subheader("🔍 Search Member")

    m = st.text_input("Enter Membership No")

    if m:
        group = df[df["MemberShip No"].astype(str) == m]

        if not group.empty:

            # PRIMARY
            primary = group[group["Type"] == "Primary"]

            if not primary.empty:
                p = primary.iloc[0]

                colA, colB = st.columns([4,1])

                with colA:
                    st.markdown(f"""
                    <div class='card'>
                    <h3>👤 {p['First Name']} {p['Surname']}</h3>
                    <p>☎️ {p['Phone No.1']}</p>
                    <p>📍 {p['LOCATION']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with colB:
                    if st.button("✏️ Edit Primary"):
                        st.session_state.edit_row = p
                        st.session_state.edit_index = int(p.name)
                        st.session_state.edit_mode = True
                        st.rerun()

            # FAMILY
            family = group[group["Type"] == "Family"]

            for i in range(len(family)):
                f = family.iloc[i]

                colA, colB = st.columns([4,1])

                with colA:
                    st.markdown(f"""
                    <div class='card'>
                    <h4>👤 {f['First Name']} {f['Surname']}</h4>
                    <p>Relation: {f['Relation']}</p>
                    <p>☎️ {f['Phone No.1']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with colB:
                    if st.button(f"✏️ Edit {i}"):
                        st.session_state.edit_row = f
                        st.session_state.edit_index = int(f.name)
                        st.session_state.edit_mode = True
                        st.rerun()

            st.dataframe(group)

        else:
            st.error("Not found")

# ---------- EDIT ----------
if "edit_mode" in st.session_state and st.session_state.edit_mode:

    row = st.session_state.edit_row
    index = int(st.session_state.edit_index) + 2

    st.subheader("✏️ Edit Member")

    fname = st.text_input("First Name", row["First Name"])
    sname = st.text_input("Surname", row["Surname"])
    phone = st.text_input("Phone", row["Phone No.1"])
    location = st.text_input("Location", row["LOCATION"])

    if st.button("Save Changes"):
        sheet.update(f"E{index}", fname)
        sheet.update(f"G{index}", sname)
        sheet.update(f"N{index}", phone)
        sheet.update(f"Q{index}", location)

        st.success("Updated Successfully")
        st.session_state.edit_mode = False
        st.rerun()
