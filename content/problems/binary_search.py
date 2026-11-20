"""Binary Search problems (original statements)."""
from dsl import problem, approach, viz

BS_VIZ = dict(arr="nums", ptr={"lo": "lo", "mid": "mid", "hi": "hi"}, win=("lo", "hi"))

problem(
    id="binary-search",
    title="Find a Value in a Sorted List",
    difficulty="Easy",
    topics=["Array", "Binary Search"],
    statement="""
    `nums` is sorted ascending with distinct values. Return the index of `target`, or `-1` if it isn't there.
    Your solution must run in O(log n).
    """,
    examples=[([[-1, 0, 3, 5, 9, 12], 9], 4, None), ([[-1, 0, 3, 5, 9, 12], 2], -1, None)],
    tests=[([[5], 5], 0), ([[1, 3], 3], 1), ([[2, 4, 6, 8, 10], 2], 0)],
    constraints=["1 ≤ nums.length ≤ 10^4"],
    hints=["Compare with the middle and discard half."],
    approaches=[approach(
        name="Binary Search", pattern="binary-search", time="O(log n)", space="O(1)",
        idea="""
        Keep a search range from LO to HI. Look at the middle value: if it is the target we're done; if it's too small the target must be to the right, otherwise to the left.

        Each step throws away half of the range, so even a million values take only about twenty steps.
        """,
        viz=viz(**BS_VIZ, vars=["target"]),
        py='''
        def search(nums, target):
            lo, hi = 0, len(nums) - 1  #> The search range is the whole list, index {lo} to {hi}.
            while lo <= hi:
                mid = (lo + hi) // 2  #> The middle is index {mid}, value {nums[mid]}.
                if nums[mid] == target:
                    return mid  #> Found {target} at index {mid}!
                if nums[mid] < target:
                    lo = mid + 1  #> {nums[mid]} is too small. Keep the right half: {lo} to {hi}.
                else:
                    hi = mid - 1  #> {nums[mid]} is too big. Keep the left half: {lo} to {hi}.
            return -1
        ''',
        java='''
        class Solution {
            public int search(int[] nums, int target) {
                int lo = 0, hi = nums.length - 1; //>
                while (lo <= hi) {
                    int mid = (lo + hi) >>> 1; //>
                    if (nums[mid] == target) return mid; //>
                    if (nums[mid] < target) lo = mid + 1; //>
                    else hi = mid - 1; //>
                }
                return -1;
            }
        }
        ''',
    )],
)

problem(
    id="insert-position",
    title="Where Would It Go?",
    difficulty="Easy",
    topics=["Array", "Binary Search"],
    statement="""
    `nums` is sorted with distinct values. Return the index of `target` if present; otherwise return the index where
    it would be inserted to keep the order. Use O(log n).
    """,
    examples=[([[1, 3, 5, 6], 5], 2, None), ([[1, 3, 5, 6], 2], 1, None)],
    tests=[([[1, 3, 5, 6], 7], 4), ([[1, 3, 5, 6], 0], 0), ([[4], 4], 0)],
    constraints=["1 ≤ nums.length ≤ 10^4"],
    hints=["Find the first index whose value is ≥ target."],
    approaches=[approach(
        name="Binary Search (lower bound)", pattern="binary-search", time="O(log n)", space="O(1)",
        idea="""
        We want the first position whose value is at least the target. Use a half-open range [LO, HI): if the middle value is smaller than the target, the answer is to the right; otherwise the middle might be the answer, so keep it.

        When LO meets HI, that's the insert position.
        """,
        viz=viz(**BS_VIZ),
        py='''
        def insert_position(nums, target):
            lo, hi = 0, len(nums)
            while lo < hi:
                mid = (lo + hi) // 2
                if nums[mid] < target:
                    lo = mid + 1  #> {nums[mid]} is less than {target}, so the answer is after index {mid}.
                else:
                    hi = mid  #> {nums[mid]} is at least {target}, so the answer is at index {mid} or before.
            return lo  #> LO and HI met at index {lo}.
        ''',
        java='''
        class Solution {
            public int insertPosition(int[] nums, int target) {
                int lo = 0, hi = nums.length;
                while (lo < hi) {
                    int mid = (lo + hi) >>> 1;
                    if (nums[mid] < target) lo = mid + 1; //>
                    else hi = mid; //>
                }
                return lo; //>
            }
        }
        ''',
    )],
)

