/* Harmful-fault sweep to weight 2a for circuits with many harmless accepted sets (e.g. San Jose binary images).
 * Input: uint32 n, then n pairs (uint64 projected syndrome, uint64 projected output part).
 * All subsets of size 0..a (a <= 3) are bucketed by the top bits of the syndrome projection and sorted by
 * (syndrome, output).  Two subsets with equal syndrome and different outputs give a zero-syndrome set of size
 * <= 2a that flips outputs (a harmful candidate, re-checked exactly by the caller); equal syndrome and equal
 * output is a harmless accepted set (or a set counted twice).
 *   harm FILE a BUCKETBITS
 * prints "H i.. | j.." for up to 200 harmful candidates, then "SUMMARY entries E harmless_pairs X harmful_groups G".
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct { uint64_t s, o, sub; } E;
static uint32_t n;
static uint64_t *S, *O;

static int cmp(const void *x, const void *y) {
    const E *a = x, *b = y;
    if (a->s != b->s) return a->s < b->s ? -1 : 1;
    if (a->o != b->o) return a->o < b->o ? -1 : 1;
    return 0;
}
static void prsub(uint64_t s) {
    for (int t = 0; t < 3; t++) { uint64_t x = (s >> (21 * t)) & 0x1FFFFF; if (x) printf(" %llu", (unsigned long long)(x - 1)); }
}

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "rb");
    int a = atoi(argv[2]), bb = atoi(argv[3]);
    if (fread(&n, 4, 1, f) != 1) return 1;
    S = malloc(8 * n); O = malloc(8 * n);
    for (uint32_t i = 0; i < n; i++) { if (fread(&S[i], 8, 1, f) != 1 || fread(&O[i], 8, 1, f) != 1) return 1; }
    fclose(f);
    double tot = 1.0 + n + (double)n * (n - 1) / 2 + (a >= 3 ? (double)n * (n - 1) * (n - 2) / 6 : 0);
    uint64_t nb = 1ULL << bb;
    size_t cap = (size_t)(tot / nb * 1.10) + (1 << 20);
    E *buf = malloc(sizeof(E) * cap);
    unsigned long long entries = 0, harmless = 0, harmful = 0;
    for (uint64_t p = 0; p < nb; p++) {
        size_t m = 0;
#define PUT(sv, ov, sb) do { if (((sv) >> (64 - bb)) == p) { if (m >= cap) { printf("OVERFLOW\n"); return 3; } buf[m].s = (sv); buf[m].o = (ov); buf[m].sub = (sb); m++; } } while (0)
        PUT(0ULL, 0ULL, 0ULL);
        for (uint32_t i = 0; i < n; i++) {
            PUT(S[i], O[i], (uint64_t)(i + 1));
            if (a >= 2) for (uint32_t j = i + 1; j < n; j++) {
                uint64_t sj = S[i] ^ S[j], oj = O[i] ^ O[j];
                PUT(sj, oj, (uint64_t)(i + 1) | ((uint64_t)(j + 1) << 21));
                if (a >= 3) for (uint32_t l = j + 1; l < n; l++)
                    PUT(sj ^ S[l], oj ^ O[l], (uint64_t)(i + 1) | ((uint64_t)(j + 1) << 21) | ((uint64_t)(l + 1) << 42));
            }
        }
        qsort(buf, m, sizeof(E), cmp);
        size_t g0 = 0;
        for (size_t i = 1; i <= m; i++) {
            if (i == m || buf[i].s != buf[g0].s) {
                if (i - g0 > 1) {
                    if (buf[i - 1].o != buf[g0].o) {
                        harmful++;
                        if (harmful <= 200) { printf("H"); prsub(buf[g0].sub); printf(" |"); prsub(buf[i - 1].sub); printf("\n"); }
                    }
                    for (size_t j = g0 + 1; j < i; j++) if (buf[j].o == buf[j - 1].o) harmless++;
                }
                g0 = i;
            }
        }
        entries += m;
        fprintf(stderr, "pass %llu entries %zu\n", (unsigned long long)p, m);
    }
    printf("SUMMARY entries %llu harmless_pairs %llu harmful_groups %llu\n", entries, harmless, harmful);
    return 0;
}
