"""Heap / Priority Queue problems (original statements)."""
from dsl import problem, approach, viz

problem(
    id="kth-largest",
    title="The k-th Largest Value",
    difficulty="Medium",
    topics=["Array", "Heap", "Sorting"],
    statement="""
    Return the `k`-th largest value in `nums` (the k-th in sorted descending order, counting duplicates).
    """,
    examples=[([[3, 2, 1, 5, 6, 4], 2], 5, None), ([[3, 2, 3, 1, 2, 4, 5, 5, 6], 4], 4, None)],
    tests=[([[1], 1], 1), ([[7, 7, 7], 2], 7), ([[-1, -5, 2], 3], -5)],
    constraints=["1 ≤ k ≤ nums.length ≤ 10^5"],
    hints=["Keep only the k largest values seen so far.", "A min-heap of size k has the answer on top."],
    approaches=[approach(
        name="Min-Heap of Size k", pattern="heap", time="O(n log k)", space="O(k)",
        idea="""
        Keep a min-heap of the k largest values seen so far. When a new value arrives, push it; if the heap grows beyond k, pop the smallest.

        After every value is processed, the smallest of the k largest, the heap's top, is the k-th largest.
        """,
        viz=viz(arr="nums", ptr={"i": "i"}, stacks=[("min-heap", "sorted(heap)")]),
        py='''
        import heapq

        def kth_largest(nums, k):
            heap = []
            for i, x in enumerate(nums):
                heapq.heappush(heap, x)
                if len(heap) > k:
                    heapq.heappop(heap)  #> More than {plural(k, "value")}, so drop the smallest.
            return heap[0]  #> The heap's top, {heap[0]}, is the {k}-th largest.
        ''',
        java='''
        class Solution {
            public int kthLargest(int[] nums, int k) {
                PriorityQueue<Integer> heap = new PriorityQueue<>();
                for (int x : nums) {
                    heap.add(x);
                    if (heap.size() > k) heap.poll(); //>
                }
                return heap.peek(); //>
            }
        }
        ''',
    )],
)

problem(
    id="last-stone",
    title="Smash the Heaviest Stones",
    difficulty="Easy",
    topics=["Array", "Heap", "Simulation"],
    statement="""
    Each turn, take the two heaviest stones `x ≤ y` and smash them: if equal both vanish, otherwise a stone of weight
    `y − x` remains. Return the weight of the last stone, or `0` if none remain.
    """,
    examples=[([[2, 7, 4, 1, 8, 1]], 1, None), ([[1]], 1, None)],
    tests=[([[3, 3]], 0), ([[10, 4, 2, 10]], 2)],
    constraints=["1 ≤ stones.length ≤ 30"],
    hints=["A max-heap always hands you the two heaviest."],
    approaches=[approach(
        name="Max-Heap Simulation", pattern="heap", time="O(n log n)", space="O(n)",
        idea="""
        Put all stones in a max-heap (Python's heap is a min-heap, so store negatives). Repeatedly pop the two heaviest, and push back their difference if it isn't zero.
        """,
        viz=viz(stacks=[("stones (max-heap)", "sorted(-x for x in heap)")]),
        py='''
        import heapq

        def last_stone(stones):
            heap = [-s for s in stones]
            heapq.heapify(heap)
            while len(heap) > 1:
                y, x = -heapq.heappop(heap), -heapq.heappop(heap)
                if y != x:
                    heapq.heappush(heap, x - y)  #> Smash {y} and {x}: a stone of {y - x} remains.
            return -heap[0] if heap else 0
        ''',
        java='''
        class Solution {
            public int lastStone(int[] stones) {
                PriorityQueue<Integer> heap = new PriorityQueue<>(Collections.reverseOrder());
                for (int s : stones) heap.add(s);
                while (heap.size() > 1) {
                    int y = heap.poll(), x = heap.poll();
                    if (y != x) heap.add(y - x); //>
                }
                return heap.isEmpty() ? 0 : heap.peek();
            }
        }
        ''',
    )],
)

