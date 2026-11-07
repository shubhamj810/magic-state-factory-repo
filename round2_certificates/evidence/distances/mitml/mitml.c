// mitml.c: exact sweep of one fault weight (w <= 8) with LINEAR partition keys.
//
// Same problem, split and output as research/plan/mitm/mitm.c (the pilot kernel), whose method this
// keeps: split w = a + b (a >= b); every accepted w-set S is found exactly C(w, a) times as a pair
// (A, B), A an a-subset, B = S \ A, with s(A) = s(B); the b-subsets are tabulated by their FULL
// syndrome (no false match, no missed match), one partition of syndrome space at a time.
//
// What changes is the partition key.  The pilot hashes the syndrome, so every partition enumerates
// all C(n, a) + C(n, b) subsets and keeps the 1/2^Q of them that land in it: a sweep costs 2^Q full
// enumerations.  Here the key is LINEAR: Q fixed linear functionals of the syndrome, so
// key(S) = XOR of the columns' keys.  A subset is in partition p exactly when its last column has
// key p ^ key(prefix), so the last column is drawn from a bucket of columns with that key; for m >= 3
// columns the last TWO are drawn from a list of pairs grouped by the XOR of their keys.  A sweep then
// costs about one enumeration plus 2^Q enumerations of the (m-2)-prefixes.  Equal syndromes
// still have equal keys, so equal-syndrome pairs always meet in the same partition.
//
// The table of a partition is built in two passes over its b-subsets (count per hash bucket, then
// place), so it needs no sort and no second copy.
//
// Usage: mitml FILE W [--count] [--parts Q] [--slice I M] [--list OUT] [--mem-mb MB] [--seed S]
//   FILE     binary: int32 n, int32 sw (<= SW), int32 ow (<= 8), then per column sw + ow uint64 words
//   W        weight to sweep (1..12; b = W/2 <= 6 columns are tabulated, a = W - b <= 6 are looked up)
//   --count  count every accepted and harmful w-set (default: stop at the first harmful one)
//   --parts  2^Q partitions (default: the smallest Q whose mean table fits in --mem-mb, default 2048)
//   --slice  only partitions p with p % M == I
//   --list   write every harmful w-set once (indices, ':' and the output xor in hex words); implies --count
//   --seed   seed of the Q functionals (any seed is exact; it only moves the partition sizes)
// Output: one JSON line.  Raw tallies of a slice are not divisible by C(w, a) in general (the splits
// of one set have different keys); an unsliced complete count asserts divisibility, a combiner sums
// the slices and asserts it on the sum.
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifndef SW
#define SW 3
#endif
#define OUTW 8
#define MAXB 6
typedef struct { uint64_t s[SW]; uint16_t ix[MAXB]; } Ent;

static int n, sw_file, ow;
static uint64_t *S, *O;            // S[j*SW + w], O[j*ow + w]
static uint32_t *KEY;              // per column linear key
static int W, A, B, Q = -1, SLICE_I = 0, SLICE_M = 1, COUNT = 0;
static long MEM_MB = 2048;
static uint64_t SEED = 0x5DEECE66DULL;
static FILE *LIST = NULL;
static uint64_t listed = 0, found_raw = 0, accepted_raw = 0;
static int witness[12], have_witness = 0, stop_now = 0;
static uint64_t max_part = 0, sum_part = 0;

// buckets of columns by key: BK[BOFF[v] .. BOFF[v+1]) sorted ascending
static uint32_t *BOFF; static uint16_t *BK;
// pairs x < y grouped by KEY[x] ^ KEY[y]: PX/PY[PGOFF[v] .. PGOFF[v+1]) sorted by x, then y
static uint32_t *PGOFF; static uint16_t *PX, *PY;

static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }

static uint64_t binom(int nn, int kk) {
    if (kk < 0 || kk > nn) return 0;
    uint64_t r = 1;
    for (int i = 1; i <= kk; i++) r = r * (uint64_t)(nn - kk + i) / (uint64_t)i;
    return r;
}

