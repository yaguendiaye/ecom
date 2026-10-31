#!/usr/bin/env python3
"""Quick data-quality and descriptive profile of a CSV file (standard library only).

Usage: describe.py data.csv [--sep ';'] [--weight COLUMN] [--max-cats 10]

For each column: type guess, missing values, and either numeric summary
(n, mean, sd, min, P25, median, P75, max, outlier count by 1.5*IQR rule)
or top categories with percentages. Weighted mean/percentages if --weight given.
"""
import argparse
import csv
import sys
from collections import Counter
from statistics import mean, median, quantiles, stdev

MISSING = {"", "na", "n/a", "nan", "null", "none", ".", "-", "nr", "nsp"}


def to_num(s: str):
    s = s.strip().replace(" ", "").replace(" ", "")
    if s.count(",") == 1 and "." not in s:  # French decimal comma
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--sep", help="Delimiter (auto-detected if omitted)")
    ap.add_argument("--weight", help="Name of the weight column")
    ap.add_argument("--max-cats", type=int, default=10)
    a = ap.parse_args()

    with open(a.path, newline="", encoding="utf-8-sig") as f:
        sample = f.read(65536)
        f.seek(0)
        sep = a.sep or csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
        rows = list(csv.DictReader(f, delimiter=sep))
    if not rows:
        sys.exit("No data rows.")
    cols = list(rows[0].keys())
    n = len(rows)

    weights = None
    if a.weight:
        if a.weight not in cols:
            sys.exit(f"Weight column '{a.weight}' not found.")
        weights = [to_num(r[a.weight] or "") for r in rows]

    dupes = n - len({tuple(r.values()) for r in rows})
    print(f"File: {a.path} | rows: {n} | columns: {len(cols)} | duplicate rows: {dupes}")
    if weights:
        valid_w = [w for w in weights if w is not None]
        print(f"Weight '{a.weight}': sum = {sum(valid_w):,.1f} (estimated population)")
    print("=" * 78)

    for c in cols:
        raw = [(r.get(c) or "").strip() for r in rows]
        present = [(i, v) for i, v in enumerate(raw) if v.lower() not in MISSING]
        miss = n - len(present)
        nums = [(i, to_num(v)) for i, v in present]
        num_ok = [(i, x) for i, x in nums if x is not None]
        is_num = present and len(num_ok) / len(present) >= 0.95
        print(f"\n[{c}]  missing: {miss} ({miss / n:.1%})  type: {'numeric' if is_num else 'categorical'}")

        if is_num:
            xs = [x for _, x in num_ok]
            if len(xs) < 2:
                print(f"  values: {xs}")
                continue
            q1, q2, q3 = quantiles(xs, n=4)
            iqr = q3 - q1
            out = sum(1 for x in xs if x < q1 - 1.5 * iqr or x > q3 + 1.5 * iqr)
            print(f"  n={len(xs)}  mean={mean(xs):,.2f}  sd={stdev(xs):,.2f}  "
                  f"min={min(xs):,.2f}  P25={q1:,.2f}  median={median(xs):,.2f}  "
                  f"P75={q3:,.2f}  max={max(xs):,.2f}")
            m = mean(xs)
            skew = sum((x - m) ** 3 for x in xs) / len(xs) / (stdev(xs) ** 3 or 1)
            print(f"  skewness={skew:.2f}  outliers(1.5*IQR)={out}  bad-non-numeric={len(present) - len(num_ok)}")
            if weights and c != a.weight:
                pairs = [(x, weights[i]) for i, x in num_ok if weights[i] is not None]
                sw = sum(w for _, w in pairs)
                if sw:
                    print(f"  weighted mean={sum(x * w for x, w in pairs) / sw:,.2f}")
        else:
            cnt = Counter(v for _, v in present)
            print(f"  distinct values: {len(cnt)}")
            wc = Counter()
            if weights:
                for i, v in present:
                    if weights[i] is not None:
                        wc[v] += weights[i]
            tw = sum(wc.values())
            for v, k in cnt.most_common(a.max_cats):
                line = f"  {v[:40]:<40} {k:>7}  {k / len(present):6.1%}"
                if tw:
                    line += f"   weighted {wc[v] / tw:6.1%}"
                print(line)
            if len(cnt) > a.max_cats:
                print(f"  ... {len(cnt) - a.max_cats} more")


if __name__ == "__main__":
    main()