problem(
    id="first-and-last",
    title="First and Last Position of a Value",
    difficulty="Medium",
    topics=["Array", "Binary Search"],
    statement="""
    `nums` is sorted ascending (values may repeat). Return `[first, last]`, the first and last index of `target`, or
    `[-1, -1]` if it does not appear. Use O(log n).
    """,
    examples=[([[5, 7, 7, 8, 8, 10], 8], [3, 4], None), ([[5, 7, 7, 8, 8, 10], 6], [-1, -1], None)],
    tests=[([[], 0], [-1, -1]), ([[2, 2], 2], [0, 1]), ([[1, 2, 3], 3], [2, 2])],
    constraints=["0 ≤ nums.length ≤ 10^5"],
    hints=["Run a lower-bound search for target and for target + 1."],
    approaches=[approach(
        name="Two Lower-Bound Searches", pattern="binary-search", time="O(log n)", space="O(1)",
        idea="""
        The first position of the target is the lower bound of target. The last position is one before the lower bound of target + 1.

        So the same small binary search answers both questions.
        """,
        viz=viz(**BS_VIZ, vars=["x"]),
        py='''
        def first_and_last(nums, target):
            def lower(x):
                lo, hi = 0, len(nums)
                while lo < hi:
                    mid = (lo + hi) // 2
                    if nums[mid] < x:
                        lo = mid + 1
                    else:
                        hi = mid
                return lo  #> The first index with a value of at least {x} is {lo}.

            first = lower(target)
            if first == len(nums) or nums[first] != target:
                return [-1, -1]
            return [first, lower(target + 1) - 1]  #> The last copy sits just before that: index {lower(target + 1) - 1}.
        ''',
        java='''
        class Solution {
            public int[] firstAndLast(int[] nums, int target) {
                int first = lower(nums, target);
                if (first == nums.length || nums[first] != target) return new int[]{-1, -1};
                return new int[]{first, lower(nums, target + 1) - 1}; //>2
            }

            private int lower(int[] nums, int x) {
                int lo = 0, hi = nums.length;
                while (lo < hi) {
                    int mid = (lo + hi) >>> 1;
                    if (nums[mid] < x) lo = mid + 1; else hi = mid;
                }
                return lo; //>1
            }
        }
        ''',
    )],
)

problem(
    id="rotated-search",
    title="Search a Rotated Sorted List",
    difficulty="Medium",
    topics=["Array", "Binary Search"],
    statement="""
    A sorted array of distinct values was rotated at an unknown pivot (for example `[0,1,2,4,5,6,7]` became
    `[4,5,6,7,0,1,2]`). Return the index of `target`, or `-1`. Use O(log n).
    """,
    examples=[([[4, 5, 6, 7, 0, 1, 2], 0], 4, None), ([[4, 5, 6, 7, 0, 1, 2], 3], -1, None)],
    tests=[([[1], 0], -1), ([[3, 1], 1], 1), ([[5, 1, 3], 5], 0)],
    constraints=["1 ≤ nums.length ≤ 5000", "values are distinct"],
    hints=["At least one half around mid is properly sorted.", "Check whether the target lies inside that sorted half."],
    approaches=[approach(
        name="Binary Search", pattern="binary-search", time="O(log n)", space="O(1)",
        idea="""
        Cut the range at the middle. One of the two halves is always in sorted order, which we can tell by comparing its ends.

        If the target lies within the sorted half's range, search there; otherwise search the other half.
        """,
        viz=viz(**BS_VIZ, vars=["target"]),
        py='''
        def rotated_search(nums, target):
            lo, hi = 0, len(nums) - 1
            while lo <= hi:
                mid = (lo + hi) // 2
                if nums[mid] == target:
                    return mid  #> Found {target} at index {mid}.
                if nums[lo] <= nums[mid]:
                    if nums[lo] <= target < nums[mid]:
                        hi = mid - 1  #> The left half is sorted and contains {target}: go left.
                    else:
                        lo = mid + 1  #> The left half is sorted but lacks {target}: go right.
                else:
                    if nums[mid] < target <= nums[hi]:
                        lo = mid + 1  #> The right half is sorted and contains {target}: go right.
                    else:
                        hi = mid - 1  #> The right half is sorted but lacks {target}: go left.
            return -1
        ''',
        java='''
        class Solution {
            public int rotatedSearch(int[] nums, int target) {
                int lo = 0, hi = nums.length - 1;
                while (lo <= hi) {
                    int mid = (lo + hi) >>> 1;
                    if (nums[mid] == target) return mid; //>
                    if (nums[lo] <= nums[mid]) {
                        if (nums[lo] <= target && target < nums[mid]) hi = mid - 1; //>
                        else lo = mid + 1; //>
                    } else {
                        if (nums[mid] < target && target <= nums[hi]) lo = mid + 1; //>
                        else hi = mid - 1; //>
                    }
                }
                return -1;
            }
        }
        ''',
    )],
)

