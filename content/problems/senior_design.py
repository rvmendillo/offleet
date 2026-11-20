"""Senior design-coding problems: production building blocks (original statements)."""
from dsl import problem, approach, viz, category

category("system-design")

problem(
    id="lru-cache",
    title="Least-Recently-Used Cache",
    difficulty="Medium",
    topics=["System Design", "Design", "Hash Map", "Linked List"],
    design=True,
    statement="""
    Build `LRUCache(capacity)` with O(1) `get(key)` (return the value or `-1`) and `put(key, value)`. When the cache
    is full, `put` of a new key evicts the least recently used key. Both `get` and `put` count as a use.
    """,
    examples=[((["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"],
                [[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]),
               [None, None, None, 1, None, -1, None, -1, 3, 4], "Key 2 is evicted when 3 arrives, then key 1 when 4 arrives.")],
    tests=[((["LRUCache", "put", "put", "get"], [[1], [1, 1], [2, 2], [1]]), [None, None, None, -1]),
           ((["LRUCache", "put", "put", "get", "get"], [[2], [5, 50], [5, 51], [5], [6]]), [None, None, None, 51, -1])],
    constraints=["1 ≤ capacity ≤ 3000", "up to 2·10^5 calls"],
    hints=["A hash map finds entries; a linked list keeps them in usage order.", "Many languages ship this combo: OrderedDict, LinkedHashMap."],
    approaches=[approach(
        name="Hash Map + Ordered List", pattern="design", time="O(1) per call", space="O(capacity)",
        idea="""
        Combine a hash map (instant lookup) with a doubly linked list ordered by recency. Every use moves the entry to the newest end; eviction removes the oldest end.

        Python's `OrderedDict` and Java's access-ordered `LinkedHashMap` are exactly this structure, so production code rarely hand-rolls it.
        """,
        why="This is the classic answer behind CDN, database buffer-pool and LLM KV-cache eviction policies.",
        viz=viz(maps=[("cache (oldest → newest)", "self.data")], vars=[("capacity", "self.capacity")]),
        py='''
        from collections import OrderedDict

        class LRUCache:
            def __init__(self, capacity):
                self.capacity, self.data = capacity, OrderedDict()

            def get(self, key):
                if key not in self.data:
                    return -1  #> Key {key} isn't cached: a miss.
                self.data.move_to_end(key)  #> Hit! Key {key} becomes the most recently used.
                return self.data[key]

            def put(self, key, value):
                self.data[key] = value
                self.data.move_to_end(key)
                if len(self.data) > self.capacity:
                    self.data.popitem(last=False)  #> Over capacity, so evict the least recently used key.
        ''',
        java='''
        class LRUCache {
            private final int capacity;
            private final LinkedHashMap<Integer, Integer> data;

            LRUCache(int capacity) {
                this.capacity = capacity;
                this.data = new LinkedHashMap<>(16, 0.75f, true) {
                    protected boolean removeEldestEntry(Map.Entry<Integer, Integer> e) { return size() > LRUCache.this.capacity; } //>3
                };
            }

            public int get(int key) { return data.getOrDefault(key, -1); } //>1,2

            public void put(int key, int value) { data.put(key, value); }
        }
        ''',
    )],
)

problem(
    id="lfu-cache",
    title="Least-Frequently-Used Cache",
    difficulty="Hard",
    topics=["System Design", "Design", "Hash Map"],
    design=True,
    statement="""
    Build `LFUCache(capacity)` with O(1) `get(key)` (value or `-1`) and `put(key, value)`. When full, `put` of a new
    key evicts the key used the fewest times; among ties, evict the least recently used. A new key starts with one use.
    """,
    examples=[((["LFUCache", "put", "put", "get", "put", "get", "get", "put", "get", "get", "get"],
                [[2], [1, 1], [2, 2], [1], [3, 3], [2], [3], [4, 4], [1], [3], [4]]),
               [None, None, None, 1, None, -1, 3, None, -1, 3, 4], None)],
    tests=[((["LFUCache", "put", "get"], [[0], [0, 0], [0]]), [None, None, -1]),
           ((["LFUCache", "put", "put", "get", "get", "put", "get"], [[2], [1, 1], [2, 2], [2], [2], [3, 3], [1]]), [None, None, None, 2, 2, None, -1])],
    constraints=["0 ≤ capacity ≤ 10^4"],
    hints=["Group keys by use count; inside a group keep recency order.", "Track the smallest use count."],
    approaches=[approach(
        name="Frequency Buckets", pattern="design", time="O(1) per call", space="O(capacity)",
        idea="""
        Keep each key's value and use count, plus one ordered bucket per count holding keys from least to most recent. Track `min_freq`, the smallest count present.

        A use moves a key from bucket f to bucket f + 1. Eviction removes the oldest key in the `min_freq` bucket.
        """,
        viz=viz(maps=[("values", "self.vals"), ("use counts", "self.freq")], vars=[("min_freq", "self.min_freq")]),
        py='''
        from collections import OrderedDict, defaultdict

        class LFUCache:
            def __init__(self, capacity):
                self.capacity, self.vals, self.freq, self.min_freq = capacity, {}, {}, 0
                self.groups = defaultdict(OrderedDict)

            def _touch(self, key):
                f = self.freq[key]
                del self.groups[f][key]
                if not self.groups[f]:
                    del self.groups[f]
                    if self.min_freq == f:
                        self.min_freq += 1
                self.freq[key] = f + 1
                self.groups[f + 1][key] = None

            def get(self, key):
                if key not in self.vals:
                    return -1
                self._touch(key)  #> Key {key} is used again; its count rises to {self.freq[key] + 1}.
                return self.vals[key]

            def put(self, key, value):
                if self.capacity == 0:
                    return
                if key in self.vals:
                    self.vals[key] = value
                    self._touch(key)
                    return
                if len(self.vals) == self.capacity:
                    old, _ = self.groups[self.min_freq].popitem(last=False)  #> Full: evict key {old}, the least frequently used.
                    del self.vals[old], self.freq[old]
                self.vals[key], self.freq[key], self.min_freq = value, 1, 1
                self.groups[1][key] = None
        ''',
        java='''
        class LFUCache {
            private final int capacity;
            private int minFreq = 0;
            private final Map<Integer, Integer> vals = new HashMap<>(), freq = new HashMap<>();
            private final Map<Integer, LinkedHashSet<Integer>> groups = new HashMap<>();

            LFUCache(int capacity) { this.capacity = capacity; }

            private void touch(int key) {
                int f = freq.get(key);
                groups.get(f).remove(key);
                if (groups.get(f).isEmpty()) { groups.remove(f); if (minFreq == f) minFreq++; }
                freq.put(key, f + 1);
                groups.computeIfAbsent(f + 1, x -> new LinkedHashSet<>()).add(key);
            }

            public int get(int key) {
                if (!vals.containsKey(key)) return -1;
                touch(key); //>
                return vals.get(key);
            }

            public void put(int key, int value) {
                if (capacity == 0) return;
                if (vals.containsKey(key)) { vals.put(key, value); touch(key); return; }
                if (vals.size() == capacity) {
                    int old = groups.get(minFreq).iterator().next(); //>
                    groups.get(minFreq).remove(old);
                    vals.remove(old);
                    freq.remove(old);
                }
                vals.put(key, value);
                freq.put(key, 1);
                minFreq = 1;
                groups.computeIfAbsent(1, x -> new LinkedHashSet<>()).add(key);
            }
        }
        ''',
    )],
)

problem(
    id="token-bucket",
    title="Token Bucket Rate Limiter",
    difficulty="Medium",
    topics=["System Design", "Design", "Rate Limiting"],
    design=True,
    statement="""
    Implement `TokenBucket(capacity, rate)`: the bucket starts full with `capacity` tokens and gains `rate` tokens per
    second (never exceeding capacity). `allow(t)` is called with non-decreasing whole-second timestamps; it refills
    the bucket for the elapsed time, then spends one token and returns `true`, or returns `false` if the bucket is empty.
    """,
    examples=[((["TokenBucket", "allow", "allow", "allow", "allow", "allow", "allow", "allow"],
                [[2, 1], [0], [0], [0], [1], [3], [3], [3]]),
               [None, True, True, False, True, True, True, False], "Bursts of 2 are allowed, then 1 per second.")],
    tests=[((["TokenBucket", "allow", "allow"], [[1, 5], [0], [0]]), [None, True, False]),
           ((["TokenBucket", "allow", "allow", "allow"], [[3, 1], [10], [10], [100]]), [None, True, True, True])],
    constraints=["1 ≤ capacity, rate ≤ 10^6"],
    hints=["Refill lazily: compute the tokens earned since the last call instead of using a timer."],
    approaches=[approach(
        name="Lazy Refill", pattern="design", time="O(1) per call", space="O(1)",
        idea="""
        Don't run a timer. On each call, add `rate × elapsed seconds` tokens, capped at capacity, then try to spend one.

        Token buckets allow short bursts up to the capacity while enforcing the average rate. API gateways and LLM providers use them for per-key limits.
        """,
        viz=viz(vars=[("tokens", "self.tokens"), ("capacity", "self.capacity"), ("last call", "self.last")]),
        py='''
        class TokenBucket:
            def __init__(self, capacity, rate):
                self.capacity, self.rate, self.tokens, self.last = capacity, rate, capacity, 0

            def allow(self, t):
                self.tokens = min(self.capacity, self.tokens + (t - self.last) * self.rate)  #> {plural(t - self.last, "second")} passed, so the bucket refills to {plural(self.tokens, "token")}.
                self.last = t
                if self.tokens > 0:
                    self.tokens -= 1
                    return True  #> Spend one token; {self.tokens} left. Allowed.
                return False  #> The bucket is empty. Rejected.
        ''',
        java='''
        class TokenBucket {
            private final long capacity, rate;
            private long tokens, last = 0;

            TokenBucket(int capacity, int rate) { this.capacity = capacity; this.rate = rate; this.tokens = capacity; }

            public boolean allow(int t) {
                tokens = Math.min(capacity, tokens + (t - last) * rate); //>
                last = t;
                if (tokens > 0) { tokens--; return true; } //>
                return false; //>
            }
        }
        ''',
    )],
)

problem(
    id="consistent-hash-ring",
    title="Consistent Hashing Ring",
    difficulty="Hard",
    topics=["System Design", "Design", "Binary Search", "Distributed Systems"],
    design=True,
    statement="""
    Spread keys across cache servers so adding or removing a server moves few keys. Positions on a ring of 360 slots
    come from `h(s) = Σ (i + 1) · code(s[i]) mod 360` (character codes, i from 0). Implement `HashRing()` with
    `addNode(name)`, `removeNode(name)` and `getNode(key)`: the owner is the first node at or clockwise after `h(key)`,
    wrapping around. Node positions never collide in the tests, and `getNode` is only called when a node exists.
    """,
    examples=[((["HashRing", "addNode", "addNode", "addNode", "getNode", "getNode", "getNode", "removeNode", "getNode", "addNode", "getNode", "getNode"],
                [[], ["alpha"], ["beta"], ["gamma"], ["user:42"], ["img:3"], ["cart:9"], ["beta"], ["user:42"], ["delta"], ["alpha"], ["user:7"]]),
               [None, None, None, None, "beta", "gamma", "beta", None, "gamma", None, "alpha", "gamma"],
               "alpha=110, beta=316, gamma=105, delta=135; user:42=258 lands on beta until beta leaves.")],
    tests=[((["HashRing", "addNode", "getNode"], [[], ["solo"], ["anything"]]), [None, None, "solo"])],
    constraints=["up to 10^4 operations"],
    hints=["Keep node positions sorted.", "Binary search for the first position ≥ h(key); wrap to the first node."],
    approaches=[approach(
        name="Sorted Ring + Binary Search", pattern="binary-search", time="O(log n) lookup", space="O(n)",
        idea="""
        Keep the node positions sorted. To place a key, binary search for the first node position at or after the key's hash; if none, wrap around to the first node.

        Removing a node only moves the keys it owned to its clockwise neighbour, unlike `hash mod N` which reshuffles almost everything. Real systems add many virtual nodes per server to balance load.
        """,
        viz=viz(arr="self.points", label="node positions", maps=[("owners", "self.owner")]),
        py='''
        import bisect

        class HashRing:
            def __init__(self):
                self.points, self.owner = [], {}

            @staticmethod
            def h(s):
                return sum((i + 1) * ord(c) for i, c in enumerate(s)) % 360

            def addNode(self, name):
                p = self.h(name)
                bisect.insort(self.points, p)
                self.owner[p] = name  #> Node {q(name)} sits at position {p} on the ring.

            def removeNode(self, name):
                p = self.h(name)
                self.points.remove(p)
                del self.owner[p]  #> Node {q(name)} leaves. Its keys move to the next node clockwise.

            def getNode(self, key):
                p = self.h(key)
                i = bisect.bisect_left(self.points, p) % len(self.points)
                return self.owner[self.points[i]]  #> Key {q(key)} hashes to {p}; the next node clockwise is {q(ret)}.
        ''',
        java='''
        class HashRing {
            private final TreeMap<Integer, String> ring = new TreeMap<>();

            private static int h(String s) {
                int x = 0;
                for (int i = 0; i < s.length(); i++) x += (i + 1) * s.charAt(i);
                return x % 360;
            }

            public void addNode(String name) { ring.put(h(name), name); } //>

            public void removeNode(String name) { ring.remove(h(name)); } //>

            public String getNode(String key) {
                Map.Entry<Integer, String> e = ring.ceilingEntry(h(key));
                return (e != null ? e : ring.firstEntry()).getValue(); //>
            }
        }
        ''',
    )],
)

problem(
    id="circuit-breaker",
    title="Circuit Breaker",
    difficulty="Medium",
    topics=["System Design", "Design", "Resilience", "State Machine"],
    design=True,
    statement="""
    Protect callers from a failing dependency. `CircuitBreaker(threshold, cooldown)` starts `"closed"`.
    `record(t, ok)` reports a call result at time `t`: success resets to `"closed"` with zero failures; a failure
    increments the failure count and trips the breaker `"open"` once failures reach `threshold` (or immediately when
    `"half-open"`). `allow(t)` returns whether a call may proceed: an `"open"` breaker turns `"half-open"` once
    `cooldown` seconds have passed since it opened. `getState()` returns the state.
    """,
    examples=[((["CircuitBreaker", "record", "record", "getState", "allow", "allow", "record", "getState"],
                [[2, 10], [1, False], [2, False], [], [5], [12], [12, True], []]),
               [None, None, None, "open", False, True, None, "closed"], None)],
    tests=[((["CircuitBreaker", "allow", "record", "getState", "allow", "record", "getState"],
             [[1, 5], [0], [0, False], [], [6], [6, False], []]), [None, True, None, "open", True, None, "open"])],
    constraints=["1 ≤ threshold ≤ 100"],
    hints=["Model it as a small state machine with three states."],
    approaches=[approach(
        name="State Machine", pattern="design", time="O(1) per call", space="O(1)",
        idea="""
        Closed: calls flow and failures are counted. Open: calls are rejected immediately so the dependency can recover. Half-open: after the cooldown, a trial call decides whether to close again or reopen.

        Libraries like Resilience4j implement exactly these transitions around remote calls.
        """,
        viz=viz(vars=[("state", "self.state"), ("failures", "self.failures"), ("opened at", "self.opened_at")]),
        py='''
        class CircuitBreaker:
            def __init__(self, threshold, cooldown):
                self.threshold, self.cooldown = threshold, cooldown
                self.state, self.failures, self.opened_at = "closed", 0, 0

            def allow(self, t):
                if self.state == "open" and t - self.opened_at >= self.cooldown:
                    self.state = "half-open"  #> The cooldown has passed, so let a trial call through: half-open.
                return self.state != "open"

            def record(self, t, ok):
                if ok:
                    self.state, self.failures = "closed", 0  #> Success: the circuit closes again.
                else:
                    self.failures += 1
                    if self.state == "half-open" or self.failures >= self.threshold:
                        self.state, self.opened_at = "open", t  #> {self.failures} failures: the breaker trips open at time {t}.

            def getState(self):
                return self.state
        ''',
        java='''
        class CircuitBreaker {
            private final int threshold, cooldown;
            private String state = "closed";
            private int failures = 0, openedAt = 0;

            CircuitBreaker(int threshold, int cooldown) { this.threshold = threshold; this.cooldown = cooldown; }

            public boolean allow(int t) {
                if (state.equals("open") && t - openedAt >= cooldown) state = "half-open"; //>
                return !state.equals("open");
            }

            public void record(int t, boolean ok) {
                if (ok) { state = "closed"; failures = 0; return; } //>
                failures++;
                if (state.equals("half-open") || failures >= threshold) { state = "open"; openedAt = t; } //>
            }

            public String getState() { return state; }
        }
        ''',
    )],
)

problem(
    id="snowflake-ids",
    title="Unique ID Generator",
    difficulty="Medium",
    topics=["System Design", "Design", "Bit Manipulation"],
    design=True,
    statement="""
    Distributed systems need unique, time-sortable IDs without a central counter. `IdGenerator(machine)` builds
    64-bit IDs as `(timestamp << 22) | (machine << 12) | sequence`. `next(ts)` receives non-decreasing timestamps; the
    sequence restarts at 0 for each new timestamp and increases by 1 for repeated timestamps (assume fewer than 4096
    per timestamp). Return the ID.
    """,
    examples=[((["IdGenerator", "next", "next", "next"], [[5], [1], [1], [2]]), [None, 4214784, 4214785, 8409088], None)],
    tests=[((["IdGenerator", "next"], [[0], [0]]), [None, 0]), ((["IdGenerator", "next", "next"], [[1023], [3], [3]]), [None, 16773120, 16773121])],
    constraints=["0 ≤ machine < 1024", "0 ≤ ts < 2^41"],
    hints=["Shift each field into its own bit range, then OR them together."],
    approaches=[approach(
        name="Bit Packing", pattern="bits", time="O(1)", space="O(1)",
        idea="""
        The top bits hold the timestamp, so IDs sort by time. The middle 10 bits name the machine, so two machines never collide. The low 12 bits are a per-timestamp sequence.

        Shifting each part into place and OR-ing them packs three numbers into one 64-bit integer.
        """,
        viz=viz(bits=[("timestamp", "ts"), ("machine", "self.machine"), ("sequence", "self.seq")]),
        py='''
        class IdGenerator:
            def __init__(self, machine):
                self.machine, self.last, self.seq = machine, -1, 0

            def next(self, ts):
                self.seq = self.seq + 1 if ts == self.last else 0
                self.last = ts
                return (ts << 22) | (self.machine << 12) | self.seq  #> Time {ts}, machine {self.machine} and sequence {self.seq} pack into {ret}.
        ''',
        java='''
        class IdGenerator {
            private final long machine;
            private long last = -1, seq = 0;

            IdGenerator(int machine) { this.machine = machine; }

            public long next(long ts) {
                seq = ts == last ? seq + 1 : 0;
                last = ts;
                return (ts << 22) | (machine << 12) | seq; //>
            }
        }
        ''',
    )],
)

problem(
    id="versioned-store",
    title="Key-Value Store With History",
    difficulty="Medium",
    topics=["System Design", "Design", "Binary Search", "Hash Map"],
    design=True,
    statement="""
    Build `VersionedStore()` with `set(key, value, t)` and `get(key, t)`: return the value most recently set for
    `key` at a time `≤ t`, or `""` if none. For each key, `set` is called with strictly increasing times.
    """,
    examples=[((["VersionedStore", "set", "get", "get", "set", "get", "get"],
                [[], ["model", "v1", 1], ["model", 1], ["model", 3], ["model", "v2", 4], ["model", 4], ["model", 5]]),
               [None, None, "v1", "v1", None, "v2", "v2"], None)],
    tests=[((["VersionedStore", "get", "set", "get"], [[], ["x", 1], ["x", "a", 5], ["x", 4]]), [None, "", None, ""])],
    constraints=["up to 2·10^5 calls"],
    hints=["Per key, timestamps are already sorted.", "Binary search for the last time ≤ t."],
    approaches=[approach(
        name="Hash Map + Binary Search", pattern="binary-search", time="O(log n) get", space="O(n)",
        idea="""
        Keep, for every key, the list of times and the matching values. Because times only grow, each list is sorted, so `get` binary-searches for the last time at or before `t`.

        This is the core of multi-version storage used for config history, feature flags and model registries.
        """,
        viz=viz(maps=[("times per key", "self.times"), ("values per key", "self.values")]),
        py='''
        import bisect

        class VersionedStore:
            def __init__(self):
                self.times, self.values = {}, {}

            def set(self, key, value, t):
                self.times.setdefault(key, []).append(t)
                self.values.setdefault(key, []).append(value)  #> Store {q(value)} for {q(key)} at time {t}.

            def get(self, key, t):
                i = bisect.bisect_right(self.times.get(key, []), t) - 1
                return self.values[key][i] if i >= 0 else ""  #> The version of {q(key)} at time {t} is {q(ret) if ret else "nothing"}.
        ''',
        java='''
        class VersionedStore {
            private final Map<String, TreeMap<Integer, String>> data = new HashMap<>();

            public void set(String key, String value, int t) {
                data.computeIfAbsent(key, k -> new TreeMap<>()).put(t, value); //>
            }

            public String get(String key, int t) {
                Map.Entry<Integer, String> e = data.getOrDefault(key, new TreeMap<>()).floorEntry(t);
                return e == null ? "" : e.getValue(); //>
            }
        }
        ''',
    )],
)
