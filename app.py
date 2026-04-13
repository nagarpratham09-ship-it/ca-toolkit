import pandas as pd
import streamlit as st
from datetime import datetime, date, timedelta
import os
import io

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="CA Toolkit — GST Reconciliation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= CUSTOM CSS =================
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}
.hero-banner {
    background: #1A202C;
    border-radius: 12px;
    padding: 50px 40px;
    margin-bottom: 28px;
    color: white;
}
.page-title {
    font-size: 28px;
    font-weight: 800;
}
.metric-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
}
.metric-box {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 20px;
}
.metric-value.success { color: #38A169; }
.metric-value.warning { color: #D69E2E; }
.metric-value.error { color: #E53E3E; }
.section-box {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ================= CLIENT DATA =================
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
    st.session_state.page = "Home"

# ================= SIDEBAR =================
st.sidebar.title("CA Toolkit")

module = st.sidebar.radio(
    "Navigation",
    ["Home", "Dashboard", "GST Tool", "Clients"],
    index=["Home", "Dashboard", "GST Tool", "Clients"].index(st.session_state.page)
)

st.session_state.page = module

# ================= CLEAN FUNCTION =================
def clean_gst_dataframe(df):
    df.columns = df.columns.str.strip()

    df['GSTIN'] = df['GSTIN'].astype(str).str.replace('.0', '', regex=False).str.strip()
    df['Invoice No'] = df['Invoice No'].astype(str).str.strip().str.replace(" ", "")
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')

    # REMOVE INVALID ROWS
    df = df[
        (df['GSTIN'].notna()) &
        (df['GSTIN'] != 'None') &
        (df['GSTIN'] != 'nan') &
        (df['GSTIN'].str.strip() != '')
    ]
    df = df[
        (df['Invoice No'].notna()) &
        (df['Invoice No'] != 'None') &
        (df['Invoice No'] != 'nan') &
        (df['Invoice No'].str.strip() != '')
    ]
    df = df[df['Amount'].notna()]

    df['key'] = df['GSTIN'] + "_" + df['Invoice No']
    return df

# ================= HOME =================
if st.session_state.page == "Home":
    st.markdown("""
    <div class="hero-banner">
        <h1>CA Toolkit</h1>
        <p>Smart GST insights & client tracking</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Open GST Tool"):
        st.session_state.page = "GST Tool"
        st.rerun()

# ================= DASHBOARD =================
elif st.session_state.page == "Dashboard":

    st.markdown('<div class="page-title">Dashboard</div>', unsafe_allow_html=True)

    total = len(client_df)
    pending = len(client_df[client_df["Status"] == "Pending"])
    completed = len(client_df[client_df["Status"] == "Completed"])

    c1, c2, c3 = st.columns(3)
    c1.metric("Total", total)
    c2.metric("Pending", pending)
    c3.metric("Completed", completed)

# ================= GST =================
elif st.session_state.page == "GST Tool":

    st.markdown('<div class="page-title">GST Reconciliation</div>', unsafe_allow_html=True)

    file1 = st.file_uploader("Upload Purchase", type=["xlsx"])
    file2 = st.file_uploader("Upload 2B", type=["xlsx"])

    if file1 and file2:

        df1 = pd.read_excel(file1)
        df2 = pd.read_excel(file2)

        df1 = clean_gst_dataframe(df1)
        df2 = clean_gst_dataframe(df2)

        merged = pd.merge(df1, df2, on='key', how='inner', suffixes=('_purchase', '_2B'))

        mismatch = merged[
            abs(merged['Amount_purchase'] - merged['Amount_2B']) > 1
        ]

        matched_keys = merged['key']
        missing_2b = df1[~df1['key'].isin(matched_keys)]
        missing_purchase = df2[~df2['key'].isin(matched_keys)]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Matched", len(merged))
        c2.metric("Missing 2B", len(missing_2b))
        c3.metric("Missing Purchase", len(missing_purchase))
        c4.metric("Mismatch", len(mismatch))

        st.write("### Missing in 2B")
        st.dataframe(missing_2b)

        st.write("### Missing in Purchase")
        st.dataframe(missing_purchase)

        st.write("### Mismatch")
        st.dataframe(mismatch)

# ================= CLIENTS =================
elif st.session_state.page == "Clients":

    st.markdown('<div class="page-title">Clients</div>', unsafe_allow_html=True)

    st.dataframe(client_df)

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
        client_df = pd.concat([client_df, new])
        client_df.to_excel(FILE_PATH, index=False)
        st.success("Added")
