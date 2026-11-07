// Exact sweep of one fault weight for a factory with at most 128 check wires: a pilot.
//
// Problem: columns j = 0..n-1, each with a check part s_j (r <= 128 bits, two words) and an output
// part o_j (k <= 512 bits, eight words).  A set F of w distinct columns is ACCEPTED when the XOR of
// its s_j is zero, and HARMFUL when it is accepted and the XOR of its o_j is non-zero.
//
// Method: split w = a + b (a >= b).  Every accepted w-set S is found exactly C(w, a) times as a pair
// (A, B), A an a-subset, B = S \ A, with s(A) = s(B).  The b-subsets are tabulated by their FULL
// syndrome (no hashing of the syndrome itself, so no false negative and no false positive), one
// partition of syndrome space at a time to bound memory; the a-subsets of the same partition are
// looked up.  The partition key is a function of the full syndrome, so equal syndromes always meet.
// Raw tallies are divided by C(w, a), and the division is asserted exact.
//
// Usage: mitm FILE W [--count] [--parts Q] [--slice I M] [--list OUT]
//   FILE    binary: int32 n, int32 sw (=2), int32 ow (<=8), then per column sw + ow uint64 words
//   W       weight to sweep (1..7)
//   --count count every accepted and harmful w-set (default: stop at the first harmful one)
//   --parts 2^Q partitions (default chosen from memory)
//   --slice only partitions p with p % M == I (several processes share one sweep)
//   --list  write every harmful w-set once (indices, then ':' and the output xor in hex words); implies --count
// Output: one JSON line.
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define OUTW 8
typedef struct { uint64_t s0, s1; uint16_t ix[4]; } Ent;   // b <= 4

static int n, sw, ow;
static uint64_t *S0, *S1, *O;     // per column
static int W, A, B, Q = -1, SLICE_I = 0, SLICE_M = 1, COUNT = 0;
static FILE *LIST = NULL;      // --list FILE: every harmful w-set once (canonical split), with its output xor
static uint64_t listed = 0;
static uint64_t found_raw = 0, accepted_raw = 0;
static int witness[8], have_witness = 0;

static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }

static inline uint32_t key_of(uint64_t s0, uint64_t s1, int q) {
    if (q == 0) return 0;
    uint64_t h = s0 * 0x9E3779B97F4A7C15ULL ^ (s1 + 0x632BE59BD9B4E019ULL) * 0xC2B2AE3D27D4EB4FULL;
    h ^= h >> 29; h *= 0xBF58476D1CE4E5B9ULL; h ^= h >> 32;
    return (uint32_t)(h >> (64 - q));
}

static int cmp_ent(const void *x, const void *y) {
    const Ent *a = (const Ent *)x, *b = (const Ent *)y;
    if (a->s0 != b->s0) return a->s0 < b->s0 ? -1 : 1;
    if (a->s1 != b->s1) return a->s1 < b->s1 ? -1 : 1;
    return 0;
}

static uint64_t binom(int nn, int kk) {
    if (kk < 0 || kk > nn) return 0;
    uint64_t r = 1;
    for (int i = 1; i <= kk; i++) r = r * (uint64_t)(nn - kk + i) / (uint64_t)i;
    return r;
}

// table of the current partition
static Ent *tab = NULL;
static size_t ntab = 0, captab = 0;
// open addressing index over the sorted table: slot -> (first position + 1, run length); keys are
// compared against the table itself, so a slot costs 8 bytes
static uint32_t *hpos, *hcnt; static size_t hmask;

static void tab_push(uint64_t s0, uint64_t s1, const int *ix) {
    if (ntab == captab) {
        captab = captab ? captab * 2 : (1 << 20);
        tab = (Ent *)realloc(tab, captab * sizeof(Ent));
        if (!tab) { fprintf(stderr, "out of memory\n"); exit(3); }
    }
    Ent *e = &tab[ntab++];
    e->s0 = s0; e->s1 = s1;
    for (int i = 0; i < 4; i++) e->ix[i] = (uint16_t)(i < B ? ix[i] : 0xFFFF);
}