problem(
    id="k-closest-points",
    title="k Closest Points to the Origin",
    difficulty="Medium",
    topics=["Array", "Heap", "Geometry"],
    statement="""
    Given points `[x, y]`, return the `k` points closest to `(0, 0)` by straight-line distance, in any order.
    The answer is unique.
    """,
    examples=[([[[1, 3], [-2, 2]], 1], [[-2, 2]], None), ([[[3, 3], [5, -1], [-2, 4]], 2], [[3, 3], [-2, 4]], None)],
    tests=[([[[0, 1]], 1], [[0, 1]]), ([[[1, 1], [2, 2], [3, 3]], 2], [[1, 1], [2, 2]])],
    check="unordered",
    constraints=["1 ≤ k ≤ points.length ≤ 10^4"],
    hints=["Compare squared distances; no square root needed.", "Keep a max-heap of size k."],
    approaches=[approach(
        name="Max-Heap of Size k", pattern="heap", time="O(n log k)", space="O(k)",
        idea="""
        Keep the k closest points in a max-heap keyed by squared distance. A new point that is closer than the farthest kept point replaces it.
        """,
        py='''
        import heapq

        def k_closest(points, k):
            heap = []
            for x, y in points:
                heapq.heappush(heap, (-(x * x + y * y), x, y))  #> Point ({x}, {y}) has squared distance {x * x + y * y}.
                if len(heap) > k:
                    heapq.heappop(heap)  #> More than {plural(k, "point")} kept, so drop the farthest.
            return [[x, y] for _, x, y in heap]
        ''',
        java='''
        class Solution {
            public int[][] kClosest(int[][] points, int k) {
                PriorityQueue<int[]> heap = new PriorityQueue<>((a, b) -> (b[0] * b[0] + b[1] * b[1]) - (a[0] * a[0] + a[1] * a[1]));
                for (int[] p : points) {
                    heap.add(p); //>
                    if (heap.size() > k) heap.poll(); //>
                }
                return heap.toArray(new int[0][]);
            }
        }
        ''',
    )],
)

problem(
    id="merge-k-sorted-lists",
    title="Merge k Sorted Chains",
    difficulty="Hard",
    topics=["Linked List", "Heap", "Divide and Conquer"],
    statement="""
    `lists` holds the heads of `k` sorted linked lists. Merge them into one sorted list and return its head.
    """,
    examples=[([[[1, 4, 5], [1, 3, 4], [2, 6]]], [1, 1, 2, 3, 4, 4, 5, 6], None), ([[]], [], None)],
    tests=[([[[]]], []), ([[[2], [], [1]]], [1, 2])],
    constraints=["0 ≤ k ≤ 10^4", "total nodes ≤ 10^4"],
    hints=["The next smallest node is the smallest of the k current heads."],
    approaches=[approach(
        name="Heap of List Heads", pattern="heap", time="O(N log k)", space="O(k)",
        idea="""
        Put the head of every list into a min-heap. Repeatedly pop the smallest node, attach it to the result, and push that node's successor.
        """,
        viz=viz(linked=(["dummy"], {"tail": "tail"}), stacks=[("heap (value)", "sorted(v for v, _, _ in heap)")]),
        py='''
        import heapq

        def merge_k(lists):
            heap = [(node.val, i, node) for i, node in enumerate(lists) if node]
            heapq.heapify(heap)
            dummy = tail = ListNode()
            while heap:
                val, i, node = heapq.heappop(heap)
                tail.next = node  #> The smallest head is {val}, from list {i}. Attach it.
                tail = node
                if node.next:
                    heapq.heappush(heap, (node.next.val, i, node.next))
            return dummy.next
        ''',
        java='''
        class Solution {
            public ListNode mergeK(ListNode[] lists) {
                PriorityQueue<ListNode> heap = new PriorityQueue<>((a, b) -> a.val - b.val);
                for (ListNode n : lists) if (n != null) heap.add(n);
                ListNode dummy = new ListNode(), tail = dummy;
                while (!heap.isEmpty()) {
                    ListNode node = heap.poll();
                    tail.next = node; //>
                    tail = node;
                    if (node.next != null) heap.add(node.next);
                }
                return dummy.next;
            }
        }
        ''',
    )],
)

