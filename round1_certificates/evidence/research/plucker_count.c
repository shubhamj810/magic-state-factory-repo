// Exact A_d of a CCZ frame (d = 2^q) by counting q-dimensional subspaces V of F_2^m with a nonzero
// q x q minor on some output set S (the harmful q-flats are a + V for exactly those V, for all 2^(m-q)
// cosets a; see frame_Ad.py for the argument).  Enumerates V by reduced row echelon form.
//
// Input (stdin): m q k, then k lines of q coordinates each (the output sets).
// Output: one JSON line with the number of subspaces, the harmless ones, A_d, per-output counts.
// usage: plucker_count [I M [PEROUT]] < sets.txt   (only chunks of 2^22 subspaces with index % M == I; PEROUT = 0 stops at the
//        first nonzero minor, so per-output counts are then meaningless)
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static int m, q, k;
static int S[1024][8];
static uint64_t perout[1024];

static int det(const uint32_t *rows, const int *cols) {
    // q x q determinant over F_2 of the submatrix rows x cols, by elimination on bit-packed rows
    uint32_t a[8];
    for (int i = 0; i < q; i++) {
        uint32_t v = 0;
        for (int j = 0; j < q; j++) v |= ((rows[i] >> cols[j]) & 1u) << j;
        a[i] = v;
    }
    for (int c = 0; c < q; c++) {
        int p = -1;
        for (int i = c; i < q; i++) if (a[i] >> c & 1) { p = i; break; }
        if (p < 0) return 0;
        uint32_t t = a[p]; a[p] = a[c]; a[c] = t;
        for (int i = c + 1; i < q; i++) if (a[i] >> c & 1) a[i] ^= a[c];
    }
    return 1;
}

int main(int argc, char **argv) {
    if (scanf("%d %d %d", &m, &q, &k) != 3) return 2;
    for (int i = 0; i < k; i++) for (int j = 0; j < q; j++) if (scanf("%d", &S[i][j]) != 1) return 2;
    int I = argc > 2 ? atoi(argv[1]) : 0, M = argc > 2 ? atoi(argv[2]) : 1;
    int PEROUT = argc > 3 ? atoi(argv[3]) : 1;     // 0: stop at the first nonzero minor (no per-output counts)
    uint64_t total = 0, harmless = 0;
    int piv[8];
    // iterate pivot sets in lexicographic order
    for (int i = 0; i < q; i++) piv[i] = i;
    long pidx = 0;          // global chunk counter: chunks of 2^22 subspaces are dealt round-robin to slices
    while (1) {
        {
            // free positions: for row i, columns > piv[i] that are not pivots
            int fr[8][32], nf[8], tot = 0;
            for (int i = 0; i < q; i++) {
                nf[i] = 0;
                for (int c = piv[i] + 1; c < m; c++) {
                    int isp = 0;
                    for (int j = 0; j < q; j++) if (piv[j] == c) isp = 1;
                    if (!isp) fr[i][nf[i]++] = c;
                }
                tot += nf[i];
            }
            uint64_t span = 1ULL << tot, CH = 1ULL << 22;
            for (uint64_t c0 = 0; c0 < span; c0 += CH, pidx++) {
              if (pidx % M != I) continue;
              uint64_t c1 = c0 + CH < span ? c0 + CH : span;
              for (uint64_t bits = c0; bits < c1; bits++) {
                uint32_t rows[8];
                uint64_t b = bits;
                for (int i = 0; i < q; i++) {
                    uint32_t r = 1u << piv[i];
                    for (int t = 0; t < nf[i]; t++) { if (b & 1) r |= 1u << fr[i][t]; b >>= 1; }
                    rows[i] = r;
                }
                total++;
                int hit = 0;
                for (int s = 0; s < k; s++) if (det(rows, S[s])) { perout[s]++; hit = 1; if (!PEROUT) break; }
                if (!hit) harmless++;
              }
            }
        }
        // next combination
        int i = q - 1;
        while (i >= 0 && piv[i] == m - q + i) i--;
        if (i < 0) break;
        piv[i]++;
        for (int j = i + 1; j < q; j++) piv[j] = piv[j - 1] + 1;
    }
    uint64_t mn = perout[0], mx = perout[0];
    for (int s = 0; s < k; s++) { if (perout[s] < mn) mn = perout[s]; if (perout[s] > mx) mx = perout[s]; }
    printf("{\"m\": %d, \"q\": %d, \"k\": %d, \"slice\": [%d, %d], \"subspaces\": %llu, \"harmless\": %llu, "
           "\"harmful\": %llu, \"per_output_min\": %llu, \"per_output_max\": %llu}\n",
           m, q, k, I, M, (unsigned long long)total, (unsigned long long)harmless,
           (unsigned long long)(total - harmless), (unsigned long long)mn, (unsigned long long)mx);
    return 0;
}
