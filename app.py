import streamlit as st
import pandas as pd
import plotly.express as px
from db_manager import DBManager
from rag_brain import RAGBrain

# --- CONFIGURATION ---
st.set_page_config(page_title="FinAI RAG", layout="wide", page_icon="🧠")

# --- WHITE THEME CSS ---
st.markdown("""
<style>
    /* Main Background */
    .stApp { background-color: #FFFFFF; color: #333333; }
    
    /* Inputs - Make them stand out on white */
    .stTextInput input, .stNumberInput input, .stDateInput input {
        background-color: #F8F9FA; 
        color: #333333; 
        border: 1px solid #E0E0E0;
    }
    
    /* Metric Cards - Clean White look with Shadow */
    .metric-card { 
        background-color: #FFFFFF; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 6px solid #6C5CE7; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #F0F0F0;
    }
    
    /* Advisory Box - Professional Light Blue */
    .advisory-box { 
        background-color: #F0F8FF; 
        padding: 30px; 
        border-radius: 12px; 
        border: 1px solid #BCDFFF; 
        margin-top: 20px; 
        color: #003366;
    }
    
    /* New Category Notification Box */
    .new-cat-box { 
        background-color: #FFF4E5; 
        padding: 15px; 
        border: 1px solid #FFB74D; 
        border-radius: 8px; 
        margin-bottom: 15px; 
        color: #663C00;
    }
    
    /* Headings */
    h1, h2, h3, h4 { color: #2c3e50; font-family: 'Helvetica Neue', sans-serif; }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZATION ---
@st.cache_resource
def get_system():
    db = DBManager()
    brain = RAGBrain(db)
    return db, brain

db, brain = get_system()

st.title("🧠 FinAI: Contextual Ledger")
st.markdown("#### RAG-Powered Financial Tracking")
st.markdown("---")

# ================= TOP SECTION: INPUT & LEDGER =================
col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.subheader("💳 Input Transaction")
    with st.form("input_form", clear_on_submit=True):
        merchant = st.text_input("Merchant Description", placeholder="e.g. Uber Ride")
        amount = st.number_input("Amount ($)", min_value=0.01)
        date = st.date_input("Date")
        
        if st.form_submit_button("Analyze & Categorize", type="primary"):
            if merchant:
                with st.spinner("🔍 Vector Search & LLM Reasoning..."):
                    # 1. Brain Processing
                    result = brain.process_transaction(merchant)
                    
                    # 2. Save to DB
                    payload = {
                        "merchant": merchant, "amount": amount, "date": date,
                        "label": result['label'], "explanation": result['explanation'],
                        "status": result['status']
                    }
                    db.save_transaction(payload)
                    
                    # 3. Update Brain Memory
                    brain.reload_index()
                    
                    st.toast(f"Labeled: {result['label']}", icon="✅")
                    st.rerun()

with col_right:
    st.subheader("📋 Transaction Ledger")
    df = db.get_ledger_data()
    
    if not df.empty:
        # Edit Options
        all_labels = sorted(db.get_all_labels())
        options = all_labels + ["➕ Create New..."]
        
        # The Grid
        edited_df = st.data_editor(
            df,
            key="ledger_edit",
            disabled=["id", "Date", "Merchant", "Amount", "Explanation"],
            column_config={
                "Label": st.column_config.SelectboxColumn("Label", options=options, required=True, width="medium"),
                "Amount": st.column_config.NumberColumn(format="$%.2f")
            },
            use_container_width=True,
            hide_index=True
        )
        
        # Handle "Create New" Logic
        new_req = edited_df[edited_df['Label'] == "➕ Create New..."]
        if not new_req.empty:
            row = new_req.iloc[0]
            st.markdown(f'<div class="new-cat-box">Define new label for: <b>{row["Merchant"]}</b></div>', unsafe_allow_html=True)
            with st.form("new_label_form"):
                col_f1, col_f2 = st.columns([3, 1])
                new_label = col_f1.text_input("New Label (Format: Word1_Word2)")
                if st.form_submit_button("Save Rule"):
                    if new_label:
                        db.update_category(row['id'], new_label)
                        brain.reload_index()
                        st.rerun()
        
        # Save Corrections Button
        if st.button("💾 Save Corrections"):
            for i, row in edited_df.iterrows():
                orig = df.loc[df['id'] == row['id'], 'Label'].values[0]
                if row['Label'] != orig and row['Label'] != "➕ Create New...":
                    db.update_category(row['id'], row['Label'])
            brain.reload_index()
            st.rerun()
    else:
        st.info("No transactions yet.")

# ================= BOTTOM SECTION: ANALYTICS =================
if not df.empty:
    st.markdown("---")
    
    # 1. METRIC CARDS
    st.subheader("📊 Financial Analytics")
    m1, m2, m3 = st.columns([1, 1, 1])
    
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin:0; color:#6C5CE7;">${df['Amount'].sum():,.2f}</h3>
            <p style="margin:0;">Total Spend</p>
        </div>
        """, unsafe_allow_html=True)
        
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin:0; color:#6C5CE7;">{len(df['Label'].unique())}</h3>
            <p style="margin:0;">Active Categories</p>
        </div>
        """, unsafe_allow_html=True)
        
    with m3:
        top_cat = df.groupby('Label')['Amount'].sum().idxmax()
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin:0; color:#6C5CE7;">{top_cat}</h3>
            <p style="margin:0;">Top Spending Area</p>
        </div>
        """, unsafe_allow_html=True)

    # 2. BIG CENTERED PIE CHART
    st.write("")
    st.write("")
    
    # We use columns to center the chart: [Spacer, Chart, Spacer]
    col_spacer_l, col_chart, col_spacer_r = st.columns([1, 3, 1])
    
    with col_chart:
        st.markdown("<h3 style='text-align: center; margin-bottom: 0;'>Spending Distribution</h3>", unsafe_allow_html=True)
        
        # Generate Pie Chart
        fig = px.pie(df, names='Label', values='Amount', hole=0.5)
        
        # Style the Chart for White Theme
        fig.update_traces(textposition='outside', textinfo='percent+label')
        fig.update_layout(
            height=550,  # Bigger Height
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)', # Transparent
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=30, b=0, l=0, r=0)
        )
        st.plotly_chart(fig, use_container_width=True)

    # 3. AI ADVISORY
    st.markdown("---")
    st.subheader("🤖 AI Wealth Manager")
    if st.button("Generate Report"):
        with st.spinner("Analyzing financial patterns..."):
            advice = brain.generate_advisory(df)
            st.markdown(f'<div class="advisory-box">{advice}</div>', unsafe_allow_html=True)