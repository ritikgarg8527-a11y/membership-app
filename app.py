import streamlit as st
import pandas as pd
import json
import os

# ---------- LOAD DATA ----------
file_path = os.path.join(os.getcwd(), "data.xlsx")
df = pd.read_excel(file_path)

# ---------- LOAD USERS ----------
with open("users.json") as f:
    users = json.load(f)

# ---------- SESSION ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- LOGIN ----------
if not st.session_state.logged_in:
    st.title("🔐 Login System")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.success("Login Successful ✅")
        else:
            st.error("Invalid Credentials ❌")

# ---------- MAIN APP ----------
else:
    st.title("📊 Membership Dashboard")

    menu = st.sidebar.selectbox("Menu", ["View", "Search/Edit", "Add"])

    # VIEW
    if menu == "View":
        st.subheader("All Members")
        st.dataframe(df)

    # SEARCH & EDIT
    elif menu == "Search/Edit":
        m = st.text_input("Enter Membership No")

        if m:
            row = df[df["MemberShip No"] == m]

            if not row.empty:
                i = row.index[0]

                fname = st.text_input("First Name", row.iloc[0]["First Name"])
                phone = st.text_input("Phone", row.iloc[0]["Phone No.1"])

                if st.button("Update"):
                    df.at[i, "First Name"] = fname
                    df.at[i, "Phone No.1"] = phone
                    df.to_excel(file_path, index=False)
                    st.success("Updated ✅")
            else:
                st.error("Not Found ❌")

    # ADD
    elif menu == "Add":
        m = st.text_input("Membership No")
        fname = st.text_input("First Name")

        if st.button("Add Member"):
            new = {"MemberShip No": m, "First Name": fname}
            df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
            df.to_excel(file_path, index=False)
            st.success("Added ✅")
