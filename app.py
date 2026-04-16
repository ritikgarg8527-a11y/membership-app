import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Membership System", layout="wide")

# ---------- UI ----------
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

# ---------- CLEAN ----------
def clean(x):
    if pd.isna(x):
        return ""
    return str(x)

# ---------- HEADER ----------
st.title("🏢 Membership System")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Add", "Search"])

# ---------- DASHBOARD ----------
if menu == "Dashboard":
    st.subheader("📊 Dashboard Overview")

    col1, col2, col3 = st.columns(3)

    total = len(df)
    primary = len(df[df["Type"] == "Primary"])
    family = len(df[df["Type"] == "Family"])

    col1.markdown(f"<div class='card'><h3>Total</h3><h2>{total}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'><h3>Primary</h3><h2>{primary}</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card'><h3>Family</h3><h2>{family}</h2></div>", unsafe_allow_html=True)

    st.dataframe(df)

# ---------- ADD ----------
elif menu == "Add":
    st.subheader("➕ Add Member")

    member_type = st.selectbox("Select Member Type", ["Primary", "Family"])

    col1, col2 = st.columns(2)

    with col1:
        if member_type == "Primary":
            id_ = st.text_input("Id *")
            user_id = st.text_input("User ID *")
        else:
            id_ = st.text_input("Id (optional)")
            user_id = st.text_input("User ID (optional)")

        membership = st.text_input("Membership No *")

        fname = st.text_input("First Name *")
        mname = st.text_input("Middle Name")
        sname = st.text_input("Surname *")

        relation = st.text_input("Relation")

    with col2:
        dob = st.text_input("Date of Birth")
        blood = st.text_input("Blood Group")
        occupation = st.text_input("Occupation")

        email = st.text_input("Email")
        box = st.text_input("Box No")

        phone1 = st.text_input("Phone No.1 *")
        phone2 = st.text_input("Phone No.2")
        phone3 = st.text_input("Phone No.3")

        location = st.text_input("Location *")
        remarks = st.text_input("Remarks")

    if st.button("Add Member"):

        # VALIDATION
        if member_type == "Primary":
            if not (id_ and user_id and membership and fname and sname and phone1 and location):
                st.error("Fill all required fields for Primary")
                st.stop()

        if member_type == "Family":
            if not (fname and sname and phone1 and location):
                st.error("Fill required fields for Family")
                st.stop()

        # ADD NEW ROW (FIXED)
        sheet.append_row([
            clean(id_),
            clean(user_id),
            clean(membership),
            member_type,

            clean(fname),
            clean(mname),
            clean(sname),
            clean(relation),

            clean(dob),
            clean(blood),
            clean(occupation),
            clean(email),

            clean(box),
            clean(phone1),
            clean(phone2),
            clean(phone3),

            clean(location),
            clean(remarks)
        ], value_input_option="USER_ENTERED")

        st.success(f"✅ {member_type} Added Successfully")
        st.rerun()

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
                    <b>{row['First Name']} {row['Surname']} ({row['Type']})</b><br>
                    📞 {row['Phone No.1']} <br>
                    📍 {row['LOCATION']}
                    </div>
                    """, unsafe_allow_html=True)

                if col2.button(f"✏️ {i}"):
                    st.session_state.edit_index = int(row.name)

                if col3.button(f"🗑 {i}"):
                    st.session_state.delete_index = int(row.name)

                # DELETE CONFIRM
                if "delete_index" in st.session_state and st.session_state.delete_index == int(row.name):
                    st.warning("Confirm delete?")
                    if st.button(f"Yes {i}"):
                        sheet.delete_rows(int(row.name) + 2)
                        del st.session_state.delete_index
                        st.rerun()

                # EDIT
                if "edit_index" in st.session_state and st.session_state.edit_index == int(row.name):

                    st.markdown("### ✏️ Edit")

                    fname = st.text_input("First Name", row["First Name"], key=f"f{i}")
                    sname = st.text_input("Surname", row["Surname"], key=f"s{i}")
                    phone1 = st.text_input("Phone", row["Phone No.1"], key=f"p{i}")
                    location = st.text_input("Location", row["LOCATION"], key=f"l{i}")

                    if st.button(f"Save {i}"):

                        idx = int(row.name) + 2

                        row_data = [clean(x) for x in row.values]

                        row_data[4] = clean(fname)
                        row_data[6] = clean(sname)
                        row_data[13] = clean(phone1)
                        row_data[16] = clean(location)

                        sheet.update(f"A{idx}:R{idx}", [row_data])

                        del st.session_state.edit_index
                        st.success("Updated")
                        st.rerun()

            st.dataframe(group)

        else:
            st.error("No data found")
