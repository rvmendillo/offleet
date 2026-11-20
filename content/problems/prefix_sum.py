"""Prefix Sum problems (original statements)."""
from dsl import problem, approach, viz

problem(
    id="range-sum-queries",
    title="Instant Range Sums",
    difficulty="Easy",
    topics=["Array", "Prefix Sum", "Design"],
    design=True,
    statement="""
    Build a class `RangeSum` that is created from an integer array `nums` and answers many queries
    `query(l, r)`: the sum of `nums[l..r]` inclusive. Each query must be O(1).
    """,
    examples=[((["RangeSum", "query", "query", "query"], [[[-2, 0, 3, -5, 2, -1]], [0, 2], [2, 5], [0, 5]]), [None, 1, -1, -3], None)],
    tests=[((["RangeSum", "query"], [[[5]], [0, 0]]), [None, 5]), ((["RangeSum", "query", "query"], [[[1, 2, 3, 4]], [1, 3], [3, 3]]), [None, 9, 4])],
    constraints=["1 ≤ nums.length ≤ 10^4", "up to 10^4 queries"],
    hints=["Precompute prefix[i] = sum of the first i values.", "sum(l..r) = prefix[r + 1] − prefix[l]."],
    approaches=[approach(
        name="Prefix Sums", pattern="prefix-sum", time="O(n) build, O(1) query", space="O(n)",
        idea="""
        Precompute `prefix`, where `prefix[i]` is the sum of the first i numbers. The sum of any range is then the difference of two prefix values.

        Building costs one pass; every query afterwards is a single subtraction.
        """,
        viz=viz(arrays=[("self.prefix", {"l": "l", "r+1": "r + 1"}, None, None, "prefix")]),
        py='''
        class RangeSum:
            def __init__(self, nums):
                self.prefix = [0]
                for x in nums:
                    self.prefix.append(self.prefix[-1] + x)  #> Running total: {self.prefix[-1]}.

            def query(self, l, r):
                return self.prefix[r + 1] - self.prefix[l]  #> prefix[{r + 1}] minus prefix[{l}] = {ret}.
        ''',
        java='''
        class RangeSum {
            private final int[] prefix;

            RangeSum(int[] nums) {
                prefix = new int[nums.length + 1];
                for (int i = 0; i < nums.length; i++) prefix[i + 1] = prefix[i] + nums[i]; //>
            }

            public int query(int l, int r) {
                return prefix[r + 1] - prefix[l]; //>
            }
        }
        ''',
    )],
)

problem(
    id="subarrays-sum-to-k",
    title="Count Runs Summing to k",
    difficulty="Medium",
    topics=["Array", "Prefix Sum", "Hash Map"],
    statement="""
    Return the number of contiguous subarrays of `nums` whose sum equals `k`. Values may be negative.
    """,
    examples=[([[1, 1, 1], 2], 2, None), ([[1, 2, 3], 3], 2, "[1, 2] and [3]")],
    tests=[([[1], 0], 0), ([[1, -1, 0], 0], 3), ([[3, 4, 7, 2, -3, 1, 4, 2], 7], 4)],
    constraints=["1 ≤ nums.length ≤ 2·10^4", "negative values allowed, so a sliding window does not work"],
    hints=["A run (i..j] sums to k exactly when prefix[j] − prefix[i] = k.", "Count earlier prefixes equal to prefix − k."],
    approaches=[approach(
        name="Prefix Sum + Hash Map", pattern="prefix-sum", time="O(n)", space="O(n)",
        idea="""
        Keep the running prefix sum. A run ending here sums to k exactly when some earlier prefix equals current − k.

        So store how many times each prefix sum has occurred, and add the count of current − k at every step. Start with prefix 0 seen once (the empty prefix).
        """,
        why="Negative numbers break the sliding window's assumption that growing the window raises the sum, which is why we need the prefix map.",
        viz=viz(arr="nums", ptr={"i": "i"}, maps=[("prefix counts", "seen")], vars=["prefix", "count"]),
        py='''
        def count_sum_k(nums, k):
            seen, prefix, count = {0: 1}, 0, 0
            for i, x in enumerate(nums):
                prefix += x
                count += seen.get(prefix - k, 0)  #> Prefix is {prefix}. Earlier prefixes equal to {prefix - k}: {seen.get(prefix - k, 0)}. Count: {count}.
                seen[prefix] = seen.get(prefix, 0) + 1
            return count
        ''',
        java='''
        class Solution {
            public int countSumK(int[] nums, int k) {
                Map<Integer, Integer> seen = new HashMap<>();
                seen.put(0, 1);
                int prefix = 0, count = 0;
                for (int x : nums) {
                    prefix += x;
                    count += seen.getOrDefault(prefix - k, 0); //>
                    seen.merge(prefix, 1, Integer::sum);
                }
                return count;
            }
        }
        ''',
    )],
)

