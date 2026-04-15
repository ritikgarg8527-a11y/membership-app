import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import datetime

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Membership System", layout="wide")

# ---------- THEME UI ----------
st.markdown("""
<style>
html[data-theme="light"] body {
    background-color: #f8fafc !important;
}
html[data-theme="dark"] body {
    background-color: #0e1117 !important;
}

.card {
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
    margin-bottom: 12px;
    background: white;
}
</style>
""", unsafe_allow_html=True)

# ---------- LOGIN ----------
USERS = {
    "admin": {"password": "1234"},
    "staff1": {"password": "1111"}
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.title("🔐 Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u in USERS and USERS[u]["password"] == p:
            st.session_state.logged_in = True
            st.session_state.username = u
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

# 👉 Activity Sheet (create manually named "Activity")
try:
    activity_sheet = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1CWKJgqVShCbatUJoUWHl6w2VCiL9Xy0LXZzXBL1npRs"
    ).worksheet("Activity")
except:
    activity_sheet = None

data = sheet.get_all_records()
df = pd.DataFrame(data)
df.columns = df.columns.str.strip()

st.title("🏢 Membership System")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Add", "Search"])

# ---------- DASHBOARD ----------
if menu == "Dashboard":
    st.subheader("Dashboard")
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

# ---------- SEARCH ----------
elif menu == "Search":

    m = st.text_input("Membership No")

    if m:
        group = df[df["MemberShip No"].astype(str) == m]

        if not group.empty:

            for i in range(len(group)):
                row = group.iloc[i]

                col1, col2, col3 = st.columns([4,1,1])

                with col1:
                    st.markdown(f"""
                    <div class='card'>
                    <h4>{row['First Name']} {row['Surname']}</h4>
                    <p>{row['Phone No.1']} | {row['LOCATION']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                # EDIT
                if col2.button(f"✏️ {i}"):
                    st.session_state.edit_index = int(row.name)

                # DELETE CONFIRM
                if col3.button(f"🗑 {i}"):
                    st.session_state.delete_index = int(row.name)

                # ---------- DELETE CONFIRM ----------
                if "delete_index" in st.session_state and st.session_state.delete_index == int(row.name):
                    st.warning("⚠️ Confirm Delete?")
                    c1, c2 = st.columns(2)

                    if c1.button(f"Yes Delete {i}"):
                        sheet.delete_rows(int(row.name) + 2)

                        if activity_sheet:
                            activity_sheet.append_row([
                                datetime.datetime.now(),
                                st.session_state.username,
                                "DELETE",
                                row["First Name"]
                            ])

                        st.success("Deleted")
                        del st.session_state.delete_index
                        st.rerun()

                    if c2.button("Cancel"):
                        del st.session_state.delete_index
                        st.rerun()

                # ---------- INLINE EDIT ----------
                if "edit_index" in st.session_state and st.session_state.edit_index == int(row.name):

                    st.markdown("### Edit Member")

                    fname = st.text_input("First Name", row["First Name"], key=f"f{i}")
                    sname = st.text_input("Surname", row["Surname"], key=f"s{i}")
                    phone = st.text_input("Phone", row["Phone No.1"], key=f"p{i}")
                    location = st.text_input("Location", row["LOCATION"], key=f"l{i}")

                    if st.button(f"Save {i}"):

                        idx = int(row.name) + 2

                        row_data = [
                            row["Id"], row["user_id"], row["MemberShip No"], row["Type"],
                            fname, "", sname, "",
                            row["DateOfBirth"], row["Blood Group"], row["Occupation"], row["E-mail"],
                            row["Box No."], phone, "", "", location, row["Remarks"]
                        ]

                        sheet.update(f"A{idx}:R{idx}", [row_data])

                        # ---------- ACTIVITY LOG ----------
                        if activity_sheet:
                            activity_sheet.append_row([
                                datetime.datetime.now(),
                                st.session_state.username,
                                "EDIT",
                                fname
                            ])

                        st.success("Updated")
                        del st.session_state.edit_index
                        st.rerun()

        else:
            st.error("No data found")
