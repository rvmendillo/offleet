"""AI Engineering coding problems: patterns from real LLM / ML systems (original statements)."""
from dsl import problem, approach, viz, category

category("ai-engineering")
R_OR = "locals().get('right', {d})"

problem(
    id="chunk-with-overlap",
    title="Chunk Tokens With Overlap",
    difficulty="Easy",
    topics=["AI Engineering", "RAG", "Sliding Window"],
    statement="""
    Retrieval-augmented generation (RAG) splits documents into overlapping chunks so no sentence is cut off from its
    context. Given `tokens`, a chunk `size` and an `overlap` (0 ≤ overlap < size), return the chunks: the first starts
    at index 0, each next chunk starts `size − overlap` tokens later, and you stop after the chunk that reaches the end.
    Return an empty list for empty input.
    """,
    examples=[([["a", "b", "c", "d", "e", "f", "g"], 3, 1], [["a", "b", "c"], ["c", "d", "e"], ["e", "f", "g"]], None),
              ([["w1", "w2", "w3", "w4", "w5"], 4, 2], [["w1", "w2", "w3", "w4"], ["w3", "w4", "w5"]], None)],
    tests=[([[], 3, 1], []), ([["x"], 5, 2], [["x"]]), ([["a", "b", "c", "d"], 2, 0], [["a", "b"], ["c", "d"]])],
    constraints=["0 ≤ tokens.length ≤ 10^5", "1 ≤ size", "0 ≤ overlap < size"],
    hints=["The window moves by size − overlap each time.", "Stop once a chunk reaches the last token."],
    approaches=[approach(
        name="Fixed Sliding Window", pattern="sliding-window", time="O(n · size)", space="O(n · size)",
        idea="""
        A chunk is a window from `left` to `right`. Each step copies the window, then slides `left` forward by size − overlap, so the last `overlap` tokens are shared with the next chunk.

        In production you'd chunk by tokens, not characters, and often snap boundaries to sentence ends.
        """,
        viz=viz(arr="tokens", ptr={"left": "left", "right": "right - 1"}, win=("left", "right - 1"), vars=["size", "overlap"]),
        py='''
        def chunk_tokens(tokens, size, overlap):
            chunks, left = [], 0
            while left < len(tokens):
                right = min(left + size, len(tokens))
                chunks.append(tokens[left:right])  #> Chunk {len(chunks)} covers tokens {left} to {right - 1}.
                if right == len(tokens):
                    break
                left += size - overlap  #> Slide by {size - overlap}, keeping {overlap} overlapping tokens.
            return chunks
        ''',
        java='''
        class Solution {
            public List<List<String>> chunkTokens(String[] tokens, int size, int overlap) {
                List<List<String>> chunks = new ArrayList<>();
                for (int left = 0; left < tokens.length; left += size - overlap) { //>2
                    int right = Math.min(left + size, tokens.length);
                    chunks.add(Arrays.asList(tokens).subList(left, right)); //>1
                    if (right == tokens.length) break;
                }
                return chunks;
            }
        }
        ''',
    )],
)

