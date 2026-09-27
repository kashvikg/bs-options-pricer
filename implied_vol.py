"""
implied_vol.py
Implied volatility inversion via Brent's method (scipy.optimize.brentq).

Given an observed market price, find the sigma that makes the Black-Scholes
price match it. Requires the market price to be within the arbitrage-free
bounds for the option, otherwise no solution exists and a ValueError is raised.
"""

import math
from scipy.optimize import brentq
from pricing import call_price, put_price
from validation import validate_inputs


def _bounds_ok(market_price, S, K, T, r, option_type):
    """Check the market price sits within the no-arbitrage bounds."""
    if option_type.lower() == "call":
        lower = max(0.0, S - K * math.exp(-r * T))
        upper = S
    else:
        lower = max(0.0, K * math.exp(-r * T) - S)
        upper = K * math.exp(-r * T)
    return lower <= market_price <= upper


def implied_volatility(market_price, S, K, T, r, option_type="call",
                        sigma_low=1e-6, sigma_high=5.0, tol=1e-8, max_iter=200):
    """Solve for implied volatility given an observed option market price.

    Parameters
    ----------
    market_price : float, observed option price
    S, K, T, r : standard Black-Scholes inputs (sigma is what we solve for)
    option_type : "call" or "put"
    sigma_low, sigma_high : bracket for Brent's method search
    tol : convergence tolerance passed to brentq
    max_iter : maximum brentq iterations

    Returns
    -------
    float, implied volatility (annualized)
    """
    validate_inputs(S, K, T, r, sigma_low, option_type)  # validates S,K,T,r shape

    if market_price <= 0:
        raise ValueError(f"market_price must be positive, got {market_price}")

    if not _bounds_ok(market_price, S, K, T, r, option_type):
        raise ValueError(
            "market_price is outside the no-arbitrage bounds for this option; "
            "no implied volatility exists."
        )

    price_fn = call_price if option_type.lower() == "call" else put_price

    def objective(sigma):
        return price_fn(S, K, T, r, sigma) - market_price

    try:
        iv = brentq(objective, sigma_low, sigma_high, xtol=tol, maxiter=max_iter)
    except ValueError as e:
        raise ValueError(
            f"Could not bracket a root for implied volatility in [{sigma_low}, {sigma_high}]: {e}"
        )
    return iv
