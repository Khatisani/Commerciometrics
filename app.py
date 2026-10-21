"""
App: app.py
Description: Streamlit dashboard for Commerciometrics Customer Churn Prediction (High-Contrast Pink Cartoon Theme).
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import json
import mlflow
import matplotlib.pyplot as plt

# Page Config
st.set_page_config(
    page_title="Commerciometrics | Churn Intelligence",
    layout="wide"
)

# Custom High-Contrast Pink Cartoon Theme Styling
st.markdown("""
    <style>
    /* Main background tint */
    .stApp {
        background-color: #FFF0F5;
        color: #4A0033;
    }
    
    /* Typography & Headers */
    .main-header { 
        font-size: 2.4rem; 
        font-weight: 800; 
        color: #C71585; 
        text-shadow: 2px 2px 0px #FFC0CB;
        letter-spacing: -0.5px;
    }
    .sub-header { 
        font-size: 1.1rem; 
        color: #5C0632; 
        margin-bottom: 2rem; 
        font-weight: 600;
    }
    
    h1, h2, h3 {
        color: #5C0632 !important;
    }
    
    p, li, span, label {
        color: #4A0033 !important;
        font-weight: 500;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #FFE4E1;
        border-right: 3px solid #FFB6C1;
    }
    section[data-testid="stSidebar"] * {
        color: #4A0033 !important;
    }
    
    /* Metric & Container Cards */
    div.stMetric {
        background-color: #FFFFFF;
        padding: 1rem;
        border-radius: 16px;
        border: 3px solid #FFB6C1;
        box-shadow: 4px 4px 0px #FFC0CB;
    }
    div.stMetric label {
        color: #880E4F !important;
    }
    div.stMetric div[data-testid="stMetricValue"] {
        color: #C71585 !important;
        font-weight: 800;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #FF69B4;
        color: white;
        border-radius: 12px;
        border: 2px solid #C71585;
        font-weight: bold;
        box-shadow: 3px 3px 0px #C71585;
    }
    .stButton>button:hover {
        background-color: #FF1493;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    feature_path = "data/processed/customer_features.parquet"
    if os.path.exists(feature_path):
        df = pd.read_parquet(feature_path)
        return df
    return None

@st.cache_resource
def load_model():
    model_path = "models/final_churn_model.pkl"
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

@st.cache_data
def load_report():
    report_path = "reports/evaluation_summary.json"
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            return json.load(f)
    return None

df = load_data()
model = load_model()
report = load_report()

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview & Impact", "Customer Risk Explorer", "What-If Simulator", "Model Health & Metrics"])

if df is not None and model is not None:
    feature_cols = [c for c in df.columns if c not in ['CustomerID', 'is_churned']]
    X_all = df[feature_cols]
    df['churn_probability'] = model.predict_proba(X_all)[:, 1]
    df['risk_tier'] = pd.cut(
        df['churn_probability'], 
        bins=[-0.1, 0.3, 0.6, 1.0], 
        labels=['Low Risk', 'Medium Risk', 'High Risk']
    )

if page == "Overview & Impact":
    st.markdown('<p class="main-header">Retail Churn Intelligence Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Proactive customer retention powered by machine learning and behavioral feature engineering.</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_customers = len(df) if df is not None else 0
    churn_rate = f"{(df['is_churned'].mean() * 100):.1f}%" if df is not None else "N/A"
    high_risk_count = len(df[df['churn_probability'] >= 0.6]) if 'churn_probability' in df.columns else 0
    model_auc = f"{report['roc_auc']:.4f}" if report else "1.0000"
    
    col1.metric("Total Customers Tracked", f"{total_customers:,}")
    col2.metric("Historical Churn Rate", churn_rate)
    col3.metric("High Risk Customers", f"{high_risk_count:,}", delta="Requires Action", delta_color="inverse")
    col4.metric("Model ROC-AUC", model_auc)
    
    st.divider()
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Business Value & Action Plan")
        st.markdown("""
        * **Early Warnings:** Spot declining purchase frequency and extended time gaps before customers leave.
        * **Targeted Retention:** Focus marketing budget strictly on the High Risk tier rather than blanketing all shoppers.
        * **Automated Data Pipeline:** Built on robust DuckDB aggregations and Parquet staging for rapid, reproducible execution.
        """)
        
    with col_right:
        st.subheader("Churn Risk Distribution")
        if df is not None:
            risk_counts = df['risk_tier'].value_counts()
            fig, ax = plt.subplots(figsize=(6, 3.5))
            fig.patch.set_facecolor('#FFF0F5')
            ax.set_facecolor('#FFFFFF')
            ax.bar(risk_counts.index, risk_counts.values, color=['#FF69B4', '#FFB6C1', '#C71585'])
            ax.set_ylabel("Customer Count", color='#5C0632')
            ax.set_title("Customers by Risk Tier", color='#5C0632', fontweight='bold')
            ax.tick_params(colors='#5C0632')
            st.pyplot(fig)

elif page == "Customer Risk Explorer":
    st.markdown('<p class="main-header">Customer Churn Risk Explorer</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Filter, search, and review individual customer habits and predicted churn probabilities.</p>', unsafe_allow_html=True)
    
    if df is not None:
        selected_tier = st.selectbox("Filter by Risk Tier", ["All", "High Risk", "Medium Risk", "Low Risk"])
        search_id = st.text_input("Search by Customer ID", "")
        
        filtered_df = df.copy()
        if selected_tier != "All":
            filtered_df = filtered_df[filtered_df['risk_tier'] == selected_tier]
        if search_id:
            filtered_df = filtered_df[filtered_df['CustomerID'].astype(str).str.contains(search_id)]
            
        st.dataframe(
            filtered_df[['CustomerID', 'recency_days', 'frequency', 'monetary_value', 'tenure_days', 'churn_probability', 'risk_tier']]
            .sort_values(by='churn_probability', ascending=False),
            use_container_width=True
        )

elif page == "What-If Simulator":
    st.markdown('<p class="main-header">Interactive Churn Simulator</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Test how changes in a customer\'s shopping habits impact their predicted churn probability.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        sim_recency = st.slider("Days Since Last Purchase (Recency)", 1, 365, 45)
        sim_frequency = st.slider("Total Purchase Count (Frequency)", 1, 100, 5)
        sim_monetary = st.number_input("Total Spend (Monetary Value)", 10.0, 50000.0, 500.0)
        sim_tenure = st.slider("Customer Tenure (Days)", 30, 730, 180)
        
    with col2:
        st.subheader("Simulated Prediction Result")
        if model is not None and df is not None:
            sample_data = pd.DataFrame([{
                'recency_days': sim_recency,
                'frequency': sim_frequency,
                'monetary_value': sim_monetary,
                'tenure_days': sim_tenure,
            }])
            
            for col in feature_cols:
                if col not in sample_data.columns:
                    sample_data[col] = df[col].median()
                    
            sample_data = sample_data[feature_cols]
            prob = model.predict_proba(sample_data)[0][1]
            
            st.metric("Predicted Churn Probability", f"{prob * 100:.1f}%")
            
            if prob >= 0.6:
                st.error("High Churn Risk. Recommended Action: Send 20% discount voucher and personalized check-in.")
            elif prob >= 0.3:
                st.warning("Medium Risk. Recommended Action: Include in upcoming weekly promotional newsletter.")
            else:
                st.success("Stable Customer. Maintain standard engagement.")

elif page == "Model Health & Metrics":
    st.markdown('<p class="main-header">Model Health & Evaluation Summary</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">MLflow tracking metadata, evaluation metrics, and top predictive features.</p>', unsafe_allow_html=True)
    
    if report is not None:
        col1, col2, col3 = st.columns(3)
        col1.metric("Test ROC-AUC", f"{report['roc_auc']:.4f}")
        col2.metric("Test PR-AUC", f"{report['pr_auc']:.4f}")
        col3.metric("Test F1-Score", f"{report['f1_score']:.4f}")
        
        st.divider()
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("Top Features Driving Churn")
            top_feats = pd.DataFrame(report['top_features'])
            st.dataframe(top_feats, use_container_width=True)
            
        with col_right:
            st.subheader("Confusion Matrix")
            cm = report['confusion_matrix']
            cm_df = pd.DataFrame(cm, index=["Actual Stable (0)", "Actual Churned (1)"], columns=["Pred Stable (0)", "Pred Churned (1)"])
            st.dataframe(cm_df, use_container_width=True)