static inline size_t slot_of(uint64_t s0, uint64_t s1) {
    uint64_t h = (s0 * 0xD6E8FEB86659FD93ULL ^ s1 * 0x9E3779B97F4A7C15ULL);
    h ^= h >> 31;
    return h & hmask;
}

static void build_index(void) {
    size_t slots = 1;
    while (slots < 2 * ntab + 2) slots <<= 1;
    hmask = slots - 1;
    hpos = (uint32_t *)calloc(slots, 4); hcnt = (uint32_t *)calloc(slots, 4);
    if (!hpos || !hcnt) { fprintf(stderr, "out of memory (index)\n"); exit(3); }
    size_t i = 0;
    while (i < ntab) {
        size_t j = i;
        while (j < ntab && tab[j].s0 == tab[i].s0 && tab[j].s1 == tab[i].s1) j++;
        size_t p = slot_of(tab[i].s0, tab[i].s1);
        while (hpos[p]) p = (p + 1) & hmask;
        hpos[p] = (uint32_t)(i + 1); hcnt[p] = (uint32_t)(j - i);
        i = j;
    }
}

static void free_index(void) { free(hpos); free(hcnt); }

static inline int lookup(uint64_t s0, uint64_t s1, uint32_t *pos) {
    size_t p = slot_of(s0, s1);
    while (hpos[p]) {
        const Ent *e = &tab[hpos[p] - 1];
        if (e->s0 == s0 && e->s1 == s1) { *pos = hpos[p] - 1; return (int)hcnt[p]; }
        p = (p + 1) & hmask;
    }
    return 0;
}

static int stop_now = 0;

// a-subset `ia` (sorted) with syndrome (s0, s1) and output xor `oa`: join against the table
static inline void join(const int *ia, uint64_t s0, uint64_t s1, const uint64_t *oa) {
    uint32_t pos;
    int cnt = lookup(s0, s1, &pos);
    for (int t = 0; t < cnt; t++) {
        const Ent *e = &tab[pos + t];
        int clash = 0;
        for (int x = 0; x < B && !clash; x++)
            for (int y = 0; y < A; y++)
                if (e->ix[x] == ia[y]) { clash = 1; break; }
        if (clash) continue;
        accepted_raw++;
        int nz = 0;
        uint64_t ox[OUTW];
        for (int w = 0; w < ow; w++) {
            uint64_t v = oa[w];
            for (int x = 0; x < B; x++) v ^= O[(size_t)e->ix[x] * ow + w];
            ox[w] = v;
            if (v) nz = 1;
        }
        if (nz) {
            found_raw++;
            if (LIST) {
                // the canonical split: A holds the a smallest indices of the set
                int amax = ia[A - 1], bmin = e->ix[0];
                for (int x = 1; x < B; x++) if (e->ix[x] < bmin) bmin = e->ix[x];
                if (amax < bmin) {
                    for (int y = 0; y < A; y++) fprintf(LIST, "%d ", ia[y]);
                    for (int x = 0; x < B; x++) fprintf(LIST, "%d ", e->ix[x]);
                    fprintf(LIST, ":");
                    for (int w = 0; w < ow; w++) fprintf(LIST, " %016llx", (unsigned long long)ox[w]);
                    fprintf(LIST, "\n");
                    listed++;
                }
            }
            if (!have_witness) {
                for (int y = 0; y < A; y++) witness[y] = ia[y];
                for (int x = 0; x < B; x++) witness[A + x] = e->ix[x];
                have_witness = 1;
            }
            if (!COUNT) { stop_now = 1; return; }
        }
    }
}

