"""Greedy problems (original statements)."""
from dsl import problem, approach, viz

problem(
    id="can-reach-end",
    title="Can You Hop to the End?",
    difficulty="Medium",
    topics=["Array", "Greedy"],
    statement="""
    You start at index 0. `nums[i]` is the farthest jump length from index `i`. Return `true` if you can reach the last index.
    """,
    examples=[([[2, 3, 1, 1, 4]], True, None), ([[3, 2, 1, 0, 4]], False, "Every path gets stuck at index 3.")],
    tests=[([[0]], True), ([[1, 0, 1]], False), ([[2, 0, 0]], True)],
    constraints=["1 ≤ nums.length ≤ 10^4"],
    hints=["Track the farthest index reachable so far."],
    approaches=[approach(
        name="Greedy Reach", pattern="greedy", time="O(n)", space="O(1)",
        idea="""
        Walk left to right keeping `reach`, the farthest index you can get to. If you ever stand on an index beyond `reach`, you're stuck. Otherwise extend `reach` with `i + nums[i]`.
        """,
        viz=viz(arr="nums", ptr={"i": "i", "reach": "reach"}),
        py='''
        def can_reach_end(nums):
            reach = 0
            for i, jump in enumerate(nums):
                if i > reach:
                    return False  #> Index {i} is beyond the farthest reachable index {reach}. Stuck!
                reach = max(reach, i + jump)  #> From index {i} you can jump to {i + jump}. Farthest so far: {reach}.
            return True
        ''',
        java='''
        class Solution {
            public boolean canReachEnd(int[] nums) {
                int reach = 0;
                for (int i = 0; i < nums.length; i++) {
                    if (i > reach) return false; //>
                    reach = Math.max(reach, i + nums[i]); //>
                }
                return true;
            }
        }
        ''',
    )],
)

problem(
    id="fewest-hops",
    title="Fewest Hops to the End",
    difficulty="Medium",
    topics=["Array", "Greedy", "Sliding Window"],
    patterns=["sliding-window"],
    statement="""
    Same setup as before, but the last index is always reachable. Return the minimum number of jumps to reach it.
    """,
    examples=[([[2, 3, 1, 1, 4]], 2, "Jump to index 1, then to the end."), ([[2, 3, 0, 1, 4]], 2, None)],
    tests=[([[0]], 0), ([[1, 1, 1, 1]], 3)],
    constraints=["1 ≤ nums.length ≤ 10^4"],
    hints=["Think of BFS levels: all indices reachable with j jumps form a window."],
    approaches=[approach(
        name="Window of Reachable Indices", pattern="greedy", time="O(n)", space="O(1)",
        idea="""
        The indices reachable with the same number of jumps form a window. Scan the current window while tracking the farthest index the next jump could reach. When you finish a window, take one jump: the next window ends at that farthest point.
        """,
        viz=viz(arr="nums", ptr={"i": "i", "end": "end", "far": "far"}, win=("locals().get('i', 0)", "end"), vars=["jumps"]),
        py='''
        def fewest_hops(nums):
            jumps = end = far = 0
            for i in range(len(nums) - 1):
                far = max(far, i + nums[i])
                if i == end:
                    jumps, end = jumps + 1, far  #> The window ends here, so take jump {jumps}. The next window reaches index {end}.
            return jumps
        ''',
        java='''
        class Solution {
            public int fewestHops(int[] nums) {
                int jumps = 0, end = 0, far = 0;
                for (int i = 0; i < nums.length - 1; i++) {
                    far = Math.max(far, i + nums[i]);
                    if (i == end) { jumps++; end = far; } //>
                }
                return jumps;
            }
        }
        ''',
    )],
)

problem(
    id="gas-loop",
    title="Where to Start a Fuel Loop",
    difficulty="Medium",
    topics=["Array", "Greedy"],
    statement="""
    Stations stand in a circle. At station `i` you may fill `gas[i]` units; driving to the next station costs
    `cost[i]`. Starting with an empty tank, return the station index from which you can drive the whole loop once,
    or `-1` if impossible. The answer is unique when it exists.
    """,
    examples=[([[1, 2, 3, 4, 5], [3, 4, 5, 1, 2]], 3, None), ([[2, 3, 4], [3, 4, 3]], -1, None)],
    tests=[([[5], [4]], 0), ([[3, 1, 1], [1, 2, 2]], 0)],
    constraints=["1 ≤ n ≤ 10^5"],
    hints=["If total gas < total cost, it's impossible.", "If the tank goes negative, no station since the start works: restart after it."],
    approaches=[approach(
        name="Greedy Restart", pattern="greedy", time="O(n)", space="O(1)",
        idea="""
        If total gas is less than total cost, no start works. Otherwise drive from a candidate start; whenever the tank goes negative at station i, no station between the start and i can work either, so restart from i + 1 with an empty tank.
        """,
        viz=viz(arrays=[("gas", {"start": "start", "i": "i"}), ("cost", {"i": "i"})], vars=["tank", "total"]),
        py='''
        def start_station(gas, cost):
            total = tank = start = 0
            for i in range(len(gas)):
                total += gas[i] - cost[i]
                tank += gas[i] - cost[i]
                if tank < 0:
                    start, tank = i + 1, 0  #> The tank went negative at station {i}, so restart from station {start}.
            return start if total >= 0 else -1
        ''',
        java='''
        class Solution {
            public int startStation(int[] gas, int[] cost) {
                int total = 0, tank = 0, start = 0;
                for (int i = 0; i < gas.length; i++) {
                    total += gas[i] - cost[i];
                    tank += gas[i] - cost[i];
                    if (tank < 0) { start = i + 1; tank = 0; } //>
                }
                return total >= 0 ? start : -1;
            }
        }
        ''',
    )],
)

