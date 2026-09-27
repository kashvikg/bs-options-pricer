"""
greeks.py
Analytic Black-Scholes Greeks: delta, gamma, vega, theta, rho.

Conventions used here:
- vega  : sensitivity per 1.00 (100%) change in volatility (divide by 100 for a 1-vol-point move)
- theta : per-year time decay (divide by 365 for a per-calendar-day figure)
- rho   : sensitivity per 1.00 (100%) change in the risk-free rate (divide by 100 for a 1% move)
"""

import math
from scipy.stats import norm
from validation import validate_inputs
from pricing import d1, d2


def delta(S, K, T, r, sigma, option_type="call"):
    """Rate of change of option price with respect to spot price."""
    validate_inputs(S, K, T, r, sigma, option_type)
    _d1 = d1(S, K, T, r, sigma)
    if option_type.lower() == "call":
        return norm.cdf(_d1)
    return norm.cdf(_d1) - 1


def gamma(S, K, T, r, sigma, option_type="call"):
    """Rate of change of delta with respect to spot price. Same for calls and puts."""
    validate_inputs(S, K, T, r, sigma, option_type)
    _d1 = d1(S, K, T, r, sigma)
    return norm.pdf(_d1) / (S * sigma * math.sqrt(T))


def vega(S, K, T, r, sigma, option_type="call"):
    """Sensitivity to volatility, per 1.00 (100%) change in sigma. Same for calls and puts."""
    validate_inputs(S, K, T, r, sigma, option_type)
    _d1 = d1(S, K, T, r, sigma)
    return S * norm.pdf(_d1) * math.sqrt(T)


def theta(S, K, T, r, sigma, option_type="call"):
    """Time decay of the option price, expressed per year."""
    validate_inputs(S, K, T, r, sigma, option_type)
    _d1 = d1(S, K, T, r, sigma)
    _d2 = d2(S, K, T, r, sigma)
    term1 = -(S * norm.pdf(_d1) * sigma) / (2 * math.sqrt(T))
    if option_type.lower() == "call":
        term2 = -r * K * math.exp(-r * T) * norm.cdf(_d2)
        return term1 + term2
    term2 = r * K * math.exp(-r * T) * norm.cdf(-_d2)
    return term1 + term2


def rho(S, K, T, r, sigma, option_type="call"):
    """Sensitivity to the risk-free rate, per 1.00 (100%) change in r."""
    validate_inputs(S, K, T, r, sigma, option_type)
    _d2 = d2(S, K, T, r, sigma)
    if option_type.lower() == "call":
        return K * T * math.exp(-r * T) * norm.cdf(_d2)
    return -K * T * math.exp(-r * T) * norm.cdf(-_d2)


def all_greeks(S, K, T, r, sigma, option_type="call"):
    """Return a dict with delta, gamma, vega, theta, rho for the given option."""
    return {
        "delta": delta(S, K, T, r, sigma, option_type),
        "gamma": gamma(S, K, T, r, sigma, option_type),
        "vega": vega(S, K, T, r, sigma, option_type),
        "theta": theta(S, K, T, r, sigma, option_type),
        "rho": rho(S, K, T, r, sigma, option_type),
    }
