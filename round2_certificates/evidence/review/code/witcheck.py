"""Re-check faults on a problem file with faultcore.Circuit.harmful and the literal OR-built XOR."""
import json, sys
sys.path.insert(0, "/Users/shubhamjain/Documents/IBM internship/Shraddha (Magic states)/magic-state-factory-repo/master_catalog")
import faultcore as FC
d = json.load(open(sys.argv[1])); k, N, cols = d["k"], d["N"], d["columns"]
P = sorted(d.get("points", [])); comp = [x for x in range(2048) if x not in set(P)] if P else None
C = FC.Circuit(cols, k, N)
for arg in sys.argv[2:]:
    spec = json.loads(arg)
    if isinstance(spec, dict):   # {"points": [...]} -> columns
        F = [comp.index(p) for p in spec["points"]]
    else:
        F = spec
    x = 0
    for j in F:
        m = 0
        for q in cols[j]:
            m |= 1 << q
        x ^= m
    print(json.dumps({"fault": F, "weight": len(set(F)), "faultcore_harmful": C.harmful(F),
                      "literal_harmful": bool(x and not x >> k), "flips": bin(x).count("1")}))
