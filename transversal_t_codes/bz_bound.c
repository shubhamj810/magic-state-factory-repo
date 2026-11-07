/* bz_bound.c: list every word of a binary code with at most t ones on one
 * information set, and report the lightest.  The C half of
 * min_distance.py's Brouwer-Zimmermann bound, for codes too long for numpy.
 *
 *     cc -O3 -o bz_bound bz_bound.c -lpthread
 *     ./bz_bound INPUT THREADS [LOG]
 *
 * INPUT is the text file min_distance.write_side writes:
 *
 *     K W T
 *     K lines of W hexadecimal 64-bit words
 *
 * Line i is row i of a generator matrix in systematic form on an information
 * set S, restricted to the coordinates outside S (packed W words per row,
 * coordinate j at bit j % 64 of word j / 64).  Row i has a single 1 on S, so
 * the sum of the rows in a set I of size w has weight w + popcount(XOR of
 * their parts), and every codeword with exactly w ones on S is one such sum.
 * The program forms the sums of every set of 1 to T rows, each once, by a
 * depth-first walk in which a child is its parent XOR one row.  It prints one
 * JSON object: the number of sums formed (``nodes``, which must equal the sum
 * of C(K, w) for w = 1..T, also printed), the lightest weight met, how many
 * sums have it, and one such set of rows.
 *
 * The work is split into one task per pair of first rows (i1 < i2), handed
 * out to THREADS threads in order; the K one-row sums are formed first.  With
 * LOG, each finished task appends a line "task nodes lightest count rows..."
 * and a restarted run skips the tasks the log lists, so a run can be stopped
 * and resumed without losing finished work.  The final object is the same
 * either way.
 */
#include <inttypes.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXW 4
#define MAXK 128
#define MAXT 32

static int K, W, T;
static uint64_t R[MAXK][MAXW];
static int npairs;
static int *pair_a, *pair_b;
static unsigned char *done_task;
static int next_task = 0;
static pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
static FILE *logf = NULL;

typedef struct {
    uint64_t nodes;
    int best;
    uint64_t count;
    int witness[MAXT];
    int wlen;
} Result;

static void result_init(Result *r) {
    r->nodes = 0;
    r->best = 1 << 30;
    r->count = 0;
    r->wlen = 0;
}

static void result_merge(Result *into, const Result *r) {
    into->nodes += r->nodes;
    if (r->count == 0)
        return;
    if (r->best < into->best) {
        into->best = r->best;
        into->count = r->count;
        into->wlen = r->wlen;
        memcpy(into->witness, r->witness, sizeof(int) * (size_t)r->wlen);
    } else if (r->best == into->best) {
        into->count += r->count;
    }
}

static inline int popc(const uint64_t *v) {
    int s = 0;
    for (int j = 0; j < W; j++)
        s += __builtin_popcountll(v[j]);
    return s;
}

static inline void meet(Result *res, int weight, const int *stack, int len) {
    if (weight < res->best) {
        res->best = weight;
        res->count = 1;
        res->wlen = len;
        memcpy(res->witness, stack, sizeof(int) * (size_t)len);
    } else if (weight == res->best) {
        res->count++;
    }
}

/* Every set extending stack[0..depth-1] by rows start..K-1, up to size T. */
static void walk(int start, int depth, const uint64_t *acc, int *stack,
                 Result *res) {
    uint64_t v[MAXW];
    int size = depth + 1;
    if (size == T) {               /* the last level: no recursion */
        for (int i = start; i < K; i++) {
            int s = 0;
            for (int j = 0; j < W; j++)
                s += __builtin_popcountll(acc[j] ^ R[i][j]);
            res->nodes++;
            if (s + size <= res->best) {
                stack[depth] = i;
                meet(res, s + size, stack, size);
            }
        }
        return;
    }
    for (int i = start; i < K; i++) {
        for (int j = 0; j < W; j++)
            v[j] = acc[j] ^ R[i][j];
        res->nodes++;
        stack[depth] = i;
        int s = popc(v) + size;
        if (s <= res->best)
            meet(res, s, stack, size);
        walk(i + 1, size, v, stack, res);
    }
}

static void run_task(int task, Result *res) {
    int a = pair_a[task], b = pair_b[task];
    uint64_t v[MAXW];
    int stack[MAXT];
    for (int j = 0; j < W; j++)
        v[j] = R[a][j] ^ R[b][j];
    stack[0] = a;
    stack[1] = b;
    res->nodes++;
    meet(res, popc(v) + 2, stack, 2);
    if (T > 2)
        walk(b + 1, 2, v, stack, res);
}

