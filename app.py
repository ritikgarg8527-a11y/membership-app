import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Membership System", layout="wide")

# ---------- SAFE UI ----------
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

# ---------- CLEAN FUNCTION ----------
def clean(x):
    if pd.isna(x):
        return ""
    return str(x)

# ---------- HEADER ----------
st.title("🏢 Membership System")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Add", "Search"])

# ---------- DASHBOARD ----------
if menu == "Dashboard":
    st.subheader("All Members")
    st.dataframe(df)

# ---------- ADD ----------
elif menu == "Add":
    st.subheader("➕ Add Member")

    member_type = st.selectbox("Select Member Type", ["Primary", "Family"])

    col1, col2 = st.columns(2)

    with col1:
        id_ = st.text_input("Id *")
        user_id = st.text_input("User ID *")
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
        ])

        st.success(f"✅ {member_type} Member Added Successfully")
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

                if col2.button(f"✏️ {i}"):
                    st.session_state.edit_index = int(row.name)

                if col3.button(f"🗑 {i}"):
                    st.session_state.delete_index = int(row.name)

                # DELETE CONFIRM
                if "delete_index" in st.session_state and st.session_state.delete_index == int(row.name):
                    st.warning("⚠️ Confirm Delete?")
                    c1, c2 = st.columns(2)

                    if c1.button(f"Yes Delete {i}"):
                        sheet.delete_rows(int(row.name) + 2)
                        del st.session_state.delete_index
                        st.success("Deleted")
                        st.rerun()

                    if c2.button("Cancel"):
                        del st.session_state.delete_index
                        st.rerun()

                # EDIT
                if "edit_index" in st.session_state and st.session_state.edit_index == int(row.name):

                    st.markdown("### ✏️ Edit Full Details")

                    fname = st.text_input("First Name", row["First Name"], key=f"f{i}")
                    mname = st.text_input("Middle Name", row["MiddleName"], key=f"m{i}")
                    sname = st.text_input("Surname", row["Surname"], key=f"s{i}")
                    relation = st.text_input("Relation", row["Relation"], key=f"r{i}")

                    dob = st.text_input("DOB", clean(row["DateOfBirth"]), key=f"d{i}")
                    blood = st.text_input("Blood Group", row["Blood Group"], key=f"b{i}")
                    occupation = st.text_input("Occupation", row["Occupation"], key=f"o{i}")

                    email = st.text_input("Email", row["E-mail"], key=f"e{i}")
                    phone1 = st.text_input("Phone1", row["Phone No.1"], key=f"p1{i}")
                    phone2 = st.text_input("Phone2", row["Phone No.2"], key=f"p2{i}")
                    phone3 = st.text_input("Phone3", row["Phone No.3"], key=f"p3{i}")

                    location = st.text_input("Location", row["LOCATION"], key=f"l{i}")
                    remarks = st.text_input("Remarks", row["Remarks"], key=f"re{i}")

                    if st.button(f"💾 Save {i}"):

                        idx = int(row.name) + 2

                        row_data = [
                            clean(row["Id"]),
                            clean(row["user_id"]),
                            clean(row["MemberShip No"]),
                            clean(row["Type"]),

                            clean(fname),
                            clean(mname),
                            clean(sname),
                            clean(relation),

                            clean(dob),
                            clean(blood),
                            clean(occupation),
                            clean(email),

                            clean(row["Box No."]),
                            clean(phone1),
                            clean(phone2),
                            clean(phone3),

                            clean(location),
                            clean(remarks)
                        ]

                        sheet.update(f"A{idx}:R{idx}", [row_data])

                        st.success("✅ Updated Successfully")
                        del st.session_state.edit_index
                        st.rerun()

            st.markdown("### 📋 Full Data")
            st.dataframe(group)

        else:
            st.error("No data found")