problem(
    id="rolling-latency-average",
    title="Rolling Latency Average",
    difficulty="Easy",
    topics=["AI Engineering", "Monitoring", "Sliding Window"],
    statement="""
    An inference service logs request latencies in milliseconds. Return the average of every window of `k`
    consecutive latencies (one average per window, in order). This is how dashboards smooth noisy metrics.
    """,
    examples=[([[120, 80, 100, 140, 60], 3], [100.0, 106.66667, 100.0], None), ([[50, 70], 1], [50.0, 70.0], None)],
    tests=[([[10, 20, 30, 40], 4], [25.0]), ([[5, 5, 5], 2], [5.0, 5.0])],
    constraints=["1 ≤ k ≤ latencies.length ≤ 10^5"],
    hints=["Keep a running sum: add the newest value, drop the oldest."],
    approaches=[approach(
        name="Fixed Sliding Window", pattern="sliding-window", time="O(n)", space="O(1) extra",
        idea="""
        Keep the sum of the current window. Add `latencies[right]`; once the window is longer than k, subtract `latencies[left]` and move `left`. Each full window contributes sum ÷ k.
        """,
        viz=viz(arr="latencies", ptr={"left": "left", "right": "right"}, win=("left", R_OR.format(d="-1")), vars=["total"], out="res"),
        py='''
        def rolling_average(latencies, k):
            res, total, left = [], 0, 0
            for right in range(len(latencies)):
                total += latencies[right]
                if right - left + 1 > k:
                    total -= latencies[left]
                    left += 1
                if right - left + 1 == k:
                    res.append(total / k)  #> The window average is {fv(total / k)} ms.
            return res
        ''',
        java='''
        class Solution {
            public List<Double> rollingAverage(int[] latencies, int k) {
                List<Double> res = new ArrayList<>();
                long sum = 0;
                for (int right = 0, left = 0; right < latencies.length; right++) {
                    sum += latencies[right];
                    for (; right - left + 1 > k; left++) sum -= latencies[left];
                    if (right - left + 1 == k) res.add((double) sum / k); //>
                }
                return res;
            }
        }
        ''',
    )],
)

problem(
    id="llm-rate-limiter",
    title="Rate-Limit an LLM Endpoint",
    difficulty="Medium",
    topics=["AI Engineering", "Design", "Sliding Window", "Queue"],
    design=True,
    statement="""
    Protect a model endpoint: `RateLimiter(limit, window)` allows at most `limit` requests in any rolling `window`
    seconds. `allow(t)` is called with non-decreasing timestamps `t` (seconds) and returns `true` if the request at
    time `t` is accepted. A request at time `p` counts against `t` while `t − p < window`.
    """,
    examples=[((["RateLimiter", "allow", "allow", "allow", "allow", "allow"], [[2, 10], [1], [2], [3], [11], [12]]),
               [None, True, True, False, True, True], "The request at 1 expires at 11.")],
    tests=[((["RateLimiter", "allow", "allow", "allow"], [[1, 5], [0], [4], [5]]), [None, True, False, True]),
           ((["RateLimiter", "allow", "allow", "allow", "allow"], [[3, 2], [1], [1], [1], [1]]), [None, True, True, True, False])],
    constraints=["1 ≤ limit ≤ 10^4", "1 ≤ window ≤ 10^6", "timestamps never decrease"],
    hints=["Keep the accepted timestamps in a queue.", "Drop timestamps that slid out of the window before deciding."],
    approaches=[approach(
        name="Sliding Window Log", pattern="sliding-window", time="O(1) amortised", space="O(limit)",
        idea="""
        Keep a queue of accepted request times. Before each decision, pop times that are at least `window` seconds old; they slid out of the window.

        If fewer than `limit` remain, accept and record the request. Each timestamp is pushed and popped once, so the cost is constant on average.
        """,
        why="Compared with a fixed-window counter this never lets a burst through at the window boundary.",
        viz=viz(queues=[("accepted times", "self.log")], vars=[("limit", "self.limit"), ("window", "self.window")]),
        py='''
        from collections import deque

        class RateLimiter:
            def __init__(self, limit, window):
                self.limit, self.window, self.log = limit, window, deque()

            def allow(self, t):
                while self.log and t - self.log[0] >= self.window:
                    self.log.popleft()  #> A request is older than {self.window} seconds, so it leaves the window.
                if len(self.log) < self.limit:
                    self.log.append(t)
                    return True  #> Time {t}: {len(self.log)} of {self.limit} slots used. Accepted.
                return False  #> Time {t}: the window is full. Rejected.
        ''',
        java='''
        class RateLimiter {
            private final int limit, window;
            private final Deque<Integer> log = new ArrayDeque<>();

            RateLimiter(int limit, int window) { this.limit = limit; this.window = window; }

            public boolean allow(int t) {
                while (!log.isEmpty() && t - log.peekFirst() >= window) log.pollFirst(); //>
                if (log.size() < limit) { log.addLast(t); return true; } //>
                return false; //>
            }
        }
        ''',
    )],
)

