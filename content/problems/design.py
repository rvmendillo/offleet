"""Data-structure design problems (original statements)."""
from dsl import problem, approach, viz

problem(
    id="prefix-tree",
    title="Build a Prefix Tree",
    difficulty="Medium",
    topics=["Trie", "Design", "String"],
    design=True,
    statement="""
    Implement `Trie()` with `insert(word)`, `search(word)` (was this exact word inserted?) and `startsWith(prefix)`
    (was any word with this prefix inserted?). Words are lowercase.
    """,
    examples=[((["Trie", "insert", "search", "search", "startsWith", "insert", "search"],
                [[], ["apple"], ["apple"], ["app"], ["app"], ["app"], ["app"]]),
               [None, None, True, False, True, None, True], None)],
    tests=[((["Trie", "search", "startsWith"], [[], ["a"], [""]]), [None, False, True])],
    constraints=["1 ≤ word.length ≤ 2000", "up to 3·10^4 calls"],
    hints=["Each node maps a letter to a child node and remembers whether a word ends there."],
    approaches=[approach(
        name="Nested Child Maps", pattern="trie", time="O(L) per call", space="O(total letters)",
        idea="""
        Each node holds a map from letter to child node and a flag marking the end of a word. Inserting walks (and creates) one node per letter; searching walks the same path and checks the flag at the end.

        Autocomplete, spell checkers and tokenizer vocabularies use tries.
        """,
        viz=viz(vars=["word", "ch"]),
        py='''
        class Trie:
            def __init__(self):
                self.root = {}

            def insert(self, word):
                node = self.root
                for ch in word:
                    node = node.setdefault(ch, {})
                node["$"] = True  #> Mark the end of {q(word)}.

            def _walk(self, s):
                node = self.root
                for ch in s:
                    if ch not in node:
                        return None
                    node = node[ch]
                return node

            def search(self, word):
                node = self._walk(word)
                return node is not None and "$" in node  #> Is {q(word)} a complete word? {yn(ret)}.

            def startsWith(self, prefix):
                return self._walk(prefix) is not None  #>^ Does any word start with {q(prefix)}? {yn(ret)}.
        ''',
        java='''
        class Trie {
            private final Map<Character, Trie> next = new HashMap<>();
            private boolean end;

            public void insert(String word) {
                Trie node = this;
                for (char ch : word.toCharArray()) node = node.next.computeIfAbsent(ch, k -> new Trie());
                node.end = true; //>
            }

            private Trie walk(String s) {
                Trie node = this;
                for (int i = 0; i < s.length() && node != null; i++) node = node.next.get(s.charAt(i));
                return node;
            }

            public boolean search(String word) { Trie n = walk(word); return n != null && n.end; } //>

            public boolean startsWith(String prefix) { return walk(prefix) != null; } //>
        }
        ''',
    )],
)

problem(
    id="wildcard-dictionary",
    title="Dictionary With Wildcards",
    difficulty="Medium",
    topics=["Trie", "Design", "DFS"],
    design=True,
    statement="""
    Implement `WordDictionary()` with `addWord(word)` and `search(pattern)`, where `.` in the pattern matches any one
    letter. Words are lowercase.
    """,
    examples=[((["WordDictionary", "addWord", "addWord", "addWord", "search", "search", "search", "search"],
                [[], ["bad"], ["dad"], ["mad"], ["pad"], ["bad"], [".ad"], ["b.."]]),
               [None, None, None, None, False, True, True, True], None)],
    tests=[((["WordDictionary", "addWord", "search", "search"], [[], ["a"], ["."], [".."]]), [None, None, True, False])],
    constraints=["1 ≤ word.length ≤ 25", "at most 2 dots per search"],
    hints=["Store words in a trie.", "At a dot, try every child."],
    approaches=[approach(
        name="Trie + DFS", pattern="trie", time="O(26^dots · L)", space="O(total letters)",
        idea="""
        Store words in a trie. Searching follows letters normally; at a `.`, branch into every child and succeed if any branch matches the rest of the pattern.
        """,
        viz=viz(vars=["pattern"]),
        py='''
        class WordDictionary:
            def __init__(self):
                self.root = {}

            def addWord(self, word):
                node = self.root
                for ch in word:
                    node = node.setdefault(ch, {})
                node["$"] = True

            def search(self, pattern):
                def dfs(node, i):
                    if i == len(pattern):
                        return "$" in node
                    if pattern[i] == ".":
                        return any(dfs(child, i + 1) for key, child in node.items() if key != "$")
                    return pattern[i] in node and dfs(node[pattern[i]], i + 1)

                return dfs(self.root, 0)  #>^ Does {q(pattern)} match a stored word? {yn(dfs(self.root, 0))}.
        ''',
        java='''
        class WordDictionary {
            private final WordDictionary[] next = new WordDictionary[26];
            private boolean end;

            public void addWord(String word) {
                WordDictionary node = this;
                for (char ch : word.toCharArray()) {
                    if (node.next[ch - 'a'] == null) node.next[ch - 'a'] = new WordDictionary();
                    node = node.next[ch - 'a'];
                }
                node.end = true;
            }

            public boolean search(String pattern) { return dfs(this, pattern, 0); } //>

            private boolean dfs(WordDictionary node, String p, int i) {
                if (i == p.length()) return node.end;
                char ch = p.charAt(i);
                if (ch != '.') return node.next[ch - 'a'] != null && dfs(node.next[ch - 'a'], p, i + 1);
                for (WordDictionary child : node.next) if (child != null && dfs(child, p, i + 1)) return true;
                return false;
            }
        }
        ''',
    )],
)