problem(
    id="running-median",
    title="Median of a Growing Stream",
    difficulty="Hard",
    topics=["Heap", "Design", "Data Stream"],
    design=True,
    statement="""
    Build `MedianFinder()` with `addNum(x)` and `findMedian()`, the median of all numbers added so far (the average of
    the two middle values when the count is even).
    """,
    examples=[((["MedianFinder", "addNum", "addNum", "findMedian", "addNum", "findMedian"], [[], [1], [2], [], [3], []]),
               [None, None, None, 1.5, None, 2.0], None)],
    tests=[((["MedianFinder", "addNum", "findMedian", "addNum", "findMedian"], [[], [-5], [], [5], []]), [None, None, -5.0, None, 0.0]),
           ((["MedianFinder", "addNum", "addNum", "addNum", "addNum", "findMedian"], [[], [6], [10], [2], [6], []]), [None, None, None, None, None, 6.0])],
    constraints=["up to 5·10^4 calls"],
    hints=["Keep the smaller half in a max-heap and the larger half in a min-heap."],
    approaches=[approach(
        name="Two Heaps", pattern="heap", time="O(log n) add, O(1) median", space="O(n)",
        idea="""
        A max-heap holds the smaller half and a min-heap holds the larger half, with sizes kept equal or the small half one bigger. The median sits on top of one or both heaps.
        """,
        viz=viz(stacks=[("small half (max-heap)", "sorted(-x for x in self.small)"), ("large half (min-heap)", "sorted(self.large)")]),
        py='''
        import heapq

        class MedianFinder:
            def __init__(self):
                self.small, self.large = [], []

            def addNum(self, x):
                heapq.heappush(self.small, -x)
                heapq.heappush(self.large, -heapq.heappop(self.small))
                if len(self.large) > len(self.small):
                    heapq.heappush(self.small, -heapq.heappop(self.large))  #> Rebalance so the small half is never smaller.

            def findMedian(self):
                if len(self.small) > len(self.large):
                    return float(-self.small[0])
                return (-self.small[0] + self.large[0]) / 2  #> The median is the average of {-self.small[0]} and {self.large[0]}.
        ''',
        java='''
        class MedianFinder {
            private final PriorityQueue<Integer> small = new PriorityQueue<>(Collections.reverseOrder());
            private final PriorityQueue<Integer> large = new PriorityQueue<>();

            public void addNum(int x) {
                small.add(x);
                large.add(small.poll());
                if (large.size() > small.size()) small.add(large.poll()); //>
            }

            public double findMedian() {
                if (small.size() > large.size()) return small.peek();
                return (small.peek() + large.peek()) / 2.0; //>
            }
        }
        ''',
    )],
)

problem(
    id="task-cooldown",
    title="Schedule Tasks With a Cooldown",
    difficulty="Medium",
    topics=["Array", "Greedy", "Heap", "Counting"],
    statement="""
    A CPU runs one task per time unit. `tasks` lists task types (letters); two runs of the same type must be at least
    `n` units apart, and the CPU may idle. Return the minimum total time to run every task.
    """,
    examples=[([["A", "A", "A", "B", "B", "B"], 2], 8, "A B idle A B idle A B"), ([["A", "C", "A", "B", "D", "B"], 1], 6, None)],
    tests=[([["A", "A", "A", "B", "B", "B"], 0], 6), ([["A", "A", "A", "A", "B", "C", "D"], 2], 10)],
    constraints=["1 ≤ tasks.length ≤ 10^4", "0 ≤ n ≤ 100"],
    hints=["The most frequent task decides the skeleton.", "Count how many types tie for the top frequency."],
    approaches=[approach(
        name="Counting Formula", pattern="greedy", time="O(n)", space="O(1)",
        idea="""
        Lay out the most frequent task with gaps of n between its runs: that makes (top − 1) full frames of n + 1 slots, plus a final frame holding every task that ties for the top count.

        Other tasks fill the gaps. If there are more tasks than slots, there's no idling and the answer is simply the number of tasks.
        """,
        viz=viz(vars=["top", "ties"]),
        py='''
        from collections import Counter

        def least_time(tasks, n):
            counts = Counter(tasks).values()
            top = max(counts)
            ties = sum(1 for c in counts if c == top)  #> The top task runs {top} times, and {ties} types tie for that count.
            return max(len(tasks), (top - 1) * (n + 1) + ties)  #> Frames give {(top - 1) * (n + 1) + ties}; there are {len(tasks)} tasks. Answer: {ret}.
        ''',
        java='''
        class Solution {
            public int leastTime(char[] tasks, int n) {
                int[] counts = new int[26];
                int top = 0, ties = 0;
                for (char t : tasks) top = Math.max(top, ++counts[t - 'A']);
                for (int c : counts) if (c == top) ties++; //>
                return Math.max(tasks.length, (top - 1) * (n + 1) + ties); //>
            }
        }
        ''',
    )],
)
