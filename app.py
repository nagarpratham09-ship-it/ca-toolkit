import pandas as pd
import streamlit as st
from datetime import datetime, date
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="CA Toolkit", layout="wide")

# 🎨 COLORFUL UI
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

.section {
    background: white;
    padding: 20px;
    border-radius: 12px;
    margin-top: 15px;
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

    file1 = st.file_uploader("Purchase Register", type=["xlsx"], key="gst1")
    file2 = st.file_uploader("GSTR-2B", type=["xlsx"], key="gst2")

    if file1 and file2:

        df1 = pd.read_excel(file1)
        df2 = pd.read_excel(file2)

        df1['key'] = df1['GSTIN'].astype(str).str.strip() + df1['Invoice No'].astype(str).str.strip()
        df2['key'] = df2['GSTIN'].astype(str).str.strip() + df2['Invoice No'].astype(str).str.strip()

        merged = pd.merge(df1, df2, on='key', suffixes=('_purchase', '_2B'))

        missing = df1[~df1['key'].isin(df2['key'])]
        mismatch = merged[merged['Amount_purchase'] != merged['Amount_2B']]

        # 🎨 CARDS
        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="card pending">Missing<br>{len(missing)}</div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="card total">Mismatch<br>{len(mismatch)}</div>', unsafe_allow_html=True)

        # 🧠 AI INSIGHTS
        st.markdown("### 🧠 AI Insights")

        if len(missing) == 0 and len(mismatch) == 0:
            st.success("All records clean. No action needed.")
        else:
            if len(missing) > 0:
                st.warning(f"{len(missing)} invoices missing → follow up vendor")
            if len(mismatch) > 0:
                st.error(f"{len(mismatch)} mismatches → verify values")

        # 📋 DETAILS
        with st.expander("View Details"):
            tab1, tab2 = st.tabs(["Missing", "Mismatch"])

            with tab1:
                st.dataframe(missing)

            with tab2:
                st.dataframe(mismatch)

        # 📊 ISSUE SUMMARY (SMALL CENTERED PIE)
        st.markdown("---")
        st.markdown("### 📊 Issue Summary")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Missing Invoices", len(missing))

        with col2:
            st.metric("Mismatch Cases", len(mismatch))

        # 👉 Centered layout
        left, center, right = st.columns([1,2,1])

        with center:
            labels = ["Missing", "Mismatch"]
            sizes = [len(missing), len(mismatch)]

            labels = [l for l, s in zip(labels, sizes) if s > 0]
            sizes = [s for s in sizes if s > 0]

            if sizes:
                fig, ax = plt.subplots(figsize=(4,4))  # smaller size
                ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                ax.set_title("Issue Distribution")
                st.pyplot(fig)
            else:
                st.success("No issues to display 🎉")

    else:
        st.info("Upload both files")

# ================= CLIENTS =================
elif module == "Clients":

    st.title("👥 Client Manager")

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

    st.markdown("### 📋 Clients")
    st.dataframe(client_df, use_container_width=True)