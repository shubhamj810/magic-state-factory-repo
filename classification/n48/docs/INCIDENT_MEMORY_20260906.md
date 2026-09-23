# Incident: memory blow-up in the length-48 sweep (2026-09-06, 21:50–22:08)

## What happened

The κ-ordered length-48 sweep (`--max-shards 313`) had finished 297 shards
(everything with κ ≤ 6 and most of κ = 7) when, on shard 298 (194 m = 8
representatives, κ = 7), both workers stopped producing output.  Seventeen
minutes later the machine was thrashing:

```
load averages: 183.92 79.87 34.49        (8 GB laptop, 2 niced workers)
vm.swapusage: total = 11520 MB  used = 11520 MB  free = 0 MB
top:  PID 88985  MEM 18G   PID 88986  MEM 16G      <- the two workers
```

`ps` showed the workers at ~100 MB RSS — resident set excludes swapped and
compressed pages, which is why the load spike was noticed before the memory
was.  `./stop48.sh` ended it; swap drained within a minute.  The 297 shards
already written are unaffected (each shard file is complete before it is
written, and had been committed at shard 280).

## Cause — certain

The cross-parent orbit memo in `classify48.py` was bounded by **entry
count** (4096 orbits), not by memory.  Up to κ = 6 the orbits met are small
(≤ 4,340 members) and the memo stays under ~100 MB.  At κ = 7 the
classification meets k = 6 orbits of **39,060** members (a probe of
`length48_m8_class_02208`, origin 200: n = 47, κ = 7, k = 6 orbit of 39,060
members, 87 s to walk, 189 s for the parent).  Each member is a frozenset of
monomial frozensets plus its 6-row basis-change matrix — several KB — so
one such orbit is ~0.3 GB, and the memo happily kept dozens of them per
worker.  Nothing pathological about the parent itself: with the memo off it
classifies in 189 s and ~1 GB.

```
 memo entries      ×  members/orbit  ×  bytes/member   =  footprint
   4096 (cap)         39,060 (κ=7)       ~5 KB             tens of GB     <- what happened
  budget 60,000 members total, orbits > 8,000 never kept   ≤ ~0.5 GB      <- fix
```

## Fix (this directory only)

1. `classify48.py`: the memo is now bounded by a **member budget**
   (`_MEMO_MEMBER_BUDGET = 60_000`) and never keeps an orbit above
   `_MEMO_MAX_ORBIT = 8_000` members.  Results are unchanged (the memo is
   speed-only; `tests/test_n48.py::test_orbit_memo_is_invisible` still
   passes), so `ENGINE` and the completed shards stay valid.
2. Two guards that turn a runaway parent into a **recorded failure** instead
   of a hang: `ORBIT_CAP` (150,000 members per orbit walk, env
   `N48_ORBIT_CAP`) raising `OrbitTooLarge`, and a per-parent alarm
   `PARENT_SECONDS` (1800 s, env `N48_PARENT_SECONDS`) raising
   `ParentTimeout`.  Both land in the shard's `failed` list with the origin
   and error, mark the representative incomplete, and make the driver exit
   1 — the catalogue builder then refuses the source, so nothing is silently
   skipped.
3. `Pool(..., maxtasksperchild=32)`: workers are recycled every 32 jobs so
   no per-process growth can outlive a shard.
4. `watchdog48.sh`: polls `top`'s footprint (not `ps` RSS) of every process
   in the sweep's process group every 30 s and runs `stop48.sh` above
   2.5 GB.  Run it alongside every sweep from now on.

## What it means for the remaining shards

Shards 298–313 are κ = 7–10.  The κ = 7 probe shows ~40k-member k = 6
orbits; k = 7 orbits at κ ≥ 8 may exceed `ORBIT_CAP` and be recorded as
failures.  Those parents then need a canonical-form classifier for cubic
gates (not an orbit walk) or a cluster — a decision for the user; the shard
files will say exactly which parents they are.
