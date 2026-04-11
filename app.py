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

/* ===== HERO SECTION ===== */
.hero-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 60px 40px;
    border-radius: 20px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
}

.hero-left {
    width: 55%;
}

.hero-left h1 {
    font-size: 48px;
    font-weight: 800;
}

.hero-left p {
    font-size: 18px;
    margin-top: 10px;
    color: #e5e7eb;
}

.hero-points {
    margin-top: 20px;
    font-size: 15px;
}

.hero-right {
    width: 35%;
}

/* ===== LOGIN CARD ===== */
.login-card {
    background: white;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0 15px 40px rgba(0,0,0,0.2);
}

/* ===== TOOL CARDS ===== */
.tool {
    background: white;
    padding: 25px;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    transition: 0.3s;
}

.tool:hover {
    transform: translateY(-6px);
}

.icon {
    font-size: 35px;
}

/* ===== NORMAL CARDS ===== */
.card {
    padding:20px;
    border-radius:15px;
    color:white;
    text-align:center;
    font-size:18px;
    font-weight:bold;
}

.total { background: linear-gradient(135deg, #6366f1, #8b5cf6); }
.pending { background: linear-gradient(135deg, #f59e0b, #f97316); }
.completed { background: linear-gradient(135deg, #10b981, #34d399); }

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

# ================= 🔥 PREMIUM HERO WELCOME =================
if st.session_state.page == "Welcome":

    col1, col2 = st.columns([2,1])

    with col1:
        st.markdown("""
        <div class="hero-left">
            <h1>💼 CA Toolkit</h1>
            <p>The easiest way to manage GST, clients & insights</p>

            <div class="hero-points">
            ✔ Track all GST mismatches<br>
            ✔ AI-style insights (no complexity)<br>
            ✔ Manage all clients in one place
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        st.subheader("Welcome Back")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            st.success("Demo login successful")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("###")

    # 🔽 TOOL CARDS BELOW
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="tool"><div class="icon">📊</div><b>Dashboard</b></div>', unsafe_allow_html=True)
        if st.button("Open Dashboard", key="dash_btn"):
            st.session_state.page = "Dashboard"
            st.rerun()

    with col2:
        st.markdown('<div class="tool"><div class="icon">📑</div><b>GST Tool</b></div>', unsafe_allow_html=True)
        if st.button("Open GST Tool", key="gst_btn"):
            st.session_state.page = "GST Tool"
            st.rerun()

    with col3:
        st.markdown('<div class="tool"><div class="icon">👥</div><b>Clients</b></div>', unsafe_allow_html=True)
        if st.button("Open Clients", key="client_btn"):
            st.session_state.page = "Clients"
            st.rerun()

    st.stop()

# ================= BACK BUTTON =================
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
    c2.markdown(f'<div class="card pending">Pending<br>{pending}</div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="card completed">Completed<br>{completed}</div>', unsafe_allow_html=True)

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
        c1.markdown(f'<div class="card pending">Missing<br>{len(missing)}</div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="card total">Mismatch<br>{len(mismatch)}</div>', unsafe_allow_html=True)

        fig, ax = plt.subplots(figsize=(4,4))
        ax.pie([len(missing), len(mismatch)], labels=["Missing","Mismatch"], autopct='%1.1f%%')
        st.pyplot(fig)

# ================= CLIENTS =================
elif st.session_state.page == "Clients":

    st.title("👥 Clients")

    st.dataframe(client_df, use_container_width=True)