problem(
    id="balance-index",
    title="Balance Point of an Array",
    difficulty="Easy",
    topics=["Array", "Prefix Sum"],
    statement="""
    Return the leftmost index `i` where the sum of the numbers strictly left of `i` equals the sum strictly right of
    `i`, or `-1` if no such index exists.
    """,
    examples=[([[1, 7, 3, 6, 5, 6]], 3, "1 + 7 + 3 = 11 = 5 + 6"), ([[1, 2, 3]], -1, None)],
    tests=[([[2, 1, -1]], 0), ([[0]], 0), ([[-1, -1, 0, 1, 1, 0]], 5)],
    constraints=["1 ≤ nums.length ≤ 10^4"],
    hints=["right sum = total − left sum − nums[i]."],
    approaches=[approach(
        name="Prefix Sum", pattern="prefix-sum", time="O(n)", space="O(1)",
        idea="""
        Compute the total once. Walking left to right, keep the sum of everything left of i; the right side is total − left − nums[i].

        The first index where both sides are equal is the answer.
        """,
        viz=viz(arr="nums", ptr={"i": "i"}, vars=["left", "total"]),
        py='''
        def balance_index(nums):
            total, left = sum(nums), 0
            for i, x in enumerate(nums):
                if left == total - left - x:
                    return i  #> At index {i}, both sides sum to {left}.
                left += x  #> Left of index {i + 1} sums to {left}; the right side is {total - left - (nums[i + 1] if i + 1 < len(nums) else 0)}.
            return -1
        ''',
        java='''
        class Solution {
            public int balanceIndex(int[] nums) {
                int total = 0, left = 0;
                for (int x : nums) total += x;
                for (int i = 0; i < nums.length; i++) {
                    if (left == total - left - nums[i]) return i; //>
                    left += nums[i]; //>
                }
                return -1;
            }
        }
        ''',
    )],
)

problem(
    id="equal-zeros-ones",
    title="Longest Run With Equal 0s and 1s",
    difficulty="Medium",
    topics=["Array", "Prefix Sum", "Hash Map"],
    statement="""
    `nums` contains only 0s and 1s. Return the length of the longest contiguous subarray with the same number of
    0s and 1s.
    """,
    examples=[([[0, 1]], 2, None), ([[0, 1, 1, 1, 0, 0]], 6, None)],
    tests=[([[0, 0, 0]], 0), ([[1, 0, 1, 0, 1]], 4), ([[0, 1, 0]], 2)],
    constraints=["1 ≤ nums.length ≤ 10^5"],
    hints=["Count a 1 as +1 and a 0 as −1: equal counts means a running balance that repeats."],
    approaches=[approach(
        name="Prefix Balance + Hash Map", pattern="prefix-sum", time="O(n)", space="O(n)",
        idea="""
        Treat each 1 as +1 and each 0 as −1, and keep a running balance. If the same balance shows up at two indexes, the stretch between them has equal 0s and 1s.

        Remember the first index of each balance; the longest gap between equal balances is the answer.
        """,
        viz=viz(arr="nums", ptr={"i": "i"}, maps=[("first index of balance", "first")], vars=["bal", "best"]),
        py='''
        def longest_equal(nums):
            first, bal, best = {0: -1}, 0, 0
            for i, x in enumerate(nums):
                bal += 1 if x == 1 else -1
                if bal in first:
                    best = max(best, i - first[bal])  #> Balance {bal} was seen at index {first[bal]}, so indexes {first[bal] + 1} to {i} are even. Best: {best}.
                else:
                    first[bal] = i  #> Balance {bal} appears for the first time at index {i}.
            return best
        ''',
        java='''
        class Solution {
            public int longestEqual(int[] nums) {
                Map<Integer, Integer> first = new HashMap<>();
                first.put(0, -1);
                int bal = 0, best = 0;
                for (int i = 0; i < nums.length; i++) {
                    bal += nums[i] == 1 ? 1 : -1;
                    if (first.containsKey(bal)) best = Math.max(best, i - first.get(bal)); //>
                    else first.put(bal, i); //>
                }
                return best;
            }
        }
        ''',
    )],
)