problem(
    id="context-budget-window",
    title="Most Documents in a Context Budget",
    difficulty="Medium",
    topics=["AI Engineering", "RAG", "Sliding Window"],
    statement="""
    Retrieved documents arrive in order with token counts `tokens`. You may send one contiguous run of them to the
    model, as long as their total stays within the context `budget`. Return the maximum number of documents you can send.
    """,
    examples=[([[400, 900, 300, 200, 500, 100], 1200], 4, "300 + 200 + 500 + 100 = 1100"), ([[5000], 4096], 0, None)],
    tests=[([[1, 1, 1], 3], 3), ([[10, 20, 30], 25], 1), ([[3, 1, 2, 1, 1], 4], 3)],
    constraints=["1 ≤ tokens.length ≤ 10^5", "token counts are positive"],
    hints=["Longest window with sum ≤ budget.", "Shrink from the left while over budget."],
    approaches=[approach(
        name="Sliding Window", pattern="sliding-window", time="O(n)", space="O(1)",
        idea="""
        Add `tokens[right]` to the window. While the total exceeds the budget, drop documents from the left. The window is then a valid prompt, so compare its size with the best.
        """,
        viz=viz(arr="tokens", ptr={"left": "left", "right": "right"}, win=("left", R_OR.format(d="-1")), vars=["total", "budget", "best"]),
        py='''
        def max_documents(tokens, budget):
            total, best, left = 0, 0, 0
            for right in range(len(tokens)):
                total += tokens[right]  #> Add a {tokens[right]}-token document. The total is {total}.
                while total > budget:
                    total -= tokens[left]
                    left += 1  #> Over budget, so drop a document on the left. The total is {total}.
                best = max(best, right - left + 1)
            return best
        ''',
        java='''
        class Solution {
            public int maxDocuments(int[] tokens, int budget) {
                int sum = 0, best = 0, left = 0;
                for (int right = 0; right < tokens.length; right++) {
                    sum += tokens[right]; //>
                    for (; sum > budget; sum -= tokens[left], left++) { } //>
                    best = Math.max(best, right - left + 1);
                }
                return best;
            }
        }
        ''',
    )],
)

problem(
    id="top-k-similar",
    title="Top-k Most Similar Embeddings",
    difficulty="Medium",
    topics=["AI Engineering", "Vector Search", "Heap", "Math"],
    statement="""
    Semantic search compares a `query` embedding with stored `vectors` using cosine similarity
    (dot product divided by the product of lengths). Return the indices of the `k` most similar vectors, most similar
    first; break ties by smaller index. No vector is all zeros.
    """,
    examples=[([[[1, 0], [0, 1], [1, 1], [-1, 0]], [1, 0.2], 2], [0, 2], None),
              ([[[3, 4], [4, 3], [0, 5]], [0, 1], 1], [2], None)],
    tests=[([[[1, 2, 3]], [1, 2, 3], 1], [0]), ([[[1, 0], [2, 0], [0, 1]], [1, 0], 3], [0, 1, 2])],
    constraints=["1 ≤ k ≤ vectors.length ≤ 10^4", "all vectors share the same dimension"],
    hints=["cos(a, b) = a·b / (|a| |b|).", "A min-heap of size k keeps the best k seen so far."],
    approaches=[approach(
        name="Min-Heap of Size k", pattern="heap", time="O(n · d + n log k)", space="O(k)",
        idea="""
        Compute each vector's cosine similarity with the query. Keep a min-heap holding the best k so far: if a new score beats the smallest in the heap, replace it.

        At the end, sort the k survivors from most to least similar. Real vector databases replace this brute force with approximate indexes such as HNSW.
        """,
        viz=viz(maps=[("scores", "{i: round(s, 3) for i, s in enumerate(scores)}")], stacks=[("heap (score, index)", "[(round(s, 3), -n) for s, n in heap]")]),
        py='''
        import heapq
        import math

        def top_k_similar(vectors, query, k):
            qn = math.sqrt(sum(x * x for x in query))
            scores, heap = [], []
            for i, v in enumerate(vectors):
                dot = sum(a * b for a, b in zip(v, query))
                scores.append(dot / (math.sqrt(sum(a * a for a in v)) * qn))  #> Vector {i} has cosine similarity {fv(scores[-1])}.
                heapq.heappush(heap, (scores[-1], -i))
                if len(heap) > k:
                    heapq.heappop(heap)  #> More than {k} candidates, so drop the weakest.
            return [-n for s, n in sorted(heap, reverse=True)]
        ''',
        java='''
        class Solution {
            public int[] topKSimilar(double[][] vectors, double[] query, int k) {
                double qn = norm(query);
                PriorityQueue<double[]> heap = new PriorityQueue<>((a, b) -> a[0] != b[0] ? Double.compare(a[0], b[0]) : Double.compare(b[1], a[1]));
                for (int i = 0; i < vectors.length; i++) {
                    double dot = 0;
                    for (int d = 0; d < query.length; d++) dot += vectors[i][d] * query[d];
                    heap.add(new double[]{dot / (norm(vectors[i]) * qn), i}); //>
                    if (heap.size() > k) heap.poll(); //>
                }
                int[] res = new int[heap.size()];
                for (int j = res.length - 1; j >= 0; j--) res[j] = (int) heap.poll()[1];
                return res;
            }

            private double norm(double[] v) {
                double s = 0;
                for (double x : v) s += x * x;
                return Math.sqrt(s);
            }
        }
        ''',
    )],
)

