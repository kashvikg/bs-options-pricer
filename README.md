Black-Scholes Options Pricer
Python project that prices European call and put options using the Black-Scholes formula and calculates the Greeks (delta, gamma, vega, theta, rho).

Only works for European options with no dividends. Built this for fun while learning about options.

**Files**
pricing.py - the call/put pricing formulas

greeks.py - delta, gamma, vega, theta, rho

validation.py - checks inputs (no negative prices etc)

implied_vol.py - solves for implied volatility from a market price

visualize.py - pulls real option data with yfinance, makes volatility smile / term structure charts

app.py - basic Streamlit web page

main.py - command line version

tests/test_bs_pricer.py - unit tests

**The formulas**
Call: C = S * N(d1) - K * e^(-rT) * N(d2)

Put: P = K * e^(-rT) * N(-d2) - S * N(-d1)

d1 = [ln(S/K) + (r + 0.5sigma^2)T] / (sigma*sqrt(T))
d2 = d1 - sigma*sqrt(T)

S = spot price, K = strike, T = years to expiry, r = risk free rate, sigma = volatility, N() = normal CDF.

Assumptions: European exercise only, no dividends, constant volatility and rate, no transaction costs.

**Setup**
pip install -r requirements.txt

**Run it**
python main.py --S 100 --K 100 --T 1 --r 0.05 --sigma 0.20 --type call
**Both call and put + parity check:**
python main.py --S 100 --K 100 --T 1 --r 0.05 --sigma 0.20 --both
**Implied vol:**
python main.py --iv --market_price 10.4506 --S 100 --K 100 --T 1 --r 0.05 --type call
**Web page version:**
streamlit run app.py

**Tests**
python -m unittest discover -s tests -v


Checked against a known benchmark (S=100, K=100, T=1, r=5%, sigma=20%):

call = 10.4506
put = 5.5735
call delta = 0.6368
put delta = -0.3632

Also tests put-call parity, greek sign checks, and bad input handling.

To add later:
dividends
American options