static uint64_t rng_state;
static uint64_t rng(void) {        // splitmix64
    uint64_t z = (rng_state += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL; z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

static inline uint64_t hash_s(const uint64_t *s) {
    uint64_t h = 0x632BE59BD9B4E019ULL;
    for (int w = 0; w < SW; w++) { h ^= s[w] * 0x9E3779B97F4A7C15ULL; h = (h ^ (h >> 29)) * 0xBF58476D1CE4E5B9ULL; }
    return h ^ (h >> 32);
}

// ------------------------------------------------------------------ the partition table
static Ent *tab = NULL; static size_t ntab = 0, captab = 0;
static uint32_t *hoff = NULL; static uint64_t hmask = 0; static size_t caph = 0;
static int pass;                   // 0: count per hash bucket, 1: place

static inline void tab_add(const uint64_t *s, const int *ix) {
    uint64_t h = hash_s(s) & hmask;
    if (pass == 0) { hoff[h + 1]++; ntab++; return; }
    Ent *e = &tab[hoff[h]++];
    for (int w = 0; w < SW; w++) e->s[w] = s[w];
    for (int i = 0; i < MAXB; i++) e->ix[i] = (uint16_t)(i < B ? ix[i] : 0xFFFF);
}

// enumerate m-subsets i0 < ... < i_{m-1} whose key is `part`, calling f(ix, syndrome, outxor-or-NULL)
typedef void (*visit_fn)(const int *ix, const uint64_t *s, const uint64_t *o);

static void enum_part(int m, uint32_t part, visit_fn f, int with_out) {
    int ix[8];
    uint64_t s[8][SW], o[8][OUTW];
    uint32_t k[8];
    memset(s[0], 0, sizeof s[0]); memset(o[0], 0, sizeof o[0]); k[0] = 0;
    // depth d holds the XOR of the first d chosen columns
    int d = 0;
    if (m == 1) {
        for (uint32_t t = BOFF[part]; t < BOFF[part + 1] && !stop_now; t++) {
            ix[0] = BK[t];
            f(ix, &S[(size_t)ix[0] * SW], with_out ? &O[(size_t)ix[0] * ow] : NULL);
        }
        return;
    }
    if (m >= 3) {
        // the first m-2 columns by nested loops, the last two from the pair group of key part ^ key(prefix)
        ix[0] = -1;
        while (d >= 0 && !stop_now) {
            ix[d]++;
            if (ix[d] > n - (m - d)) { d--; continue; }
            int j = ix[d];
            for (int w = 0; w < SW; w++) s[d + 1][w] = s[d][w] ^ S[(size_t)j * SW + w];
            if (with_out) for (int w = 0; w < ow; w++) o[d + 1][w] = o[d][w] ^ O[(size_t)j * ow + w];
            k[d + 1] = k[d] ^ KEY[j];
            if (d + 1 < m - 2) { d++; ix[d] = ix[d - 1]; continue; }
            uint32_t v = part ^ k[m - 2];
            uint32_t L = PGOFF[v], R = PGOFF[v + 1], hi = R;
            while (L < R) { uint32_t mid = (L + R) >> 1; if (PX[mid] <= j) L = mid + 1; else R = mid; }
            for (uint32_t t = L; t < hi && !stop_now; t++) {
                int x = PX[t], y = PY[t];
                ix[m - 2] = x; ix[m - 1] = y;
                uint64_t ss[SW], oo[OUTW];
                for (int w = 0; w < SW; w++) ss[w] = s[m - 2][w] ^ S[(size_t)x * SW + w] ^ S[(size_t)y * SW + w];
                if (with_out) for (int w = 0; w < ow; w++) oo[w] = o[m - 2][w] ^ O[(size_t)x * ow + w] ^ O[(size_t)y * ow + w];
                f(ix, ss, with_out ? oo : NULL);
            }
        }
        return;
    }
    // m == 2: the first column by a loop, the second from the bucket of key part ^ key(first)
    ix[0] = -1;
    while (d >= 0 && !stop_now) {
        ix[d]++;
        if (ix[d] > n - (m - d)) { d--; continue; }
        int j = ix[d];
        for (int w = 0; w < SW; w++) s[d + 1][w] = s[d][w] ^ S[(size_t)j * SW + w];
        if (with_out) for (int w = 0; w < ow; w++) o[d + 1][w] = o[d][w] ^ O[(size_t)j * ow + w];
        k[d + 1] = k[d] ^ KEY[j];
        if (d + 1 < m - 1) { d++; ix[d] = ix[d - 1]; continue; }
        // last column: key part ^ k[m-1], index > ix[m-2]
        uint32_t v = part ^ k[m - 1];
        uint32_t lo = BOFF[v], hi = BOFF[v + 1];
        // first entry > j (binary search)
        uint32_t L = lo, R = hi;
        while (L < R) { uint32_t mid = (L + R) >> 1; if (BK[mid] <= j) L = mid + 1; else R = mid; }
        for (uint32_t t = L; t < hi && !stop_now; t++) {
            int c = BK[t];
            ix[m - 1] = c;
            uint64_t ss[SW], oo[OUTW];
            for (int w = 0; w < SW; w++) ss[w] = s[m - 1][w] ^ S[(size_t)c * SW + w];
            if (with_out) for (int w = 0; w < ow; w++) oo[w] = o[m - 1][w] ^ O[(size_t)c * ow + w];
            f(ix, ss, with_out ? oo : NULL);
        }
    }
}

static void visit_b(const int *ix, const uint64_t *s, const uint64_t *o) { (void)o; tab_add(s, ix); }

static void visit_a(const int *ia, const uint64_t *s, const uint64_t *oa) {
    uint64_t h = hash_s(s) & hmask;
    for (uint32_t t = hoff[h]; t < hoff[h + 1]; t++) {
        const Ent *e = &tab[t];
        int eq = 1;
        for (int w = 0; w < SW; w++) if (e->s[w] != s[w]) { eq = 0; break; }
        if (!eq) continue;
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
        if (!nz) continue;
        found_raw++;
        if (LIST) {
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

static void build_table(uint32_t part) {
    // pass 0: count; size the hash array from the count
    pass = 0; ntab = 0;
    // a provisional mask is needed for counting: use the bucket count implied by the mean size
    // (counting with one mask and placing with another is wrong, so count twice if needed)
    for (;;) {
        memset(hoff, 0, (hmask + 2) * sizeof(uint32_t));
        ntab = 0;
        enum_part(B, part, visit_b, 0);
        if (ntab <= 2 * (hmask + 1) || hmask + 1 >= ((uint64_t)1 << 31)) break;
        // too full: grow the hash array and count again
        uint64_t slots = hmask + 1;
        while (slots < ntab) slots <<= 1;
        hmask = slots - 1;
        if (slots + 2 > caph) {
            caph = slots + 2;
            hoff = (uint32_t *)realloc(hoff, caph * sizeof(uint32_t));
            if (!hoff) { fprintf(stderr, "out of memory (hash)\n"); exit(3); }
        }
    }
    if (ntab > 0xFFFFFFF0ULL) { fprintf(stderr, "partition too large\n"); exit(3); }
    if (ntab > max_part) max_part = ntab;
    sum_part += ntab;
    for (uint64_t h = 0; h <= hmask; h++) hoff[h + 1] += hoff[h];
    if (ntab > captab) {
        captab = ntab + ntab / 8 + 16;
        free(tab);
        tab = (Ent *)malloc(captab * sizeof(Ent));
        if (!tab) { fprintf(stderr, "out of memory (table)\n"); exit(3); }
    }
    pass = 1;
    enum_part(B, part, visit_b, 0);
    // hoff[h] now holds the END of bucket h; shift back so bucket h is [hoff[h], hoff[h+1])
    for (uint64_t h = hmask + 1; h > 0; h--) hoff[h] = hoff[h - 1];
    hoff[0] = 0;
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: mitml FILE W [--count] [--parts Q] [--slice I M] [--list OUT] [--mem-mb MB] [--seed S]\n"); return 2; }
    for (int i = 3; i < argc; i++) {
        if (!strcmp(argv[i], "--count")) COUNT = 1;
        else if (!strcmp(argv[i], "--parts") && i + 1 < argc) Q = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--mem-mb") && i + 1 < argc) MEM_MB = atol(argv[++i]);
        else if (!strcmp(argv[i], "--seed") && i + 1 < argc) SEED = strtoull(argv[++i], NULL, 10);
        else if (!strcmp(argv[i], "--list") && i + 1 < argc) { LIST = fopen(argv[++i], "w"); COUNT = 1; if (!LIST) { perror("list"); return 2; } }
        else if (!strcmp(argv[i], "--slice") && i + 2 < argc) { SLICE_I = atoi(argv[++i]); SLICE_M = atoi(argv[++i]); }
        else { fprintf(stderr, "bad option %s\n", argv[i]); return 2; }
    }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror("open"); return 2; }
    int32_t hdr[3];
    if (fread(hdr, 4, 3, f) != 3) return 2;
    n = hdr[0]; sw_file = hdr[1]; ow = hdr[2];
    if (sw_file < 1 || sw_file > SW || ow < 1 || ow > OUTW || n < 1 || n > 65535) { fprintf(stderr, "bad header (sw %d > SW %d?)\n", sw_file, SW); return 2; }
    S = calloc((size_t)n * SW, 8); O = malloc((size_t)n * ow * 8); KEY = malloc((size_t)n * 4);
    for (int j = 0; j < n; j++) {
        uint64_t buf[16];
        if (fread(buf, 8, sw_file + ow, f) != (size_t)(sw_file + ow)) { fprintf(stderr, "short file\n"); return 2; }
        for (int w = 0; w < sw_file; w++) S[(size_t)j * SW + w] = buf[w];
        for (int w = 0; w < ow; w++) O[(size_t)j * ow + w] = buf[sw_file + w];
    }
    fclose(f);
    W = atoi(argv[2]);
    if (W < 1 || W > 12) { fprintf(stderr, "W must be 1..12\n"); return 2; }
    A = (W + 1) / 2; B = W / 2;
    double t0 = now();
    uint64_t nb = binom(n, B);
    if (W == 1) Q = 0;
    if (Q < 0) {
        uint64_t per = (uint64_t)MEM_MB * 1000000ULL / (sizeof(Ent) + 8);
        Q = 0;
        while ((nb >> Q) > per && Q < 20) Q++;
    }
    if (Q > 20) { fprintf(stderr, "Q too large\n"); return 2; }
    // Q random linear functionals of the syndrome
    rng_state = SEED;
    uint64_t R[20][SW];
    for (int q = 0; q < Q; q++) for (int w = 0; w < SW; w++) R[q][w] = rng();
    for (int j = 0; j < n; j++) {
        uint32_t key = 0;
        for (int q = 0; q < Q; q++) {
            uint64_t x = 0;
            for (int w = 0; w < SW; w++) x ^= S[(size_t)j * SW + w] & R[q][w];
            key |= (uint32_t)(__builtin_popcountll(x) & 1) << q;
        }
        KEY[j] = key;
    }
    uint32_t parts = 1u << Q;
    BOFF = calloc(parts + 1, 4); BK = malloc((size_t)n * 2);
    for (int j = 0; j < n; j++) BOFF[KEY[j] + 1]++;
    for (uint32_t v = 0; v < parts; v++) BOFF[v + 1] += BOFF[v];
    {
        uint32_t *fill = malloc((parts + 1) * 4); memcpy(fill, BOFF, (parts + 1) * 4);
        for (int j = 0; j < n; j++) BK[fill[KEY[j]]++] = (uint16_t)j;   // ascending j within a bucket
        free(fill);
    }
    if (W >= 5) {                      // some side has m >= 3 columns
        uint64_t np = (uint64_t)n * (n - 1) / 2;
        PGOFF = calloc(parts + 1, 4); PX = malloc(np * 2); PY = malloc(np * 2);
        if (!PGOFF || !PX || !PY) { fprintf(stderr, "out of memory (pairs)\n"); return 3; }
        for (int x = 0; x < n; x++) for (int y = x + 1; y < n; y++) PGOFF[(KEY[x] ^ KEY[y]) + 1]++;
        for (uint32_t v = 0; v < parts; v++) PGOFF[v + 1] += PGOFF[v];
        uint32_t *fill = malloc((parts + 1) * 4); memcpy(fill, PGOFF, (parts + 1) * 4);
        for (int x = 0; x < n; x++) for (int y = x + 1; y < n; y++) {
            uint32_t t = fill[KEY[x] ^ KEY[y]]++;
            PX[t] = (uint16_t)x; PY[t] = (uint16_t)y;
        }
        free(fill);
    }
    if (W == 1) {
        for (int j = 0; j < n && SLICE_I == 0; j++) {   // one partition: slice 0 holds it
            int z = 1;
            for (int w = 0; w < SW; w++) if (S[(size_t)j * SW + w]) z = 0;
            if (!z) continue;
            accepted_raw++;
            int nz = 0;
            for (int w = 0; w < ow; w++) if (O[(size_t)j * ow + w]) nz = 1;
            if (nz) { found_raw++; if (!have_witness) { witness[0] = j; have_witness = 1; } if (!COUNT) break; }
        }
    } else {
        uint64_t mean = (nb >> Q) + 1, slots = 1;
        while (slots < mean) slots <<= 1;
        hmask = slots - 1; caph = slots + 2;
        hoff = (uint32_t *)malloc(caph * sizeof(uint32_t));
        if (!hoff) { fprintf(stderr, "out of memory (hash)\n"); return 3; }
        for (uint32_t p = 0; p < parts && !stop_now; p++) {
            if ((int)(p % SLICE_M) != SLICE_I) continue;
            build_table(p);
            enum_part(A, p, visit_a, 1);
        }
    }
    double dt = now() - t0;
    uint64_t div = (W == 1) ? 1 : binom(W, A);
    int complete = !stop_now;
    printf("{\"kernel\": \"mitml-SW%d\", \"n\": %d, \"w\": %d, \"a\": %d, \"b\": %d, \"parts_log2\": %d, \"seed\": %llu, "
           "\"slice\": [%d, %d], \"count_mode\": %d, \"complete\": %d, \"harmful_raw\": %llu, \"accepted_raw\": %llu, "
           "\"divisor\": %llu, \"table_max\": %llu, \"table_sum\": %llu, ",
           SW, n, W, A, B, Q, (unsigned long long)SEED, SLICE_I, SLICE_M, COUNT, complete,
           (unsigned long long)found_raw, (unsigned long long)accepted_raw, (unsigned long long)div,
           (unsigned long long)max_part, (unsigned long long)sum_part);
    if (COUNT && complete && SLICE_M == 1) {
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
