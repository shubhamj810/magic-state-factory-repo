import sys, json, itertools
sys.path.insert(0, 'code')
import dbl
def tform(L):
    return dbl.form(L)
def rep_labels(L, tmax=8):
    """smallest multiset of labels l in F2^k \\ 0 with sum l^(x3) = form(L) mod 2 (brute force)."""
    k = len(L); f = dbl.form(L)
    labs = list(range(1, 1 << k))
    def fo(ls):
        out = {}
        for (i, j, l) in f:
            out[(i, j, l)] = sum(((x >> i) & (x >> j) & (x >> l)) & 1 for x in ls) & 1
        return out
    for t in range(1, tmax + 1):
        for ls in itertools.combinations_with_replacement(labs, t):
            if fo(ls) == f:
                return list(ls)
    return None
if __name__ == '__main__':
    for p in sys.argv[1:]:
        t = dbl.load_factory(p)
        print(p.split('/')[-1][:12], t['n'], t['k'], 'labels', rep_labels(t['L']))