problem(
    id="rotated-minimum",
    title="Smallest Value After Rotation",
    difficulty="Medium",
    topics=["Array", "Binary Search"],
    statement="""
    A sorted array of distinct values has been rotated some number of times. Return its minimum value in O(log n).
    """,
    examples=[([[3, 4, 5, 1, 2]], 1, None), ([[11, 13, 15, 17]], 11, None)],
    tests=[([[2, 1]], 1), ([[4, 5, 6, 7, 0, 1, 2]], 0), ([[1]], 1)],
    constraints=["1 ≤ nums.length ≤ 5000"],
    hints=["Compare the middle with the right end."],
    approaches=[approach(
        name="Binary Search", pattern="binary-search", time="O(log n)", space="O(1)",
        idea="""
        Compare the middle value with the last value of the range. If the middle is bigger, the drop (and the minimum) is to the right of mid. Otherwise the minimum is at mid or to its left.
        """,
        viz=viz(**BS_VIZ),
        py='''
        def rotated_min(nums):
            lo, hi = 0, len(nums) - 1
            while lo < hi:
                mid = (lo + hi) // 2
                if nums[mid] > nums[hi]:
                    lo = mid + 1  #> {nums[mid]} is bigger than {nums[hi]}, so the minimum is right of index {mid}.
                else:
                    hi = mid  #> {nums[mid]} is not bigger than the end, so the minimum is at index {mid} or left of it.
            return nums[lo]  #> The range narrowed to index {lo}: the minimum is {nums[lo]}.
        ''',
        java='''
        class Solution {
            public int rotatedMin(int[] nums) {
                int lo = 0, hi = nums.length - 1;
                while (lo < hi) {
                    int mid = (lo + hi) >>> 1;
                    if (nums[mid] > nums[hi]) lo = mid + 1; //>
                    else hi = mid; //>
                }
                return nums[lo]; //>
            }
        }
        ''',
    )],
)

problem(
    id="integer-square-root",
    title="Whole-Number Square Root",
    difficulty="Easy",
    topics=["Math", "Binary Search"],
    statement="""
    Given a non-negative integer `x`, return the largest integer `r` with `r × r ≤ x`, without using any built-in
    power or square-root function.
    """,
    examples=[([8], 2, "2 × 2 = 4 ≤ 8 but 3 × 3 = 9 > 8."), ([16], 4, None)],
    tests=[([0], 0), ([1], 1), ([2147395599], 46339)],
    constraints=["0 ≤ x ≤ 2^31 − 1"],
    hints=["Binary search the answer between 0 and x."],
    approaches=[approach(
        name="Binary Search on the Answer", pattern="binary-search", time="O(log x)", space="O(1)",
        idea="""
        The answer lies between 0 and x. Guess the middle: if its square fits under x, the answer is at least that big; otherwise it's smaller. Keep halving until the range closes.
        """,
        viz=viz(vars=["lo", "mid", "hi"]),
        demo=[40],
        py='''
        def int_sqrt(x):
            lo, hi = 0, x
            while lo < hi:
                mid = (lo + hi + 1) // 2
                if mid * mid <= x:
                    lo = mid  #> {mid} squared is {mid * mid}, which fits. The answer is at least {mid}.
                else:
                    hi = mid - 1  #> {mid} squared is {mid * mid}, too big. The answer is below {mid}.
            return lo
        ''',
        java='''
        class Solution {
            public int intSqrt(int x) {
                long lo = 0, hi = x;
                while (lo < hi) {
                    long mid = (lo + hi + 1) / 2;
                    if (mid * mid <= x) lo = mid; //>
                    else hi = mid - 1; //>
                }
                return (int) lo;
            }
        }
        ''',
    )],
)

