"""
pricing.py
Black-Scholes closed-form pricing for non-dividend-paying European options.

Model assumptions:
- European exercise only (no early exercise)
- No dividends paid during the option's life
- Constant, known risk-free rate and volatility
- Log-normal distribution of the underlying's returns
- No transaction costs or taxes; markets are frictionless and continuous
"""

import math
from scipy.stats import norm
from validation import validate_inputs


def d1(S, K, T, r, sigma):
    """First Black-Scholes auxiliary term d1."""
    return (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))


def d2(S, K, T, r, sigma):
    """Second Black-Scholes auxiliary term d2 = d1 - sigma * sqrt(T)."""
    return d1(S, K, T, r, sigma) - sigma * math.sqrt(T)


def call_price(S, K, T, r, sigma):
    """Price a European call option using the Black-Scholes formula.

    C = S * N(d1) - K * e^(-rT) * N(d2)
    """
    validate_inputs(S, K, T, r, sigma, "call")
    _d1 = d1(S, K, T, r, sigma)
    _d2 = d2(S, K, T, r, sigma)
    return S * norm.cdf(_d1) - K * math.exp(-r * T) * norm.cdf(_d2)


def put_price(S, K, T, r, sigma):
    """Price a European put option using the Black-Scholes formula.

    P = K * e^(-rT) * N(-d2) - S * N(-d1)
    """
    validate_inputs(S, K, T, r, sigma, "put")
    _d1 = d1(S, K, T, r, sigma)
    _d2 = d2(S, K, T, r, sigma)
    return K * math.exp(-r * T) * norm.cdf(-_d2) - S * norm.cdf(-_d1)


def price(S, K, T, r, sigma, option_type="call"):
    """Dispatch to call_price or put_price based on option_type."""
    validate_inputs(S, K, T, r, sigma, option_type)
    if option_type.lower() == "call":
        return call_price(S, K, T, r, sigma)
    return put_price(S, K, T, r, sigma)


def put_call_parity_check(S, K, T, r, sigma, tol=1e-8):
    """Check put-call parity: C - P == S - K * e^(-rT).

    Returns True if the identity holds within tolerance, False otherwise.
    """
    c = call_price(S, K, T, r, sigma)
    p = put_price(S, K, T, r, sigma)
    lhs = c - p
    rhs = S - K * math.exp(-r * T)
    return abs(lhs - rhs) < tol
