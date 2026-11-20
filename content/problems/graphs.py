"""Graph problems: grids, BFS/DFS, topological sort, union-find, shortest paths (original statements)."""
from dsl import problem, approach, viz

problem(
    id="count-islands",
    title="Count the Islands",
    difficulty="Medium",
    topics=["Graph", "DFS", "Matrix"],
    statement="""
    `grid` is a map of `"1"` (land) and `"0"` (water). An island is land connected up, down, left or right.
    Return the number of islands. You may modify the grid.
    """,
    examples=[([[["1", "1", "0", "0"], ["1", "0", "0", "1"], ["0", "0", "1", "1"], ["0", "0", "0", "1"]]], 2, None),
              ([[["1", "0", "1"], ["0", "1", "0"]]], 3, "Diagonals don't connect.")],
    tests=[([[["0"]]], 0), ([[["1", "1"], ["1", "1"]]], 1)],
    constraints=["1 ≤ m, n ≤ 300"],
    hints=["When you find land, sink the whole island so you never count it twice."],
    approaches=[approach(
        name="DFS Flood Fill", pattern="graph", time="O(m · n)", space="O(m · n)",
        idea="""
        Scan every cell. When you hit land, that's a new island: count it, then run a depth-first search that turns the whole connected island into water so it won't be counted again.
        """,
        why="Each cell is sunk at most once; the recursion can go as deep as the island's size.",
        viz=viz(grid=("grid", {"you": ("r", "c")}), vars=["count"]),
        py='''
        def count_islands(grid):
            m, n = len(grid), len(grid[0])

            def sink(r, c):
                if 0 <= r < m and 0 <= c < n and grid[r][c] == "1":
                    grid[r][c] = "#"
                    sink(r + 1, c)
                    sink(r - 1, c)
                    sink(r, c + 1)
                    sink(r, c - 1)

            count = 0
            for r in range(m):
                for c in range(n):
                    if grid[r][c] == "1":
                        count += 1  #> New land at row {r}, column {c}: island number {count}.
                        sink(r, c)  #> Sink every cell of this island.
            return count
        ''',
        java='''
        class Solution {
            public int countIslands(char[][] grid) {
                int count = 0;
                for (int r = 0; r < grid.length; r++)
                    for (int c = 0; c < grid[0].length; c++)
                        if (grid[r][c] == '1') { count++; sink(grid, r, c); } //>1,2
                return count;
            }

            private void sink(char[][] g, int r, int c) {
                if (r < 0 || c < 0 || r >= g.length || c >= g[0].length || g[r][c] != '1') return;
                g[r][c] = '#';
                sink(g, r + 1, c); sink(g, r - 1, c); sink(g, r, c + 1); sink(g, r, c - 1);
            }
        }
        ''',
    )],
)

problem(
    id="largest-island",
    title="Largest Island Area",
    difficulty="Medium",
    topics=["Graph", "DFS", "Matrix"],
    statement="""
    `grid` contains `1` for land and `0` for water. Return the area (number of cells) of the largest island,
    where cells connect up, down, left and right, or `0` if there is no land.
    """,
    examples=[([[[1, 1, 0], [0, 1, 0], [0, 0, 1]]], 3, None), ([[[0, 0]]], 0, None)],
    tests=[([[[1]]], 1), ([[[1, 0, 1], [1, 0, 1], [1, 1, 1]]], 7)],
    constraints=["1 ≤ m, n ≤ 50"],
    hints=["DFS returns the size of the island it sinks."],
    approaches=[approach(
        name="DFS Returning Area", pattern="graph", time="O(m · n)", space="O(m · n)",
        idea="""
        A depth-first search from a land cell sinks the island and returns how many cells it sank: 1 plus the areas found in the four directions. Keep the biggest.
        """,
        viz=viz(grid=("grid", {"start": ("r", "c")}), vars=["best"]),
        py='''
        def largest_island(grid):
            m, n = len(grid), len(grid[0])

            def area(r, c):
                if not (0 <= r < m and 0 <= c < n) or grid[r][c] != 1:
                    return 0
                grid[r][c] = 2
                return 1 + area(r + 1, c) + area(r - 1, c) + area(r, c + 1) + area(r, c - 1)

            best = 0
            for r in range(m):
                for c in range(n):
                    if grid[r][c] == 1:
                        best = max(best, area(r, c))  #>^ The island starting at row {r}, column {c} is sunk. Best area so far: {best}.
            return best
        ''',
        java='''
        class Solution {
            public int largestIsland(int[][] grid) {
                int best = 0;
                for (int r = 0; r < grid.length; r++)
                    for (int c = 0; c < grid[0].length; c++)
                        if (grid[r][c] == 1) best = Math.max(best, area(grid, r, c)); //>
                return best;
            }

            private int area(int[][] g, int r, int c) {
                if (r < 0 || c < 0 || r >= g.length || c >= g[0].length || g[r][c] != 1) return 0;
                g[r][c] = 2;
                return 1 + area(g, r + 1, c) + area(g, r - 1, c) + area(g, r, c + 1) + area(g, r, c - 1);
            }
        }
        ''',
    )],
)

