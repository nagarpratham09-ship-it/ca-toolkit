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
}

.tool {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    padding:30px;
    border-radius:16px;
    color:white;
    text-align:center;
}

.card {
    padding:20px;
    border-radius:15px;
    color:white;
    text-align:center;
    font-weight:bold;
}

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

        # ===== EXISTING AI INSIGHTS =====
        st.markdown("### 🧠 AI Insights")

        if len(missing) > 0:
            st.warning(f"{len(missing)} invoices missing → Vendor filing issue")
        if len(mismatch) > 0:
            st.error(f"{len(mismatch)} mismatches → Check entries")
        if len(missing) == 0 and len(mismatch) == 0:
            st.success("All records clean")

       
# ================= CLIENTS =================
elif st.session_state.page == "Clients":

    st.title("👥 Client Management")

    # ================= TABLE =================
    st.subheader("📋 Client Records")
    st.dataframe(client_df, use_container_width=True)

    # ================= ADD CLIENT =================
    st.markdown("### ➕ Add New Client")

    col1, col2, col3 = st.columns(3)

    with col1:
        new_name = st.text_input("Client Name")

    with col2:
        new_status = st.selectbox("Status", ["Pending", "Completed"])

    with col3:
        new_due = st.date_input("Due Date")

    if st.button("➕ Add Client"):
        if new_name:
            new_row = pd.DataFrame([{
                "Client Name": new_name,
                "Status": new_status,
                "Due Date": new_due,
                "Last Updated": datetime.now()
            }])

            client_df = pd.concat([client_df, new_row], ignore_index=True)
            client_df.to_excel(FILE_PATH, index=False)

            st.success("Client added successfully")
            st.rerun()
        else:
            st.warning("Enter client name")

    # ================= UPDATE / DELETE =================
    st.markdown("### ✏️ Update / Delete Client")

    if not client_df.empty:

        selected_client = st.selectbox(
            "Select Client",
            client_df["Client Name"]
        )

        client_row = client_df[client_df["Client Name"] == selected_client].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            updated_status = st.selectbox(
                "Update Status",
                ["Pending", "Completed"],
                index=0 if client_row["Status"] == "Pending" else 1
            )

        with col2:
            updated_due = st.date_input(
                "Update Due Date",
                value=client_row["Due Date"]
            )

        # 👉 SAME LINE BUTTONS
        colA, colB = st.columns(2)

        with colA:
            if st.button("✅ Update"):
                client_df.loc[
                    client_df["Client Name"] == selected_client,
                    ["Status", "Due Date", "Last Updated"]
                ] = [updated_status, updated_due, datetime.now()]

                client_df.to_excel(FILE_PATH, index=False)
                st.success("Client updated")
                st.rerun()

        with colB:
            if st.button("🗑️ Delete"):
                client_df = client_df[
                    client_df["Client Name"] != selected_client
                ]

                client_df.to_excel(FILE_PATH, index=False)
                st.warning("Client deleted")
                st.rerun()

    else:
        st.info("No clients available")

    st.title("👥 Clients")
    # ================= CLIENT TABLE =================
st.subheader("📋 Client Records")

st.dataframe(client_df, use_container_width=True)

st.markdown("### ✏️ Manage Clients")

# Select client
if not client_df.empty:
    selected_client = st.selectbox(
        "Select Client",
        client_df["Client Name"]
    )

    client_row = client_df[client_df["Client Name"] == selected_client].iloc[0]

    new_name = st.text_input("Client Name", value=client_row["Client Name"])
    new_status = st.selectbox(
        "Status",
        ["Pending", "Completed"],
        index=0 if client_row["Status"] == "Pending" else 1
    )
    new_due = st.date_input("Due Date", value=client_row["Due Date"])

    # 👉 UPDATE + DELETE IN SAME LINE
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Update Client"):
            client_df.loc[client_df["Client Name"] == selected_client, [
                "Client Name", "Status", "Due Date", "Last Updated"
            ]] = [new_name, new_status, new_due, datetime.now()]

            client_df.to_excel(FILE_PATH, index=False)
            st.success("Client updated successfully")
            st.rerun()

    with col2:
        if st.button("🗑️ Delete Client"):
            client_df = client_df[client_df["Client Name"] != selected_client]

            client_df.to_excel(FILE_PATH, index=False)
            st.warning("Client deleted")
            st.rerun()

else:
    st.info("No clients available")