problem(
    id="stable-softmax",
    title="Numerically Stable Softmax",
    difficulty="Easy",
    topics=["AI Engineering", "Math", "Deep Learning"],
    statement="""
    Convert model `logits` into probabilities with softmax: `p[i] = e^logits[i] / Σ e^logits[j]`. Large logits like
    1000 overflow `exp`, so make it numerically stable. Return the probabilities.
    """,
    examples=[([[1.0, 2.0, 3.0]], [0.09003, 0.24473, 0.66524], None), ([[1000.0, 1000.0]], [0.5, 0.5], "A naive version overflows here.")],
    tests=[([[0.0]], [1.0]), ([[-5.0, 5.0]], [0.0000454, 0.9999546])],
    constraints=["1 ≤ logits.length ≤ 10^5"],
    hints=["Softmax doesn't change if you subtract the same number from every logit.", "Subtract the maximum."],
    approaches=[approach(
        name="Max-Shift Trick", pattern="math", time="O(n)", space="O(n)",
        idea="""
        Softmax is unchanged if you subtract the same constant from every logit, because it cancels in the fraction. Subtract the maximum: now every exponent is at most 0, so `exp` can't overflow.

        The same trick appears inside every attention layer of a transformer.
        """,
        viz=viz(arrays=[("logits", {}), ("[round(e, 4) for e in exps]", {}, None, None, "exp(x − max)")], vars=["m", "total"]),
        py='''
        import math

        def softmax(logits):
            m = max(logits)  #> The largest logit is {m}. Subtract it from every value.
            exps = [math.exp(x - m) for x in logits]
            total = sum(exps)  #> The shifted exponentials add up to {fv(total)}.
            return [e / total for e in exps]
        ''',
        java='''
        class Solution {
            public double[] softmax(double[] logits) {
                double m = Double.NEGATIVE_INFINITY, total = 0;
                for (double x : logits) m = Math.max(m, x); //>
                double[] p = new double[logits.length];
                for (int i = 0; i < p.length; i++) total += p[i] = Math.exp(logits[i] - m); //>
                for (int i = 0; i < p.length; i++) p[i] /= total;
                return p;
            }
        }
        ''',
    )],
)

