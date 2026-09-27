"""
visualize.py (optional module)
Pulls historical prices and option chains with yfinance and produces:
  1. Volatility smile: implied vol vs strike for a fixed expiration
  2. Term structure: implied vol vs time to expiration for near-the-money options

Requires: yfinance, matplotlib (pip install yfinance matplotlib)
This module is optional and not required for the core pricer or test suite.
"""

import math
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt

try:
    import yfinance as yf
except ImportError:
    yf = None

from implied_vol import implied_volatility


def _years_to_expiry(expiry_str):
    expiry = datetime.strptime(expiry_str, "%Y-%m-%d")
    return max((expiry - datetime.now()).days, 1) / 365.0


def get_risk_free_rate(default=0.05):
    """Best-effort fetch of a risk-free proxy (13-week T-bill ^IRX). Falls back to default."""
    if yf is None:
        return default
    try:
        irx = yf.Ticker("^IRX").history(period="5d")["Close"].iloc[-1]
        return irx / 100.0
    except Exception:
        return default


def volatility_smile(ticker_symbol, expiry_index=0, option_type="call", save_path=None):
    """Plot implied volatility vs strike for one expiration date."""
    if yf is None:
        raise ImportError("yfinance is required for visualize.py; pip install yfinance")

    ticker = yf.Ticker(ticker_symbol)
    expiries = ticker.options
    if not expiries:
        raise ValueError(f"No option expirations found for {ticker_symbol}")
    expiry = expiries[expiry_index]

    chain = ticker.option_chain(expiry)
    df = chain.calls if option_type == "call" else chain.puts

    S = ticker.history(period="1d")["Close"].iloc[-1]
    r = get_risk_free_rate()
    T = _years_to_expiry(expiry)

    strikes, ivs = [], []
    for _, row in df.iterrows():
        mid = (row["bid"] + row["ask"]) / 2 if row["bid"] > 0 and row["ask"] > 0 else row["lastPrice"]
        if mid <= 0:
            continue
        try:
            iv = implied_volatility(mid, S, row["strike"], T, r, option_type)
            strikes.append(row["strike"])
            ivs.append(iv)
        except ValueError:
            continue

    plt.figure(figsize=(8, 5))
    plt.plot(strikes, ivs, marker="o", linewidth=1)
    plt.axvline(S, color="gray", linestyle="--", label=f"Spot = {S:.2f}")
    plt.title(f"{ticker_symbol} Volatility Smile ({option_type}s, exp {expiry})")
    plt.xlabel("Strike")
    plt.ylabel("Implied Volatility")
    plt.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    plt.close()
    return strikes, ivs


def term_structure(ticker_symbol, option_type="call", save_path=None, max_expiries=8):
    """Plot near-the-money implied volatility vs time to expiration."""
    if yf is None:
        raise ImportError("yfinance is required for visualize.py; pip install yfinance")

    ticker = yf.Ticker(ticker_symbol)
    expiries = ticker.options[:max_expiries]
    S = ticker.history(period="1d")["Close"].iloc[-1]
    r = get_risk_free_rate()

    tenors, ivs = [], []
    for expiry in expiries:
        chain = ticker.option_chain(expiry)
        df = chain.calls if option_type == "call" else chain.puts
        df = df.iloc[(df["strike"] - S).abs().argsort()[:1]]  # closest strike to ATM
        if df.empty:
            continue
        row = df.iloc[0]
        mid = (row["bid"] + row["ask"]) / 2 if row["bid"] > 0 and row["ask"] > 0 else row["lastPrice"]
        if mid <= 0:
            continue
        T = _years_to_expiry(expiry)
        try:
            iv = implied_volatility(mid, S, row["strike"], T, r, option_type)
            tenors.append(T * 365)
            ivs.append(iv)
        except ValueError:
            continue

    plt.figure(figsize=(8, 5))
    plt.plot(tenors, ivs, marker="o", linewidth=1)
    plt.title(f"{ticker_symbol} ATM Volatility Term Structure ({option_type}s)")
    plt.xlabel("Days to Expiration")
    plt.ylabel("Implied Volatility")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    plt.close()
    return tenors, ivs


if __name__ == "__main__":
    volatility_smile("AAPL", save_path="volatility_smile.png")
    term_structure("AAPL", save_path="term_structure.png")