problem(
    id="paint-fill",
    title="Paint Bucket Fill",
    difficulty="Easy",
    topics=["Graph", "DFS", "Matrix"],
    statement="""
    `image[r][c]` is a pixel color. Starting from pixel `(sr, sc)`, repaint it and every pixel of the same original
    color connected to it (up, down, left, right) with `color`. Return the image.
    """,
    examples=[([[[1, 1, 1], [1, 1, 0], [1, 0, 1]], 1, 1, 2], [[2, 2, 2], [2, 2, 0], [2, 0, 1]], None),
              ([[[0, 0], [0, 0]], 0, 0, 0], [[0, 0], [0, 0]], "Same color: nothing changes.")],
    tests=[([[[5]], 0, 0, 3], [[3]])],
    constraints=["1 ≤ m, n ≤ 50"],
    hints=["If the new color equals the old one, stop immediately (or you'd loop forever)."],
    approaches=[approach(
        name="DFS", pattern="graph", time="O(m · n)", space="O(m · n)",
        idea="""
        Remember the starting color. Recursively repaint a pixel if it still has that color, then spread to its four neighbours. If the new color equals the old one, there's nothing to do.
        """,
        viz=viz(grid=("image", {"paint": ("r", "c")})),
        py='''
        def paint_fill(image, sr, sc, color):
            old = image[sr][sc]
            if old == color:
                return image

            def fill(r, c):
                if 0 <= r < len(image) and 0 <= c < len(image[0]) and image[r][c] == old:
                    image[r][c] = color  #> Repaint row {r}, column {c}.
                    fill(r + 1, c)
                    fill(r - 1, c)
                    fill(r, c + 1)
                    fill(r, c - 1)

            fill(sr, sc)
            return image
        ''',
        java='''
        class Solution {
            public int[][] paintFill(int[][] image, int sr, int sc, int color) {
                if (image[sr][sc] != color) fill(image, sr, sc, image[sr][sc], color);
                return image;
            }

            private void fill(int[][] img, int r, int c, int old, int color) {
                if (r < 0 || c < 0 || r >= img.length || c >= img[0].length || img[r][c] != old) return;
                img[r][c] = color; //>
                fill(img, r + 1, c, old, color); fill(img, r - 1, c, old, color);
                fill(img, r, c + 1, old, color); fill(img, r, c - 1, old, color);
            }
        }
        ''',
    )],
)

