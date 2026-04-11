import pandas as pd
import streamlit as st
from datetime import datetime, date
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="CA Toolkit", layout="wide")

# 🎨 ADD-ON UI (NO LOGIC CHANGE)
st.markdown("""
<style>

/* Background */
.main {
    background-color: #f6f8fc;
}

/* Headings */
h1, h2, h3 {
    font-weight: 700;
}

/* Improve existing cards */
.card {
    border-radius: 16px !important;
    box-shadow: 0 8px 20px rgba(0,0,0,0.08) !important;
}

/* Improve sections */
.section {
    border-radius: 16px !important;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06) !important;
}

/* Buttons */
.stButton > button {
    border-radius: 10px !important;
    padding: 10px 18px !important;
    font-weight: 600 !important;
}

/* Inputs */
.stTextInput input,
.stSelectbox div,
.stDateInput input {
    border-radius: 10px !important;
}

/* Table */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* Spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

</style>
""", unsafe_allow_html=True)

FILE_PATH = "clients_data.xlsx"

# Load data
if os.path.exists(FILE_PATH):
    client_df = pd.read_excel(FILE_PATH)
else:
    client_df = pd.DataFrame(columns=["Client Name", "Status", "Due Date", "Last Updated"])

if "Due Date" in client_df.columns:
    client_df["Due Date"] = pd.to_datetime(client_df["Due Date"], errors='coerce').dt.date

today = date.today()

# Sidebar
st.sidebar.title("💼 CA Toolkit")
module = st.sidebar.radio("", ["Dashboard", "GST Tool", "Clients"])

# ================= DASHBOARD =================
if module == "Dashboard":

    st.title("📊 Dashboard")

    total = len(client_df)
    pending = len(client_df[client_df["Status"] == "Pending"])
    completed = len(client_df[client_df["Status"] == "Completed"])

    c1, c2, c3 = st.columns(3)

    c1.markdown(f'<div class="card total">Total<br>{total}</div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="card pending">Pending<br>{pending}</div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="card completed">Completed<br>{completed}</div>', unsafe_allow_html=True)

    st.markdown("### 📋 Client List")
    st.dataframe(client_df, use_container_width=True)

# ================= GST TOOL =================
elif module == "GST Tool":

    st.title("📊 GST Reconciliation")

    file1 = st.file_uploader("Purchase Register", type=["xlsx"])
    file2 = st.file_uploader("GSTR-2B", type=["xlsx"])

    if file1 and file2:

        df1 = pd.read_excel(file1)
        df2 = pd.read_excel(file2)

        df1['key'] = df1['GSTIN'].astype(str).str.strip() + df1['Invoice No'].astype(str).str.strip()
        df2['key'] = df2['GSTIN'].astype(str).str.strip() + df2['Invoice No'].astype(str).str.strip()

        merged = pd.merge(df1, df2, on='key', suffixes=('_purchase', '_2B'))

        missing = df1[~df1['key'].isin(df2['key'])]
        mismatch = merged[merged['Amount_purchase'] != merged['Amount_2B']]

        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="card pending">Missing<br>{len(missing)}</div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="card total">Mismatch<br>{len(mismatch)}</div>', unsafe_allow_html=True)

        st.markdown("### 📊 Issue Summary")

        labels = ["Missing", "Mismatch"]
        sizes = [len(missing), len(mismatch)]

        labels = [l for l, s in zip(labels, sizes) if s > 0]
        sizes = [s for s in sizes if s > 0]

        if sizes:
            fig, ax = plt.subplots(figsize=(4,4))
            ax.pie(sizes, labels=labels, autopct='%1.1f%%')
            st.pyplot(fig)

# ================= CLIENTS =================
elif module == "Clients":

    st.title("👥 Client Management System")

    # TABLE FIRST
    st.subheader("📋 Client Database")
    st.dataframe(client_df, use_container_width=True)

    st.markdown("---")

    # ADD CLIENT
    st.subheader("➕ Add New Client")

    col1, col2, col3 = st.columns(3)

    with col1:
        name = st.text_input("Client Name")

    with col2:
        status = st.selectbox("Status", ["Pending", "Completed"], key="add_status")

    with col3:
        due = st.date_input("Due Date", key="add_due")

    if st.button("Add Client"):
        if name:
            new = pd.DataFrame([{
                "Client Name": name,
                "Status": status,
                "Due Date": due,
                "Last Updated": datetime.now()
            }])

            client_df = pd.concat([client_df, new], ignore_index=True)
            client_df.to_excel(FILE_PATH, index=False)
            st.success("Client added")

    st.markdown("---")

    # UPDATE DELETE
    st.subheader("✏️ Manage Clients")

    if not client_df.empty:

        selected = st.selectbox("Select Client", client_df["Client Name"], key="select_client")
        idx = client_df[client_df["Client Name"] == selected].index[0]

        col1, col2 = st.columns(2)

        with col1:
            new_status = st.selectbox(
                "Update Status",
                ["Pending", "Completed"],
                index=0 if client_df.loc[idx, "Status"] == "Pending" else 1,
                key="update_status"
            )

            if st.button("Update Client"):
                client_df.loc[idx, "Status"] = new_status
                client_df.loc[idx, "Last Updated"] = datetime.now()
                client_df.to_excel(FILE_PATH, index=False)
                st.success("Updated successfully")

        with col2:
            if st.button("Delete Client"):
                client_df = client_df.drop(idx)
                client_df.to_excel(FILE_PATH, index=False)
                st.warning("Deleted successfully")