problem(
    id="stream-average",
    title="Moving Average of a Stream",
    difficulty="Easy",
    topics=["Design", "Sliding Window", "Queue"],
    design=True,
    statement="""
    `MovingAverage(size)` receives numbers one at a time with `next(val)` and returns the average of the last `size`
    values (or of all values while fewer than `size` have arrived).
    """,
    examples=[((["MovingAverage", "next", "next", "next", "next"], [[3], [1], [10], [3], [5]]), [None, 1.0, 5.5, 4.66667, 6.0], None)],
    tests=[((["MovingAverage", "next", "next"], [[1], [4], [-2]]), [None, 4.0, -2.0])],
    constraints=["1 ≤ size ≤ 1000"],
    hints=["Keep the window in a queue and its running sum."],
    approaches=[approach(
        name="Sliding Window Queue", pattern="sliding-window", time="O(1) per call", space="O(size)",
        idea="""
        Keep the last `size` values in a queue with their running sum. Add the new value on the right; if the window is too long, remove the oldest value from the left and subtract it.
        """,
        viz=viz(queues=[("window", "self.window")], vars=[("sum", "self.total")]),
        py='''
        from collections import deque

        class MovingAverage:
            def __init__(self, size):
                self.size, self.window, self.total = size, deque(), 0

            def next(self, val):
                self.window.append(val)
                self.total += val
                if len(self.window) > self.size:
                    self.total -= self.window.popleft()  #> The window is too long, so drop the oldest value.
                return self.total / len(self.window)  #> The average of {list(self.window)} is {fv(ret)}.
        ''',
        java='''
        class MovingAverage {
            private final int size;
            private final Deque<Integer> window = new ArrayDeque<>();
            private double total;

            MovingAverage(int size) { this.size = size; }

            public double next(int val) {
                window.addLast(val);
                total += val;
                if (window.size() > size) total -= window.pollFirst(); //>
                return total / window.size(); //>
            }
        }
        ''',
    )],
)

problem(
    id="hit-counter",
    title="Hits in the Last Five Minutes",
    difficulty="Medium",
    topics=["Design", "Sliding Window", "Queue"],
    design=True,
    statement="""
    Build `HitCounter()` with `hit(t)` (record a hit at second `t`) and `getHits(t)` (hits in the past 300 seconds,
    i.e. with timestamps in `(t − 300, t]`). Timestamps never decrease.
    """,
    examples=[((["HitCounter", "hit", "hit", "hit", "getHits", "hit", "getHits", "getHits"], [[], [1], [2], [3], [4], [300], [300], [301]]),
               [None, None, None, None, 3, None, 4, 3], None)],
    tests=[((["HitCounter", "getHits", "hit", "getHits"], [[], [5], [10], [309]]), [None, 0, None, 1])],
    constraints=["up to 300 calls per second"],
    hints=["Expire timestamps older than 300 seconds from the front of a queue."],
    approaches=[approach(
        name="Sliding Window Queue", pattern="sliding-window", time="O(1) amortised", space="O(window)",
        idea="""
        Hits arrive in time order, so keep their timestamps in a queue. Before answering, drop timestamps that slid out of the 300-second window from the front; the queue length is the answer.
        """,
        viz=viz(queues=[("hits in window", "self.hits")]),
        py='''
        from collections import deque

        class HitCounter:
            def __init__(self):
                self.hits = deque()

            def hit(self, t):
                self.hits.append(t)

            def getHits(self, t):
                while self.hits and self.hits[0] <= t - 300:
                    self.hits.popleft()  #> A hit is older than 300 seconds at time {t}, so drop it.
                return len(self.hits)  #> {ret} hits in the last five minutes.
        ''',
        java='''
        class HitCounter {
            private final Deque<Integer> hits = new ArrayDeque<>();

            public void hit(int t) { hits.addLast(t); }

            public int getHits(int t) {
                while (!hits.isEmpty() && hits.peekFirst() <= t - 300) hits.pollFirst(); //>
                return hits.size(); //>
            }
        }
        ''',
    )],
)