problem(
    id="spreading-rot",
    title="Minutes Until Everything Rots",
    difficulty="Medium",
    topics=["Graph", "BFS", "Matrix"],
    statement="""
    In `grid`, `0` is empty, `1` is fresh fruit and `2` is rotten fruit. Every minute, fresh fruit next to rotten fruit
    (up, down, left, right) becomes rotten. Return the minutes until no fresh fruit remains, or `-1` if that never happens.
    """,
    examples=[([[[2, 1, 1], [1, 1, 0], [0, 1, 1]]], 4, None), ([[[2, 1, 1], [0, 1, 1], [1, 0, 1]]], -1, "The bottom-left fruit is unreachable.")],
    tests=[([[[0, 2]]], 0), ([[[1]]], -1), ([[[2, 2], [1, 1]]], 1)],
    constraints=["1 ≤ m, n ≤ 10"],
    hints=["All rotten fruit spread at the same time: start a BFS from all of them at once."],
    approaches=[approach(
        name="Multi-Source BFS", pattern="graph", time="O(m · n)", space="O(m · n)",
        idea="""
        Put every rotten fruit in the queue at minute 0. Process the queue one minute (one level) at a time, rotting fresh neighbours and adding them for the next minute.

        If fresh fruit remains when the queue empties, some fruit can never be reached.
        """,
        viz=viz(grid=("grid", {}), vars=["minutes", "fresh"], queues=[("rotting now", "list(q)")]),
        py='''
        from collections import deque

        def minutes_to_rot(grid):
            m, n = len(grid), len(grid[0])
            q = deque((r, c) for r in range(m) for c in range(n) if grid[r][c] == 2)
            fresh = sum(row.count(1) for row in grid)
            minutes = 0
            while q and fresh:
                for _ in range(len(q)):
                    r, c = q.popleft()
                    for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                        if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == 1:
                            grid[nr][nc] = 2
                            fresh -= 1
                            q.append((nr, nc))
                minutes += 1  #> After minute {minutes}, {fresh} fresh fruit remain.
            return minutes if fresh == 0 else -1
        ''',
        java='''
        class Solution {
            public int minutesToRot(int[][] grid) {
                int m = grid.length, n = grid[0].length, fresh = 0, minutes = 0;
                Deque<int[]> q = new ArrayDeque<>();
                for (int r = 0; r < m; r++)
                    for (int c = 0; c < n; c++) {
                        if (grid[r][c] == 2) q.add(new int[]{r, c});
                        if (grid[r][c] == 1) fresh++;
                    }
                int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
                while (!q.isEmpty() && fresh > 0) {
                    for (int k = q.size(); k > 0; k--) {
                        int[] cell = q.poll();
                        for (int[] d : dirs) {
                            int r = cell[0] + d[0], c = cell[1] + d[1];
                            if (r >= 0 && c >= 0 && r < m && c < n && grid[r][c] == 1) {
                                grid[r][c] = 2;
                                fresh--;
                                q.add(new int[]{r, c});
                            }
                        }
                    }
                    minutes++; //>
                }
                return fresh == 0 ? minutes : -1;
            }
        }
        ''',
    )],
)

problem(
    id="can-finish-courses",
    title="Can Every Course Be Taken?",
    difficulty="Medium",
    topics=["Graph", "Topological Sort", "BFS"],
    statement="""
    There are `n` courses numbered `0..n−1`. Each pair `[a, b]` in `prereqs` means course `b` must be taken before
    course `a`. Return `true` if it's possible to finish every course (no circular requirements).
    """,
    examples=[([2, [[1, 0]]], True, None), ([2, [[1, 0], [0, 1]]], False, "Each course needs the other first.")],
    tests=[([3, []], True), ([4, [[1, 0], [2, 1], [3, 2], [1, 3]]], False), ([3, [[1, 0], [2, 0]]], True)],
    constraints=["1 ≤ n ≤ 2000", "0 ≤ prereqs.length ≤ 5000"],
    hints=["Count each course's unmet prerequisites (in-degree).", "Repeatedly take courses whose count is zero."],
    approaches=[approach(
        name="Kahn's Topological Sort", pattern="graph", time="O(V + E)", space="O(V + E)",
        idea="""
        Count each course's unmet prerequisites. Courses with none can be taken now: put them in a queue. Taking a course reduces the count of every course that depends on it, possibly freeing new ones.

        If every course eventually gets taken, there's no cycle.
        """,
        viz=viz(graph=("{i: nbrs for i, nbrs in enumerate(adj)}", {"take": "c"}, "taken_set", True), vars=["taken"]),
        demo=[4, [[1, 0], [2, 0], [3, 1], [3, 2]]],
        py='''
        from collections import deque

        def can_finish(n, prereqs):
            adj, indeg = [[] for _ in range(n)], [0] * n
            for a, b in prereqs:
                adj[b].append(a)
                indeg[a] += 1
            q = deque(i for i in range(n) if indeg[i] == 0)
            taken, taken_set = 0, set()
            while q:
                c = q.popleft()
                taken += 1
                taken_set.add(c)  #> Take course {c}. Courses taken: {taken}.
                for nxt in adj[c]:
                    indeg[nxt] -= 1
                    if indeg[nxt] == 0:
                        q.append(nxt)
            return taken == n
        ''',
        java='''
        class Solution {
            public boolean canFinish(int n, int[][] prereqs) {
                List<List<Integer>> adj = new ArrayList<>();
                for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
                int[] indeg = new int[n];
                for (int[] p : prereqs) { adj.get(p[1]).add(p[0]); indeg[p[0]]++; }
                Deque<Integer> q = new ArrayDeque<>();
                for (int i = 0; i < n; i++) if (indeg[i] == 0) q.add(i);
                int taken = 0;
                while (!q.isEmpty()) {
                    int c = q.poll();
                    taken++; //>
                    for (int next : adj.get(c)) if (--indeg[next] == 0) q.add(next);
                }
                return taken == n;
            }
        }
        ''',
    )],
)

