"""
tests/test_bs_pricer.py
Unit test suite for the Black-Scholes Options Pricer (~14 tests).

Covers:
  - Benchmark pricing against known reference values
  - Put-call parity
  - Greek sanity checks (signs, bounds, symmetry)
  - Input validation errors
  - Implied volatility round-trip
"""

import math
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pricing import call_price, put_price, put_call_parity_check
from greeks import delta, gamma, vega, theta, rho, all_greeks
from implied_vol import implied_volatility
from validation import validate_inputs

# Benchmark case: S=100, K=100, T=1, r=0.05, sigma=0.20
S, K, T, r, sigma = 100, 100, 1, 0.05, 0.20


class TestBenchmarkPricing(unittest.TestCase):

    def test_call_price_benchmark(self):
        self.assertAlmostEqual(call_price(S, K, T, r, sigma), 10.4506, places=4)

    def test_put_price_benchmark(self):
        self.assertAlmostEqual(put_price(S, K, T, r, sigma), 5.5735, places=4)

    def test_call_delta_benchmark(self):
        self.assertAlmostEqual(delta(S, K, T, r, sigma, "call"), 0.6368, places=4)

    def test_put_delta_benchmark(self):
        self.assertAlmostEqual(delta(S, K, T, r, sigma, "put"), -0.3632, places=4)


class TestPutCallParity(unittest.TestCase):

    def test_parity_benchmark_case(self):
        self.assertTrue(put_call_parity_check(S, K, T, r, sigma))

    def test_parity_holds_across_random_params(self):
        cases = [(120, 100, 0.5, 0.03, 0.25), (80, 90, 2.0, 0.01, 0.35)]
        for s, k, t, rr, sg in cases:
            with self.subTest(s=s, k=k, t=t, rr=rr, sg=sg):
                self.assertTrue(put_call_parity_check(s, k, t, rr, sg))


class TestGreekSanity(unittest.TestCase):

    def test_call_delta_between_0_and_1(self):
        self.assertTrue(0 < delta(S, K, T, r, sigma, "call") < 1)

    def test_put_delta_between_neg1_and_0(self):
        self.assertTrue(-1 < delta(S, K, T, r, sigma, "put") < 0)

    def test_gamma_positive_and_equal_for_call_and_put(self):
        g_call = gamma(S, K, T, r, sigma, "call")
        g_put = gamma(S, K, T, r, sigma, "put")
        self.assertGreater(g_call, 0)
        self.assertAlmostEqual(g_call, g_put, places=10)

    def test_vega_positive_and_equal_for_call_and_put(self):
        v_call = vega(S, K, T, r, sigma, "call")
        v_put = vega(S, K, T, r, sigma, "put")
        self.assertGreater(v_call, 0)
        self.assertAlmostEqual(v_call, v_put, places=10)

    def test_call_theta_is_negative(self):
        self.assertLess(theta(S, K, T, r, sigma, "call"), 0)

    def test_rho_signs(self):
        self.assertGreater(rho(S, K, T, r, sigma, "call"), 0)
        self.assertLess(rho(S, K, T, r, sigma, "put"), 0)


class TestInputValidation(unittest.TestCase):

    def test_negative_or_zero_spot_strike_raises(self):
        with self.assertRaises(ValueError):
            call_price(-100, K, T, r, sigma)
        with self.assertRaises(ValueError):
            call_price(S, 0, T, r, sigma)

    def test_negative_time_and_bad_sigma_raise(self):
        with self.assertRaises(ValueError):
            call_price(S, K, -1, r, sigma)
        with self.assertRaises(ValueError):
            call_price(S, K, T, r, 0)

    def test_invalid_option_type_raises(self):
        with self.assertRaises(ValueError):
            validate_inputs(S, K, T, r, sigma, "straddle")


class TestImpliedVolatility(unittest.TestCase):

    def test_iv_recovers_input_sigma_call_and_put(self):
        call_mkt = call_price(S, K, T, r, sigma)
        put_mkt = put_price(S, K, T, r, sigma)
        self.assertAlmostEqual(implied_volatility(call_mkt, S, K, T, r, "call"), sigma, places=4)
        self.assertAlmostEqual(implied_volatility(put_mkt, S, K, T, r, "put"), sigma, places=4)

    def test_iv_out_of_bounds_price_raises(self):
        with self.assertRaises(ValueError):
            implied_volatility(-5, S, K, T, r, "call")
        with self.assertRaises(ValueError):
            implied_volatility(S + 50, S, K, T, r, "call")


if __name__ == "__main__":
    unittest.main(verbosity=2)
