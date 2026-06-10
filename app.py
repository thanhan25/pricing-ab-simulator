import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as stats
import statsmodels.stats.api as sms
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(page_title="Algorithmic Pricing & A/B Engine", layout="wide")
st.title("?? Algorithmic Pricing Engine & A/B Testing Simulator")
st.markdown("---")

# Sidebar - Parameters
st.sidebar.header("?? Simulation Parameters")

# Section 1: Pricing & Econometrics
st.sidebar.subheader("1. Price & Demand Elasticity")
price_A = st.sidebar.number_input("Control Price (A) (€)", value=50.0, step=1.0)
price_B = st.sidebar.number_input("Variant Price (B) (€)", value=55.0, step=1.0)
baseline_cr = st.sidebar.slider("Control Base Conversion Rate (%)", 1.0, 20.0, 5.0) / 100

# Calculate Price Elasticity of Demand (PED) implicitly based on variation
elasticity = st.sidebar.slider("Hypothesized Price Elasticity of Demand (PED)", -3.0, -0.5, -1.5, step=0.1)

# Section 2: Statistical Framework
st.sidebar.subheader("2. Experiment Configuration")
alpha = st.sidebar.slider("Significance Level (Alpha)", 0.01, 0.10, 0.05, step=0.01)
power = st.sidebar.slider("Statistical Power (1 - Beta)", 0.70, 0.95, 0.80, step=0.05)

# Calculate expected Variant conversion rate using economic elasticity formulas
price_pct_change = (price_B - price_A) / price_A
expected_cr_change = price_pct_change * elasticity
variant_cr = max(0.005, baseline_cr * (1 + expected_cr_change))

# ---- COMPUTE SAMPLE SIZE NEEDED (Power Analysis) ----
effect_size = sms.proportion_effectsize(baseline_cr, variant_cr)
required_n = sms.NormalIndPower().solve_power(
    effect_size=effect_size, 
    alpha=alpha, 
    power=power, 
    ratio=1.0, 
    alternative='two-sided'
)
required_n = int(np.ceil(required_n))

st.sidebar.markdown(f"**Required Sample Size per Branch:** {required_n:,} users")

# ---- SIMULATE DATA RUN ----
st.header("?? Live Experiment Simulation")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Control CR (A)", f"{baseline_cr*100:.2f}%", help="Baseline e-commerce conversion rate")
with col2:
    st.metric("Variant CR (B)", f"{variant_cr*100:.2f}%", help="Calculated variant conversion rate adjusted via Price Elasticity")
with col3:
    st.metric("Price Delta", f"{price_pct_change*100:+.1f}%")
with col4:
    st.metric("Implied Elasticity", f"{elasticity:.1f}")

if st.button("?? Run Live A/B Simulation Pipeline", use_container_width=True):
    # Generating synthetic Bernoulli outcomes based on calculated probabilities
    np.random.seed(42)
    control_conversions = np.random.binomial(1, baseline_cr, required_n)
    variant_conversions = np.random.binomial(1, variant_cr, required_n)
    
    n_A, clicks_A = required_n, control_conversions.sum()
    n_B, clicks_B = required_n, variant_conversions.sum()
    
    sim_cr_A = clicks_A / n_A
    sim_cr_B = clicks_B / n_B
    
    # Hypothesis Testing (Two-Proportion Z-Test)
    p_pool = (clicks_A + clicks_B) / (n_A + n_B)
    z_stat = (sim_cr_B - sim_cr_A) / np.sqrt(p_pool * (1 - p_pool) * (1/n_A + 1/n_B))
    p_value = stats.norm.sf(abs(z_stat)) * 2
    
    # Financial Impact Calculations
    rev_A = clicks_A * price_A
    rev_B = clicks_B * price_B
    rev_per_visitor_A = rev_A / n_A
    rev_per_visitor_B = rev_B / n_B
    net_revenue_delta = (rev_per_visitor_B - rev_per_visitor_A) * n_A
    
    # Display Results
    st.markdown("---")
    st.subheader("?? Statistical & Financial Inference Dashboard")
    
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        st.subheader("Statistical Validation")
        st.write(f"**Z-Score Statistic:** {z_stat:.4f}")
        if p_value < alpha:
            st.success(f"**Significant Result!** p-value = {p_value:.5f} < alpha ({alpha}). Reject Null Hypothesis.")
        else:
            st.warning(f"**Not Statistically Significant.** p-value = {p_value:.5f} >= alpha ({alpha}). Fail to Reject Null Hypothesis.")
            
    with res_col2:
        st.subheader("Enterprise Financial Impact (Normalized to Control Traffic)")
        st.write(f"**Control Revenue per Visitor (RPV):** €{rev_per_visitor_A:.2f}")
        st.write(f"**Variant Revenue per Visitor (RPV):** €{rev_per_visitor_B:.2f}")
        
        if net_revenue_delta > 0:
            st.metric("Net Projected Revenue Shift", f"€{net_revenue_delta:+,.2f}", delta="Profitable Run")
        else:
            st.metric("Net Projected Revenue Shift", f"€{net_revenue_delta:+,.2f}", delta="Loss-Making Run", delta_color="inverse")

    # Interactive Probability Plot
    st.markdown("---")
    st.subheader("?? Lift Distribution & Confidence Belts")
    
    # Standard errors for visualization
    se_A = np.sqrt(sim_cr_A * (1 - sim_cr_A) / n_A)
    se_B = np.sqrt(sim_cr_B * (1 - sim_cr_B) / n_B)
    
    x = np.linspace(min(sim_cr_A - 4*se_A, sim_cr_B - 4*se_B), max(sim_cr_A + 4*se_A, sim_cr_B + 4*se_B), 500)
    y_A = stats.norm.pdf(x, sim_cr_A, se_A)
    y_B = stats.norm.pdf(x, sim_cr_B, se_B)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x*100, y=y_A, mode='lines', name='Control (A) Distribution', fill='tozeroy'))
    fig.add_trace(go.Scatter(x=x*100, y=y_B, mode='lines', name='Variant (B) Distribution', fill='tozeroy'))
    fig.update_layout(title="Conversion Rate Probability Distributions (Central Limit Theorem applied)",
                      xaxis_title="Conversion Rate (%)", yaxis_title="Probability Density", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
