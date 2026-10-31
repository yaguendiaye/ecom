#!/usr/bin/env python3
"""Survey sample-size calculator (standard library only).

Examples
  Proportion, ±5 pts, 95%:            sample_size.py --margin 0.05
  With population, deff, response:    sample_size.py --margin 0.05 --population 12000 --deff 1.5 --response 0.8
  Mean (sd and margin in same unit):  sample_size.py --mean --sd 250000 --margin 50000
  Per-domain (e.g. 5 regions):        sample_size.py --margin 0.07 --domains 5
"""
import argparse
import math
from statistics import NormalDist


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--margin", type=float, required=True,
                    help="Margin of error: proportion (0.05 = ±5 pts) or, with --mean, same unit as --sd")
    ap.add_argument("--confidence", type=float, default=0.95, help="Confidence level (default 0.95)")
    ap.add_argument("--p", type=float, default=0.5, help="Expected proportion (default 0.5 = most conservative)")
    ap.add_argument("--mean", action="store_true", help="Estimate a mean instead of a proportion")
    ap.add_argument("--sd", type=float, help="Expected standard deviation (required with --mean)")
    ap.add_argument("--population", type=int, help="Population size N (finite population correction)")
    ap.add_argument("--deff", type=float, default=1.0, help="Design effect (default 1.0; clusters ~1.5-2.5)")
    ap.add_argument("--response", type=float, default=1.0, help="Expected response rate (default 1.0)")
    ap.add_argument("--domains", type=int, default=1, help="Number of domains needing separate estimates")
    a = ap.parse_args()

    if not 0 < a.confidence < 1 or not 0 < a.response <= 1 or a.margin <= 0:
        ap.error("confidence must be in (0,1), response in (0,1], margin > 0")
    z = NormalDist().inv_cdf(1 - (1 - a.confidence) / 2)

    if a.mean:
        if not a.sd:
            ap.error("--sd is required with --mean")
        n0 = (z * a.sd / a.margin) ** 2
    else:
        if not 0 < a.p < 1 or a.margin >= 1:
            ap.error("--p must be in (0,1) and --margin < 1 for proportions")
        n0 = z ** 2 * a.p * (1 - a.p) / a.margin ** 2

    n_fpc = n0 / (1 + (n0 - 1) / a.population) if a.population else n0
    n_design = n_fpc * a.deff
    n_final = math.ceil(n_design / a.response)
    total = n_final * a.domains

    print(f"z (confidence {a.confidence:.0%})       : {z:.3f}")
    print(f"Base sample n0                 : {math.ceil(n0)}")
    if a.population:
        print(f"After finite pop. correction   : {math.ceil(n_fpc)}  (N = {a.population})")
    if a.deff != 1:
        print(f"After design effect x{a.deff:g}       : {math.ceil(n_design)}")
    if a.response != 1:
        print(f"After response rate {a.response:.0%}       : {n_final}")
    print(f"=> Sample to draw per domain   : {n_final}")
    if a.domains > 1:
        print(f"=> Total for {a.domains} domains         : {total}")
    if a.population and n_final > a.population:
        print("Note: required sample exceeds population — consider a census.")


if __name__ == "__main__":
    main()
