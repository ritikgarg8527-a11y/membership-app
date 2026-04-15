import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import datetime

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Membership System", layout="wide")

# ---------- THEME SAFE UI ----------
st.markdown("""
<style>

/* LIGHT MODE */
html[data-theme="light"] body {
    background-color: #f8fafc !important;
}
html[data-theme="light"] .card {
    background-color: #ffffff !important;
    color: #111827 !important;
}

/* DARK MODE */
html[data-theme="dark"] body {
    background-color: #0e1117 !important;
}
html[data-theme="dark"] .card {
    background-color: #1e293b !important;
    color: #e5e7eb !important;
}

/* COMMON CARD */
.card {
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
    margin-bottom: 12px;
}

/* TEXT */
.card h3, .card h4 {
    font-weight: 600;
}
.card p {
    font-size: 14px;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: inherit !important;
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

# ---------- HEADER ----------
st.title("🏢 Membership Management System")
st.caption("Professional Membership Dashboard")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Add", "Search / Edit / Delete"])

# ---------- DASHBOARD ----------
if menu == "Dashboard":
    st.subheader("📊 Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.markdown(f"<div class='card'><h3>Total</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'><h3>Primary</h3><h2>{len(df[df['Type']=='Primary'])}</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card'><h3>Family</h3><h2>{len(df[df['Type']=='Family'])}</h2></div>", unsafe_allow_html=True)

    st.dataframe(df)

# ---------- ADD ----------
elif menu == "Add":
    st.subheader("➕ Add Member")

    member_type = st.selectbox("Primary / Family Member", ["Primary", "Family"])

    col1, col2 = st.columns(2)

    with col1:
        id_ = st.text_input("Id")
        user_id = st.text_input("User ID")
        membership = st.text_input("Membership No")

        fname = st.text_input("First Name")
        mname = st.text_input("Middle Name")
        sname = st.text_input("Surname")

        relation = st.text_input("Relation")

    with col2:
        dob = st.date_input("DOB")
        blood = st.text_input("Blood Group")
        occupation = st.text_input("Occupation")

        email = st.text_input("Email")
        box = st.text_input("Box")

        phone1 = st.text_input("Phone 1")
        phone2 = st.text_input("Phone 2")
        phone3 = st.text_input("Phone 3")

        location = st.text_input("Location")
        remarks = st.text_input("Remarks")

    if st.button("Add"):
        sheet.append_row([
            id_, user_id, membership, member_type,
            fname, mname, sname, relation,
            str(dob), blood, occupation, email,
            box, phone1, phone2, phone3, location, remarks
        ])
        st.success("Added")
        st.rerun()

# ---------- SEARCH / EDIT / DELETE ----------
elif menu == "Search / Edit / Delete":
    st.subheader("🔍 Search Member")

    m = st.text_input("Enter Membership No")

    if m:
        group = df[df["MemberShip No"].astype(str) == m]

        if not group.empty:

            for i in range(len(group)):
                row = group.iloc[i]

                colA, colB = st.columns([4,1])

                with colA:
                    st.markdown(f"""
                    <div class='card'>
                    <h4>👤 {row['First Name']} {row['Surname']} ({row['Type']})</h4>
                    <p>📞 {row['Phone No.1']} | 📍 {row['LOCATION']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with colB:
                    if st.button(f"✏️ Edit {i}"):
                        st.session_state.edit_index = int(row.name)

                    if st.button(f"🗑 Delete {i}"):
                        sheet.delete_rows(int(row.name) + 2)
                        st.success("Deleted")
                        st.rerun()

                # ---------- INLINE EDIT ----------
                if "edit_index" in st.session_state and st.session_state.edit_index == int(row.name):

                    st.markdown("### ✏️ Edit Details")

                    fname = st.text_input("First Name", row["First Name"], key=f"fname{i}")
                    mname = st.text_input("Middle Name", row["MiddleName"], key=f"mname{i}")
                    sname = st.text_input("Surname", row["Surname"], key=f"sname{i}")
                    relation = st.text_input("Relation", row["Relation"], key=f"rel{i}")

                    dob = st.text_input("DOB", row["DateOfBirth"], key=f"dob{i}")
                    blood = st.text_input("Blood", row["Blood Group"], key=f"blood{i}")
                    occupation = st.text_input("Occupation", row["Occupation"], key=f"occ{i}")

                    email = st.text_input("Email", row["E-mail"], key=f"email{i}")
                    phone1 = st.text_input("Phone1", row["Phone No.1"], key=f"p1{i}")
                    phone2 = st.text_input("Phone2", row["Phone No.2"], key=f"p2{i}")
                    phone3 = st.text_input("Phone3", row["Phone No.3"], key=f"p3{i}")

                    location = st.text_input("Location", row["LOCATION"], key=f"loc{i}")
                    remarks = st.text_input("Remarks", row["Remarks"], key=f"rem{i}")

                    if st.button(f"💾 Save {i}"):
                        idx = int(row.name) + 2

                        sheet.update(f"E{idx}", fname)
                        sheet.update(f"F{idx}", mname)
                        sheet.update(f"G{idx}", sname)
                        sheet.update(f"H{idx}", relation)
                        sheet.update(f"I{idx}", dob)
                        sheet.update(f"J{idx}", blood)
                        sheet.update(f"K{idx}", occupation)
                        sheet.update(f"L{idx}", email)
                        sheet.update(f"N{idx}", phone1)
                        sheet.update(f"O{idx}", phone2)
                        sheet.update(f"P{idx}", phone3)
                        sheet.update(f"Q{idx}", location)
                        sheet.update(f"R{idx}", remarks)

                        st.success("Updated")
                        del st.session_state.edit_index
                        st.rerun()

            st.dataframe(group)

        else:
            st.error("Not found")
