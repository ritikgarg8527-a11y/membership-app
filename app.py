import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import datetime

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Membership System", layout="wide")

# ---------- SAFE UI (NO THEME BREAK) ----------
st.markdown("""
<style>
.card {
    padding: 16px;
    border-radius: 10px;
    border: 1px solid rgba(128,128,128,0.2);
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------- LOGIN ----------
USERNAME = "admin"
PASSWORD = "1234"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == USERNAME and p == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
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
st.title("🏢 Membership System")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Add", "Search"])

# ---------- DASHBOARD ----------
if menu == "Dashboard":
    st.subheader("All Members")
    st.dataframe(df)

# ---------- ADD ----------
elif menu == "Add":
    st.subheader("Add Member")

    fname = st.text_input("First Name")
    sname = st.text_input("Surname")
    phone = st.text_input("Phone")
    location = st.text_input("Location")

    if st.button("Add"):
        sheet.append_row([
            "", "", "", "Primary",
            fname, "", sname, "",
            "", "", "", "",
            "", phone, "", "", location, ""
        ])
        st.success("Added")
        st.rerun()

# ---------- SEARCH ----------
elif menu == "Search":

    m = st.text_input("Membership No")

    if m:
        group = df[df["MemberShip No"].astype(str) == m]

        if not group.empty:

            st.success("Records Found")

            for i in range(len(group)):
                row = group.iloc[i]

                col1, col2, col3 = st.columns([4,1,1])

                with col1:
                    st.markdown(f"""
                    <div class='card'>
                    <b>{row['First Name']} {row['Surname']} ({row['Type']})</b><br>
                    📞 {row['Phone No.1']} <br>
                    📍 {row['LOCATION']}
                    </div>
                    """, unsafe_allow_html=True)

                # EDIT BUTTON
                if col2.button(f"✏️ {i}"):
                    st.session_state.edit_index = int(row.name)

                # DELETE BUTTON
                if col3.button(f"🗑 {i}"):
                    st.session_state.delete_index = int(row.name)

                # ---------- DELETE CONFIRM ----------
                if "delete_index" in st.session_state and st.session_state.delete_index == int(row.name):
                    st.warning("Confirm delete?")
                    if st.button(f"Yes Delete {i}"):
                        sheet.delete_rows(int(row.name)+2)
                        del st.session_state.delete_index
                        st.rerun()

                # ---------- FULL EDIT FORM ----------
                if "edit_index" in st.session_state and st.session_state.edit_index == int(row.name):

                    st.markdown("### ✏️ Edit Full Details")

                    fname = st.text_input("First Name", row["First Name"], key=f"f{i}")
                    mname = st.text_input("Middle Name", row["MiddleName"], key=f"m{i}")
                    sname = st.text_input("Surname", row["Surname"], key=f"s{i}")
                    relation = st.text_input("Relation", row["Relation"], key=f"r{i}")

                    dob = st.text_input("DOB", row["DateOfBirth"], key=f"d{i}")
                    blood = st.text_input("Blood Group", row["Blood Group"], key=f"b{i}")
                    occupation = st.text_input("Occupation", row["Occupation"], key=f"o{i}")

                    email = st.text_input("Email", row["E-mail"], key=f"e{i}")
                    phone1 = st.text_input("Phone1", row["Phone No.1"], key=f"p1{i}")
                    phone2 = st.text_input("Phone2", row["Phone No.2"], key=f"p2{i}")
                    phone3 = st.text_input("Phone3", row["Phone No.3"], key=f"p3{i}")

                    location = st.text_input("Location", row["LOCATION"], key=f"l{i}")
                    remarks = st.text_input("Remarks", row["Remarks"], key=f"re{i}")

                    if st.button(f"Save {i}"):

                        idx = int(row.name) + 2

                        row_data = [
                            row["Id"], row["user_id"], row["MemberShip No"], row["Type"],
                            fname, mname, sname, relation,
                            dob, blood, occupation, email,
                            row["Box No."], phone1, phone2, phone3,
                            location, remarks
                        ]

                        sheet.update(f"A{idx}:R{idx}", [row_data])

                        st.success("Updated")
                        del st.session_state.edit_index
                        st.rerun()

            # ---------- TABLE BACK ----------
            st.markdown("### 📋 Full Data")
            st.dataframe(group)

        else:
            st.error("No data found")
