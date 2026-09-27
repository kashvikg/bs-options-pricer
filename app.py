"""
app.py
Minimal Streamlit web interface for the Black-Scholes Options Pricer.

Run with:
    streamlit run app.py
"""

import streamlit as st
from pricing import call_price, put_price, put_call_parity_check
from greeks import all_greeks
from implied_vol import implied_volatility

st.set_page_config(page_title="Black-Scholes Pricer", layout="centered")

st.title("Black-Scholes Options Pricer")
st.caption("European, non-dividend-paying options")

col1, col2 = st.columns(2)
with col1:
    S = st.number_input("Spot price (S)", value=100.0, min_value=0.01)
    K = st.number_input("Strike price (K)", value=100.0, min_value=0.01)
    T = st.number_input("Time to expiration in years (T)", value=1.0, min_value=0.001)
with col2:
    r = st.number_input("Risk-free rate (r)", value=0.05, format="%.4f")
    sigma = st.number_input("Volatility (sigma)", value=0.20, min_value=0.0001, format="%.4f")
    option_type = st.selectbox("Option type", ["call", "put"])

if st.button("Price Option", type="primary"):
    try:
        px = call_price(S, K, T, r, sigma) if option_type == "call" else put_price(S, K, T, r, sigma)
        g = all_greeks(S, K, T, r, sigma, option_type)

        st.subheader(f"{option_type.capitalize()} Price: {px:.4f}")

        st.table({
            "Greek": ["Delta", "Gamma", "Vega", "Theta", "Rho"],
            "Value": [
                f"{g['delta']:.4f}",
                f"{g['gamma']:.4f}",
                f"{g['vega']:.4f}",
                f"{g['theta']:.4f}",
                f"{g['rho']:.4f}",
            ],
        })

        parity_ok = put_call_parity_check(S, K, T, r, sigma)
        st.caption(f"Put-call parity holds: {parity_ok}")

    except ValueError as e:
        st.error(str(e))

st.divider()
st.subheader("Implied Volatility Solver")

iv_col1, iv_col2 = st.columns(2)
with iv_col1:
    market_price = st.number_input("Observed market price", value=10.45, min_value=0.01)
with iv_col2:
    iv_option_type = st.selectbox("Option type ", ["call", "put"], key="iv_type")

if st.button("Solve Implied Volatility"):
    try:
        iv = implied_volatility(market_price, S, K, T, r, iv_option_type)
        st.success(f"Implied volatility: {iv:.4%}")
    except ValueError as e:
        st.error(str(e))
