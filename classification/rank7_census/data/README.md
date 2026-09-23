# Gillot–Langevin `RM(3,7)` orbit data

`B-0-3-7.dat` is the external orbit table used by the check-parent-first
`r <= 7` classification. It contains 3,486 representatives of `RM(3,7)` under
`AGL(7,2)`, together with stabilizer generators and reported stabilizer orders.

Source and citation:

- Valérie Gillot and Philippe Langevin, “Classification of Some Cosets of the
  Reed–Muller Code,” *Cryptography and Communications* 15 (2023), 1129–1137,
  DOI [`10.1007/s12095-023-00652-4`](https://doi.org/10.1007/s12095-023-00652-4).
- Upstream numerical-data page:
  <https://langevin.univ-tln.fr/project/agl7/data/index.php>

Bundled file integrity:

```text
SHA-256  07ead6fb7809c4f249b3a6b6e4f895b5d1d43fbbc3606cccbe0c3bcb3fa75846
bytes   776843
lines   19548
```

The upstream page makes the data publicly downloadable but does not state a
separate data license. The file is included unchanged for reproducibility and
is not relicensed by this repository; Gillot and Langevin retain any applicable
rights. Confirm redistribution terms with the authors or your institution
before a public release if your policy requires an explicit data license.

## Integrity correction

The final class (`index 3485`, `anf=a`, weight 64) reports
`stabSize=|AGL(7,2)|`, which would make its orbit a singleton. The orbit is the
254 nonconstant affine functions, so the correct stabilizer size is
`|AGL(7,2)| / 254 = 82570075176960`.

The source file is deliberately unchanged. The parser applies this correction
in memory when checking orbit sizes. After correction,

```text
sum(|AGL(7,2)| / |Stab(f)|) = 2^64 = |RM(3,7)|.
```

The affected class has weight 64, outside the `n <= 44` factory census, so it
does not change any enumerated parent. Reproduce the integrity check from the repository root with:

```bash
.venv/bin/python classification/rank7_census/cli.py data-check
```
