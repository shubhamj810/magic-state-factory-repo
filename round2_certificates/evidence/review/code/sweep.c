/* Independent exhaustive check that no nonempty set of at most 2a columns has zero (projected) syndrome,
 * optionally also no set of 2a+1 columns.
 *
 * Input file: uint32 n, then n uint64 projected syndromes (a linear map of the true check syndromes to 64 bits,
 * so equal true syndromes give equal projections; a projected collision is re-checked exactly in Python).
 *
 *   sweep dist FILE a BUCKETBITS        all subsets of size 0..a, bucketed by top bits; report every value
 *                                       that occurs twice (=> a zero-syndrome set of size <= 2a, or a
 *                                       projection collision).
 *   sweep odd FILE a                    table of subsets of size 0..a (must fit in memory, no buckets),
 *                                       then every (a+1)-subset is looked up; report hits (=> a zero-syndrome
 *                                       set of size <= 2a+1).
 *   sweep find FILE a VALUE...          print every subset of size 0..a whose value is one of VALUE (hex).
 *   sweep find1 FILE a VALUE...         same for subsets of size exactly a+1.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t *S;
static uint32_t n;

static void load(const char *path) {
    FILE *f = fopen(path, "rb");
    if (!f) { perror("open"); exit(1); }
    if (fread(&n, 4, 1, f) != 1) exit(1);
    S = malloc(sizeof(uint64_t) * n);
    if (fread(S, 8, n, f) != n) exit(1);
    fclose(f);
}

static void radix(uint64_t *a, uint64_t *tmp, size_t m) {
    for (int sh = 0; sh < 64; sh += 8) {
        size_t cnt[257] = {0};
        for (size_t i = 0; i < m; i++) cnt[((a[i] >> sh) & 255) + 1]++;
        for (int b = 0; b < 256; b++) cnt[b + 1] += cnt[b];
        for (size_t i = 0; i < m; i++) tmp[cnt[(a[i] >> sh) & 255]++] = a[i];
        uint64_t *t = a; a = tmp; tmp = t;
    }
    /* 8 passes: even number, result is back in the original array */
}

typedef struct { uint64_t *v; size_t m, cap; } Vec;
static void push(Vec *x, uint64_t v) {
    if (x->m == x->cap) { x->cap = x->cap ? 2 * x->cap : (1 << 20); x->v = realloc(x->v, x->cap * 8); if (!x->v) { fprintf(stderr, "oom\n"); exit(2);} }
    x->v[x->m++] = v;
}

/* enumerate subsets of size 0..a (a <= 4); call f(value) */
#define ENUM(a, BODY) do { \
    uint64_t v; \
    v = 0; BODY; \
    if (a >= 1) for (uint32_t i = 0; i < n; i++) { uint64_t vi = S[i]; v = vi; BODY; \
      if (a >= 2) for (uint32_t j = i + 1; j < n; j++) { uint64_t vj = vi ^ S[j]; v = vj; BODY; \
        if (a >= 3) for (uint32_t l = j + 1; l < n; l++) { uint64_t vl = vj ^ S[l]; v = vl; BODY; \
          if (a >= 4) for (uint32_t q = l + 1; q < n; q++) { v = vl ^ S[q]; BODY; } } } } \
} while (0)