problem(
    id="course-order",
    title="An Order for Every Course",
    difficulty="Medium",
    topics=["Graph", "Topological Sort", "Heap"],
    statement="""
    Same setup: `n` courses and pairs `[a, b]` meaning `b` comes before `a`. Return an order that takes every course,
    always choosing the **smallest-numbered** available course next (so the answer is unique), or `[]` if impossible.
    """,
    examples=[([4, [[1, 0], [2, 0], [3, 1], [3, 2]]], [0, 1, 2, 3], None), ([2, [[0, 1], [1, 0]]], [], None)],
    tests=[([1, []], [0]), ([3, [[0, 2]]], [1, 2, 0])],
    constraints=["1 ≤ n ≤ 2000"],
    hints=["Kahn's algorithm with a min-heap instead of a queue."],
    approaches=[approach(
        name="Kahn's Algorithm with a Min-Heap", pattern="graph", time="O((V + E) log V)", space="O(V + E)",
        idea="""
        Run Kahn's topological sort, but keep the available courses in a min-heap so the smallest number always goes next. If fewer than n courses come out, there's a cycle.
        """,
        viz=viz(graph=("{i: nbrs for i, nbrs in enumerate(adj)}", {"take": "c"}, "order", True), out="order"),
        py='''
        import heapq

        def course_order(n, prereqs):
            adj, indeg = [[] for _ in range(n)], [0] * n
            for a, b in prereqs:
                adj[b].append(a)
                indeg[a] += 1
            heap = [i for i in range(n) if indeg[i] == 0]
            heapq.heapify(heap)
            order = []
            while heap:
                c = heapq.heappop(heap)
                order.append(c)  #> The smallest available course is {c}.
                for nxt in adj[c]:
                    indeg[nxt] -= 1
                    if indeg[nxt] == 0:
                        heapq.heappush(heap, nxt)
            return order if len(order) == n else []
        ''',
        java='''
        class Solution {
            public int[] courseOrder(int n, int[][] prereqs) {
                List<List<Integer>> adj = new ArrayList<>();
                for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
                int[] indeg = new int[n];
                for (int[] p : prereqs) { adj.get(p[1]).add(p[0]); indeg[p[0]]++; }
                PriorityQueue<Integer> heap = new PriorityQueue<>();
                for (int i = 0; i < n; i++) if (indeg[i] == 0) heap.add(i);
                int[] order = new int[n];
                int k = 0;
                while (!heap.isEmpty()) {
                    int c = heap.poll();
                    order[k++] = c; //>
                    for (int next : adj.get(c)) if (--indeg[next] == 0) heap.add(next);
                }
                return k == n ? order : new int[0];
            }
        }
        ''',
    )],
)

problem(
    id="clone-graph",
    title="Deep Copy a Graph",
    difficulty="Medium",
    topics=["Graph", "BFS", "Hash Map"],
    statement="""
    Each `Node` has a value and a list of `neighbors`. Given one node of a connected undirected graph, return a deep
    copy of the whole graph. In the examples the graph is shown as an adjacency list where node `i + 1` is at index `i`.
    """,
    examples=[([[[2, 4], [1, 3], [2, 4], [1, 3]]], [[2, 4], [1, 3], [2, 4], [1, 3]], None), ([[[]]], [[]], None)],
    tests=[([[]], []), ([[[2], [1]]], [[2], [1]])],
    constraints=["0 ≤ number of nodes ≤ 100"],
    hints=["Map each original node to its copy so you never copy a node twice."],
    approaches=[approach(
        name="BFS + Copy Map", pattern="graph", time="O(V + E)", space="O(V)",
        idea="""
        Keep a map from original nodes to their copies. BFS from the start node: for every neighbour, create its copy the first time you see it, then connect the copies.
        """,
        viz=viz(maps=[("copied", "{k.val: v.val for k, v in copies.items()}")]),
        py='''
        from collections import deque

        def clone(node):
            if not node:
                return None
            copies = {node: Node(node.val)}
            q = deque([node])
            while q:
                cur = q.popleft()
                for nb in cur.neighbors:
                    if nb not in copies:
                        copies[nb] = Node(nb.val)  #> Copy node {nb.val} for the first time.
                        q.append(nb)
                    copies[cur].neighbors.append(copies[nb])
            return copies[node]
        ''',
        java='''
        class Solution {
            public Node clone(Node node) {
                if (node == null) return null;
                Map<Node, Node> copies = new HashMap<>();
                copies.put(node, new Node(node.val));
                Deque<Node> q = new ArrayDeque<>(List.of(node));
                while (!q.isEmpty()) {
                    Node cur = q.poll();
                    for (Node nb : cur.neighbors) {
                        if (!copies.containsKey(nb)) { copies.put(nb, new Node(nb.val)); q.add(nb); } //>
                        copies.get(cur).neighbors.add(copies.get(nb));
                    }
                }
                return copies.get(node);
            }
        }
        ''',
    )],
)

