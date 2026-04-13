import pandas as pd
import streamlit as st
from datetime import datetime, date
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="CA Toolkit", layout="wide")

# ================= AI FUNCTION =================
def find_probable_matches(df1, df2):
    probable = []

    for _, row1 in df1.iterrows():
        for _, row2 in df2.iterrows():

            if row1['GSTIN'] == row2['GSTIN']:

                inv1 = row1['Invoice No']
                inv2 = row2['Invoice No']

                if inv1[:4] == inv2[:4] or inv1[-3:] == inv2[-3:]:

                    probable.append({
                        "GSTIN": row1['GSTIN'],
                        "Purchase Invoice": inv1,
                        "2B Invoice": inv2,
                        "Purchase Amount": row1['Amount'],
                        "2B Amount": row2['Amount']
                    })

    return pd.DataFrame(probable)


# ================= UI =================
st.markdown("""
<style>
.main { background-color: #f8fafc; }
.hero { text-align:center; padding: 60px 20px; }
.hero h1 { font-size: 52px; font-weight: 800; }
.hero p { font-size: 18px; color: #6b7280; }
.feature { background:white; padding:25px; border-radius:16px; text-align:center; box-shadow:0 8px 20px rgba(0,0,0,0.05);}
.tool { background: linear-gradient(135deg, #6366f1, #8b5cf6); padding:30px; border-radius:16px; color:white; text-align:center;}
.card { padding:20px; border-radius:15px; color:white; text-align:center; font-weight:bold;}
.section { background:white; padding:20px; border-radius:12px; margin-top:20px;}
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

# ================= GST =================
elif st.session_state.page == "GST Tool":

    st.title("📊 GST Reconciliation")

    file1 = st.file_uploader("Purchase Register", type=["xlsx"])
    file2 = st.file_uploader("GSTR-2B", type=["xlsx"])

    if file1 and file2:

        df1 = pd.read_excel(file1)
        df2 = pd.read_excel(file2)

        df1.columns = df1.columns.str.strip()
        df2.columns = df2.columns.str.strip()

        required_cols = ["GSTIN", "Invoice No", "Amount"]

        for col in required_cols:
            if col not in df1.columns:
                st.error(f"Purchase file missing column: {col}")
                st.stop()
            if col not in df2.columns:
                st.error(f"2B file missing column: {col}")
                st.stop()

        # ===== AUTO CLEAN (UPGRADED) =====
        def clean_df(df):
            df = df.copy()
            df = df.dropna(how='all')
            df = df.dropna(axis=1, how='all')

            df['GSTIN'] = (
                df['GSTIN']
                .astype(str)
                .str.upper()
                .str.replace(r'[^A-Z0-9]', '', regex=True)
            )

            df['Invoice No'] = (
                df['Invoice No']
                .astype(str)
                .str.upper()
                .str.replace(r'[^A-Z0-9]', '', regex=True)
            )

            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')

            df = df[
                (df['GSTIN'].str.len() >= 10) &
                (df['Invoice No'].str.len() >= 3)
            ]

            return df

        df1 = clean_df(df1)
        df2 = clean_df(df2)

        df1['key'] = df1['GSTIN'] + "_" + df1['Invoice No']
        df2['key'] = df2['GSTIN'] + "_" + df2['Invoice No']

        df1 = df1.drop_duplicates(subset='key')
        df2 = df2.drop_duplicates(subset='key')

        keys_1 = set(df1['key'])
        keys_2 = set(df2['key'])

        common_keys = keys_1.intersection(keys_2)

        matched = pd.merge(df1, df2, on='key', suffixes=('_purchase', '_2B'))

        missing_2b = df1[df1['key'].isin(keys_1 - keys_2)]
        missing_purchase = df2[df2['key'].isin(keys_2 - keys_1)]

        mismatch = matched[
            abs(matched['Amount_purchase'] - matched['Amount_2B']) > 1
        ]

        # ===== AI MATCH =====
        probable_matches = find_probable_matches(missing_2b, missing_purchase)

        # ===== SUMMARY =====
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Matched", len(common_keys))
        c2.metric("Missing in 2B", len(missing_2b))
        c3.metric("Missing in Purchase", len(missing_purchase))
        c4.metric("Mismatch", len(mismatch))

        # ===== SMART INSIGHTS =====
        st.markdown("### 🧠 Smart Insights")

        if len(missing_2b) > 0:
            st.warning("⚠️ Vendor has not uploaded invoices in GSTR-1")

        if len(missing_purchase) > 0:
            st.error("❌ You have missed booking some purchase invoices")

        if len(mismatch) > 0:
            st.error("⚠️ Values mismatch → Possible entry error")

        if len(probable_matches) > 0:
            st.info("💡 Some invoices look similar → Check formatting")

        if len(missing_2b) == 0 and len(missing_purchase) == 0 and len(mismatch) == 0:
            st.success("✅ Perfect reconciliation")

        # ===== AI TABLE =====
        if not probable_matches.empty:
            st.markdown("### 🤖 AI Suggested Matches")
            st.dataframe(probable_matches, use_container_width=True)

        # ===== DOWNLOAD =====
        st.markdown("### 📤 Download Reports")

        col1, col2, col3 = st.columns(3)

        col1.download_button("Missing in 2B", missing_2b.to_csv(index=False), "missing_2b.csv")
        col2.download_button("Missing in Purchase", missing_purchase.to_csv(index=False), "missing_purchase.csv")
        col3.download_button("Mismatch", mismatch.to_csv(index=False), "mismatch.csv")

        # ===== TABS =====
        tab1, tab2, tab3 = st.tabs(["❌ Missing in 2B", "❌ Missing in Purchase", "⚠️ Mismatch"])

        with tab1:
            st.dataframe(missing_2b)

        with tab2:
            st.dataframe(missing_purchase) 

# ================= CLIENTS =================
elif module == "Clients":

    st.title("👥 Client Management System")

    # 🔍 SEARCH + FILTER (same)
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("🔍 Search & Filter")

    col1, col2 = st.columns(2)
    with col1:
        search = st.text_input("Search Client")
    with col2:
        filter_status = st.selectbox("Filter Status", ["All", "Pending", "Completed"])

    filtered_df = client_df.copy()

    if search:
        filtered_df = filtered_df[filtered_df["Client Name"].str.contains(search, case=False)]

    if filter_status != "All":
        filtered_df = filtered_df[filtered_df["Status"] == filter_status]

    st.markdown('</div>', unsafe_allow_html=True)

    # 📤 EXPORT CLIENT (NEW)
    st.download_button("📤 Export Clients", filtered_df.to_csv(index=False), "clients.csv")

    # TABLE
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📋 Client Database")
    st.dataframe(filtered_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ADD
    st.markdown('<div class="section">', unsafe_allow_html=True)
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
            st.success("Client added successfully")

    st.markdown('</div>', unsafe_allow_html=True)

    # UPDATE DELETE
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("✏️ Manage Existing Clients")

    if not filtered_df.empty:

        selected = st.selectbox("Select Client", filtered_df["Client Name"], key="select_client")
        idx = client_df[client_df["Client Name"] == selected].index[0]

        col1, col2 = st.columns(2)

        with col1:
            new_status = st.selectbox("Update Status", ["Pending", "Completed"], key="update_status")

            if st.button("Update Client"):
                client_df.loc[idx, "Status"] = new_status
                client_df.loc[idx, "Last Updated"] = datetime.now()
                client_df.to_excel(FILE_PATH, index=False)
                st.success("Client updated successfully")

        with col2:
            if st.button("Delete Client"):
                client_df = client_df.drop(idx)
                client_df.to_excel(FILE_PATH, index=False)
                st.warning("Client deleted successfully")

    st.markdown('</div>', unsafe_allow_html=True)




        with tab3:
            st.dataframe(mismatch)
