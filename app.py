import pandas as pd
import streamlit as st
from datetime import datetime, date
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="CA Toolkit", layout="wide")

# ================= UI =================
st.markdown("""
<style>
.main { background-color: #f8fafc; }

.hero {
    text-align:center;
    padding: 60px 20px;
}

.hero h1 {
    font-size: 52px;
    font-weight: 800;
}

.hero p {
    font-size: 18px;
    color: #6b7280;
}

.feature {
    background:white;
    padding:25px;
    border-radius:16px;
    text-align:center;
    box-shadow:0 8px 20px rgba(0,0,0,0.05);
    transition:0.3s;
}

.feature:hover {
    transform: translateY(-6px);
}

.tool {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    padding:30px;
    border-radius:16px;
    color:white;
    text-align:center;
    font-size:18px;
    font-weight:600;
}

.card {
    padding:20px;
    border-radius:15px;
    color:white;
    text-align:center;
    font-size:18px;
    font-weight:bold;
}

.total { background: linear-gradient(135deg, #6366f1, #8b5cf6); }
pending { background: linear-gradient(135deg, #f59e0b, #f97316); }
completed { background: linear-gradient(135deg, #10b981, #34d399); }

.section {
    background:white;
    padding:20px;
    border-radius:12px;
    margin-top:20px;
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

# ================= SESSION =================
if "page" not in st.session_state:
    st.session_state.page = "Welcome"

# ================= LANDING =================
if st.session_state.page == "Welcome":

    st.markdown("""
    <div class="hero">
        <h1>💼 CA Toolkit</h1>
        <p>Smart GST insights, client tracking & automation — all in one place</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🚀 Why use this?")

    f1, f2, f3 = st.columns(3)
    f1.markdown('<div class="feature">📊<br><b>GST Insights</b><br>Detect mismatches instantly</div>', unsafe_allow_html=True)
    f2.markdown('<div class="feature">⚡ Fast Workflow<br>Save hours of manual work</div>', unsafe_allow_html=True)
    f3.markdown('<div class="feature">📁 Client Management<br>Track all clients</div>', unsafe_allow_html=True)

    st.markdown("### 🎯 Get Started")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="tool">📊 Dashboard</div>', unsafe_allow_html=True)
        if st.button("Open Dashboard"):
            st.session_state.page = "Dashboard"
            st.rerun()

    with col2:
        st.markdown('<div class="tool">📑 GST Tool</div>', unsafe_allow_html=True)
        if st.button("Open GST Tool"):
            st.session_state.page = "GST Tool"
            st.rerun()

    with col3:
        st.markdown('<div class="tool">👥 Clients</div>', unsafe_allow_html=True)
        if st.button("Open Clients"):
            st.session_state.page = "Clients"
            st.rerun()

    st.stop()

# ================= BACK =================
if st.button("⬅ Back to Home"):
    st.session_state.page = "Welcome"
    st.rerun()

# ================= SIDEBAR =================
st.sidebar.title("💼 CA Toolkit")

module = st.sidebar.radio(
    "",
    ["Dashboard", "GST Tool", "Clients"],
    index=["Dashboard", "GST Tool", "Clients"].index(st.session_state.page)
)

st.session_state.page = module

# ================= DASHBOARD =================
if st.session_state.page == "Dashboard":

    st.title("📊 Dashboard")

    total = len(client_df)
    pending = len(client_df[client_df["Status"] == "Pending"])
    completed = len(client_df[client_df["Status"] == "Completed"])

    c1, c2, c3 = st.columns(3)

    c1.markdown(f'<div class="card total">Total<br>{total}</div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="card total">Pending<br>{pending}</div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="card total">Completed<br>{completed}</div>', unsafe_allow_html=True)

    st.dataframe(client_df, use_container_width=True)

# ================= GST =================
elif st.session_state.page == "GST Tool":

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
        c1.markdown(f'<div class="card total">Missing<br>{len(missing)}</div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="card total">Mismatch<br>{len(mismatch)}</div>', unsafe_allow_html=True)

        # ================= 🔥 UNIQUE FEATURE =================
        st.markdown("### 🤖 Smart Error Insights")

        if len(missing) > 0:
            st.warning(f"{len(missing)} invoices missing → Vendor likely not filed GSTR-1")

        if len(mismatch) > 0:
            st.error(f"{len(mismatch)} mismatches → Amount or GST value mismatch, check entries")

        if len(missing) == 0 and len(mismatch) == 0:
            st.success("No issues detected. Clean records.")

        # ================= PIE =================
        left, center, right = st.columns([1,2,1])
        with center:
            fig, ax = plt.subplots(figsize=(3,3))
            ax.pie([len(missing), len(mismatch)],
                   labels=["Missing","Mismatch"],
                   autopct='%1.1f%%')
            st.pyplot(fig)

# ================= CLIENTS =================
elif st.session_state.page == "Clients":

    st.title("👥 Clients")
    st.dataframe(client_df, use_container_width=True)
