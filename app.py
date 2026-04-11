import pandas as pd
import streamlit as st
from datetime import datetime, date
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="CA Toolkit", layout="wide")

# 🎨 UI
st.markdown("""
<style>
.main { background-color: #f5f7fb; }
.card {
    padding: 20px;
    border-radius: 15px;
    color: white;
    text-align: center;
    font-size: 20px;
    font-weight: bold;
}
.total { background: linear-gradient(135deg, #667eea, #764ba2); }
.pending { background: linear-gradient(135deg, #ff9966, #ff5e62); }
.completed { background: linear-gradient(135deg, #56ab2f, #a8e063); }
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

    st.dataframe(client_df, use_container_width=True)

# ================= GST TOOL =================
elif module == "GST Tool":

    st.title("📊 GST Reconciliation")

    file1 = st.file_uploader("Purchase Register", type=["xlsx"])
    file2 = st.file_uploader("GSTR-2B", type=["xlsx"])

    if file1 and file2:

        df1 = pd.read_excel(file1)
        df2 = pd.read_excel(file2)

        df1['key'] = df1['GSTIN'].astype(str) + df1['Invoice No'].astype(str)
        df2['key'] = df2['GSTIN'].astype(str) + df2['Invoice No'].astype(str)

        merged = pd.merge(df1, df2, on='key', suffixes=('_p', '_2b'))

        missing = df1[~df1['key'].isin(df2['key'])]
        mismatch = merged[merged['Amount_p'] != merged['Amount_2b']]

        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="card pending">Missing<br>{len(missing)}</div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="card total">Mismatch<br>{len(mismatch)}</div>', unsafe_allow_html=True)

        # PIE CHART
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

    st.title("👥 Client Manager")

    # ADD
    name = st.text_input("Client Name")
    status = st.selectbox("Status", ["Pending", "Completed"])
    due = st.date_input("Due Date")

    if st.button("Add"):
        new = pd.DataFrame([{
            "Client Name": name,
            "Status": status,
            "Due Date": due,
            "Last Updated": datetime.now()
        }])
        client_df = pd.concat([client_df, new], ignore_index=True)
        client_df.to_excel(FILE_PATH, index=False)

    st.markdown("---")

    # UPDATE + DELETE
    if not client_df.empty:

        selected = st.selectbox("Select Client", client_df["Client Name"])
        idx = client_df[client_df["Client Name"] == selected].index[0]

        col1, col2 = st.columns(2)

        with col1:
            new_status = st.selectbox("Update Status", ["Pending", "Completed"])
            if st.button("Update"):
                client_df.loc[idx, "Status"] = new_status
                client_df.to_excel(FILE_PATH, index=False)

        with col2:
            if st.button("Delete"):
                client_df = client_df.drop(idx)
                client_df.to_excel(FILE_PATH, index=False)

    st.dataframe(client_df)
