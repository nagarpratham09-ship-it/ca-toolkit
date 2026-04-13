import pandas as pd
import streamlit as st
from datetime import datetime, date
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="CA Toolkit", layout="wide")

# ================= AI ADD-ON =================
def find_probable_matches(df1, df2):
    probable = []

    for _, row1 in df1.iterrows():
        for _, row2 in df2.iterrows():

            if row1['GSTIN'] == row2['GSTIN']:

                inv1 = str(row1['Invoice No'])
                inv2 = str(row2['Invoice No'])

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

        df1.columns = df1.columns.str.strip()
        df2.columns = df2.columns.str.strip()

        df1['GSTIN'] = df1['GSTIN'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df2['GSTIN'] = df2['GSTIN'].astype(str).str.replace('.0', '', regex=False).str.strip()

        df1['Invoice No'] = df1['Invoice No'].astype(str).str.strip().str.replace(" ", "")
        df2['Invoice No'] = df2['Invoice No'].astype(str).str.strip().str.replace(" ", "")

        df1['Amount'] = pd.to_numeric(df1['Amount'], errors='coerce')
        df2['Amount'] = pd.to_numeric(df2['Amount'], errors='coerce')

        df1['key'] = df1['GSTIN'] + "_" + df1['Invoice No']
        df2['key'] = df2['GSTIN'] + "_" + df2['Invoice No']

        merged = pd.merge(df1, df2, on='key', how='inner', suffixes=('_purchase', '_2B'))

        mismatch = merged[
            abs(merged['Amount_purchase'] - merged['Amount_2B']) > 1
        ].copy()

        matched_keys = merged['key']
        missing = df1[~df1['key'].isin(matched_keys)].copy()

        # ================= ADD-ON AI =================
        probable_matches = find_probable_matches(missing, df2)

        # ================= SUMMARY =================
        c1, c2, c3 = st.columns(3)
        c1.metric("Matched", len(merged))
        c2.metric("Missing", len(missing))
        c3.metric("Mismatch", len(mismatch))

        # ================= INSIGHTS (UPGRADED) =================
        st.markdown("### 🧠 Insights")

        if len(missing) > 0:
            st.warning(f"{len(missing)} invoices missing → Vendor issue")

        if len(mismatch) > 0:
            st.error(f"{len(mismatch)} mismatches → Check entries")

        # ADD-ON
        if len(missing) > 0:
            st.info("💡 Possible reason: Vendor not filed or invoice mismatch")

        if len(missing) == 0 and len(mismatch) == 0:
            st.success("✅ Clean reconciliation")

        # ================= DOWNLOAD =================
        st.markdown("### 📤 Download Reports")

        col1, col2 = st.columns(2)

        col1.download_button("Download Missing", missing.to_csv(index=False), "missing.csv")
        col2.download_button("Download Mismatch", mismatch.to_csv(index=False), "mismatch.csv")

        # ================= AI TABLE =================
        if not probable_matches.empty:
            st.markdown("### 🤖 AI Suggested Matches")
            st.dataframe(probable_matches, use_container_width=True)

        # ================= TABS =================
        tab1, tab2 = st.tabs(["❌ Missing", "⚠️ Mismatch"])

        with tab1:
            st.dataframe(missing)

        with tab2:
            st.dataframe(mismatch)


# ================= CLIENTS =================
elif module == "Clients":

    st.title("👥 Client Management System")

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

    st.download_button("📤 Export Clients", filtered_df.to_csv(index=False), "clients.csv")

    st.dataframe(filtered_df, use_container_width=True)

    name = st.text_input("Client Name")
    status = st.selectbox("Status", ["Pending", "Completed"])
    due = st.date_input("Due Date")

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

    if not filtered_df.empty:
        selected = st.selectbox("Select Client", filtered_df["Client Name"])
        idx = client_df[client_df["Client Name"] == selected].index[0]

        new_status = st.selectbox("Update Status", ["Pending", "Completed"])

        if st.button("Update"):
            client_df.loc[idx, "Status"] = new_status
            client_df.to_excel(FILE_PATH, index=False)
            st.success("Updated")

        if st.button("Delete"):
            client_df = client_df.drop(idx)
            client_df.to_excel(FILE_PATH, index=False)
            st.warning("Deleted")