// enumerate all m-subsets (m <= 4) by nested loops with incremental XOR, calling f
static void enum_b(uint32_t part, int q) {
    int ix[4];
    if (B == 0) return;
    for (ix[0] = 0; ix[0] < n; ix[0]++) {
        uint64_t a0 = S0[ix[0]], a1 = S1[ix[0]];
        if (B == 1) { if (key_of(a0, a1, q) == part) tab_push(a0, a1, ix); continue; }
        for (ix[1] = ix[0] + 1; ix[1] < n; ix[1]++) {
            uint64_t b0 = a0 ^ S0[ix[1]], b1 = a1 ^ S1[ix[1]];
            if (B == 2) { if (key_of(b0, b1, q) == part) tab_push(b0, b1, ix); continue; }
            for (ix[2] = ix[1] + 1; ix[2] < n; ix[2]++) {
                uint64_t c0 = b0 ^ S0[ix[2]], c1 = b1 ^ S1[ix[2]];
                if (B == 3) { if (key_of(c0, c1, q) == part) tab_push(c0, c1, ix); continue; }
                for (ix[3] = ix[2] + 1; ix[3] < n; ix[3]++) {
                    uint64_t d0 = c0 ^ S0[ix[3]], d1 = c1 ^ S1[ix[3]];
                    if (key_of(d0, d1, q) == part) tab_push(d0, d1, ix);
                }
            }
        }
    }
}

