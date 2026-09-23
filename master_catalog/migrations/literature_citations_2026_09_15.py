#!/usr/bin/env python3
"""One-off migration: credit every master-catalogue class to the works that state it.

    python master_catalog/migrations/literature_citations_2026_09_15.py [--dry-run]

Run after `gl_dedup_2026_09_15.py`.  The policy, as set by the catalogue's owner:

* **n <= 54.**  Every class is credited to the length-54 classification
  (Wills, Jain and Singh) and to the symmetry-and-AI report (Jain, Wills and
  Singh).  A class that the classification's own Pareto table (Table
  ``tab:complete-pareto``) attributes to a published protocol is ALSO credited
  to that work.
* **n > 54.**  A class that a published work states -- same ``n``, same ``k``,
  the same output gate up to a CNOT frame and diagonal Cliffords, and the same
  distance -- is credited to that work.  Every other class is new to the
  literature and credited to the symmetry-and-AI report.

WHAT COUNTS AS "STATES"
-----------------------
Each entry of `LITERATURE` below names one explicit protocol or code, the exact
place in the paper where its parameters are printed, and how its gate is
identified with a catalogue row.  The entries were read from the papers
themselves (not from abstracts or citing works) and are deliberately narrow:

* the distance must agree.  Where the catalogue row carries only a proved
  FLOOR, the published distance must not be below it (a floor of 6 is
  consistent with a published 6 or 7);
* the gate must be the stated one: ``T`` on every output for a triorthogonal
  code, disjoint ``CCZ``s for a CCZ^m protocol, or -- for the Reed-Muller codes
  whose papers describe a circuit of CCZs -- the stated structure, checked on
  the row;
* protocols built by PIPELINING several codes (Haah, Hastings, Poulin and
  Wecker 2017), protocols on non-T inputs, asymptotic families and parameter
  sets whose gate the paper does not establish (CSS-T tables, where transversal
  T may act as the logical identity) are not matched.

No entry may land on two rows -- that stops the migration.  An entry that lands
on none is printed as "not held", for the owner to read.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE.parent
sys.path.insert(0, str(CATALOGUE))

import catalogfile as CF                                          # noqa: E402
import glcanon as GC                                              # noqa: E402
import merge_results as MR                                        # noqa: E402
import verify_catalog as VC                                       # noqa: E402

REFERENCES = {
    "wills2026classification": MR.DEFAULT_REFERENCES["wills2026classification"],
    "jain2026symmetry": MR.DEFAULT_REFERENCES["jain2026symmetry"],
    "bravyi2005universal": {
        "short": "Bravyi & Kitaev (2005)",
        "full": "S. Bravyi and A. Kitaev, \"Universal quantum computation with "
                "ideal Clifford gates and noisy ancillas,\" Phys. Rev. A 71, "
                "022316 (2005).",
    },
    "nezami2022classification": {
        "short": "Nezami & Haah (2022)",
        "full": "S. Nezami and J. Haah, \"Classification of small triorthogonal "
                "codes,\" Phys. Rev. A 106, 012437 (2022).",
    },
    "jacinto2026exploring": {
        "short": "Jacinto et al. (2026)",
        "full": "H. Jacinto, X. Valcarce, V. Barizien, É. Gouzien, and N. "
                "Sangouard, \"Exploring the landscape of compact magic-state "
                "distillation factories,\" arXiv:2606.07734 (2026).",
    },
    "gong2026magic": {
        "short": "Gong et al. (2026)",
        "full": "A. Gong, C. A. Pattison, P. Rall, and A. Wills, \"Magic State "
                "Distillation via Codes over Binary Extension Fields,\" "
                "arXiv:2608.09727 (2026).",
    },
    "haah2018codes": {
        "short": "Haah & Hastings (2018)",
        "full": "J. Haah and M. B. Hastings, \"Codes and Protocols for "
                "Distilling T, controlled-S, and Toffoli Gates,\" Quantum 2, 71 "
                "(2018).",
    },
    "vuillot2022quantum": {
        "short": "Vuillot & Breuckmann (2022)",
        "full": "C. Vuillot and N. P. Breuckmann, \"Quantum Pin Codes,\" IEEE "
                "Trans. Inf. Theory 68, 5955 (2022).",
    },
    "rengaswamy2020optimality": {
        "short": "Rengaswamy et al. (2020)",
        "full": "N. Rengaswamy, R. Calderbank, M. Newman, and H. D. Pfister, "
                "\"On Optimality of CSS Codes for Transversal T,\" IEEE J. Sel. "
                "Areas Inf. Theory 1, 499 (2020).",
    },
    "gong2024computation": {
        "short": "Gong & Renes (2024)",
        "full": "A. Gong and J. M. Renes, \"Computation with quantum Reed-Muller "
                "codes and their mapping onto 2D atom arrays,\" arXiv:2410.23263 "
                "(2024).",
    },
    "shi2024triorthogonal": {
        "short": "Shi et al. (2024)",
        "full": "M. Shi, H. Lu, J.-L. Kim, and P. Solé, \"Triorthogonal codes "
                "and self-dual codes,\" Quantum Inf. Process. 23, 280 (2024).",
    },
}


def t_everywhere(k):
    return frozenset(frozenset((q,)) for q in range(k))


def disjoint_ccz(m):
    return frozenset(frozenset((3 * i, 3 * i + 1, 3 * i + 2)) for i in range(m))


def monomials(*terms):
    return frozenset(frozenset(t) for t in terms)


def ccz_circuit_each_output_in(times):
    """Only CCZs, every output in exactly ``times`` of them (Rengaswamy Ex. 6)."""
    def check(row, gate):
        if not gate or any(len(m) != 3 for m in gate):
            return False
        counts = [sum(1 for m in gate if q in m) for q in range(row["k"])]
        return all(c == times for c in counts)
    return check


def reed_muller_pair(r_small, r_big, m):
    """A CCZ-only gate on the code CSS(RM(r_small, m), RM(r_big, m)^perp):
    ``n = 2^m``, ``N = dim RM(r_big, m)``, ``N - k = dim RM(r_small, m)``."""
    from math import comb
    dim = lambda r: sum(comb(m, i) for i in range(r + 1))

    def check(row, gate):
        return (row["n"] == 2 ** m and row["N"] == dim(r_big)
                and row["N"] - row["k"] == dim(r_small)
                and gate and all(len(mono) == 3 for mono in gate))
    return check


#: (n, k, published d, gate or structure check, keys, where it is printed)
LITERATURE = [
    # ---- the length-54 classification's Pareto table, Table tab:complete-pareto
    (15, 1, 3, t_everywhere(1), ["bravyi2005universal"],
     "Wills et al. Table (15T->T); Bravyi & Kitaev (2005)"),
    (28, 2, 3, t_everywhere(2), ["nezami2022classification"],
     "Wills et al. Table (28T->T^2, S=9); Nezami & Haah (2022)"),
    (35, 2, 3, t_everywhere(2), ["nezami2022classification"],
     "Wills et al. Table (35T->T^2, dagger: logical restriction of 35T->3T)"),
    (35, 2, 3, monomials((0, 1)), ["nezami2022classification"],
     "Wills et al. Table (35T->CS, dagger: logical restriction of 35T->3T)"),
    (35, 3, 3, t_everywhere(3), ["nezami2022classification"],
     "Wills et al. Table (35T->T^3, S=9); Nezami & Haah (2022)"),
    (47, 3, 3, disjoint_ccz(1), ["jacinto2026exploring"],
     "Wills et al. Table (47T->CCZ, S=9); Jacinto et al. (2026)"),
    (48, 3, 4, disjoint_ccz(1), ["jacinto2026exploring"],
     "Wills et al. Table (48T->CCZ, S=10, d=4); Jacinto et al. (2026)"),
    (48, 5, 3, monomials((3, 4), (0, 2, 4), (1, 2, 3)), ["gong2026magic"],
     "Wills et al. Table (48T->CS45.CCZ135.CCZ234, star: Gong et al. binarised "
     "Construction 4.21 with a logical row deleted)"),
    (48, 6, 3, monomials((0, 1), (0, 2, 3), (0, 2, 4), (0, 3, 5), (1, 2, 3),
                         (1, 4, 5)), ["gong2026magic"],
     "Wills et al. Table (48T->CS12.CCZ134.CCZ135.CCZ146.CCZ234.CCZ256, star: "
     "Gong et al. binarised Construction 4.21)"),
    # ---- n > 54
    # Haah & Hastings (2018): Table 1 (punctured RM(2,7)), Sec. 4.5, Table 2
    # (punctured RM(3,10)); all T -> T^k
    (109, 19, 3, t_everywhere(19), ["haah2018codes"], "Haah & Hastings Table 1"),
    (112, 16, 3, t_everywhere(16), ["haah2018codes"], "Haah & Hastings Table 1"),
    (114, 14, 3, t_everywhere(14), ["haah2018codes"], "Haah & Hastings Table 1"),
    (116, 12, 4, t_everywhere(12), ["haah2018codes", "vuillot2022quantum"],
     "Haah & Hastings Table 1; Vuillot & Breuckmann Table VII"),
    (118, 10, 4, t_everywhere(10), ["haah2018codes"], "Haah & Hastings Table 1"),
    (125, 3, 5, t_everywhere(3), ["haah2018codes"],
     "Haah & Hastings Sec. 4.5 (the unique d=5 puncture of RM(2,7))"),
    (863, 161, 3, t_everywhere(161), ["haah2018codes"], "Haah & Hastings Table 2"),
    (872, 152, 4, t_everywhere(152), ["haah2018codes"], "Haah & Hastings Table 2"),
    (887, 137, 5, t_everywhere(137), ["haah2018codes"], "Haah & Hastings Table 2"),
    (912, 112, 6, t_everywhere(112), ["haah2018codes"], "Haah & Hastings Table 2"),
    (937, 87, 7, t_everywhere(87), ["haah2018codes"],
     "Haah & Hastings Table 2 (the catalogue proves only d >= 6)"),
    # 64T -> 2 CCZ at d = 4
    (64, 6, 4, disjoint_ccz(2),
     ["haah2018codes", "gong2026magic", "jacinto2026exploring"],
     "Haah & Hastings Sec. 4.2 (64T->2CCZ); Gong et al. Construction 5.10; "
     "Jacinto et al. Sec. V C"),
    # Reed-Muller codes whose transversal T is a circuit of CCZs
    (64, 15, 4, ccz_circuit_each_output_in(3),
     ["rengaswamy2020optimality", "vuillot2022quantum", "gong2026magic"],
     "Rengaswamy et al. Example 6 (15 CCZs, each logical in three); Vuillot & "
     "Breuckmann Table VIII; Gong et al. Construction 4.1"),
    (512, 84, 8, reed_muller_pair(2, 3, 9),
     ["rengaswamy2020optimality", "vuillot2022quantum"],
     "Rengaswamy et al. Example 8 (m=9, r=3); Vuillot & Breuckmann Table VIII "
     "(the catalogue proves only d >= 6)"),
    # single-output T factories
    (64, 1, 4, t_everywhere(1), ["jacinto2026exploring"],
     "Jacinto et al. Table II (cyclic symmetry, N=10, n=64, d=4)"),
    (165, 1, 4, t_everywhere(1), ["jacinto2026exploring"],
     "Jacinto et al. Table I and Table II (N=10, n=165, d=4)"),
    (127, 1, 7, t_everywhere(1), ["gong2024computation"],
     "Gong & Renes: triply even punctured quantum Reed-Muller code [[127,1,7]]"),
    # Shi, Lu, Kim and Sole (2024), Table 2: triorthogonal [[n,k,dZ=3]]
    *[(n, k, 3, t_everywhere(k), ["shi2024triorthogonal"],
       "Shi et al. Table 2 (triorthogonal, Z-distance 3)")
      for n, k in ((55, 3), (56, 2), (56, 4), (57, 3), (58, 2), (58, 4),
                   (59, 3), (60, 2), (60, 4), (61, 3), (62, 2), (62, 4),
                   (63, 3), (63, 5), (64, 2), (64, 4), (65, 3), (65, 5),
                   (66, 2), (66, 4))],
    # Vuillot & Breuckmann Table VII, remaining T -> T^k rows
    *[(n, k, 4, t_everywhere(k), ["vuillot2022quantum"],
       "Vuillot & Breuckmann Table VII")
      for n, k in ((175, 17), (236, 20), (261, 27), (466, 46))],
]

#: A published protocol the catalogue does not hold matches no row, and that is
#: reported rather than fatal: the tables above are longer than this catalogue.
#: When this ran, [[48,3]] CCZ was held only at d = 3 -- the pre-2026-09-15 key
#: left the distance out, so a merge had dropped the wider d = 4 circuit -- and
#: the d = 4 row was restored afterwards.  An AMBIGUOUS match is still fatal.


def matches(row, n, k, d, gate):
    if (row["n"], row["k"]) != (n, k):
        return False
    if row["d_is_exact"] and row["d"] != d:
        return False
    if not row["d_is_exact"] and row["d"] > d:
        return False
    mine = VC.row_monomials(row)
    if callable(gate):
        return bool(gate(row, mine))
    return GC.gl_isomorphic(k, mine, gate) is True


def cite(payload):
    rows = payload["factories"]
    literature = {id(row): [] for row in rows}
    report = []
    for n, k, d, gate, keys, where in LITERATURE:
        hits = [row for row in rows if matches(row, n, k, d, gate)]
        if len(hits) > 1:
            raise SystemExit(f"[[{n},{k},{d}]] ({where}) matches {len(hits)} "
                             f"rows; refusing an ambiguous citation")
        if not hits:
            report.append(f"  (not held) [[{n},{k},{d}]] {where}")
            continue
        row = hits[0]
        for key in keys:
            if key not in literature[id(row)]:
                literature[id(row)].append(key)
        report.append(f"  [[{n},{k},{d}]] -> {', '.join(keys)}  ({where})")
    for row in rows:
        credited = literature[id(row)]
        if row["n"] <= MR.CLASSIFICATION_LENGTH:
            row["citations"] = (["wills2026classification", "jain2026symmetry"]
                                + credited)
        else:
            row["citations"] = credited or ["jain2026symmetry"]
    used = {key for row in rows for key in row["citations"]}
    payload["references"] = {key: dict(entry)
                             for key, entry in REFERENCES.items() if key in used}
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load()
    report = cite(payload)
    print("\n".join(report))
    rows = payload["factories"]
    big = [r for r in rows if r["n"] > MR.CLASSIFICATION_LENGTH]
    print(f"\n{sum(1 for r in rows if r['n'] <= 54)} classes with n <= 54; "
          f"{len(big)} with n > 54, of which "
          f"{sum(1 for r in big if r['citations'] != ['jain2026symmetry'])} "
          f"credited to the literature")
    residue = VC.citation_problems(payload) + VC.header_problems(payload)
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("citations would not resolve; nothing written")
    if args.dry_run:
        print("dry run: nothing written")
        return 0
    CF.write(payload)
    print("wrote master_catalog.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
