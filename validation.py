"""
validation.py
Input validation helpers for the Black-Scholes pricer.
All functions raise ValueError with a clear message on bad input.
"""

import math


def validate_inputs(S, K, T, r, sigma, option_type="call"):
    """Validate the five core Black-Scholes inputs plus option type.

    Parameters
    ----------
    S : float, spot price (must be > 0)
    K : float, strike price (must be > 0)
    T : float, time to expiration in years (must be > 0)
    r : float, risk-free rate, continuously compounded (can be negative, but must be finite)
    sigma : float, annualized volatility (must be > 0)
    option_type : str, "call" or "put"
    """
    for name, val in (("S", S), ("K", K), ("T", T), ("r", r), ("sigma", sigma)):
        if not isinstance(val, (int, float)):
            raise ValueError(f"{name} must be numeric, got {type(val).__name__}")
        if val != val:  # NaN check
            raise ValueError(f"{name} cannot be NaN")
        if math.isinf(val):
            raise ValueError(f"{name} must be finite")

    if S <= 0:
        raise ValueError(f"Spot price S must be positive, got {S}")
    if K <= 0:
        raise ValueError(f"Strike price K must be positive, got {K}")
    if T <= 0:
        raise ValueError(f"Time to expiration T must be positive, got {T}")
    if sigma <= 0:
        raise ValueError(f"Volatility sigma must be positive, got {sigma}")

    if not isinstance(option_type, str) or option_type.lower() not in ("call", "put"):
        raise ValueError(f"option_type must be 'call' or 'put', got {option_type!r}")

    return True