problem(
    id="sums-divisible-by-k",
    title="Runs With Sum Divisible by k",
    difficulty="Medium",
    topics=["Array", "Prefix Sum", "Hash Map", "Math"],
    statement="""
    Return the number of non-empty contiguous subarrays of `nums` whose sum is divisible by `k`.
    """,
    examples=[([[4, 5, 0, -2, -3, 1], 5], 7, None), ([[5], 9], 0, None)],
    tests=[([[0], 3], 1), ([[2, 2, 2], 2], 6), ([[-1, 2, 9], 2], 2)],
    constraints=["1 ≤ nums.length ≤ 3·10^4", "2 ≤ k ≤ 10^4"],
    hints=["Two prefixes with the same remainder mod k bracket a divisible run.",
           "Normalise negative remainders into 0..k−1."],
    approaches=[approach(
        name="Prefix Remainders", pattern="prefix-sum", time="O(n + k)", space="O(k)",
        idea="""
        A run's sum is divisible by k exactly when the prefix sums before and after it leave the same remainder mod k.

        Count remainders as we go; each new prefix forms a valid run with every earlier prefix that had the same remainder.
        """,
        viz=viz(arr="nums", ptr={"i": "i"}, vars=["rem", "count"]),
        py='''
        def divisible_runs(nums, k):
            seen = [0] * k
            seen[0] = 1
            rem = count = 0
            for i, x in enumerate(nums):
                rem = (rem + x) % k
                count += seen[rem]  #> Remainder {rem} was seen {plural(seen[rem], "time")} before. Count: {count}.
                seen[rem] += 1
            return count
        ''',
        java='''
        class Solution {
            public int divisibleRuns(int[] nums, int k) {
                int[] seen = new int[k];
                seen[0] = 1;
                int rem = 0, count = 0;
                for (int x : nums) {
                    rem = ((rem + x) % k + k) % k;
                    count += seen[rem]++; //>
                }
                return count;
            }
        }
        ''',
    )],
)

problem(
    id="seat-bookings",
    title="Seats Booked per Flight",
    difficulty="Medium",
    topics=["Array", "Prefix Sum", "Difference Array"],
    statement="""
    Flights are numbered `1` to `n`. Each booking `[first, last, seats]` reserves `seats` seats on every flight from
    `first` to `last` inclusive. Return an array where entry `i` is the total seats booked on flight `i + 1`.
    """,
    examples=[([[[1, 2, 10], [2, 3, 20], [2, 5, 25]], 5], [10, 55, 45, 25, 25], None), ([[[1, 2, 10], [2, 2, 15]], 2], [10, 25], None)],
    tests=[([[[1, 1, 5]], 1], [5]), ([[[2, 3, 4]], 4], [0, 4, 4, 0])],
    constraints=["1 ≤ n ≤ 2·10^4", "up to 2·10^4 bookings"],
    hints=["Record +seats where a booking starts and −seats right after it ends.", "A prefix sum turns those marks into totals."],
    approaches=[approach(
        name="Difference Array + Prefix Sum", pattern="prefix-sum", time="O(n + b)", space="O(n)",
        idea="""
        Instead of adding seats to every flight in a range, mark the change: add the seats at the first flight and subtract them just after the last one.

        One running sum over these marks then produces every flight's total.
        """,
        viz=viz(arr="diff", label="difference marks", vars=["running"], out="res"),
        py='''
        def seat_totals(bookings, n):
            diff = [0] * (n + 1)
            for first, last, seats in bookings:
                diff[first - 1] += seats
                diff[last] -= seats  #> Booking {first} to {last}: +{seats} at flight {first}, −{seats} after flight {last}.
            res, running = [], 0
            for i in range(n):
                running += diff[i]
                res.append(running)  #> Flight {i + 1} has {running} seats booked.
            return res
        ''',
        java='''
        class Solution {
            public int[] seatTotals(int[][] bookings, int n) {
                int[] diff = new int[n + 1];
                for (int[] b : bookings) { diff[b[0] - 1] += b[2]; diff[b[1]] -= b[2]; } //>
                int[] res = new int[n];
                for (int i = 0, running = 0; i < n; i++) res[i] = running += diff[i]; //>
                return res;
            }
        }
        ''',
    )],
)