problem(
    id="bpe-merge-step",
    title="One Byte-Pair Encoding Merge",
    difficulty="Medium",
    topics=["AI Engineering", "Tokenization", "Hash Map"],
    statement="""
    Tokenizers like BPE learn merges: find the most frequent pair of adjacent tokens and fuse every occurrence into one
    token. Given `tokens`, count adjacent pairs (overlapping pairs count), pick the most frequent (ties: the pair that
    appears first), then merge its occurrences left to right without overlapping. Return the new token list; if there
    are fewer than two tokens, return it unchanged.
    """,
    examples=[([["l", "o", "w", "l", "o", "w", "e", "r"]], ["lo", "w", "lo", "w", "e", "r"], "\"l o\" appears twice and comes first."),
              ([["a", "a", "a"]], ["aa", "a"], None)],
    tests=[([["x"]], ["x"]), ([["a", "b", "c", "b", "c"]], ["a", "bc", "bc"]), ([["h", "i"]], ["hi"])],
    constraints=["0 ≤ tokens.length ≤ 10^5"],
    hints=["Count pairs in one pass with a hash map.", "Then rebuild the list, skipping one token after each merge."],
    approaches=[approach(
        name="Count Pairs + Rebuild", pattern="hash-map", time="O(n)", space="O(n)",
        idea="""
        One pass counts every adjacent pair and remembers where it first appears. The winner has the highest count, with earliest position breaking ties.

        A second pass rebuilds the list: when the current token and the next form the winning pair, emit them fused and jump two steps.
        """,
        viz=viz(arr="tokens", ptr={"i": "i"}, maps=[("pair counts", "{a + ' ' + b: c for (a, b), c in counts.items()}")], out="out"),
        py='''
        def merge_most_frequent(tokens):
            counts, first = {}, {}
            for i in range(len(tokens) - 1):
                pair = (tokens[i], tokens[i + 1])
                counts[pair] = counts.get(pair, 0) + 1
                first.setdefault(pair, i)
            if not counts:
                return tokens
            best = max(counts, key=lambda p: (counts[p], -first[p]))  #> The most frequent pair is {q(best[0] + " " + best[1])}, seen {counts[best]} times.
            out, i = [], 0
            while i < len(tokens):
                if i + 1 < len(tokens) and (tokens[i], tokens[i + 1]) == best:
                    out.append(tokens[i] + tokens[i + 1])  #> Fuse them into {q(out[-1])}.
                    i += 2
                else:
                    out.append(tokens[i])
                    i += 1
            return out
        ''',
        java='''
        class Solution {
            public List<String> mergeMostFrequent(String[] tokens) {
                if (tokens.length < 2) return Arrays.asList(tokens);
                Map<String, int[]> stats = new HashMap<>();
                String best = null;
                for (int i = 0; i + 1 < tokens.length; i++) {
                    String key = tokens[i] + "\\u0000" + tokens[i + 1];
                    int[] s = stats.computeIfAbsent(key, x -> new int[]{0, stats.size()});
                    s[0]++;
                }
                for (Map.Entry<String, int[]> e : stats.entrySet()) {
                    int[] s = e.getValue(), b = best == null ? null : stats.get(best);
                    if (b == null || s[0] > b[0] || (s[0] == b[0] && s[1] < b[1])) best = e.getKey(); //>
                }
                List<String> out = new ArrayList<>();
                for (int i = 0; i < tokens.length; i++) {
                    if (i + 1 < tokens.length && (tokens[i] + "\\u0000" + tokens[i + 1]).equals(best)) out.add(tokens[i] + tokens[++i]); //>
                    else out.add(tokens[i]);
                }
                return out;
            }
        }
        ''',
    )],
)