static Result total;

static void *worker(void *arg) {
    (void)arg;
    for (;;) {
        int task;
        pthread_mutex_lock(&lock);
        while (next_task < npairs && done_task[next_task])
            next_task++;
        task = next_task < npairs ? next_task++ : -1;
        pthread_mutex_unlock(&lock);
        if (task < 0)
            return NULL;
        Result r;
        result_init(&r);
        run_task(task, &r);
        pthread_mutex_lock(&lock);
        result_merge(&total, &r);
        if (logf) {
            fprintf(logf, "%d %" PRIu64 " %d %" PRIu64, task, r.nodes, r.best,
                    r.count);
            for (int i = 0; i < r.wlen; i++)
                fprintf(logf, " %d", r.witness[i]);
            fprintf(logf, "\n");
            fflush(logf);
        }
        pthread_mutex_unlock(&lock);
    }
}

static uint64_t binom(int n, int k) {
    uint64_t c = 1;
    for (int i = 1; i <= k; i++)
        c = c * (uint64_t)(n - k + i) / (uint64_t)i;   /* exact at each step */
    return c;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "usage: %s INPUT THREADS [LOG]\n", argv[0]);
        return 2;
    }
    FILE *in = fopen(argv[1], "r");
    if (!in || fscanf(in, "%d %d %d", &K, &W, &T) != 3 || K < 2 || K > MAXK ||
        W < 1 || W > MAXW || T < 2 || T > MAXT || T > K) {
        fprintf(stderr, "bad input header\n");
        return 2;
    }
    for (int i = 0; i < K; i++)
        for (int j = 0; j < W; j++)
            if (fscanf(in, "%" SCNx64, &R[i][j]) != 1) {
                fprintf(stderr, "bad input row %d\n", i);
                return 2;
            }
    fclose(in);
    int threads = atoi(argv[2]);
    if (threads < 1 || threads > 64) {
        fprintf(stderr, "bad thread count\n");
        return 2;
    }
    npairs = K * (K - 1) / 2;
    pair_a = malloc(sizeof(int) * (size_t)npairs);
    pair_b = malloc(sizeof(int) * (size_t)npairs);
    done_task = calloc((size_t)npairs, 1);
    for (int a = 0, t = 0; a < K; a++)
        for (int b = a + 1; b < K; b++, t++) {
            pair_a[t] = a;
            pair_b[t] = b;
        }
    result_init(&total);
    if (argc > 3) {
        FILE *old = fopen(argv[3], "r");
        if (old) {                 /* resume: fold in the finished tasks */
            char line[1024];
            while (fgets(line, sizeof line, old)) {
                Result r;
                result_init(&r);
                int task, used, off = 0;
                if (sscanf(line, "%d %" SCNu64 " %d %" SCNu64 "%n", &task,
                           &r.nodes, &r.best, &r.count, &used) != 4)
                    continue;      /* a line cut short by a kill */
                if (task < 0 || task >= npairs || done_task[task])
                    continue;
                if (strchr(line, '\n') == NULL)
                    continue;
                off = used;
                int idx;
                while (r.wlen < MAXT && sscanf(line + off, "%d%n", &idx, &used) == 1) {
                    r.witness[r.wlen++] = idx;
                    off += used;
                }
                done_task[task] = 1;
                result_merge(&total, &r);
            }
            fclose(old);
        }
        logf = fopen(argv[3], "a");
    }
    /* the K one-row sums */
    for (int i = 0; i < K; i++) {
        int stack[1] = {i};
        Result r;
        result_init(&r);
        r.nodes = 1;
        meet(&r, popc(R[i]) + 1, stack, 1);
        result_merge(&total, &r);
    }
    pthread_t tid[64];
    for (int i = 0; i < threads; i++)
        pthread_create(&tid[i], NULL, worker, NULL);
    for (int i = 0; i < threads; i++)
        pthread_join(tid[i], NULL);
    uint64_t expected = 0;
    for (int w = 1; w <= T; w++)
        expected += binom(K, w);
    printf("{\"k\": %d, \"words\": %d, \"t\": %d, \"nodes\": %" PRIu64
           ", \"expected_nodes\": %" PRIu64 ", \"lightest\": %d, "
           "\"count_at_lightest\": %" PRIu64 ", \"witness_rows\": [",
           K, W, T, total.nodes, expected, total.best, total.count);
    for (int i = 0; i < total.wlen; i++)
        printf("%s%d", i ? ", " : "", total.witness[i]);
    printf("]}\n");
    return total.nodes == expected ? 0 : 1;
}