static void enum_a(uint32_t part, int q) {
    int ix[4];
    uint64_t o[4][OUTW];
    for (ix[0] = 0; ix[0] < n && !stop_now; ix[0]++) {
        uint64_t a0 = S0[ix[0]], a1 = S1[ix[0]];
        for (int w = 0; w < ow; w++) o[0][w] = O[(size_t)ix[0] * ow + w];
        if (A == 1) { if (key_of(a0, a1, q) == part) join(ix, a0, a1, o[0]); continue; }
        for (ix[1] = ix[0] + 1; ix[1] < n && !stop_now; ix[1]++) {
            uint64_t b0 = a0 ^ S0[ix[1]], b1 = a1 ^ S1[ix[1]];
            if (A == 2) {
                if (key_of(b0, b1, q) == part) {
                    for (int w = 0; w < ow; w++) o[1][w] = o[0][w] ^ O[(size_t)ix[1] * ow + w];
                    join(ix, b0, b1, o[1]);
                }
                continue;
            }
            for (int w = 0; w < ow; w++) o[1][w] = o[0][w] ^ O[(size_t)ix[1] * ow + w];
            for (ix[2] = ix[1] + 1; ix[2] < n && !stop_now; ix[2]++) {
                uint64_t c0 = b0 ^ S0[ix[2]], c1 = b1 ^ S1[ix[2]];
                if (A == 3) {
                    if (key_of(c0, c1, q) == part) {
                        for (int w = 0; w < ow; w++) o[2][w] = o[1][w] ^ O[(size_t)ix[2] * ow + w];
                        join(ix, c0, c1, o[2]);
                    }
                    continue;
                }
                for (int w = 0; w < ow; w++) o[2][w] = o[1][w] ^ O[(size_t)ix[2] * ow + w];
                for (ix[3] = ix[2] + 1; ix[3] < n && !stop_now; ix[3]++) {
                    uint64_t d0 = c0 ^ S0[ix[3]], d1 = c1 ^ S1[ix[3]];
                    if (key_of(d0, d1, q) == part) {
                        for (int w = 0; w < ow; w++) o[3][w] = o[2][w] ^ O[(size_t)ix[3] * ow + w];
                        join(ix, d0, d1, o[3]);
                    }
                }
            }
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: mitm FILE W [--count] [--parts Q] [--slice I M]\n"); return 2; }
    for (int i = 3; i < argc; i++) {
        if (!strcmp(argv[i], "--count")) COUNT = 1;
        else if (!strcmp(argv[i], "--parts") && i + 1 < argc) Q = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--list") && i + 1 < argc) { LIST = fopen(argv[++i], "w"); COUNT = 1; if (!LIST) { perror("list"); return 2; } }
        else if (!strcmp(argv[i], "--slice") && i + 2 < argc) { SLICE_I = atoi(argv[++i]); SLICE_M = atoi(argv[++i]); }
        else { fprintf(stderr, "bad option %s\n", argv[i]); return 2; }
    }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror("open"); return 2; }
    int32_t hdr[3];
    if (fread(hdr, 4, 3, f) != 3) return 2;
    n = hdr[0]; sw = hdr[1]; ow = hdr[2];
    if (sw != 2 || ow < 1 || ow > OUTW || n < 1 || n > 65535) { fprintf(stderr, "bad header\n"); return 2; }
    S0 = malloc(n * 8); S1 = malloc(n * 8); O = malloc((size_t)n * ow * 8);
    for (int j = 0; j < n; j++) {
        uint64_t buf[2 + OUTW];
        if (fread(buf, 8, 2 + ow, f) != (size_t)(2 + ow)) { fprintf(stderr, "short file\n"); return 2; }
        S0[j] = buf[0]; S1[j] = buf[1];
        for (int w = 0; w < ow; w++) O[(size_t)j * ow + w] = buf[2 + w];
    }
    fclose(f);
    W = atoi(argv[2]);
    if (W < 1 || W > 8) { fprintf(stderr, "W must be 1..8\n"); return 2; }
    A = (W + 1) / 2; B = W / 2;
    double t0 = now();
    if (W == 1) {
        for (int j = 0; j < n; j++) {
            if (S0[j] == 0 && S1[j] == 0) {
                accepted_raw++;
                int nz = 0;
                for (int w = 0; w < ow; w++) if (O[(size_t)j * ow + w]) nz = 1;
                if (nz) { found_raw++; if (!have_witness) { witness[0] = j; have_witness = 1; } }
            }
        }
    } else {
        if (B > 4 || A > 4) { fprintf(stderr, "W up to 8\n"); return 2; }
        uint64_t nb = binom(n, B);
        if (Q < 0) {                               // about 2^25 table entries per partition (~1.3 GB with the index)
            Q = 0;
            while ((nb >> Q) > (1ULL << 25)) Q++;
        }
        uint32_t parts = 1u << Q;
        for (uint32_t p = 0; p < parts && !stop_now; p++) {
            if ((int)(p % SLICE_M) != SLICE_I) continue;
            ntab = 0;
            enum_b(p, Q);
            qsort(tab, ntab, sizeof(Ent), cmp_ent);
            build_index();
            enum_a(p, Q);
            free_index();
        }
    }
    double dt = now() - t0;
    uint64_t div = (W == 1) ? 1 : binom(W, A);
    int complete = !stop_now;
    printf("{\"n\": %d, \"w\": %d, \"a\": %d, \"b\": %d, \"parts_log2\": %d, \"slice\": [%d, %d], \"count_mode\": %d, "
           "\"complete\": %d, \"harmful_raw\": %llu, \"accepted_raw\": %llu, \"divisor\": %llu, ",
           n, W, A, B, Q < 0 ? 0 : Q, SLICE_I, SLICE_M, COUNT, complete,
           (unsigned long long)found_raw, (unsigned long long)accepted_raw, (unsigned long long)div);
    if (COUNT && complete) {
        if (found_raw % div || accepted_raw % div) { printf("\"error\": \"tally not divisible\"}\n"); return 4; }
        printf("\"harmful\": %llu, \"accepted\": %llu, ", (unsigned long long)(found_raw / div),
               (unsigned long long)(accepted_raw / div));
    }
    if (LIST) { fclose(LIST); printf("\"listed\": %llu, ", (unsigned long long)listed); }
    printf("\"status\": \"%s\", \"witness\": [", have_witness ? "found" : (complete ? "clean" : "stopped"));
    if (have_witness) for (int i = 0; i < W; i++) printf("%s%d", i ? ", " : "", witness[i]);
    printf("], \"seconds\": %.3f}\n", dt);
    return 0;
}