problem(
    id="snack-speed",
    title="Slowest Snacking Speed",
    difficulty="Medium",
    topics=["Array", "Binary Search"],
    statement="""
    There are `piles[i]` snacks in pile `i`. Each hour you pick one pile and eat up to `k` snacks from it (if it has
    fewer, you finish it and wait for the hour to end). Return the smallest integer speed `k` that lets you finish all
    piles within `h` hours.
    """,
    examples=[([[3, 6, 7, 11], 8], 4, None), ([[30, 11, 23, 4, 20], 5], 30, None)],
    tests=[([[30, 11, 23, 4, 20], 6], 23), ([[1], 1], 1), ([[5, 5], 10], 1)],
    constraints=["1 ≤ piles.length ≤ h ≤ 10^9", "1 ≤ piles[i] ≤ 10^9"],
    hints=["If speed k works, every faster speed works too.", "Binary search on k; hours needed = Σ ceil(pile / k)."],
    approaches=[approach(
        name="Binary Search on the Answer", pattern="binary-search", time="O(n log m)", space="O(1)",
        idea="""
        Faster speeds always finish sooner, so the possible speeds split into "too slow" then "fast enough". Binary search for the first speed that is fast enough.

        For a guessed speed, the hours needed are the sum over piles of pile divided by speed, rounded up.
        """,
        viz=viz(arr="piles", vars=["lo", "hi", "k", "hours"]),
        py='''
        def min_speed(piles, h):
            lo, hi = 1, max(piles)
            while lo < hi:
                k = (lo + hi) // 2
                hours = sum((p + k - 1) // k for p in piles)
                if hours <= h:
                    hi = k  #> At speed {k} we need {hours} hours, which fits in {h}. Try slower.
                else:
                    lo = k + 1  #> At speed {k} we need {hours} hours, more than {h}. Go faster.
            return lo
        ''',
        java='''
        class Solution {
            public int minSpeed(int[] piles, int h) {
                int lo = 1, hi = 0;
                for (int p : piles) hi = Math.max(hi, p);
                while (lo < hi) {
                    int k = lo + (hi - lo) / 2;
                    long hours = 0;
                    for (int p : piles) hours += (p + k - 1) / k;
                    if (hours <= h) hi = k; //>
                    else lo = k + 1; //>
                }
                return lo;
            }
        }
        ''',
    )],
)

problem(
    id="ship-capacity",
    title="Smallest Truck for the Deadline",
    difficulty="Medium",
    topics=["Array", "Binary Search", "Greedy"],
    statement="""
    Packages with weights `weights` must be shipped in the given order within `days` days. Each day you load packages
    onto a truck in order until adding the next one would exceed the truck's capacity. Return the smallest capacity
    that ships everything on time.
    """,
    examples=[([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5], 15, None), ([[3, 2, 2, 4, 1, 4], 3], 6, None)],
    tests=[([[1, 2, 3, 1, 1], 4], 3), ([[10], 1], 10), ([[5, 5, 5], 3], 5)],
    constraints=["1 ≤ days ≤ weights.length ≤ 5·10^4"],
    hints=["The capacity is between the heaviest package and the total weight.", "Check a capacity greedily, then binary search."],
    approaches=[approach(
        name="Binary Search on the Answer", pattern="binary-search", time="O(n log S)", space="O(1)",
        idea="""
        Any capacity from the heaviest package up to the total weight might work, and bigger is always easier. Binary search that range.

        To test a capacity, fill each day greedily and count the days used.
        """,
        viz=viz(arr="weights", vars=["lo", "hi", "cap", "need"]),
        py='''
        def min_capacity(weights, days):
            lo, hi = max(weights), sum(weights)
            while lo < hi:
                cap = (lo + hi) // 2
                need, load = 1, 0
                for w in weights:
                    if load + w > cap:
                        need, load = need + 1, 0
                    load += w
                if need <= days:
                    hi = cap  #> Capacity {cap} needs {need} days. That works, so try smaller.
                else:
                    lo = cap + 1  #> Capacity {cap} needs {need} days, too many. Go bigger.
            return lo
        ''',
        java='''
        class Solution {
            public int minCapacity(int[] weights, int days) {
                int lo = 0, hi = 0;
                for (int w : weights) { lo = Math.max(lo, w); hi += w; }
                while (lo < hi) {
                    int cap = (lo + hi) >>> 1, need = 1, load = 0;
                    for (int w : weights) {
                        if (load + w > cap) { need++; load = 0; }
                        load += w;
                    }
                    if (need <= days) hi = cap; //>
                    else lo = cap + 1; //>
                }
                return lo;
            }
        }
        ''',
    )],
)

