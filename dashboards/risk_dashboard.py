"""
Real-time Risk Dashboard
Displays fraud detection alerts, risk scores, and compliance metrics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="Fintech Risk Operations Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stAlert {
        background-color: #1e1e1e;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar filters
st.sidebar.header("Dashboard Filters")

# Time range filter
time_range = st.sidebar.selectbox(
    "Time Range",
    ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Custom"]
)

# Risk level filter
risk_level = st.sidebar.multiselect(
    "Risk Level",
    ["CRITICAL", "HIGH", "MEDIUM", "LOW", "MINIMAL"],
    default=["CRITICAL", "HIGH"]
)

# Transaction type filter
transaction_type = st.sidebar.multiselect(
    "Transaction Type",
    ["Payment", "Transfer", "Withdrawal", "Deposit"],
    default=["Payment", "Transfer"]
)

# Main header
st.title("🛡️ Fintech Risk Operations Dashboard")
st.markdown("---")

# Mock data generation
@st.cache_data(ttl=300)
def generate_mock_data():
    """Generate mock transaction data for dashboard"""
    np.random.seed(42)
    
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=30),
        end=datetime.now(),
        freq='1H'
    )
    
    n_transactions = 1000
    
    data = {
        'transaction_id': [f"TXN{i:06d}" for i in range(n_transactions)],
        'timestamp': np.random.choice(dates, n_transactions),
        'amount': np.random.exponential(scale=1000, size=n_transactions),
        'merchant': np.random.choice(['Amazon', 'Walmart', 'Target', 'Best Buy', 'Apple'], n_transactions),
        'category': np.random.choice(['Electronics', 'Groceries', 'Clothing', 'Home', 'Services'], n_transactions),
        'user_id': [f"USER{i:04d}" for i in np.random.randint(1, 100, n_transactions)],
        'location': np.random.choice(['US', 'UK', 'CA', 'DE', 'FR'], n_transactions),
        'fraud_probability': np.random.beta(2, 50, n_transactions),
        'risk_score': np.random.randint(0, 100, n_transactions),
        'status': np.random.choice(['approved', 'declined', 'flagged', 'pending'], n_transactions, p=[0.7, 0.1, 0.15, 0.05])
    }
    
    df = pd.DataFrame(data)
    df['is_fraud'] = df['fraud_probability'] > 0.5
    df['risk_level'] = pd.cut(
        df['risk_score'],
        bins=[0, 20, 40, 60, 80, 100],
        labels=['MINIMAL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    )
    
    return df

df = generate_mock_data()

# Apply filters
if risk_level:
    df = df[df['risk_level'].isin(risk_level)]
if transaction_type:
    # Map transaction types to categories for filtering
    category_map = {
        'Payment': ['Electronics', 'Clothing', 'Services'],
        'Transfer': ['Services'],
        'Withdrawal': ['Services'],
        'Deposit': ['Services']
    }
    filtered_categories = []
    for t in transaction_type:
        filtered_categories.extend(category_map.get(t, []))
    df = df[df['category'].isin(filtered_categories)]

# Key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Transactions",
        f"{len(df):,}",
        delta=f"{len(df) - 850:+}"
    )

with col2:
    fraud_count = df['is_fraud'].sum()
    st.metric(
        "Fraud Detected",
        f"{fraud_count:,}",
        delta=f"{fraud_count - 45:+}",
        delta_color="inverse"
    )

with col3:
    avg_risk = df['risk_score'].mean()
    st.metric(
        "Avg Risk Score",
        f"{avg_risk:.1f}",
        delta=f"{avg_risk - 35:+.1f}"
    )

with col4:
    flagged_rate = (df['status'] == 'flagged').sum() / len(df) * 100
    st.metric(
        "Flagged Rate",
        f"{flagged_rate:.1f}%",
        delta=f"{flagged_rate - 15:+.1f}%"
    )

st.markdown("---")

# Charts row
col1, col2 = st.columns(2)

with col1:
    st.subheader("Risk Level Distribution")
    risk_counts = df['risk_level'].value_counts().reset_index()
    risk_counts.columns = ['Risk Level', 'Count']
    
    fig = px.bar(
        risk_counts,
        x='Risk Level',
        y='Count',
        color='Risk Level',
        color_discrete_map={
            'CRITICAL': '#ef4444',
            'HIGH': '#f97316',
            'MEDIUM': '#eab308',
            'LOW': '#22c55e',
            'MINIMAL': '#3b82f6'
        }
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Fraud Probability Distribution")
    fig = px.histogram(
        df,
        x='fraud_probability',
        nbins=50,
        color='is_fraud',
        color_discrete_map={True: '#ef4444', False: '#3b82f6'}
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Time series
st.subheader("Risk Trends Over Time")
df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
hourly_risk = df.groupby('hour').agg({
    'risk_score': 'mean',
    'fraud_probability': 'mean',
    'transaction_id': 'count'
}).reset_index()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=hourly_risk['hour'],
    y=hourly_risk['risk_score'],
    mode='lines+markers',
    name='Avg Risk Score',
    line=dict(color='#f97316')
))
fig.add_trace(go.Scatter(
    x=hourly_risk['hour'],
    y=hourly_risk['fraud_probability'] * 100,
    mode='lines+markers',
    name='Avg Fraud Probability (%)',
    line=dict(color='#ef4444')
))

fig.update_layout(
    xaxis_title="Hour of Day",
    yaxis_title="Score",
    hovermode='x unified'
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Recent alerts
st.subheader("🚨 Recent Fraud Alerts")

high_risk_transactions = df[
    (df['risk_level'].isin(['CRITICAL', 'HIGH'])) |
    (df['is_fraud'] == True)
].sort_values('timestamp', ascending=False).head(10)

if not high_risk_transactions.empty:
    for _, row in high_risk_transactions.iterrows():
        with st.expander(
            f"⚠️ {row['transaction_id']} - {row['risk_level']} (Risk: {row['risk_score']})"
        ):
            col1, col2, col3 = st.columns(3)
            col1.write(f"**Amount:** ${row['amount']:,.2f}")
            col2.write(f"**Merchant:** {row['merchant']}")
            col3.write(f"**Fraud Prob:** {row['fraud_probability']:.2%}")
            
            st.write(f"**User ID:** {row['user_id']}")
            st.write(f"**Location:** {row['location']}")
            st.write(f"**Status:** {row['status']}")
            
            if row['is_fraud']:
                st.error("🚨 FRAUD DETECTED - Immediate action required")
else:
    st.info("No high-risk transactions detected in current view")

st.markdown("---")

# Compliance metrics
st.subheader("📊 Compliance Metrics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Regulatory Compliance",
        "98.5%",
        delta="+0.5%"
    )

with col2:
    st.metric(
        "Audit Readiness",
        "95.2%",
        delta="+2.3%"
    )

with col3:
    st.metric(
        "SLA Adherence",
        "99.1%",
        delta="-0.2%"
    )

# Download report
st.markdown("---")
st.subheader("📥 Export Reports")

col1, col2 = st.columns(2)

with col1:
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Transaction Data (CSV)",
        data=csv,
        file_name=f"risk_report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

with col2:
    report_data = {
        "generated_at": datetime.now().isoformat(),
        "total_transactions": len(df),
        "fraud_detected": int(df['is_fraud'].sum()),
        "avg_risk_score": float(df['risk_score'].mean()),
        "flagged_rate": float((df['status'] == 'flagged').sum() / len(df) * 100)
    }
    st.download_button(
        label="Download Compliance Report (JSON)",
        data=json.dumps(report_data, indent=2),
        file_name=f"compliance_report_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json"
    )