problem(
    id="word-ladder",
    title="Shortest Word Ladder",
    difficulty="Hard",
    topics=["Graph", "BFS", "String"],
    statement="""
    Transform `begin` into `end` by changing one letter at a time, where every intermediate word must be in `words`.
    Return the number of words in the shortest such sequence (including `begin` and `end`), or `0` if impossible.
    """,
    examples=[(["hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]], 5, "hit → hot → dot → dog → cog"),
              (["hit", "cog", ["hot", "dot", "dog", "lot", "log"]], 0, None)],
    tests=[(["a", "c", ["a", "b", "c"]], 2), (["same", "sane", ["sane"]], 2)],
    constraints=["1 ≤ words.length ≤ 5000", "all words have the same length"],
    hints=["Each word is a node; one-letter changes are edges.", "BFS finds the fewest steps."],
    approaches=[approach(
        name="BFS Over Words", pattern="graph", time="O(n · L · 26)", space="O(n)",
        idea="""
        Breadth-first search explores words in order of distance from `begin`. From each word, try changing every letter to every other letter; unvisited dictionary words go into the queue one step further away.

        The first time we reach `end`, the step count is minimal.
        """,
        viz=viz(queues=[("queue (word, steps)", "list(queue)")], vars=["word", "steps"]),
        py='''
        from collections import deque

        def ladder_length(begin, end, words):
            unseen = set(words)
            queue = deque([(begin, 1)])
            while queue:
                word, steps = queue.popleft()
                if word == end:
                    return steps  #> Reached {q(end)} in {steps} words.
                for i in range(len(word)):
                    for ch in "abcdefghijklmnopqrstuvwxyz":
                        nxt = word[:i] + ch + word[i + 1:]
                        if nxt in unseen:
                            unseen.remove(nxt)
                            queue.append((nxt, steps + 1))  #> {q(word)} → {q(nxt)}: {steps + 1} words so far.
            return 0
        ''',
        java='''
        class Solution {
            public int ladderLength(String begin, String end, String[] words) {
                Set<String> unseen = new HashSet<>(Arrays.asList(words));
                Deque<Object[]> q = new ArrayDeque<>();
                q.add(new Object[]{begin, 1});
                while (!q.isEmpty()) {
                    Object[] cur = q.poll();
                    String word = (String) cur[0];
                    int steps = (Integer) cur[1];
                    if (word.equals(end)) return steps; //>
                    char[] c = word.toCharArray();
                    for (int i = 0; i < c.length; i++) {
                        char orig = c[i];
                        for (char ch = 'a'; ch <= 'z'; ch++) {
                            c[i] = ch;
                            String next = new String(c);
                            if (unseen.remove(next)) q.add(new Object[]{next, steps + 1}); //>
                        }
                        c[i] = orig;
                    }
                }
                return 0;
            }
        }
        ''',
    )],
)

problem(
    id="redundant-link",
    title="The Link That Makes a Loop",
    difficulty="Medium",
    topics=["Graph", "Union-Find"],
    statement="""
    A tree of `n` nodes (labelled `1..n`) got one extra edge, creating exactly one cycle. `edges` lists all edges.
    Return the edge that can be removed to make it a tree again; if several work, return the one that appears last.
    """,
    examples=[([[[1, 2], [1, 3], [2, 3]]], [2, 3], None), ([[[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]], [1, 4], None)],
    tests=[([[[1, 2], [2, 1]]], [2, 1]), ([[[3, 1], [1, 2], [2, 3]]], [2, 3])],
    constraints=["3 ≤ n ≤ 1000"],
    hints=["Add edges one by one; the first edge whose ends are already connected closes the loop."],
    approaches=[approach(
        name="Union-Find", pattern="union-find", time="O(n · α(n))", space="O(n)",
        idea="""
        Union-find tracks which nodes are already connected. Add edges in order: if both ends already share a root, this edge closes the cycle, so it's the answer. Otherwise merge their groups.
        """,
        why="With path compression each find is nearly constant time.",
        viz=viz(maps=[("parent", "{i: p for i, p in enumerate(parent) if i}")], vars=["a", "b"]),
        py='''
        def redundant_link(edges):
            parent = list(range(len(edges) + 1))

            def find(x):
                while parent[x] != x:
                    parent[x] = parent[parent[x]]
                    x = parent[x]
                return x

            for a, b in edges:
                ra, rb = find(a), find(b)  #>^ Node {a} belongs to group {ra}, node {b} to group {rb}.
                if ra == rb:
                    return [a, b]  #> They're already connected, so [{a}, {b}] closes the loop.
                parent[ra] = rb
            return []
        ''',
        java='''
        class Solution {
            private int[] parent;

            public int[] redundantLink(int[][] edges) {
                parent = new int[edges.length + 1];
                for (int i = 0; i < parent.length; i++) parent[i] = i;
                for (int[] e : edges) {
                    int ra = find(e[0]), rb = find(e[1]); //>
                    if (ra == rb) return e; //>
                    parent[ra] = rb;
                }
                return new int[0];
            }

            private int find(int x) {
                while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
                return x;
            }
        }
        ''',
    )],
)

problem(
    id="signal-delay",
    title="How Long Until Every Server Hears?",
    difficulty="Medium",
    topics=["Graph", "Shortest Path", "Heap"],
    statement="""
    `times[i] = [u, v, w]` means a signal sent from server `u` reaches server `v` after `w` milliseconds (one-way).
    Servers are labelled `1..n`. A signal starts at server `k`. Return how long until every server has received it,
    or `-1` if some server never does.
    """,
    examples=[([[[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2], 2, None), ([[[1, 2, 1]], 2, 2], -1, None)],
    tests=[([[[1, 2, 1]], 2, 1], 1), ([[[1, 2, 4], [1, 3, 1], [3, 2, 1]], 3, 1], 2)],
    constraints=["1 ≤ n ≤ 100", "weights are positive"],
    hints=["Shortest paths from one source with positive weights: Dijkstra."],
    approaches=[approach(
        name="Dijkstra", pattern="graph", time="O(E log V)", space="O(V + E)",
        idea="""
        Always settle the closest unsettled server next, using a min-heap of (time, server). When a server is settled, its time is final; relax its outgoing links.

        The answer is the largest settled time, or −1 if some server was never reached.
        """,
        viz=viz(graph=("{u: [v for v, w in adj.get(u, [])] for u in range(1, n + 1)}", {"at": "u"}, "dist", True),
                maps=[("arrival time", "dist")]),
        py='''
        import heapq

        def network_delay(times, n, k):
            adj = {}
            for u, v, w in times:
                adj.setdefault(u, []).append((v, w))
            dist, heap = {}, [(0, k)]
            while heap:
                d, u = heapq.heappop(heap)
                if u in dist:
                    continue
                dist[u] = d  #> Server {u} hears the signal at {d} ms.
                for v, w in adj.get(u, []):
                    if v not in dist:
                        heapq.heappush(heap, (d + w, v))
            return max(dist.values()) if len(dist) == n else -1
        ''',
        java='''
        class Solution {
            public int networkDelay(int[][] times, int n, int k) {
                Map<Integer, List<int[]>> adj = new HashMap<>();
                for (int[] t : times) adj.computeIfAbsent(t[0], x -> new ArrayList<>()).add(new int[]{t[1], t[2]});
                Map<Integer, Integer> dist = new HashMap<>();
                PriorityQueue<int[]> heap = new PriorityQueue<>((a, b) -> a[0] - b[0]);
                heap.add(new int[]{0, k});
                while (!heap.isEmpty()) {
                    int[] top = heap.poll();
                    if (dist.containsKey(top[1])) continue;
                    dist.put(top[1], top[0]); //>
                    for (int[] e : adj.getOrDefault(top[1], List.of()))
                        if (!dist.containsKey(e[0])) heap.add(new int[]{top[0] + e[1], e[0]});
                }
                return dist.size() == n ? Collections.max(dist.values()) : -1;
            }
        }
        ''',
    )],
)
