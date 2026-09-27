# Black-Scholes Options Pricer

A modular Python implementation of the Black-Scholes model for pricing
**non-dividend-paying European options**, computing the full set of
first- and second-order Greeks, inverting implied volatility from market
prices, and optionally visualizing volatility smiles and term structures
pulled live from Yahoo Finance. Includes a minimal Streamlit web page.

## Features

- Closed-form Black-Scholes pricing for European calls and puts
- Analytic Greeks: delta, gamma, vega, theta, rho
- Strict input validation with descriptive `ValueError` messages
- Implied volatility solver using Brent's method (`scipy.optimize.brentq`)
- Optional `yfinance`-powered volatility smile and term structure plots
- Minimal Streamlit web interface (`app.py`)
- 17-test `unittest` suite covering benchmark pricing, put-call parity,
  Greek sanity checks, input validation, and implied volatility round-trips

## Project Structure

```
bs_pricer/
├── main.py            # CLI entry point
├── app.py             # Streamlit web interface
├── pricing.py         # Black-Scholes call/put pricing, d1/d2, parity check
├── greeks.py          # delta, gamma, vega, theta, rho
├── implied_vol.py     # implied volatility via brentq
├── validation.py      # input validation helpers
├── visualize.py       # optional yfinance smile / term-structure plots
├── requirements.txt
├── .gitignore
└── tests/
    ├── __init__.py
    └── test_bs_pricer.py
```

## Model & Assumptions

The pricer implements the classic Black-Scholes-Merton formula for a
**non-dividend-paying European option**:

Call price:

\[
C = S \, N(d_1) - K e^{-rT} N(d_2)
\]

Put price:

\[
P = K e^{-rT} N(-d_2) - S \, N(-d_1)
\]

where

\[
d_1 = \frac{\ln(S/K) + (r + \tfrac{1}{2}\sigma^2)T}{\sigma \sqrt{T}}, \qquad
d_2 = d_1 - \sigma \sqrt{T}
\]

and \(N(\cdot)\) is the standard normal CDF.

**Assumptions behind the model:**

- European exercise only — no early exercise (unlike American options)
- No dividends paid on the underlying during the option's life
- Constant, known volatility (\(\sigma\)) and risk-free rate (\(r\))
- The underlying follows geometric Brownian motion (log-normal returns)
- Frictionless markets: no transaction costs, taxes, or liquidity constraints
- Continuous trading and the ability to borrow/lend at the risk-free rate

### Greeks

| Greek | Formula (call) | Formula (put) | Meaning |
|---|---|---|---|
| Delta | \(N(d_1)\) | \(N(d_1) - 1\) | Price sensitivity to \(S\) |
| Gamma | \(\dfrac{N'(d_1)}{S\sigma\sqrt{T}}\) | same as call | Delta sensitivity to \(S\) |
| Vega | \(S\,N'(d_1)\sqrt{T}\) | same as call | Price sensitivity to \(\sigma\) |
| Theta | \(-\dfrac{S N'(d_1)\sigma}{2\sqrt{T}} - rKe^{-rT}N(d_2)\) | \(-\dfrac{S N'(d_1)\sigma}{2\sqrt{T}} + rKe^{-rT}N(-d_2)\) | Price sensitivity to time |
| Rho | \(KTe^{-rT}N(d_2)\) | \(-KTe^{-rT}N(-d_2)\) | Price sensitivity to \(r\) |

Vega and rho are reported per a full 1.00 (100%) move in volatility or rate,
respectively; theta is reported per year. Divide by 100 (vega/rho) or 365
(theta) to convert to per-vol-point, per-percent, or per-day units.

## Installation

```bash
git clone <your-repo-url>
cd bs_pricer
python -m venv venv
venv\\Scripts\\activate      # Windows
source venv/bin/activate    # Mac/Linux
pip install -r requirements.txt
```

## Usage

### Command line

```bash
python main.py --S 100 --K 100 --T 1 --r 0.05 --sigma 0.20 --type call
```

Output:

```
==================================================
Black-Scholes Call Option
==================================================
  S (spot)        : 100.0
  K (strike)      : 100.0
  T (years)       : 1.0
  r (risk-free)   : 0.05
  sigma (vol)     : 0.2
--------------------------------------------------
  Price           : 10.4506
  Delta           : 0.6368
  Gamma           : 0.0188
  Vega (per 1.00) : 37.5240
  Theta (per yr)  : -6.4140
  Rho (per 1.00)  : 53.2325
==================================================
```

Price both call and put plus a parity check:

```bash
python main.py --S 100 --K 100 --T 1 --r 0.05 --sigma 0.20 --both
```

Solve for implied volatility:

```bash
python main.py --iv --market_price 10.4506 --S 100 --K 100 --T 1 --r 0.05 --type call
```

### Web interface

```bash
streamlit run app.py
```

Opens a local browser page with number inputs for S, K, T, r, sigma, a
call/put selector, a "Price Option" button that shows price + all five
Greeks + a parity check, and a separate implied volatility solver section.

### As a library

```python
from pricing import call_price, put_price
from greeks import all_greeks
from implied_vol import implied_volatility

price = call_price(S=100, K=100, T=1, r=0.05, sigma=0.20)   # 10.4506
greeks = all_greeks(S=100, K=100, T=1, r=0.05, sigma=0.20, option_type="call")
iv = implied_volatility(market_price=10.45, S=100, K=100, T=1, r=0.05, option_type="call")
```

### Optional: volatility smile & term structure

```python
from visualize import volatility_smile, term_structure

volatility_smile("AAPL", save_path="smile.png")
term_structure("AAPL", save_path="term_structure.png")
```

Pulls live option chains via `yfinance`, derives implied vol at each
strike/expiration using `implied_vol.py`, and saves the charts as PNGs.

## Running the Tests

```bash
python -m unittest discover -s tests -v
```

All 17 tests pass:

```
Ran 17 tests in 0.005s

OK
```

**Test coverage:**

- **Benchmark pricing** — verifies call = 10.4506, put = 5.5735, call delta =
  0.6368, put delta = -0.3632 for S=100, K=100, T=1, r=0.05, sigma=0.20
- **Put-call parity** — checks \(C - P = S - Ke^{-rT}\) on the benchmark
  case and several randomized parameter sets
- **Greek sanity checks** — delta bounds, gamma/vega equality across calls
  and puts, theta sign, rho sign
- **Input validation** — negative/zero spot, strike, sigma; negative time;
  invalid option type
- **Implied volatility** — round-trip recovery of the input sigma from a
  computed price, and rejection of prices outside no-arbitrage bounds

## Benchmark Reference Case

| Input | Value |
|---|---|
| S (spot) | 100 |
| K (strike) | 100 |
| T (years) | 1 |
| r (risk-free rate) | 0.05 |
| sigma (volatility) | 0.20 |

| Output | Value |
|---|---|
| Call price | 10.4506 |
| Put price | 5.5735 |
| Call delta | 0.6368 |
| Put delta | -0.3632 |

## License

MIT — feel free to fork and extend.
