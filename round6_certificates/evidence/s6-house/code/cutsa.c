// cutsa.c: simulated annealing on a column order to lower its cut rank (max over t of
// rank(G[:, :t]) + rank(G[:, t:]) - rank(G)), the quantity that sets the size of tropidist's dense DP table.
// Objective, lexicographic: the maximum, the number of cuts at the maximum, the sum of the profile.
//
// input (text): n N, then n lines "len w1 w2 ...", then the starting order (n integers).
// usage: cutsa IN SEED SECONDS > OUT    (OUT: the best order found, then "score max nmax sum")
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#define WMAX 8
static int n, N, NW;
static uint64_t *V;     // n x NW

static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }
static uint64_t rs;
static uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }

static void ranks(const int *ord, int *out, int rev) {
    static uint64_t basis[512][WMAX]; static int has[512];
    memset(has, 0, sizeof has);
    int r = 0; out[0] = 0;
    for (int t = 0; t < n; t++) {
        int c = rev ? ord[n - 1 - t] : ord[t];
        uint64_t x[WMAX]; memcpy(x, &V[(size_t)c * NW], NW * 8);
        for (int wi = NW - 1; wi >= 0; wi--) {
            while (x[wi]) {
                int p = wi * 64 + 63 - __builtin_clzll(x[wi]);
                if (!has[p]) { memcpy(basis[p], x, NW * 8); has[p] = 1; r++; goto done; }
                for (int k = 0; k <= wi; k++) x[k] ^= basis[p][k];
            }
        }
    done:
        out[t + 1] = r;
    }
}

static void score(const int *ord, long *sc) {
    static int pre[70000], suf[70000];
    ranks(ord, pre, 0); ranks(ord, suf, 1);
    int tot = pre[n], mx = 0, nmx = 0; long sum = 0;
    for (int t = 0; t <= n; t++) {
        int v = pre[t] + suf[n - t] - tot;
        sum += v;
        if (v > mx) { mx = v; nmx = 1; } else if (v == mx) nmx++;
    }
    sc[0] = mx; sc[1] = nmx; sc[2] = sum;
}
static double val(const long *s) { return s[0] * 1e7 + s[1] * 1e3 + s[2] * 1e-2; }

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r");
    if (!f || fscanf(f, "%d %d", &n, &N) != 2) return 2;
    NW = (N + 63) / 64;
    if (NW > WMAX || N > 512) return 2;
    V = calloc((size_t)n * NW, 8);
    for (int j = 0; j < n; j++) {
        int len; if (fscanf(f, "%d", &len) != 1) return 2;
        for (int i = 0; i < len; i++) { int q; if (fscanf(f, "%d", &q) != 1) return 2; V[(size_t)j * NW + q / 64] |= 1ULL << (q % 64); }
    }
    int *ord = malloc(n * sizeof(int)), *best = malloc(n * sizeof(int)), *cand = malloc(n * sizeof(int));
    for (int j = 0; j < n; j++) if (fscanf(f, "%d", &ord[j]) != 1) return 2;
    fclose(f);
    rs = strtoull(argv[2], NULL, 10) * 0x9E3779B97F4A7C15ULL + 3;
    double secs = atof(argv[3]), t0 = now();
    long cs[3], bs[3], s[3];
    score(ord, cs); memcpy(bs, cs, sizeof cs); memcpy(best, ord, n * sizeof(int));
    fprintf(stderr, "start %ld %ld %ld\n", cs[0], cs[1], cs[2]);
    long it = 0;
    while (now() - t0 < secs) {
        it++;
        double frac = (now() - t0) / secs, T = 3e3 * (1 - frac) + 1;
        memcpy(cand, ord, n * sizeof(int));
        int i = rnd() % n, span = 1 + rnd() % 40, j = i + (int)(rnd() % (2 * span + 1)) - span;
        if (j < 0) j = 0; if (j >= n) j = n - 1;
        if (rnd() & 1) { int x = cand[i]; cand[i] = cand[j]; cand[j] = x; }
        else { int x = cand[i]; if (i < j) memmove(&cand[i], &cand[i + 1], (j - i) * sizeof(int)); else memmove(&cand[j + 1], &cand[j], (i - j) * sizeof(int)); cand[j] = x; }
        score(cand, s);
        double d = val(s) - val(cs);
        if (d <= 0 || (double)(rnd() % 1000000) / 1e6 < __builtin_exp(-d / T)) {
            memcpy(ord, cand, n * sizeof(int)); memcpy(cs, s, sizeof s);
            if (val(s) < val(bs)) { memcpy(bs, s, sizeof s); memcpy(best, cand, n * sizeof(int)); }
        }
    }
    for (int j = 0; j < n; j++) printf("%d%c", best[j], j + 1 < n ? ' ' : '\n');
    printf("score %ld %ld %ld\n", bs[0], bs[1], bs[2]);
    fprintf(stderr, "best %ld %ld %ld after %ld moves\n", bs[0], bs[1], bs[2], it);
    return 0;
}
