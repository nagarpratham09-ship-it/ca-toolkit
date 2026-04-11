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

.hero { text-align:center; padding: 60px 20px; }

.hero h1 { font-size: 52px; font-weight: 800; }

.hero p { font-size: 18px; color: #6b7280; }

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
        <p>Smart GST insights, client tracking & automation</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    if st.button("📊 Dashboard"):
        st.session_state.page = "Dashboard"; st.rerun()

    if st.button("📑 GST Tool"):
        st.session_state.page = "GST Tool"; st.rerun()

    if st.button("👥 Clients"):
        st.session_state.page = "Clients"; st.rerun()

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

# ================= GST =================
if st.session_state.page == "GST Tool":

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

        st.subheader("🤖 Smart Insights")

        # ================= INVOICE LEVEL AI =================
        insights = []

        # Missing
        for _, row in missing.iterrows():
            insights.append({
                "Invoice": row["Invoice No"],
                "Issue": "Missing",
                "Reason": "Vendor not filed GSTR-1",
                "Action": "Follow up with vendor"
            })

        # Mismatch
        for _, row in mismatch.iterrows():
            diff = row["Amount_p"] - row["Amount_2b"]

            if abs(diff) < 10:
                reason = "Minor rounding difference"
                action = "Can ignore or adjust"
            else:
                reason = "Incorrect invoice value"
                action = "Check GST or entry"

            insights.append({
                "Invoice": row["Invoice No"],
                "Issue": "Mismatch",
                "Reason": reason,
                "Action": action
            })

        insights_df = pd.DataFrame(insights)

        st.dataframe(insights_df, use_container_width=True)

        # ================= PIE =================
        left, center, right = st.columns([1,2,1])
        with center:
            fig, ax = plt.subplots(figsize=(3,3))
            ax.pie([len(missing), len(mismatch)],
                   labels=["Missing","Mismatch"],
                   autopct='%1.1f%%')
            st.pyplot(fig)
