#!/usr/bin/env python3
"""One-off migration: the source provenance of the round-3 rows names each parent by its
catalogue label.

    python master_catalog/migrations/round3_provenance_2026_11_08.py [--dry-run]

The 66 rows imported on 7 to 8 November 2026 from s3-mid, s3-d56 and s3-d7 kept the searches'
own wording in their source's ``provenance``. Some of it named a parent only by a bare file
name or digest prefix ("<sha>.json", "lin_lift_95_24.json", "small-radical:e16b7d73..."),
called a single row a direct sum ("(1 pairs) of the direct sum 94.16.4.a"), or wrote
"(1 pairs)". Each parent was resolved by the SHA-256 of its columns
(research/search2/catalogue/stage3/code/prov66.py and resolve_short.py): a parent the
catalogue holds is named by its label; small-d7's [[217,7,7]] circuit 9c3da8b2, which the
catalogue no longer stores, is named by its research-branch path. ``CHANGES`` lists every
string before and after. Only these strings change: no regime, credit, citation or number.
The file-level checks pass before anything is written. Idempotent.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import catalogfile as CF                                          # noqa: E402
import distance_policy_2026_11_07 as DP                           # noqa: E402
import verify_catalog as VC                                       # noqa: E402

#: (label, provenance before, provenance after)
CHANGES = (
    ('76.17.3.a',
     'paired-column contraction (1 pairs) of the direct sum 15.1.3.a + 63.16.3.a',
     'one paired-column contraction of the direct sum 15.1.3.a + 63.16.3.a'),
    ('87.18.3.a',
     'paired-column contraction (2 pairs) of the direct sum 28.2.3.a + 63.16.3.a',
     'two paired-column contractions of the direct sum 28.2.3.a + 63.16.3.a'),
    ('92.16.4.a',
     'paired-column contraction (1 pairs) of the direct sum 94.16.4.a',
     'one paired-column contraction of 94.16.4.a'),
    ('92.19.3.a',
     'paired-column contraction (3 pairs) of the direct sum 35.3.3.b + 63.16.3.a',
     'three paired-column contractions of the direct sum 35.3.3.b + 63.16.3.a'),
    ('93.16.3.a',
     'descent from 94.16.4.a (N = 26): one shortening at column 0 with the all-ones check, so n and N each fall by 1 and d by 1; s3-mid: shortening of research/search2/small-d4/data/circuits/078e3fd5abd42bcac4d943795cafc69be12ebd7e5a17292226ed5ee42bf8ac74.json at column 0 with the all-ones check (formal CCZ d=3 row)',
     'descent from 94.16.4.a (N = 26): one shortening at column 0 with the all-ones check, so n and N each fall by 1 and d by 1; s3-mid: shortening of 94.16.4.a at column 0 with the all-ones check (formal CCZ d=3 row)'),
    ('95.24.3.a',
     'lift:96.23.4.a:p0',
     'lift of the even d=4 row 96.23.4.a at column 0'),
    ('104.25.3.a',
     'paired-column contraction (3 pairs) of the direct sum 15.1.3.a + lin_lift_95_24.json',
     "three paired-column contractions of the direct sum 15.1.3.a + 95.24.3.a (s3-mid's lin_lift_95_24.json)"),
    ('111.28.3.a',
     'lift:112.27.4.a:p0',
     'lift of the even d=4 row 112.27.4.a at column 0'),
    ('119.30.3.a',
     'lift:120.29.4.a:p0',
     'lift of the even d=4 row 120.29.4.a at column 0'),
    ('123.31.3.a',
     'lift:124.30.4.a:p0',
     'lift of the even d=4 row 124.30.4.a at column 0'),
    ('124.32.3.a',
     'paired-column contraction (1 pairs) of the direct sum 63.16.3.a + 63.16.3.a',
     'one paired-column contraction of the direct sum 63.16.3.a + 63.16.3.a'),
    ('125.6.5.a',
     'one shortening of the [[126,6,6]] contraction of 72.3.6.a + 72.3.6.a (claim above)',
     'one shortening of 126.6.6.a, the contraction of the direct sum 72.3.6.a + 72.3.6.a'),
    ('127.33.3.a',
     'lift:128.32.4.a:p0',
     'lift of the even d=4 row 128.32.4.a at column 0'),
    ('135.34.3.a',
     'lift of the even d=4 row 8bc041f2a3feffa7f7348350d76e68d6c96f88a947465a153a0c03b8529bd65d.json at column 0',
     'lift of the even d=4 row 136.33.4.a at column 0'),
    ('147.37.3.a',
     'lift of the even d=4 row 5fa85842c5dc1fc4cd3e9661d2b4a4eeebc81de19d4eef985638016eb5f0e35d.json at column 0',
     'lift of the even d=4 row 148.36.4.a at column 0'),
    ('151.38.3.a',
     'lift of the even d=4 row 41ed083234b04a76a8fd0f065ae140c28bc82257b007766da77edde7c8b66b0e.json at column 0',
     'lift of the even d=4 row 152.37.4.a at column 0'),
    ('153.39.3.a',
     'lift of the even d=4 row dc43d46c84f70372ec3749389c50acb7391596c4639e9e70963f693201e36df4.json at column 0',
     'lift of the even d=4 row 154.38.4.a at column 0'),
    ('154.2.7.a',
     'paired-column contraction (gamma_frontier CONTRACTION_PROOF.md) of the Golay doubling [[162,2,7]] (2 Golay [[23,1,7]] blocks) of s3-d56 [[70,2,5]] T0.T1 claim ea0d7d6c at D=7; the moves are in the claim file',
     "paired-column contraction (gamma_frontier CONTRACTION_PROOF.md) of the Golay doubling [[162,2,7]] (2 Golay [[23,1,7]] blocks) of 70.2.5.a (s3-d56's T0.T1 claim ea0d7d6c) at D=7; the moves are in the claim file"),
    ('159.40.3.a',
     'lift of the even d=4 row d9da2f8542fce043b4bc990aebf572069563423cd382411887a3c528d966c3de.json at column 0',
     'lift of the even d=4 row 160.39.4.a at column 0'),
    ('163.41.3.a',
     'lift of the even d=4 row 7d3cc576c7bb61be65e5607437ad288836fe9edfe3b23167f539e6377dc52a5e.json at column 0',
     'lift of the even d=4 row 164.40.4.a at column 0'),
    ('165.42.3.a',
     'lift of the even d=4 row 7cf5132eb5bb464b9642fb35e6a619f4452911f27f67c4f537d0e0c00cd197b3.json at column 0',
     'lift of the even d=4 row 166.41.4.a at column 0'),
    ('167.43.3.a',
     'lift of the even d=4 row d1ac8593eadf03e50b96c7a972cbecdbd8bd4ffaa8803b0e05517575e04907f0.json at column 0',
     'lift of the even d=4 row 168.42.4.a at column 0'),
    ('171.44.3.a',
     'lift of the even d=4 row 8d80f516ca7eb786bb56d9a1d59a5a03f122cf5df743368e53c14cb1bce9a256.json at column 0',
     'lift of the even d=4 row 172.43.4.a at column 0'),
    ('175.45.3.a',
     'lift of the even d=4 row 451c182bc35e8355298f2c33d40898b88aaab730ca9652d7090fd347d2309ed0.json at column 0',
     'lift of the even d=4 row 176.44.4.a at column 0'),
    ('179.46.3.a',
     'lift of the even d=4 row 1924c0776b4bbfa2b56bd2979e31f3dbf5769549ea287a3c73a38bd67937986f.json at column 0',
     'lift of the even d=4 row 180.45.4.a at column 0'),
    ('183.47.3.a',
     'lift of the even d=4 row a981de5dc3b490712d94e89a670038e728ba30bebb5f0e0111581c0ab34bc4be.json at column 0',
     'lift of the even d=4 row 184.46.4.a at column 0'),
    ('185.2.7.a',
     'Golay doubling (Jain-Albert map generalised to k outputs): 2 Golay [[23,1,7]] blocks with labels [1, 2], doubled onto small-radical:e16b7d7315571727 (n=93, k=2)',
     "Golay doubling (Jain-Albert map generalised to k outputs): 2 Golay [[23,1,7]] blocks with labels [1, 2], doubled onto small-radical's e16b7d73, which is 93.3.5.a, with two of its three outputs kept (n=93, k=2)"),
    ('186.2.6.a',
     'Golay doubling (Jain-Albert map generalised to k outputs): 3 Golay [[23,1,7]] blocks with labels [1, 2, 3], doubled onto cat:48.2.4.a (n=48, k=2)',
     'Golay doubling (Jain-Albert map generalised to k outputs): 3 Golay [[23,1,7]] blocks with labels [1, 2, 3], doubled onto 48.2.4.a (n=48, k=2)'),
    ('189.49.3.a',
     'lift of the even d=4 row 76d2befe2ae78b39d5bbf756ed5691171d87f03f0eb55dd91303a927ffebe6d9.json at column 0',
     'lift of the even d=4 row 190.48.4.a at column 0'),
    ('195.51.3.a',
     'lift of the even d=4 row 1de3c43fbb197406224da9c4ba262b2991f3f488f5b633aa942ae76df2c01cd1.json at column 0',
     'lift of the even d=4 row 196.50.4.a at column 0'),
    ('201.52.3.a',
     'lift of the even d=4 row ac0e2f8a896c5b1851f4deaa9f8826fd31289e0df5cfb8b72630ac9f4242d2f4.json at column 0',
     'lift of the even d=4 row 202.51.4.a at column 0'),
    ('203.53.3.a',
     'lift of the even d=4 row 667b51ad53a7dee3c4e4e5b90c35dcbfe8dafcf75d549eeb3a9867bee87aa0cc.json at column 0',
     'lift of the even d=4 row 204.52.4.a at column 0'),
    ('205.3.7.a',
     'paired-column contraction (gamma_frontier CONTRACTION_PROOF.md) of the Golay doubling [[231,3,7]] of small-radical [[93,3,5]] e16b7d73 (3 Golay [[23,1,7]] blocks) at D=7; the moves are in the claim file',
     "paired-column contraction (gamma_frontier CONTRACTION_PROOF.md) of the Golay doubling [[231,3,7]] of 93.3.5.a (small-radical's e16b7d73) (3 Golay [[23,1,7]] blocks) at D=7; the moves are in the claim file"),
    ('207.55.3.a',
     'lift of the even d=4 row 7287bc2eab00272ecb398d9c059c30c5c1e03758d35d650ff7c7eff8377be36e.json at column 0',
     'lift of the even d=4 row 208.54.4.a at column 0'),
    ('211.3.7.a',
     'paired-column contraction (gamma_frontier CONTRACTION_PROOF.md) of the direct sum data/claims/2e7f5934848d72a39527f9005952162ef97a5483155fd1fe5ee0b62527af4005.json + 95.1.7.a at D=7; the moves are in the claim file',
     "paired-column contraction (gamma_frontier CONTRACTION_PROOF.md) of the direct sum 158.2.7.a (s3-d7's 2e7f5934) + 95.1.7.a at D=7; the moves are in the claim file"),
    ('211.58.3.a',
     'lift of the even d=4 row fee1e49df148bb0751b3716c08b6f3c5e2d7e603ff94ef4d83dd076d0d3e92b0.json at column 0',
     'lift of the even d=4 row 212.57.4.a at column 0'),
    ('213.2.7.a',
     'paired-column contraction (gamma_frontier CONTRACTION_PROOF.md) of the Golay doubling [[231,2,7]] (CS01) of small-radical [[93,2,5]] CS f0e29414 (3 Golay [[23,1,7]] blocks) at D=7; the moves are in the claim file',
     "paired-column contraction (gamma_frontier CONTRACTION_PROOF.md) of the Golay doubling [[231,2,7]] (CS01) of 93.2.5.a (small-radical's CS f0e29414) (3 Golay [[23,1,7]] blocks) at D=7; the moves are in the claim file"),
    ('219.60.3.a',
     'lift of the even d=4 row 1d1cd0ff0a170ba2f6cd9fa0f9668bc955e3b53b5952bc272b8db6a37f35d348.json at column 0',
     'lift of the even d=4 row 220.59.4.a at column 0'),
    ('221.61.3.a',
     'lift of the even d=4 row 3dab192e933dc7a4ce3a3a275f4a6b988f00bd4ef050fa552b5a7ed461eac15f.json at column 0',
     'lift of the even d=4 row 222.60.4.a at column 0'),
    ('223.64.3.a',
     'lift of the even d=4 row 11e4b245038d150f7d37b44cd473295ce750c51f8a431fbfc2395611658d0534.json at column 0',
     'lift of the even d=4 row 224.63.4.a at column 0'),
    ('227.66.3.a',
     'lift of the even d=4 row ea71695c8e8e49fd960309746676e2db8c1d9d43b85af4b806e516fd171885f5.json at column 0',
     'lift of the even d=4 row 228.65.4.a at column 0'),
    ('231.2.7.a',
     'Golay doubling (Jain-Albert map generalised to k outputs): 3 Golay [[23,1,7]] blocks with labels [1, 2, 3], doubled onto small-radical:f0e29414b5acdbd7 (n=93, k=2)',
     "Golay doubling (Jain-Albert map generalised to k outputs): 3 Golay [[23,1,7]] blocks with labels [1, 2, 3], doubled onto 93.2.5.a (small-radical's f0e29414; n=93, k=2)"),
    ('231.69.3.a',
     'lift of the even d=4 row e6ff1bc56277771ab7ca0ead1bd2c8b7813c0a2b758899be21ed74235fa96b42.json at column 0',
     'lift of the even d=4 row 232.68.4.a at column 0'),
    ('239.75.3.a',
     'lift of the even d=4 row 6f97de6551ee3cafc9710106b5bb8e4f772c19f45e05cf363088449eaef5bbee.json at column 0',
     'lift of the even d=4 row 240.74.4.a at column 0'),
    ('256.3.6.a',
     'Golay doubling (Jain-Albert map generalised to k outputs): 4 Golay [[23,1,7]] blocks with labels [2, 3, 4, 5], doubled onto cat:72.3.4.a (n=72, k=3)',
     'Golay doubling (Jain-Albert map generalised to k outputs): 4 Golay [[23,1,7]] blocks with labels [2, 3, 4, 5], doubled onto 72.3.4.a (n=72, k=3)'),
    ('268.8.7.a',
     'paired-column contraction (gamma_frontier CONTRACTION_PROOF.md) of the direct sum small-d7 [[217,7,7]] 9c3da8b2 + 95.1.7.a at D=7; the moves are in the claim file',
     "paired-column contraction (gamma_frontier CONTRACTION_PROOF.md) of the direct sum small-d7's [[217,7,7]] circuit 9c3da8b2 (research/search2/small-d7/data/claims/9c3da8b2e0653b80185ffb7c695e16043627cbe57a70531ad09e023b65878d92.json; the class of 217.7.7.a, which now stores small-cyc's circuit 69bae4f9) + 95.1.7.a at D=7; the moves are in the claim file"),
    ('272.3.7.a',
     'paired-column contraction (gamma_frontier CONTRACTION_PROOF.md) of the Golay doubling [[304,3,7]] (CS01·CS02) of small-radical [[120,3,5]] CS 6766fa8b (4 Golay [[23,1,7]] blocks) at D=7; the moves are in the claim file',
     "paired-column contraction (gamma_frontier CONTRACTION_PROOF.md) of the Golay doubling [[304,3,7]] (CS01·CS02) of 120.3.5.a (small-radical's CS 6766fa8b) (4 Golay [[23,1,7]] blocks) at D=7; the moves are in the claim file"),
    ('304.3.7.a',
     'Golay doubling (Jain-Albert map generalised to k outputs): 4 Golay [[23,1,7]] blocks with labels [2, 3, 4, 5], doubled onto small-radical:6766fa8b37b29666 (n=120, k=3)',
     "Golay doubling (Jain-Albert map generalised to k outputs): 4 Golay [[23,1,7]] blocks with labels [2, 3, 4, 5], doubled onto 120.3.5.a (small-radical's 6766fa8b; n=120, k=3)"),
    ('319.9.7.a',
     'paired-column contraction (gamma_frontier CONTRACTION_PROOF.md) of the direct sum s3-d7 [[268,8,7]] 75a34baa (itself a contraction of small-d7 [[217,7,7]] 9c3da8b2 + 95.1.7.a) + 95.1.7.a at D=7; the moves are in the claim file',
     "paired-column contraction (gamma_frontier CONTRACTION_PROOF.md) of the direct sum 268.8.7.a (s3-d7's 75a34baa, itself a contraction of the direct sum small-d7's [[217,7,7]] circuit 9c3da8b2 (research/search2/small-d7/data/claims/9c3da8b2e0653b80185ffb7c695e16043627cbe57a70531ad09e023b65878d92.json; the class of 217.7.7.a, which now stores small-cyc's circuit 69bae4f9) + 95.1.7.a) + 95.1.7.a at D=7; the moves are in the claim file"),
)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = CF.load_all()
    by = {row["catalog_label"]: row for row in payload["factories"]}
    changed = 0
    for label, old, new in CHANGES:
        (source,) = [s for s in by[label]["sources"]
                     if s["label"].startswith(("s3-mid", "s3-d56", "s3-d7"))]
        if source["provenance"] == new:
            continue
        if source["provenance"] != old:
            raise SystemExit(f"{label}: the provenance is not the one expected")
        source["provenance"] = new
        changed += 1
    rows = payload["factories"]
    residue = (VC.duplicate_label_problems(rows) + VC.provenance_problems(payload)
               + VC.citation_problems(payload) + VC.header_problems(payload))
    if residue:
        for kind, detail in residue:
            print(f"  - {kind}: {detail}")
        raise SystemExit("the catalogue fails a file-level check; nothing written")
    print(f"{changed} of {len(CHANGES)} provenance strings changed")
    if args.dry_run or not DP._changes(payload):
        print("nothing written" + (": dry run" if args.dry_run else ""))
        return 0
    CF.write_all(payload)
    print("wrote master_catalog.json, master_catalog_large.json and MASTER_CATALOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