problem(
    id="precision-at-k",
    title="Precision at k for Retrieval",
    difficulty="Easy",
    topics=["AI Engineering", "Evaluation", "Hash Set"],
    statement="""
    To evaluate a retriever, compare its ranked results `retrieved` with the set of truly `relevant` document ids.
    Precision@k is the fraction of the top `k` results that are relevant. Return it as a decimal
    (if fewer than k results exist, still divide by k).
    """,
    examples=[([["d3", "d1", "d7", "d2"], ["d1", "d2", "d9"], 3], 0.33333, "Only d1 is relevant in the top 3."),
              ([["a", "b"], ["a", "b"], 2], 1.0, None)],
    tests=[([[], ["x"], 5], 0.0), ([["x", "y", "z"], ["z"], 2], 0.0), ([["p", "q"], ["p"], 4], 0.25)],
    check="float",
    constraints=["1 ≤ k ≤ 10^4"],
    hints=["Put the relevant ids in a set for O(1) membership checks."],
    approaches=[approach(
        name="Hash Set", pattern="hash-map", time="O(k + r)", space="O(r)",
        idea="""
        Load the relevant ids into a set. Walk the first k retrieved ids and count how many are in the set. Divide by k.

        Pair it with recall@k (hits divided by the number of relevant docs) to see both sides of retrieval quality.
        """,
        viz=viz(arr="retrieved", ptr={"i": "i"}, maps=[("relevant", "rel")], vars=["hits"]),
        py='''
        def precision_at_k(retrieved, relevant, k):
            rel, hits = set(relevant), 0
            for i, doc in enumerate(retrieved[:k]):
                if doc in rel:
                    hits += 1  #> {q(doc)} at rank {i + 1} is relevant. Hits: {hits}.
            return hits / k  #> {hits} relevant out of the top {k}.
        ''',
        java='''
        class Solution {
            public double precisionAtK(String[] retrieved, String[] relevant, int k) {
                Set<String> rel = new HashSet<>(Arrays.asList(relevant));
                int hits = 0;
                for (int i = 0; i < Math.min(k, retrieved.length); i++) if (rel.contains(retrieved[i])) hits++; //>
                return (double) hits / k; //>
            }
        }
        ''',
    )],
)

problem(
    id="merge-ranked-shards",
    title="Merge Ranked Search Shards",
    difficulty="Medium",
    topics=["AI Engineering", "Search", "Heap"],
    statement="""
    A search index is split into shards. Each shard returns its scores sorted from highest to lowest. Merge them and
    return the `n` highest scores overall, highest first (fewer if there aren't enough).
    """,
    examples=[([[[90, 70, 10], [85, 80], [95, 5]], 4], [95, 90, 85, 80], None), ([[[3], []], 5], [3], None)],
    tests=[([[[]], 2], []), ([[[5, 5], [5]], 2], [5, 5]), ([[[9, 1], [8, 2], [7, 3]], 6], [9, 8, 7, 3, 2, 1])],
    constraints=["1 ≤ number of shards ≤ 1000", "each shard is sorted descending"],
    hints=["Only the front of each shard can be the next best score.", "A max-heap of shard fronts finds it fast."],
    approaches=[approach(
        name="Heap of Shard Fronts", pattern="heap", time="O(n log s)", space="O(s)",
        idea="""
        The next best score must be at the front of some shard. Put every shard's front into a max-heap. Pop the biggest, add it to the answer, and push the next score from the same shard.

        This is the k-way merge used by distributed search engines and log aggregators.
        """,
        viz=viz(stacks=[("heap (score, shard)", "sorted([(-s, i) for s, i, j in heap], reverse=True)")], out="res"),
        py='''
        import heapq

        def merge_shards(shards, n):
            heap = [(-s[0], i, 0) for i, s in enumerate(shards) if s]
            heapq.heapify(heap)
            res = []
            while heap and len(res) < n:
                neg, i, j = heapq.heappop(heap)
                res.append(-neg)  #> The best remaining score is {-neg}, from shard {i}.
                if j + 1 < len(shards[i]):
                    heapq.heappush(heap, (-shards[i][j + 1], i, j + 1))
            return res
        ''',
        java='''
        class Solution {
            public List<Integer> mergeShards(int[][] shards, int n) {
                PriorityQueue<int[]> heap = new PriorityQueue<>((a, b) -> b[0] - a[0]);
                for (int i = 0; i < shards.length; i++) if (shards[i].length > 0) heap.add(new int[]{shards[i][0], i, 0});
                List<Integer> res = new ArrayList<>();
                while (!heap.isEmpty() && res.size() < n) {
                    int[] top = heap.poll();
                    res.add(top[0]); //>
                    int i = top[1], j = top[2] + 1;
                    if (j < shards[i].length) heap.add(new int[]{shards[i][j], i, j});
                }
                return res;
            }
        }
        ''',
    )],
)
