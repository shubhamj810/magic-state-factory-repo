// wdist.c: the weight distribution D_0..D_n of the span of m binary vectors of length n <= 512, every
// word of the span visited once.  The 2^m words are split by their top h generator coefficients into
// 2^h chunks (OpenMP, dynamic schedule); inside a chunk the low m - h coefficients run in Gray-code
// order, one XOR of the vector and one popcount per word.  The generators must be independent (the
// caller passes a basis); the output is "D_0 D_1 ... D_n" on one line, and the sum must be 2^m.
// Input (text): n m, then m lines of W = ceil(n/64) hex words (word 0 first).
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef _OPENMP
#include <omp.h>
#endif
#define MAXW 8
int main(int argc, char **argv) {
    int n, m;
    if (scanf("%d %d", &n, &m) != 2 || n < 1 || n > 512 || m < 1 || m > 62) { fprintf(stderr, "bad header\n"); return 2; }
    int W = (n + 63) / 64;
    uint64_t (*G)[MAXW] = calloc(m, sizeof *G);
    for (int i = 0; i < m; i++)
        for (int w = 0; w < W; w++) {
            unsigned long long x;
            if (scanf("%llx", &x) != 1) { fprintf(stderr, "short input\n"); return 2; }
            G[i][w] = x;
        }
    int h = m > 14 ? 14 : m / 2;
    int lo = m - h;
    uint64_t chunks = 1ULL << h, steps = 1ULL << lo;
    uint64_t *hist = calloc((size_t)(n + 1), sizeof(uint64_t));
    #pragma omp parallel
    {
        uint64_t *loc = calloc((size_t)(n + 1), sizeof(uint64_t));
        #pragma omp for schedule(dynamic, 1)
        for (uint64_t c = 0; c < chunks; c++) {
            uint64_t v[MAXW] = {0};
            for (int j = 0; j < h; j++)
                if ((c >> j) & 1) for (int w = 0; w < W; w++) v[w] ^= G[lo + j][w];
            for (uint64_t s = 0; s < steps; s++) {
                if (s) { int b = __builtin_ctzll(s); for (int w = 0; w < W; w++) v[w] ^= G[b][w]; }
                int wt = 0;
                for (int w = 0; w < W; w++) wt += __builtin_popcountll(v[w]);
                loc[wt]++;
            }
        }
        #pragma omp critical
        for (int i = 0; i <= n; i++) hist[i] += loc[i];
        free(loc);
    }
    uint64_t tot = 0;
    for (int i = 0; i <= n; i++) { printf("%llu%c", (unsigned long long)hist[i], i < n ? ' ' : '\n'); tot += hist[i]; }
    if (tot != (1ULL << m)) { fprintf(stderr, "total %llu != 2^%d\n", (unsigned long long)tot, m); return 4; }
    return 0;
}