static int nt; static uint64_t *T;
static void rec(int depth, uint32_t from, uint64_t v, int a, uint32_t *idx) {
    for (uint32_t i = from; i < n; i++) {
        uint64_t w = v ^ S[i];
        idx[depth] = i;
        for (int t = 0; t < nt; t++) if (w == T[t]) {
            printf("SET %llx :", (unsigned long long)w);
            for (int u = 0; u <= depth; u++) printf(" %u", idx[u]);
            printf("\n");
        }
        if (depth + 1 < a) rec(depth + 1, i + 1, w, a, idx);
    }
}

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage\n"); return 1; }
    load(argv[2]);
    int a = atoi(argv[3]);
    if (!strcmp(argv[1], "dist")) {
        int bb = atoi(argv[4]);
        uint64_t nb = 1ULL << bb;
        unsigned long long total = 0, dups = 0;
        double tot = 1.0 + n + (double)n * (n - 1) / 2 + (a >= 3 ? (double)n * (n - 1) * (n - 2) / 6 : 0) + (a >= 4 ? (double)n * (n - 1) * (n - 2) * (n - 3) / 24 : 0);
        size_t cap = (size_t)(tot / nb * 1.05) + (1 << 20);
        uint64_t *buf = malloc(8 * cap), *tmp = malloc(8 * cap);
        if (!buf || !tmp) { fprintf(stderr, "oom\n"); return 2; }
        for (uint64_t p = 0; p < nb; p++) {
            size_t m = 0;
            int over = 0;
            ENUM(a, if ((v >> (64 - bb)) == p) { if (m < cap) buf[m++] = v; else over = 1; });
            if (over) { printf("OVERFLOW pass %llu\n", (unsigned long long)p); return 3; }
            radix(buf, tmp, m);
            for (size_t i = 1; i < m; i++)
                if (buf[i] == buf[i - 1]) {
                    dups++;
                    if (dups <= 1000000) printf("DUP %016llx\n", (unsigned long long)buf[i]);
                }
            total += m;
            fprintf(stderr, "pass %llu/%llu entries %zu\n", (unsigned long long)p, (unsigned long long)nb, m);
        }
        printf("TOTAL %llu DUPS %llu\n", total, dups);
    } else if (!strcmp(argv[1], "odd")) {
        Vec x = {0};
        ENUM(a, push(&x, v));
        uint64_t *tmp = malloc(8 * (x.m + 1));
        radix(x.v, tmp, x.m);
        free(tmp);
        unsigned long long dups = 0, hits = 0, q = 0;
        for (size_t i = 1; i < x.m; i++) if (x.v[i] == x.v[i - 1]) { dups++; if (dups <= 1000000) printf("DUP %016llx\n", (unsigned long long)x.v[i]); }
        int hb = 1; while ((1ULL << hb) < 2 * x.m + 16) hb++;
        uint64_t hmask = (1ULL << hb) - 1;
        uint64_t *H = calloc(1ULL << hb, 8);
        for (size_t i = 0; i < x.m; i++) { uint64_t v = x.v[i]; if (!v) continue;
            uint64_t h = (v * 0x9E3779B97F4A7C15ULL) >> (64 - hb);
            while (H[h] && H[h] != v) h = (h + 1) & hmask;
            H[h] = v; }
        free(x.v); x.v = 0;
        /* (a+1)-subsets */
        int b = a + 1;
        uint32_t idx[8];
        /* iterative combinations */
        for (int t = 0; t < b; t++) idx[t] = t;
        uint64_t pre[9];
        while (1) {
            pre[0] = 0;
            for (int t = 0; t < b; t++) pre[t + 1] = pre[t] ^ S[idx[t]];
            /* fast inner loop over last index */
                uint64_t base = pre[b - 1];
            for (uint32_t last = idx[b - 1]; last < n; last++) {
                uint64_t v = base ^ S[last];
                q++;
                int hit = 0;
                if (v == 0) hit = 1;
                else {
                    uint64_t h = (v * 0x9E3779B97F4A7C15ULL) >> (64 - hb);
                    while (H[h]) { if (H[h] == v) { hit = 1; break; } h = (h + 1) & hmask; }
                }
                if (hit) { hits++; if (hits <= 1000000) printf("HIT %016llx\n", (unsigned long long)v); }
            }
            /* advance idx[0..b-2] */
            int t = b - 2;
            while (t >= 0 && idx[t] == n - b + t) t--;
            if (t < 0) break;
            idx[t]++;
            for (int u = t + 1; u < b; u++) idx[u] = idx[u - 1] + 1;
        }
        printf("TABLE %zu DUPS %llu QUERIES %llu HITS %llu\n", x.m, dups, q, hits);
    } else if (!strcmp(argv[1], "find")) {
        /* every subset of size 1..a whose value is one of the targets */
        nt = argc - 4;
        T = malloc(8 * nt);
        for (int t = 0; t < nt; t++) T[t] = strtoull(argv[4 + t], 0, 16);
        uint32_t idx[16];
        rec(0, 0, 0, a, idx);
    }
    return 0;
}