problem(
    id="find-a-peak",
    title="Find a Peak",
    difficulty="Medium",
    topics=["Array", "Binary Search"],
    statement="""
    A peak is a value strictly greater than its neighbours (treat outside the array as −∞). Adjacent values are
    never equal. Return the index of any peak in O(log n). For this exercise the input has exactly one peak.
    """,
    examples=[([[1, 2, 3, 1]], 2, None), ([[1, 3, 5, 4, 2]], 2, None)],
    tests=[([[7]], 0), ([[2, 1]], 0), ([[1, 2]], 1)],
    constraints=["1 ≤ nums.length ≤ 1000"],
    hints=["If mid is lower than its right neighbour, a peak exists to the right."],
    approaches=[approach(
        name="Binary Search on the Slope", pattern="binary-search", time="O(log n)", space="O(1)",
        idea="""
        Look at the middle and its right neighbour. If the slope goes up, there must be a peak to the right; if it goes down, a peak is at mid or to the left. Halve the range accordingly.
        """,
        viz=viz(**BS_VIZ),
        py='''
        def find_peak(nums):
            lo, hi = 0, len(nums) - 1
            while lo < hi:
                mid = (lo + hi) // 2
                if nums[mid] < nums[mid + 1]:
                    lo = mid + 1  #> Uphill from {nums[mid]} to {nums[mid + 1]}: a peak is to the right.
                else:
                    hi = mid  #> Downhill after {nums[mid]}: a peak is here or to the left.
            return lo
        ''',
        java='''
        class Solution {
            public int findPeak(int[] nums) {
                int lo = 0, hi = nums.length - 1;
                while (lo < hi) {
                    int mid = (lo + hi) >>> 1;
                    if (nums[mid] < nums[mid + 1]) lo = mid + 1; //>
                    else hi = mid; //>
                }
                return lo;
            }
        }
        ''',
    )],
)

problem(
    id="search-sorted-grid",
    title="Search a Fully Sorted Grid",
    difficulty="Medium",
    topics=["Matrix", "Binary Search"],
    statement="""
    In the `m × n` grid `grid`, each row is sorted left to right and each row's first value is greater than the
    previous row's last value. Return `true` if `target` is in the grid, in O(log(m·n)).
    """,
    examples=[([[[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 3], True, None), ([[[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 13], False, None)],
    tests=[([[[1]], 1], True), ([[[1, 2], [3, 4]], 4], True), ([[[1, 2], [3, 4]], 0], False)],
    constraints=["1 ≤ m, n ≤ 100"],
    hints=["Reading row by row gives one long sorted list.", "Index k maps to row k // n and column k % n."],
    approaches=[approach(
        name="Binary Search as One List", pattern="binary-search", time="O(log(m·n))", space="O(1)",
        idea="""
        Read row by row, the grid is one long sorted list of m·n values. Binary search positions 0 to m·n − 1 and convert each position into a row and column.
        """,
        viz=viz(grid=("grid", {"mid": ("mid // len(grid[0])", "mid % len(grid[0])")}, None, "grid"), vars=["lo", "hi"]),
        py='''
        def search_grid(grid, target):
            m, n = len(grid), len(grid[0])
            lo, hi = 0, m * n - 1
            while lo <= hi:
                mid = (lo + hi) // 2
                val = grid[mid // n][mid % n]  #> Position {mid} is row {mid // n}, column {mid % n}: value {val}.
                if val == target:
                    return True
                if val < target:
                    lo = mid + 1
                else:
                    hi = mid - 1
            return False
        ''',
        java='''
        class Solution {
            public boolean searchGrid(int[][] grid, int target) {
                int m = grid.length, n = grid[0].length, lo = 0, hi = m * n - 1;
                while (lo <= hi) {
                    int mid = (lo + hi) >>> 1, val = grid[mid / n][mid % n]; //>
                    if (val == target) return true;
                    if (val < target) lo = mid + 1; else hi = mid - 1;
                }
                return false;
            }
        }
        ''',
    )],
)
