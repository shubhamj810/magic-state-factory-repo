// trellis_count.c: the counting pass of trellis_count.py.  Input: int32 nsteps, W, maxcut; per step int32 a, b
// (cut ranks before and after), then a + 1 uint64: the coordinate words of the a basis vectors of S_t and of
// the column g in the basis of S_{t+1} extended to S_t + <g> (bits >= b: outside S_{t+1}).
// Output: the counts of weight 0..W at the final state (the weight enumerator of the kernel, truncated).
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "rb");
    int32_t h[3];
    if (!f || fread(h, 4, 3, f) != 3) return 2;
    int ns = h[0], W = h[1], maxcut = h[2];
    if (maxcut > 34) { fprintf(stderr, "cut rank %d too large\n", maxcut); return 3; }
    size_t S = (size_t)1 << maxcut, R = (size_t)W + 1;
    uint64_t *cur = calloc(S * R, 8), *nxt = calloc(S * R, 8);
    if (!cur || !nxt) { fprintf(stderr, "out of memory\n"); return 3; }
    cur[0] = 1;
    uint64_t packed[64];
    for (int t = 0; t < ns; t++) {
        int32_t ab[2];
        if (fread(ab, 4, 2, f) != 2) return 2;
        int a = ab[0], b = ab[1];
        if (fread(packed, 8, a + 1, f) != (size_t)(a + 1)) return 2;
        uint64_t pg = packed[a], keep = (b >= 64) ? ~0ULL : ((1ULL << b) - 1);
        size_t na = (size_t)1 << a, nb = (size_t)1 << b;
        memset(nxt, 0, nb * R * 8);
        uint64_t P = 0;
        for (size_t kk = 0; kk < na; kk++) {
            if (kk) P ^= packed[__builtin_ctzll(kk)];
            size_t i = kk ^ (kk >> 1);
            const uint64_t *ci = &cur[i * R];
            int any = 0;
            for (size_t w = 0; w < R; w++) if (ci[w]) { any = 1; break; }
            if (!any) continue;
            if ((P & ~keep) == 0) {
                uint64_t *d = &nxt[P * R];
                for (size_t w = 0; w < R; w++) d[w] += ci[w];
            }
            uint64_t Q = P ^ pg;
            if ((Q & ~keep) == 0) {
                uint64_t *d = &nxt[Q * R];
                for (size_t w = 0; w + 1 < R; w++) d[w + 1] += ci[w];
            }
        }
        uint64_t *tmp = cur; cur = nxt; nxt = tmp;
        // states of the old step beyond nb are stale in `cur` but never read: the next step reads 2^b of them
    }
    for (size_t w = 0; w < R; w++) printf("%llu%c", (unsigned long long)cur[w], w + 1 < R ? ' ' : '\n');
    return 0;
}
