"""
main.py
Command-line entry point for the Black-Scholes Options Pricer.

Run with no arguments to see the benchmark example, or pass your own inputs:

    python main.py --S 100 --K 100 --T 1 --r 0.05 --sigma 0.20 --type call

Implied volatility mode:

    python main.py --iv --market_price 10.45 --S 100 --K 100 --T 1 --r 0.05 --type call
"""

import argparse
from pricing import call_price, put_price, put_call_parity_check
from greeks import all_greeks
from implied_vol import implied_volatility
from validation import validate_inputs


def print_report(S, K, T, r, sigma, option_type):
    validate_inputs(S, K, T, r, sigma, option_type)
    px = call_price(S, K, T, r, sigma) if option_type == "call" else put_price(S, K, T, r, sigma)
    g = all_greeks(S, K, T, r, sigma, option_type)

    print(f"\n{'='*50}")
    print(f"Black-Scholes {option_type.capitalize()} Option")
    print(f"{'='*50}")
    print(f"  S (spot)        : {S}")
    print(f"  K (strike)      : {K}")
    print(f"  T (years)       : {T}")
    print(f"  r (risk-free)   : {r}")
    print(f"  sigma (vol)     : {sigma}")
    print(f"{'-'*50}")
    print(f"  Price           : {px:.4f}")
    print(f"  Delta           : {g['delta']:.4f}")
    print(f"  Gamma           : {g['gamma']:.4f}")
    print(f"  Vega (per 1.00) : {g['vega']:.4f}")
    print(f"  Theta (per yr)  : {g['theta']:.4f}")
    print(f"  Rho (per 1.00)  : {g['rho']:.4f}")
    print(f"{'='*50}\n")


def main():
    parser = argparse.ArgumentParser(description="Black-Scholes European Options Pricer")
    parser.add_argument("--S", type=float, default=100.0, help="Spot price")
    parser.add_argument("--K", type=float, default=100.0, help="Strike price")
    parser.add_argument("--T", type=float, default=1.0, help="Time to expiration (years)")
    parser.add_argument("--r", type=float, default=0.05, help="Risk-free rate")
    parser.add_argument("--sigma", type=float, default=0.20, help="Volatility")
    parser.add_argument("--type", type=str, default="call", choices=["call", "put"],
                         help="Option type")
    parser.add_argument("--iv", action="store_true", help="Solve for implied volatility instead")
    parser.add_argument("--market_price", type=float, default=None,
                         help="Observed market price (required with --iv)")
    parser.add_argument("--both", action="store_true",
                         help="Print both call and put reports, plus a parity check")
    args = parser.parse_args()

    if args.iv:
        if args.market_price is None:
            parser.error("--market_price is required when using --iv")
        iv = implied_volatility(args.market_price, args.S, args.K, args.T, args.r, args.type)
        print(f"\nImplied volatility for {args.type} @ market price {args.market_price}: "
              f"{iv:.4%}\n")
        return

    if args.both:
        print_report(args.S, args.K, args.T, args.r, args.sigma, "call")
        print_report(args.S, args.K, args.T, args.r, args.sigma, "put")
        parity_ok = put_call_parity_check(args.S, args.K, args.T, args.r, args.sigma)
        print(f"Put-call parity holds: {parity_ok}\n")
        return

    print_report(args.S, args.K, args.T, args.r, args.sigma, args.type)


if __name__ == "__main__":
    main()
