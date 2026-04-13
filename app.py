import pandas as pd
import streamlit as st
from datetime import datetime, date, timedelta
import os
import io

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title=\"CA Toolkit — GST Reconciliation\",
    page_icon=\"📊\",
    layout=\"wide\",
    initial_sidebar_state=\"expanded\"
)

# ================= CUSTOM CSS (Same as Website) =================
st.markdown(\"\"\"
<style>
@import url('https://fonts.googleapis.com/css2?family=Chivo:wght@400;500;600;700;800;900&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

/* Hide default streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Global */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

/* Hero Section */
.hero-banner {
    background: #1A202C;
    background-image: url('https://images.unsplash.com/photo-1770816305998-57eec25ac2d5?w=1200&q=60');
    background-size: cover;
    background-blend-mode: overlay;
    border-radius: 12px;
    padding: 50px 40px;
    margin-bottom: 28px;
    color: white;
}

.hero-banner h1 {
    font-family: 'Chivo', sans-serif;
    font-size: 42px;
    font-weight: 900;
    letter-spacing: -1px;
    margin: 0 0 8px 0;
    color: white;
}

.hero-banner p {
    font-size: 16px;
    opacity: 0.75;
    margin: 0;
    max-width: 500px;
}

/* Page Title */
.page-title {
    font-family: 'Chivo', sans-serif;
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #1A202C;
    margin-bottom: 4px;
}

.page-subtitle {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 14px;
    color: #64748B;
    margin-bottom: 24px;
}

/* Metric Cards */
.metric-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    margin-bottom: 28px;
}

.metric-box {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 20px;
    transition: transform 0.15s;
}

.metric-box:hover {
    transform: translateY(-1px);
}

.metric-label {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #64748B;
    font-weight: 600;
    margin-bottom: 8px;
}

.metric-value {
    font-family: 'Chivo', sans-serif;
    font-size: 32px;
    font-weight: 800;
    line-height: 1;
    color: #1A202C;
}

.metric-value.success { color: #38A169; }
.metric-value.warning { color: #D69E2E; }
.metric-value.error { color: #E53E3E; }

/* Section Card */
.section-box {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
}

.section-title {
    font-family: 'Chivo', sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: #1A202C;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid #E2E8F0;
}

/* Status Badge */
.badge {
    display: inline-block;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.badge-success { background: #F0FFF4; color: #38A169; }
.badge-warning { background: #FFFFF0; color: #D69E2E; }
.badge-error { background: #FEF2F2; color: #E53E3E; }

/* Feature Cards */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 32px;
}

.feature-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 28px 24px;
    text-align: center;
    transition: transform 0.15s, box-shadow 0.15s;
}

.feature-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}

.feature-card h3 {
    font-family: 'Chivo', sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: #1A202C;
    margin: 12px 0 6px 0;
}

.feature-card p {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 13px;
    color: #64748B;
    margin: 0;
}

.feature-icon {
    font-size: 28px;
}

/* Overline */
.overline-text {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    font-weight: 700;
    color: #64748B;
    margin-bottom: 12px;
}

/* Insight Box */
.insight-success {
    background: #F0FFF4;
    border: 1px solid #C6F6D5;
    border-radius: 8px;
    padding: 14px 20px;
    color: #38A169;
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 16px;
}

.insight-warning {
    background: #FFFFF0;
    border: 1px solid #FEFCBF;
    border-radius: 8px;
    padding: 14px 20px;
    color: #D69E2E;
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 16px;
}

.insight-error {
    background: #FEF2F2;
    border: 1px solid #FED7D7;
    border-radius: 8px;
    padding: 14px 20px;
    color: #E53E3E;
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 16px;
}

/* Upload Zone */
.upload-label {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #64748B;
    margin-bottom: 6px;
}

/* Sidebar styling */
section[data-testid=\"stSidebar\"] {
    background: #1A202C;
}

section[data-testid=\"stSidebar\"] .stRadio label {
    color: rgba(255,255,255,0.7) !important;
}

section[data-testid=\"stSidebar\"] .stRadio label:hover {
    color: white !important;
}

section[data-testid=\"stSidebar\"] h1 {
    color: white !important;
    font-family: 'Chivo', sans-serif;
    font-size: 20px !important;
    font-weight: 800 !important;
}

section[data-testid=\"stSidebar\"] .stMarkdown p {
    color: rgba(255,255,255,0.5) !important;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.15em;
}

/* Table styling */
.dataframe {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 13px !important;
}
</style>
\"\"\", unsafe_allow_html=True)

# ================= CLIENT DATA FILE =================
FILE_PATH = \"clients_data.xlsx\"

if os.path.exists(FILE_PATH):
    client_df = pd.read_excel(FILE_PATH)
else:
    client_df = pd.DataFrame(columns=[\"Client Name\", \"Status\", \"Due Date\", \"Last Updated\"])

if \"Due Date\" in client_df.columns:
    client_df[\"Due Date\"] = pd.to_datetime(client_df[\"Due Date\"], errors='coerce').dt.date

today = date.today()

# ================= SEED DATA (if empty) =================
if client_df.empty:
    seed_data = [
        {\"Client Name\": \"Reliance Industries\", \"Status\": \"Pending\", \"Due Date\": today + timedelta(days=1), \"Last Updated\": datetime.now()},
        {\"Client Name\": \"Tata Motors\", \"Status\": \"Completed\", \"Due Date\": today - timedelta(days=5), \"Last Updated\": datetime.now()},
        {\"Client Name\": \"Infosys Ltd\", \"Status\": \"Pending\", \"Due Date\": today, \"Last Updated\": datetime.now()},
        {\"Client Name\": \"Wipro Technologies\", \"Status\": \"Pending\", \"Due Date\": today - timedelta(days=2), \"Last Updated\": datetime.now()},
        {\"Client Name\": \"HCL Technologies\", \"Status\": \"Completed\", \"Due Date\": today + timedelta(days=5), \"Last Updated\": datetime.now()},
    ]
    client_df = pd.DataFrame(seed_data)
    client_df.to_excel(FILE_PATH, index=False)

# ================= SESSION STATE =================
if \"page\" not in st.session_state:
    st.session_state.page = \"Home\"

# ================= SIDEBAR =================
st.sidebar.markdown(\"# CA Toolkit\")
st.sidebar.markdown(\"GST Reconciliation\")
st.sidebar.markdown(\"---\")

module = st.sidebar.radio(
    \"Navigation\",
    [\"Home\", \"Dashboard\", \"GST Tool\", \"Clients\"],
    index=[\"Home\", \"Dashboard\", \"GST Tool\", \"Clients\"].index(st.session_state.page),
    label_visibility=\"collapsed\"
)

st.session_state.page = module

# ================= HELPER: GST CLEAN FUNCTION =================
def clean_gst_dataframe(df):
    \"\"\"Clean and normalize a GST dataframe. Removes blank/invalid rows.\"\"\"
    df.columns = df.columns.str.strip()

    # Normalize GSTIN
    df['GSTIN'] = df['GSTIN'].astype(str).str.replace('.0', '', regex=False).str.strip()

    # Normalize Invoice No
    df['Invoice No'] = df['Invoice No'].astype(str).str.strip().str.replace(\" \", \"\")

    # Normalize Amount
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')

    # ===== FIX: Remove blank/invalid rows =====
    # This prevents blank Excel rows from creating false \"Missing\" records
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

    # Create matching key
    df['key'] = df['GSTIN'] + \"_\" + df['Invoice No']
    return df

# =================================================================
#                         HOME PAGE
# =================================================================
if st.session_state.page == \"Home\":

    st.markdown(\"\"\"
    <div class=\"hero-banner\">
        <h1>CA Toolkit</h1>
        <p>Smart GST insights, client tracking & automation — all in one place. Built for Chartered Accountants.</p>
    </div>
    \"\"\", unsafe_allow_html=True)

    st.markdown('<div class=\"overline-text\">GET STARTED</div>', unsafe_allow_html=True)

    st.markdown(\"\"\"
    <div class=\"feature-grid\">
        <div class=\"feature-card\">
            <div class=\"feature-icon\">📊</div>
            <h3>Dashboard</h3>
            <p>Client overview, deadlines & priority panel</p>
        </div>
        <div class=\"feature-card\">
            <div class=\"feature-icon\">📑</div>
            <h3>GST Tool</h3>
            <p>Upload & reconcile Purchase vs GSTR-2B</p>
        </div>
        <div class=\"feature-card\">
            <div class=\"feature-icon\">👥</div>
            <h3>Clients</h3>
            <p>Manage client records & export data</p>
        </div>
    </div>
    \"\"\", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(\"Open Dashboard\", use_container_width=True, type=\"primary\"):
            st.session_state.page = \"Dashboard\"
            st.rerun()
    with col2:
        if st.button(\"Open GST Tool\", use_container_width=True, type=\"primary\"):
            st.session_state.page = \"GST Tool\"
            st.rerun()
    with col3:
        if st.button(\"Open Clients\", use_container_width=True, type=\"primary\"):
            st.session_state.page = \"Clients\"
            st.rerun()

# =================================================================
#                       DASHBOARD PAGE
# =================================================================
elif st.session_state.page == \"Dashboard\":

    st.markdown('<div class=\"page-title\">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class=\"page-subtitle\">Client overview and deadline tracking</div>', unsafe_allow_html=True)

    # -------- METRICS --------
    total = len(client_df)
    pending = len(client_df[client_df[\"Status\"] == \"Pending\"])
    completed = len(client_df[client_df[\"Status\"] == \"Completed\"])

    # Calculate days left
    client_df_calc = client_df.copy()
    client_df_calc[\"Days Left\"] = (
        pd.to_datetime(client_df_calc[\"Due Date\"]) - pd.Timestamp.today()
    ).dt.days

    urgent_clients = client_df_calc[
        (client_df_calc[\"Days Left\"] >= 0) & (client_df_calc[\"Days Left\"] <= 2)
    ]
    overdue_clients = client_df_calc[client_df_calc[\"Days Left\"] < 0]

    st.markdown(f\"\"\"
    <div class=\"metric-row\">
        <div class=\"metric-box\">
            <div class=\"metric-label\">Total Clients</div>
            <div class=\"metric-value\">{total}</div>
        </div>
        <div class=\"metric-box\">
            <div class=\"metric-label\">Pending</div>
            <div class=\"metric-value warning\">{pending}</div>
        </div>
        <div class=\"metric-box\">
            <div class=\"metric-label\">Completed</div>
            <div class=\"metric-value success\">{completed}</div>
        </div>
        <div class=\"metric-box\">
            <div class=\"metric-label\">Overdue</div>
            <div class=\"metric-value error\">{len(overdue_clients)}</div>
        </div>
    </div>
    \"\"\", unsafe_allow_html=True)

    # -------- URGENT --------
    st.markdown('<div class=\"section-box\"><div class=\"section-title\">Urgent Deadlines (within 2 days)</div>', unsafe_allow_html=True)
    if not urgent_clients.empty:
        st.dataframe(
            urgent_clients[[\"Client Name\", \"Status\", \"Due Date\", \"Days Left\"]],
            use_container_width=True, hide_index=True
        )
    else:
        st.markdown('<div class=\"insight-success\">No urgent deadlines</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # -------- OVERDUE --------
    st.markdown('<div class=\"section-box\"><div class=\"section-title\">Overdue Clients</div>', unsafe_allow_html=True)
    if not overdue_clients.empty:
        display_overdue = overdue_clients.copy()
        display_overdue[\"Days Overdue\"] = display_overdue[\"Days Left\"].abs()
        st.dataframe(
            display_overdue[[\"Client Name\", \"Due Date\", \"Days Overdue\"]],
            use_container_width=True, hide_index=True
        )
    else:
        st.markdown('<div class=\"insight-success\">No overdue clients</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # -------- ALL CLIENTS --------
    st.markdown('<div class=\"section-box\"><div class=\"section-title\">All Clients</div>', unsafe_allow_html=True)
    st.dataframe(client_df[[\"Client Name\", \"Status\", \"Due Date\"]], use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =================================================================
#                       GST TOOL PAGE
# =================================================================
elif st.session_state.page == \"GST Tool\":

    st.markdown('<div class=\"page-title\">GST Reconciliation</div>', unsafe_allow_html=True)
    st.markdown('<div class=\"page-subtitle\">Upload Purchase Register & GSTR-2B to reconcile</div>', unsafe_allow_html=True)

    # -------- FILE UPLOAD --------
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class=\"upload-label\">Purchase Register</div>', unsafe_allow_html=True)
        file1 = st.file_uploader(\"Upload Purchase Register (.xlsx)\", type=[\"xlsx\"], key=\"purchase\", label_visibility=\"collapsed\")

    with col2:
        st.markdown('<div class=\"upload-label\">GSTR-2B</div>', unsafe_allow_html=True)
        file2 = st.file_uploader(\"Upload GSTR-2B (.xlsx)\", type=[\"xlsx\"], key=\"gstr2b\", label_visibility=\"collapsed\")

    if file1 and file2:

        if st.button(\"Reconcile\", type=\"primary\", use_container_width=False):

            with st.spinner(\"Processing...\"):

                df1 = pd.read_excel(file1)
                df2 = pd.read_excel(file2)

                # Check required columns
                required = {'GSTIN', 'Invoice No', 'Amount'}
                for name, df in [(\"Purchase Register\", df1), (\"GSTR-2B\", df2)]:
                    missing_cols = required - set(df.columns.str.strip())
                    if missing_cols:
                        st.error(f\"{name} is missing columns: {', '.join(missing_cols)}\")
                        st.stop()

                # Clean using the fix function
                df1 = clean_gst_dataframe(df1)
                df2 = clean_gst_dataframe(df2)

                # Merge (inner join)
                merged = pd.merge(df1, df2, on='key', how='inner', suffixes=('_purchase', '_2B'))

                # Mismatch
                mismatch = merged[abs(merged['Amount_purchase'] - merged['Amount_2B']) > 1].copy()

                # Missing in 2B
                matched_keys = merged['key']
                missing_in_2b = df1[~df1['key'].isin(matched_keys)].copy()

                # Missing in Purchase
                missing_in_purchase = df2[~df2['key'].isin(matched_keys)].copy()

                matched_count = len(merged) - len(mismatch)

                # -------- METRICS --------
                st.markdown(f\"\"\"
                <div class=\"metric-row\">
                    <div class=\"metric-box\">
                        <div class=\"metric-label\">Matched</div>
                        <div class=\"metric-value success\">{matched_count}</div>
                    </div>
                    <div class=\"metric-box\">
                        <div class=\"metric-label\">Missing in 2B</div>
                        <div class=\"metric-value warning\">{len(missing_in_2b)}</div>
                    </div>
                    <div class=\"metric-box\">
                        <div class=\"metric-label\">Missing in Purchase</div>
                        <div class=\"metric-value\">{len(missing_in_purchase)}</div>
                    </div>
                    <div class=\"metric-box\">
                        <div class=\"metric-label\">Mismatch</div>
                        <div class=\"metric-value error\">{len(mismatch)}</div>
                    </div>
                </div>
                \"\"\", unsafe_allow_html=True)

                # -------- INSIGHTS --------
                if len(missing_in_2b) == 0 and len(mismatch) == 0 and len(missing_in_purchase) == 0:
                    st.markdown('<div class=\"insight-success\">All records are clean — no missing or mismatched invoices found.</div>', unsafe_allow_html=True)

                if len(missing_in_2b) > 0:
                    st.markdown(f'<div class=\"insight-warning\">{len(missing_in_2b)} invoices missing in GSTR-2B → Vendor issue</div>', unsafe_allow_html=True)

                if len(mismatch) > 0:
                    st.markdown(f'<div class=\"insight-error\">{len(mismatch)} amount mismatches detected → Check entries</div>', unsafe_allow_html=True)

                # -------- TABS --------
                tab1, tab2, tab3, tab4 = st.tabs([
                    f\"Matched ({matched_count})\",
                    f\"Missing in 2B ({len(missing_in_2b)})\",
                    f\"Missing in Purchase ({len(missing_in_purchase)})\",
                    f\"Mismatched ({len(mismatch)})\"
                ])

                with tab1:
                    if not merged.empty:
                        display_matched = merged[['GSTIN_purchase', 'Invoice No_purchase', 'Amount_purchase', 'Amount_2B']].copy()
                        display_matched.columns = ['GSTIN', 'Invoice No', 'Purchase Amount', '2B Amount']
                        st.dataframe(display_matched, use_container_width=True, hide_index=True)
                    else:
                        st.info(\"No matched records\")

                with tab2:
                    if not missing_in_2b.empty:
                        st.dataframe(
                            missing_in_2b[['GSTIN', 'Invoice No', 'Amount']],
                            use_container_width=True, hide_index=True
                        )
                    else:
                        st.markdown('<div class=\"insight-success\">No missing invoices in GSTR-2B</div>', unsafe_allow_html=True)

                with tab3:
                    if not missing_in_purchase.empty:
                        st.dataframe(
                            missing_in_purchase[['GSTIN', 'Invoice No', 'Amount']],
                            use_container_width=True, hide_index=True
                        )
                    else:
                        st.markdown('<div class=\"insight-success\">No missing invoices in Purchase Register</div>', unsafe_allow_html=True)

                with tab4:
                    if not mismatch.empty:
                        mismatch['Difference'] = mismatch['Amount_purchase'] - mismatch['Amount_2B']
                        display_mismatch = mismatch[['GSTIN_purchase', 'Invoice No_purchase', 'Amount_purchase', 'Amount_2B', 'Difference']].copy()
                        display_mismatch.columns = ['GSTIN', 'Invoice No', 'Purchase Amount', '2B Amount', 'Difference']
                        st.dataframe(display_mismatch, use_container_width=True, hide_index=True)
                    else:
                        st.markdown('<div class=\"insight-success\">No mismatched invoices</div>', unsafe_allow_html=True)

                # -------- EXPORT BUTTON --------
                st.markdown(\"---\")
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    if not merged.empty:
                        merged[['GSTIN_purchase', 'Invoice No_purchase', 'Amount_purchase', 'Amount_2B']].to_excel(
                            writer, sheet_name='Matched', index=False
                        )
                    if not missing_in_2b.empty:
                        missing_in_2b[['GSTIN', 'Invoice No', 'Amount']].to_excel(
                            writer, sheet_name='Missing in 2B', index=False
                        )
                    if not missing_in_purchase.empty:
                        missing_in_purchase[['GSTIN', 'Invoice No', 'Amount']].to_excel(
                            writer, sheet_name='Missing in Purchase', index=False
                        )
                    if not mismatch.empty:
                        mismatch['Difference'] = mismatch['Amount_purchase'] - mismatch['Amount_2B']
                        mismatch[['GSTIN_purchase', 'Invoice No_purchase', 'Amount_purchase', 'Amount_2B', 'Difference']].to_excel(
                            writer, sheet_name='Mismatched', index=False
                        )
                output.seek(0)

                st.download_button(
                    label=\"Download Reconciliation Report (.xlsx)\",
                    data=output,
                    file_name=\"reconciliation_report.xlsx\",
                    mime=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\",
                    type=\"primary\"
                )

    else:
        st.info(\"Upload both files above and click **Reconcile** to start.\")

# =================================================================
#                       CLIENTS PAGE
# =================================================================
elif st.session_state.page == \"Clients\":

    st.markdown('<div class=\"page-title\">Client Management</div>', unsafe_allow_html=True)
    st.markdown('<div class=\"page-subtitle\">Track, search and manage all your clients</div>', unsafe_allow_html=True)

    # -------- SEARCH & FILTER --------
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input(\"Search clients...\", label_visibility=\"collapsed\", placeholder=\"Search clients...\")
    with col2:
        filter_status = st.selectbox(\"Filter\", [\"All\", \"Pending\", \"Completed\"], label_visibility=\"collapsed\")

    filtered_df = client_df.copy()
    if search:
        filtered_df = filtered_df[filtered_df[\"Client Name\"].str.contains(search, case=False, na=False)]
    if filter_status != \"All\":
        filtered_df = filtered_df[filtered_df[\"Status\"] == filter_status]

    # -------- ACTION BUTTONS --------
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 4])
    with btn_col1:
        st.download_button(
            \"Export CSV\",
            filtered_df.to_csv(index=False),
            \"clients.csv\",
            use_container_width=True
        )
    with btn_col2:
        add_clicked = st.button(\"Add Client\", type=\"primary\", use_container_width=True)

    # -------- CLIENT TABLE --------
    st.markdown('<div class=\"section-box\"><div class=\"section-title\">Client Database</div>', unsafe_allow_html=True)
    if not filtered_df.empty:
        st.dataframe(
            filtered_df[[\"Client Name\", \"Status\", \"Due Date\", \"Last Updated\"]],
            use_container_width=True, hide_index=True
        )
    else:
        st.info(\"No clients found\")
    st.markdown('</div>', unsafe_allow_html=True)

    # -------- ADD CLIENT --------
    if add_clicked:
        st.session_state.show_add = True

    if st.session_state.get(\"show_add\", False):
        st.markdown('<div class=\"section-box\"><div class=\"section-title\">Add New Client</div>', unsafe_allow_html=True)

        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            new_name = st.text_input(\"Client Name\", key=\"new_client_name\")
        with ac2:
            new_status = st.selectbox(\"Status\", [\"Pending\", \"Completed\"], key=\"new_client_status\")
        with ac3:
            new_due = st.date_input(\"Due Date\", key=\"new_client_due\")

        sc1, sc2 = st.columns([1, 5])
        with sc1:
            if st.button(\"Save Client\", type=\"primary\"):
                if new_name:
                    new_row = pd.DataFrame([{
                        \"Client Name\": new_name,
                        \"Status\": new_status,
                        \"Due Date\": new_due,
                        \"Last Updated\": datetime.now()
                    }])
                    client_df = pd.concat([client_df, new_row], ignore_index=True)
                    client_df.to_excel(FILE_PATH, index=False)
                    st.session_state.show_add = False
                    st.success(f\"Client '{new_name}' added successfully!\")
                    st.rerun()
                else:
                    st.warning(\"Please enter a client name\")
        with sc2:
            if st.button(\"Cancel\"):
                st.session_state.show_add = False
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # -------- MANAGE CLIENTS --------
    if not filtered_df.empty:
        st.markdown('<div class=\"section-box\"><div class=\"section-title\">Manage Existing Clients</div>', unsafe_allow_html=True)

        selected = st.selectbox(\"Select Client\", filtered_df[\"Client Name\"], key=\"manage_client\")
        idx = client_df[client_df[\"Client Name\"] == selected].index[0]

        mc1, mc2, mc3 = st.columns(3)

        with mc1:
            updated_status = st.selectbox(
                \"Update Status\",
                [\"Pending\", \"Completed\"],
                index=[\"Pending\", \"Completed\"].index(client_df.loc[idx, \"Status\"]) if client_df.loc[idx, \"Status\"] in [\"Pending\", \"Completed\"] else 0,
                key=\"update_status\"
            )

        with mc2:
            current_due = client_df.loc[idx, \"Due Date\"]
            if pd.notna(current_due):
                if isinstance(current_due, date):
                    updated_due = st.date_input(\"Update Due Date\", value=current_due, key=\"update_due\")
                else:
                    updated_due = st.date_input(\"Update Due Date\", key=\"update_due\")
            else:
                updated_due = st.date_input(\"Update Due Date\", key=\"update_due\")

        with mc3:
            st.write(\"\")  # spacing
            st.write(\"\")
            uc1, uc2 = st.columns(2)
            with uc1:
                if st.button(\"Update\", type=\"primary\", use_container_width=True):
                    client_df.loc[idx, \"Status\"] = updated_status
                    client_df.loc[idx, \"Due Date\"] = updated_due
                    client_df.loc[idx, \"Last Updated\"] = datetime.now()
                    client_df.to_excel(FILE_PATH, index=False)
                    st.success(f\"'{selected}' updated!\")
                    st.rerun()
            with uc2:
                if st.button(\"Delete\", type=\"secondary\", use_container_width=True):
                    client_df = client_df.drop(idx)
                    client_df.to_excel(FILE_PATH, index=False)
                    st.warning(f\"'{selected}' deleted!\")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
"
