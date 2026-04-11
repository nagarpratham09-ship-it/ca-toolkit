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

# ================= DATA =================
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

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Dashboard"):
            st.session_state.page = "Dashboard"
            st.rerun()

    with col2:
        if st.button("📑 GST Tool"):
            st.session_state.page = "GST Tool"
            st.rerun()

    with col3:
        if st.button("👥 Clients"):
            st.session_state.page = "Clients"
            st.rerun()

    st.stop()

# ================= BACK =================
if st.button("⬅ Back to Home"):
    st.session_state.page = "Welcome"
    st.rerun()

# ================= SIDEBAR =================
module = st.sidebar.radio(
    "💼 CA Toolkit",
    ["Dashboard", "GST Tool", "Clients"],
    index=["Dashboard","GST Tool","Clients"].index(st.session_state.page)
)
st.session_state.page = module

# ================= DASHBOARD =================
if st.session_state.page == "Dashboard":

    st.title("📊 Dashboard")

    total = len(client_df)
    pending = len(client_df[client_df["Status"] == "Pending"])
    completed = len(client_df[client_df["Status"] == "Completed"])

    c1, c2, c3 = st.columns(3)

    c1.metric("Total", total)
    c2.metric("Pending", pending)
    c3.metric("Completed", completed)

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
        c1.metric("Missing", len(missing))
        c2.metric("Mismatch", len(mismatch))

        # ================= SMART INSIGHTS =================
        st.markdown("### 🧠 Smart Insights")

        if len(missing) > 0:
            st.warning("Missing invoices → Vendor issue")
        if len(mismatch) > 0:
            st.error("Mismatch found → Check entries")
        if len(missing) == 0 and len(mismatch) == 0:
            st.success("All clean")

        # ================= INVOICE LEVEL =================
        st.markdown("### 📄 Invoice-Level Explanation")

        insights = []

        # Missing
        for _, row in missing.iterrows():
            insights.append({
                "Invoice": row.get("Invoice No"),
                "Issue": "Missing",
                "Reason": "Vendor not filed",
                "Risk": "Medium",
                "Action": "Follow up"
            })

        # Mismatch with risk logic
        for _, row in mismatch.iterrows():
            diff = abs(row.get("Amount_purchase", 0) - row.get("Amount_2B", 0))

            if diff <= 5:
                reason = "Rounding difference"
                action = "Ignore"
                risk = "Low"
            elif diff <= 500:
                reason = "Data entry mismatch"
                action = "Check entry"
                risk = "Medium"
            else:
                reason = "High value mismatch"
                action = "Urgent check"
                risk = "High"

            insights.append({
                "Invoice": row.get("Invoice No_purchase"),
                "Issue": "Mismatch",
                "Reason": reason,
                "Risk": risk,
                "Action": action
            })

        insights_df = pd.DataFrame(insights)

        # ================= RISK SUMMARY =================
        st.markdown("### 🚨 Risk Summary")

        high = insights_df[insights_df["Risk"]=="High"].shape[0]
        medium = insights_df[insights_df["Risk"]=="Medium"].shape[0]
        low = insights_df[insights_df["Risk"]=="Low"].shape[0]

        c1, c2, c3 = st.columns(3)
        c1.metric("🔴 High", high)
        c2.metric("🟡 Medium", medium)
        c3.metric("🟢 Low", low)

        # ================= COLOR TABLE =================
        def highlight_risk(row):
            if row["Risk"] == "High":
                return ["background-color: #fecaca"] * len(row)
            elif row["Risk"] == "Medium":
                return ["background-color: #fef3c7"] * len(row)
            else:
                return ["background-color: #dcfce7"] * len(row)

        styled_df = insights_df.style.apply(highlight_risk, axis=1)

        st.dataframe(styled_df, use_container_width=True)

        # ================= PIE =================
        fig, ax = plt.subplots(figsize=(3,3))
        ax.pie([len(missing), len(mismatch)],
               labels=["Missing","Mismatch"],
               autopct='%1.1f%%')
        st.pyplot(fig)

# ================= CLIENTS =================
elif st.session_state.page == "Clients":

    st.title("👥 Clients")
    st.dataframe(client_df, use_container_width=True)