problem(
    id="label-partitions",
    title="Split So Each Letter Stays in One Part",
    difficulty="Medium",
    topics=["String", "Greedy", "Two Pointers"],
    patterns=["two-pointers"],
    statement="""
    Split the lowercase string `s` into as many parts as possible so every letter appears in at most one part.
    Return the sizes of the parts in order.
    """,
    examples=[(["ababcbacadefegdehijhklij"], [9, 7, 8], None), (["eccbbbbdec"], [10], None)],
    tests=[(["a"], [1]), (["abc"], [1, 1, 1])],
    constraints=["1 ≤ s.length ≤ 500"],
    hints=["Record each letter's last position.", "A part can close once you pass the last position of every letter in it."],
    approaches=[approach(
        name="Two Pointers With Last Positions", pattern="two-pointers", time="O(n)", space="O(1)",
        idea="""
        Record where each letter appears last. Grow the current part with a `right` pointer; the part must stretch at least to the last position of every letter it contains (`end`).

        When `right` reaches `end`, close the part, record its size, and start the next part at `left = right + 1`.
        """,
        viz=viz(arr="s", ptr={"left": "left", "right": "right", "end": "end"}, win=("left", "locals().get('right', -1)"), out="sizes"),
        py='''
        def partition_sizes(s):
            last = {ch: i for i, ch in enumerate(s)}
            sizes, left, end = [], 0, 0
            for right, ch in enumerate(s):
                end = max(end, last[ch])
                if right == end:
                    sizes.append(right - left + 1)  #> Every letter in {q(s[left:right + 1])} ends here: a part of size {sizes[-1]}.
                    left = right + 1
            return sizes
        ''',
        java='''
        class Solution {
            public List<Integer> partitionSizes(String s) {
                int[] last = new int[26];
                for (int i = 0; i < s.length(); i++) last[s.charAt(i) - 'a'] = i;
                List<Integer> sizes = new ArrayList<>();
                for (int right = 0, left = 0, end = 0; right < s.length(); right++) {
                    end = Math.max(end, last[s.charAt(right) - 'a']);
                    if (right == end) { sizes.add(right - left + 1); left = right + 1; } //>
                }
                return sizes;
            }
        }
        ''',
    )],
)

problem(
    id="cookie-matching",
    title="Hand Out Cookies",
    difficulty="Easy",
    topics=["Array", "Greedy", "Two Pointers", "Sorting"],
    patterns=["two-pointers"],
    statement="""
    Child `i` is content with a cookie of size at least `greed[i]`; cookie `j` has size `sizes[j]`. Each child gets at
    most one cookie. Return the maximum number of content children.
    """,
    examples=[([[1, 2, 3], [1, 1]], 1, None), ([[1, 2], [1, 2, 3]], 2, None)],
    tests=[([[], [1]], 0), ([[5, 1], [4, 1]], 1), ([[2, 2, 3], [1, 2, 2, 3]], 3)],
    constraints=["0 ≤ greed.length, sizes.length ≤ 3·10^4"],
    hints=["Sort both lists.", "Give the smallest cookie that satisfies the least greedy child."],
    approaches=[approach(
        name="Sort + Two Pointers", pattern="two-pointers", time="O(n log n)", space="O(1) extra",
        idea="""
        Sort children by greed and cookies by size. Pointer `child` waits for a cookie; pointer `cookie` scans sizes. If the cookie is big enough, the child is happy and both move; otherwise the cookie is too small for anyone left and is skipped.
        """,
        viz=viz(arrays=[("greed", {"child": "child"}), ("sizes", {"cookie": "cookie"})]),
        demo=[[2, 2, 3], [1, 2, 2, 3]],
        py='''
        def content_children(greed, sizes):
            greed.sort()
            sizes.sort()
            child = 0
            for cookie in range(len(sizes)):
                if child < len(greed) and sizes[cookie] >= greed[child]:
                    child += 1  #> A cookie of size {sizes[cookie]} satisfies a child with greed {greed[child - 1]}.
            return child
        ''',
        java='''
        class Solution {
            public int contentChildren(int[] greed, int[] sizes) {
                Arrays.sort(greed);
                Arrays.sort(sizes);
                int child = 0;
                for (int cookie = 0; cookie < sizes.length; cookie++)
                    if (child < greed.length && sizes[cookie] >= greed[child]) child++; //>
                return child;
            }
        }
        ''',
    )],
)
