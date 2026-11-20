"""Dynamic Programming problems (original statements). Rolling-window O(1) space wherever possible."""
from dsl import problem, approach, viz

problem(
    id="climb-stairs",
    title="Ways to Climb the Stairs",
    difficulty="Easy",
    topics=["Dynamic Programming", "Math"],
    patterns=["sliding-window"],
    statement="""
    You climb a staircase of `n` steps, taking 1 or 2 steps at a time. How many distinct ways reach the top?
    """,
    examples=[([2], 2, "1 + 1 or 2"), ([3], 3, "1 + 1 + 1, 1 + 2, 2 + 1")],
    tests=[([1], 1), ([5], 8), ([10], 89)],
    constraints=["1 ≤ n ≤ 45"],
    hints=["To stand on step i you came from step i − 1 or step i − 2.", "Only the last two answers are ever needed."],
    approaches=[approach(
        name="Rolling Window of Two", pattern="dp", time="O(n)", space="O(1)",
        idea="""
        Ways to reach step i = ways to reach step i − 1 + ways to reach step i − 2. Instead of a whole table, slide a window of the last two answers forward.
        """,
        why="This is the Fibonacci recurrence; the two-value window makes the space constant.",
        viz=viz(vars=["step", "prev", "cur"]),
        demo=[5],
        py='''
        def climb(n):
            prev, cur = 1, 1
            for step in range(2, n + 1):
                prev, cur = cur, prev + cur  #> Step {step} can be reached in {cur} ways.
            return cur
        ''',
        java='''
        class Solution {
            public int climb(int n) {
                int prev = 1, cur = 1;
                for (int step = 2; step <= n; step++) { int next = prev + cur; prev = cur; cur = next; } //>
                return cur;
            }
        }
        ''',
    )],
)

problem(
    id="cheapest-stairs",
    title="Cheapest Way Up",
    difficulty="Easy",
    topics=["Array", "Dynamic Programming"],
    statement="""
    `cost[i]` is what you pay to stand on step `i`, after which you may climb 1 or 2 steps. You can start on step 0 or
    step 1. Return the minimum cost to get past the last step.
    """,
    examples=[([[10, 15, 20]], 15, "Start on step 1 and jump over the top."), ([[1, 100, 1, 1, 1, 100, 1, 1, 100, 1]], 6, None)],
    tests=[([[0, 0]], 0), ([[5, 1]], 1)],
    constraints=["2 ≤ cost.length ≤ 1000"],
    hints=["best(i) = cost[i] + min(best(i − 1), best(i − 2))."],
    approaches=[approach(
        name="Rolling Window of Two", pattern="dp", time="O(n)", space="O(1)",
        idea="""
        The cheapest way to stand on a step is its cost plus the cheaper of the two steps below it. Keep only those last two values and roll them forward. The top is reached from either of the last two steps.
        """,
        viz=viz(arr="cost", ptr={"i": "i"}, vars=["a", "b"]),
        demo=[[1, 100, 1, 1, 1, 100, 1]],
        py='''
        def cheapest_climb(cost):
            a, b = cost[0], cost[1]
            for i in range(2, len(cost)):
                a, b = b, cost[i] + min(a, b)  #> Standing on step {i} costs at best {b}.
            return min(a, b)
        ''',
        java='''
        class Solution {
            public int cheapestClimb(int[] cost) {
                int a = cost[0], b = cost[1];
                for (int i = 2; i < cost.length; i++) { int c = cost[i] + Math.min(a, b); a = b; b = c; } //>
                return Math.min(a, b);
            }
        }
        ''',
    )],
)

problem(
    id="house-robber",
    title="Rob Houses Without Neighbours",
    difficulty="Medium",
    topics=["Array", "Dynamic Programming"],
    statement="""
    Houses on a street hold `nums[i]` money. You can't take from two adjacent houses. Return the most money you can take.
    """,
    examples=[([[1, 2, 3, 1]], 4, "Houses 0 and 2."), ([[2, 7, 9, 3, 1]], 12, "Houses 0, 2 and 4.")],
    tests=[([[5]], 5), ([[2, 1, 1, 2]], 4)],
    constraints=["1 ≤ nums.length ≤ 100"],
    hints=["At each house: skip it, or take it plus the best from two houses back."],
    approaches=[approach(
        name="Rolling Window of Two", pattern="dp", time="O(n)", space="O(1)",
        idea="""
        For each house, the best total is either the best up to the previous house (skip this one), or this house plus the best up to two houses back. Two rolling values are enough.
        """,
        viz=viz(arr="nums", ptr={"house": "i"}, vars=[("best two back", "skip"), ("best so far", "take")]),
        py='''
        def rob(nums):
            skip = take = 0
            for i, x in enumerate(nums):
                skip, take = take, max(take, skip + x)  #> At house {i}: skip it for {skip}, or rob it for {skip + x}... best is {take}.
            return take
        ''',
        java='''
        class Solution {
            public int rob(int[] nums) {
                int skip = 0, take = 0;
                for (int x : nums) { int next = Math.max(take, skip + x); skip = take; take = next; } //>
                return take;
            }
        }
        ''',
    )],
)

problem(
    id="circular-robber",
    title="Rob Houses Arranged in a Circle",
    difficulty="Medium",
    topics=["Array", "Dynamic Programming"],
    statement="""
    Same as before, but the houses form a circle: the first and last houses are neighbours. Return the most money you can take.
    """,
    examples=[([[2, 3, 2]], 3, None), ([[1, 2, 3, 1]], 4, None)],
    tests=[([[7]], 7), ([[1, 2, 3]], 3), ([[200, 3, 140, 20, 10]], 340)],
    constraints=["1 ≤ nums.length ≤ 100"],
    hints=["You can't take both the first and the last house.", "Solve the line without the first house, and without the last."],
    approaches=[approach(
        name="Two Linear Passes", pattern="dp", time="O(n)", space="O(1)",
        idea="""
        Since the first and last houses can't both be robbed, solve the straight-line version twice: once without the first house and once without the last. Take the better answer.
        """,
        viz=viz(vars=["skip", "take"]),
        py='''
        def rob_circle(nums):
            def line(houses):
                skip = take = 0
                for x in houses:
                    skip, take = take, max(take, skip + x)  #> House worth {x}: the best total so far is {take}.
                return take

            if len(nums) == 1:
                return nums[0]
            return max(line(nums[1:]), line(nums[:-1]))  #> Either skip the first house or skip the last house.
        ''',
        java='''
        class Solution {
            public int robCircle(int[] nums) {
                if (nums.length == 1) return nums[0];
                return Math.max(line(nums, 1, nums.length), line(nums, 0, nums.length - 1)); //>2
            }

            private int line(int[] nums, int from, int to) {
                int skip = 0, take = 0;
                for (int i = from; i < to; i++) { int next = Math.max(take, skip + nums[i]); skip = take; take = next; } //>1
                return take;
            }
        }
        ''',
    )],
)

problem(
    id="fewest-coins",
    title="Fewest Coins for an Amount",
    difficulty="Medium",
    topics=["Array", "Dynamic Programming"],
    statement="""
    Using unlimited coins of the given denominations, return the fewest coins that add up to `amount`, or `-1` if it
    can't be made.
    """,
    examples=[([[1, 2, 5], 11], 3, "5 + 5 + 1"), ([[2], 3], -1, None)],
    tests=[([[1], 0], 0), ([[2, 5, 10, 1], 27], 4), ([[186, 419, 83, 408], 6249], 20)],
    constraints=["1 ≤ coins.length ≤ 12", "0 ≤ amount ≤ 10^4"],
    hints=["best[a] = 1 + min(best[a − coin]) over coins.", "Build up from 0."],
    approaches=[approach(
        name="Bottom-Up DP", pattern="dp", time="O(amount · coins)", space="O(amount)",
        idea="""
        Let `best[a]` be the fewest coins making amount a, with `best[0] = 0`. For every amount, try finishing with each coin: one coin plus the best way to make the rest.

        Amounts that can't be made keep an "infinity" marker of amount + 1.
        """,
        viz=viz(table=("best", {"a": "a"}, None, "best[a]")),
        demo=[[1, 2, 5], 7],
        py='''
        def fewest_coins(coins, amount):
            best = [0] + [amount + 1] * amount
            for a in range(1, amount + 1):
                best[a] = min([best[a - c] + 1 for c in coins if c <= a] + [amount + 1])  #> Amount {a} needs {best[a] if best[a] <= amount else "infinitely many"} coins at best.
            return best[amount] if best[amount] <= amount else -1
        ''',
        java='''
        class Solution {
            public int fewestCoins(int[] coins, int amount) {
                int[] best = new int[amount + 1];
                Arrays.fill(best, amount + 1);
                best[0] = 0;
                for (int a = 1; a <= amount; a++)
                    for (int c : coins) if (c <= a) best[a] = Math.min(best[a], best[a - c] + 1); //>
                return best[amount] <= amount ? best[amount] : -1;
            }
        }
        ''',
    )],
)

problem(
    id="coin-combinations",
    title="Ways to Make Change",
    difficulty="Medium",
    topics=["Array", "Dynamic Programming"],
    statement="""
    Return the number of different combinations of coins (unlimited supply, order doesn't matter) that make `amount`.
    """,
    examples=[([5, [1, 2, 5]], 4, "5, 2+2+1, 2+1+1+1, 1+1+1+1+1"), ([3, [2]], 0, None)],
    tests=[([0, [7]], 1), ([10, [10]], 1), ([4, [1, 2, 3]], 4)],
    constraints=["0 ≤ amount ≤ 5000", "1 ≤ coins.length ≤ 300"],
    hints=["Loop over coins outside and amounts inside, so each combination is counted once."],
    approaches=[approach(
        name="Unbounded Knapsack", pattern="dp", time="O(amount · coins)", space="O(amount)",
        idea="""
        `ways[a]` counts combinations for amount a, with `ways[0] = 1`. Process one coin at a time: for every amount from the coin upward, add `ways[a − coin]`.

        Putting coins in the outer loop means each combination is built in one fixed coin order, so it's never counted twice.
        """,
        viz=viz(table=("ways", {"a": "a"}, None, "ways[a]"), vars=["coin"]),
        demo=[5, [1, 2, 5]],
        py='''
        def change_ways(amount, coins):
            ways = [1] + [0] * amount
            for coin in coins:
                for a in range(coin, amount + 1):
                    ways[a] += ways[a - coin]  #> Using coins up to {coin}, amount {a} can be made {ways[a]} ways.
            return ways[amount]
        ''',
        java='''
        class Solution {
            public int changeWays(int amount, int[] coins) {
                int[] ways = new int[amount + 1];
                ways[0] = 1;
                for (int coin : coins)
                    for (int a = coin; a <= amount; a++) ways[a] += ways[a - coin]; //>
                return ways[amount];
            }
        }
        ''',
    )],
)

problem(
    id="longest-rising-subsequence",
    title="Longest Rising Subsequence",
    difficulty="Medium",
    topics=["Array", "Dynamic Programming", "Binary Search"],
    statement="""
    Return the length of the longest strictly increasing subsequence of `nums` (elements in order, not necessarily
    adjacent).
    """,
    examples=[([[10, 9, 2, 5, 3, 7, 101, 18]], 4, "2, 3, 7, 18"), ([[7, 7, 7]], 1, None)],
    tests=[([[0, 1, 0, 3, 2, 3]], 4), ([[5]], 1)],
    constraints=["1 ≤ nums.length ≤ 2500"],
    hints=["Keep the smallest possible tail for every subsequence length.", "Binary search where each number fits."],
    approaches=[approach(
        name="Tails + Binary Search", pattern="binary-search", time="O(n log n)", space="O(n)",
        idea="""
        `tails[k]` is the smallest possible last value of a rising subsequence of length k + 1. For each number, binary search the first tail that is at least as big and replace it, or append if the number is bigger than every tail.

        The number of tails is the answer. (`tails` itself is not necessarily a real subsequence.)
        """,
        viz=viz(arrays=[("nums", {"x": "i"}), ("tails", {})]),
        py='''
        import bisect

        def longest_rising(nums):
            tails = []
            for i, x in enumerate(nums):
                k = bisect.bisect_left(tails, x)
                if k == len(tails):
                    tails.append(x)  #> {x} is bigger than every tail, so a longer subsequence exists: length {len(tails)}.
                else:
                    tails[k] = x  #> {x} becomes the smallest tail for length {k + 1}.
            return len(tails)
        ''',
        java='''
        class Solution {
            public int longestRising(int[] nums) {
                int[] tails = new int[nums.length];
                int size = 0;
                for (int x : nums) {
                    int lo = 0, hi = size;
                    while (lo < hi) { int mid = (lo + hi) >>> 1; if (tails[mid] < x) lo = mid + 1; else hi = mid; }
                    tails[lo] = x; //>1,2
                    if (lo == size) size++;
                }
                return size;
            }
        }
        ''',
    )],
)

problem(
    id="longest-common-subsequence",
    title="Longest Shared Subsequence",
    difficulty="Medium",
    topics=["String", "Dynamic Programming"],
    statement="""
    Return the length of the longest subsequence that appears in both strings `a` and `b`.
    """,
    examples=[(["abcde", "ace"], 3, "\"ace\""), (["abc", "def"], 0, None)],
    tests=[(["abc", "abc"], 3), (["bl", "yby"], 1)],
    constraints=["1 ≤ a.length, b.length ≤ 1000"],
    hints=["If the last letters match, they extend the answer.", "Otherwise drop the last letter of one string."],
    approaches=[approach(
        name="2D DP With Rolling Rows", pattern="dp", time="O(m · n)", space="O(n)",
        idea="""
        `dp[i][j]` is the answer for the first i letters of `a` and first j of `b`. Matching letters add one to the diagonal value; otherwise take the better of dropping a letter from either string.

        Each row only needs the row above, so two rows suffice.
        """,
        viz=viz(table=("[prev, cur]", {"cell": ("1", "j")}, None, "dp rows"), vars=["i", "j"]),
        demo=["abcde", "ace"],
        py='''
        def lcs(a, b):
            prev = [0] * (len(b) + 1)
            for i in range(1, len(a) + 1):
                cur = [0] * (len(b) + 1)
                for j in range(1, len(b) + 1):
                    cur[j] = prev[j - 1] + 1 if a[i - 1] == b[j - 1] else max(prev[j], cur[j - 1])
                prev = cur  #> After letter {q(a[i - 1])}: {cur}.
            return prev[-1]
        ''',
        java='''
        class Solution {
            public int lcs(String a, String b) {
                int[] prev = new int[b.length() + 1];
                for (int i = 1; i <= a.length(); i++) {
                    int[] cur = new int[b.length() + 1];
                    for (int j = 1; j <= b.length(); j++)
                        cur[j] = a.charAt(i - 1) == b.charAt(j - 1) ? prev[j - 1] + 1 : Math.max(prev[j], cur[j - 1]);
                    prev = cur; //>
                }
                return prev[b.length()];
            }
        }
        ''',
    )],
)

problem(
    id="edit-distance",
    title="Fewest Edits Between Two Words",
    difficulty="Hard",
    topics=["String", "Dynamic Programming"],
    statement="""
    Return the minimum number of single-character insertions, deletions or replacements that turn `a` into `b`.
    """,
    examples=[(["horse", "ros"], 3, "horse → rorse → rose → ros"), (["intention", "execution"], 5, None)],
    tests=[(["", "abc"], 3), (["same", "same"], 0), (["kitten", "sitting"], 3)],
    constraints=["0 ≤ a.length, b.length ≤ 500"],
    hints=["dp[i][j] = edits for the first i letters of a and first j of b."],
    approaches=[approach(
        name="2D DP With Rolling Rows", pattern="dp", time="O(m · n)", space="O(n)",
        idea="""
        If the current letters match, no edit is needed: copy the diagonal. Otherwise take 1 + the cheapest of replace (diagonal), delete (above) or insert (left).

        Only the previous row is needed to compute the next one.
        """,
        viz=viz(table=("[prev, cur]", {}, None, "dp rows"), vars=["i"]),
        demo=["horse", "ros"],
        py='''
        def edit_distance(a, b):
            prev = list(range(len(b) + 1))
            for i in range(1, len(a) + 1):
                cur = [i] + [0] * len(b)
                for j in range(1, len(b) + 1):
                    if a[i - 1] == b[j - 1]:
                        cur[j] = prev[j - 1]
                    else:
                        cur[j] = 1 + min(prev[j - 1], prev[j], cur[j - 1])
                prev = cur  #> Turning {q(a[:i])} into each prefix of {q(b)} costs {cur}.
            return prev[-1]
        ''',
        java='''
        class Solution {
            public int editDistance(String a, String b) {
                int[] prev = new int[b.length() + 1];
                for (int j = 0; j <= b.length(); j++) prev[j] = j;
                for (int i = 1; i <= a.length(); i++) {
                    int[] cur = new int[b.length() + 1];
                    cur[0] = i;
                    for (int j = 1; j <= b.length(); j++)
                        cur[j] = a.charAt(i - 1) == b.charAt(j - 1) ? prev[j - 1] : 1 + Math.min(prev[j - 1], Math.min(prev[j], cur[j - 1]));
                    prev = cur; //>
                }
                return prev[b.length()];
            }
        }
        ''',
    )],
)

problem(
    id="word-split",
    title="Split Into Dictionary Words",
    difficulty="Medium",
    topics=["String", "Dynamic Programming", "Hash Set"],
    statement="""
    Return `true` if `s` can be split into a sequence of one or more words from `words` (words may be reused).
    """,
    examples=[(["applepenapple", ["apple", "pen"]], True, None), (["catsandog", ["cats", "dog", "sand", "and", "cat"]], False, None)],
    tests=[(["a", ["a"]], True), (["aaab", ["a", "aa"]], False)],
    constraints=["1 ≤ s.length ≤ 300"],
    hints=["ok[i] = the first i characters can be split."],
    approaches=[approach(
        name="DP Over Prefixes", pattern="dp", time="O(n²)", space="O(n)",
        idea="""
        `ok[i]` says the first i characters split cleanly, with `ok[0] = true`. Position i is reachable if some earlier reachable position j has `s[j:i]` in the dictionary.
        """,
        viz=viz(table=("ok", {"i": "i"}, None, "ok[i]"), vars=["i"]),
        py='''
        def word_split(s, words):
            vocab = set(words)
            ok = [True] + [False] * len(s)
            for i in range(1, len(s) + 1):
                ok[i] = any(ok[j] and s[j:i] in vocab for j in range(i))  #> {q(s[:i])} {"can" if ok[i] else "can't"} be split into words.
            return ok[-1]
        ''',
        java='''
        class Solution {
            public boolean wordSplit(String s, String[] words) {
                Set<String> vocab = new HashSet<>(Arrays.asList(words));
                boolean[] ok = new boolean[s.length() + 1];
                ok[0] = true;
                for (int i = 1; i <= s.length(); i++)
                    for (int j = 0; j < i && !ok[i]; j++) ok[i] = ok[j] && vocab.contains(s.substring(j, i)); //>
                return ok[s.length()];
            }
        }
        ''',
    )],
)

problem(
    id="decode-digits",
    title="Ways to Decode a Digit String",
    difficulty="Medium",
    topics=["String", "Dynamic Programming"],
    statement="""
    Letters are encoded as 1 → A, 2 → B, …, 26 → Z. Return the number of ways to decode the digit string `s`.
    """,
    examples=[(["12"], 2, "AB or L"), (["226"], 3, "BZ, VF, BBF")],
    tests=[(["06"], 0), (["10"], 1), (["11106"], 2)],
    constraints=["1 ≤ s.length ≤ 100"],
    hints=["The last digit alone (if not 0) or the last two digits (10–26) can end a decoding."],
    approaches=[approach(
        name="Rolling Window of Two", pattern="dp", time="O(n)", space="O(1)",
        idea="""
        Ways to decode the first i digits = ways for i − 1 (if digit i is 1–9) plus ways for i − 2 (if the last two digits form 10–26). Keep a rolling window of the last two counts.
        """,
        viz=viz(arr="s", ptr={"i": "i - 1"}, vars=["two_back", "one_back"]),
        demo=["226"],
        py='''
        def decode_ways(s):
            two_back, one_back = 1, 1 if s[0] != "0" else 0
            for i in range(2, len(s) + 1):
                cur = one_back if s[i - 1] != "0" else 0
                if "10" <= s[i - 2:i] <= "26":
                    cur += two_back
                two_back, one_back = one_back, cur  #> {q(s[:i])} can be decoded {cur} ways.
            return one_back
        ''',
        java='''
        class Solution {
            public int decodeWays(String s) {
                int twoBack = 1, oneBack = s.charAt(0) != '0' ? 1 : 0;
                for (int i = 2; i <= s.length(); i++) {
                    int cur = s.charAt(i - 1) != '0' ? oneBack : 0;
                    int two = Integer.parseInt(s.substring(i - 2, i));
                    if (two >= 10 && two <= 26) cur += twoBack;
                    twoBack = oneBack;
                    oneBack = cur; //>
                }
                return oneBack;
            }
        }
        ''',
    )],
)

problem(
    id="equal-halves",
    title="Split Into Two Equal Sums",
    difficulty="Medium",
    topics=["Array", "Dynamic Programming"],
    statement="""
    Return `true` if `nums` (positive integers) can be split into two groups with equal sums.
    """,
    examples=[([[1, 5, 11, 5]], True, "[1, 5, 5] and [11]"), ([[1, 2, 3, 5]], False, None)],
    tests=[([[2, 2]], True), ([[1]], False), ([[3, 3, 3, 4, 5]], True)],
    constraints=["1 ≤ nums.length ≤ 200", "1 ≤ nums[i] ≤ 100"],
    hints=["Look for a subset summing to half the total.", "Track every reachable sum."],
    approaches=[approach(
        name="Reachable Sums", pattern="dp", time="O(n · sum)", space="O(sum)",
        idea="""
        If the total is odd it's impossible. Otherwise we need a subset summing to half. Keep the set of sums reachable so far; each number adds itself to every reachable sum.
        """,
        viz=viz(maps=[("reachable sums", "reach")], vars=["target"]),
        py='''
        def can_split(nums):
            total = sum(nums)
            if total % 2:
                return False
            target, reach = total // 2, {0}
            for x in nums:
                reach |= {r + x for r in reach if r + x <= target}  #> With {x}, reachable sums are {sorted(reach)}.
            return target in reach
        ''',
        java='''
        class Solution {
            public boolean canSplit(int[] nums) {
                int total = 0;
                for (int x : nums) total += x;
                if (total % 2 == 1) return false;
                boolean[] reach = new boolean[total / 2 + 1];
                reach[0] = true;
                for (int x : nums)
                    for (int s = total / 2; s >= x; s--) reach[s] |= reach[s - x]; //>
                return reach[total / 2];
            }
        }
        ''',
    )],
)

problem(
    id="max-product-run",
    title="Largest Product of a Run",
    difficulty="Medium",
    topics=["Array", "Dynamic Programming"],
    statement="""
    Return the largest product of any non-empty contiguous subarray of `nums`.
    """,
    examples=[([[2, 3, -2, 4]], 6, "[2, 3]"), ([[-2, 0, -1]], 0, None)],
    tests=[([[-2, 3, -4]], 24), ([[-3]], -3), ([[0, 2]], 2)],
    constraints=["1 ≤ nums.length ≤ 2·10^4"],
    hints=["A negative number flips the biggest product into the smallest and vice versa.", "Track both."],
    approaches=[approach(
        name="Rolling Max and Min", pattern="dp", time="O(n)", space="O(1)",
        idea="""
        Track the largest and smallest product of a run ending at the current number. Multiplying by a negative swaps their roles, so compute both from the previous pair (or start fresh at the number itself).
        """,
        viz=viz(arr="nums", ptr={"i": "i"}, vars=["hi", "lo", "best"]),
        py='''
        def max_product(nums):
            hi = lo = best = nums[0]
            for i in range(1, len(nums)):
                x = nums[i]
                hi, lo = max(x, hi * x, lo * x), min(x, hi * x, lo * x)
                best = max(best, hi)  #> Runs ending at {x}: largest {hi}, smallest {lo}. Best: {best}.
            return best
        ''',
        java='''
        class Solution {
            public int maxProduct(int[] nums) {
                int hi = nums[0], lo = nums[0], best = nums[0];
                for (int i = 1; i < nums.length; i++) {
                    int x = nums[i], a = hi * x, b = lo * x;
                    hi = Math.max(x, Math.max(a, b));
                    lo = Math.min(x, Math.min(a, b));
                    best = Math.max(best, hi); //>
                }
                return best;
            }
        }
        ''',
    )],
)

problem(
    id="longest-palindrome-inside",
    title="Longest Palindrome Inside a String",
    difficulty="Medium",
    topics=["String", "Two Pointers", "Dynamic Programming"],
    statement="""
    Return the longest contiguous substring of `s` that reads the same forwards and backwards. If several have the
    maximum length, return the one that starts first.
    """,
    examples=[(["babad"], "bab", "\"aba\" also has length 3 but starts later."), (["cbbd"], "bb", None)],
    tests=[(["a"], "a"), (["forgeeksskeegfor"], "geeksskeeg"), (["abacdfgdcaba"], "aba")],
    constraints=["1 ≤ s.length ≤ 1000"],
    hints=["Every palindrome has a center: one letter or a gap between two letters.", "Expand two pointers outward from each center."],
    approaches=[approach(
        name="Expand Around Center (Two Pointers)", pattern="two-pointers", time="O(n²)", space="O(1)",
        idea="""
        Every palindrome mirrors around a center, which is either one character or the gap between two characters. From each of the 2n − 1 centers, move `left` and `right` outward while the characters match.

        Keep the longest stretch found.
        """,
        viz=viz(arr="s", ptr={"left": "left", "right": "right"}, win=("left + 1", "right - 1"), vars=["best"]),
        demo=["cabad"],
        py='''
        def longest_palindrome(s):
            best = s[0]
            for center in range(2 * len(s) - 1):
                left, right = center // 2, (center + 1) // 2
                while left >= 0 and right < len(s) and s[left] == s[right]:
                    left, right = left - 1, right + 1  #> {q(s[left + 1])} matches {q(s[right - 1])}, so expand outward.
                if right - left - 1 > len(best):
                    best = s[left + 1:right]  #> Expanding from center {center} finds {q(best)}, the longest so far.
            return best
        ''',
        java='''
        class Solution {
            public String longestPalindrome(String s) {
                int start = 0, len = 1;
                for (int center = 0; center < 2 * s.length() - 1; center++) {
                    int left = center / 2, right = (center + 1) / 2;
                    for (; left >= 0 && right < s.length() && s.charAt(left) == s.charAt(right); left--, right++) { } //>1
                    if (right - left - 1 > len) { start = left + 1; len = right - left - 1; } //>2
                }
                return s.substring(start, start + len);
            }
        }
        ''',
    )],
)

problem(
    id="count-palindromes",
    title="Count Palindromic Substrings",
    difficulty="Medium",
    topics=["String", "Two Pointers"],
    statement="""
    Return how many substrings of `s` are palindromes (substrings at different positions count separately).
    """,
    examples=[(["abc"], 3, "a, b, c"), (["aaa"], 6, "a, a, a, aa, aa, aaa")],
    tests=[(["a"], 1), (["abba"], 6)],
    constraints=["1 ≤ s.length ≤ 1000"],
    hints=["Expand around every center and count each successful expansion."],
    approaches=[approach(
        name="Expand Around Center (Two Pointers)", pattern="two-pointers", time="O(n²)", space="O(1)",
        idea="""
        From each of the 2n − 1 centers, move `left` and `right` outward. Every step where the characters still match reveals one more palindrome.
        """,
        viz=viz(arr="s", ptr={"left": "left", "right": "right"}, win=("left", "right"), vars=["count"]),
        demo=["aba"],
        py='''
        def count_palindromes(s):
            count = 0
            for center in range(2 * len(s) - 1):
                left, right = center // 2, (center + 1) // 2
                while left >= 0 and right < len(s) and s[left] == s[right]:
                    count += 1  #> {q(s[left:right + 1])} is a palindrome. Count: {count}.
                    left, right = left - 1, right + 1
            return count
        ''',
        java='''
        class Solution {
            public int countPalindromes(String s) {
                int count = 0;
                for (int center = 0; center < 2 * s.length() - 1; center++)
                    for (int left = center / 2, right = (center + 1) / 2;
                         left >= 0 && right < s.length() && s.charAt(left) == s.charAt(right); left--, right++) count++; //>
                return count;
            }
        }
        ''',
    )],
)

problem(
    id="grid-paths",
    title="Paths Across a Grid",
    difficulty="Medium",
    topics=["Math", "Dynamic Programming"],
    statement="""
    A robot starts at the top-left of an `m × n` grid and may only move right or down. How many paths reach the
    bottom-right corner?
    """,
    examples=[([3, 7], 28, None), ([3, 2], 3, None)],
    tests=[([1, 1], 1), ([10, 10], 48620)],
    constraints=["1 ≤ m, n ≤ 100", "the answer fits in a 32-bit int"],
    hints=["paths(r, c) = paths(r − 1, c) + paths(r, c − 1).", "One row of the table is enough."],
    approaches=[approach(
        name="1D Rolling Row", pattern="dp", time="O(m · n)", space="O(n)",
        idea="""
        The number of paths to a cell is the sum of paths to the cell above and the cell to the left. Keep a single row: updating it left to right turns the old value (above) plus the new left value into the new count.
        """,
        viz=viz(table=("row", {"c": "c"}, None, "paths per column"), vars=["r"]),
        demo=[3, 4],
        py='''
        def grid_paths(m, n):
            row = [1] * n
            for r in range(1, m):
                for c in range(1, n):
                    row[c] += row[c - 1]  #> Row {r}, column {c}: {row[c]} paths (from above plus from the left).
            return row[-1]
        ''',
        java='''
        class Solution {
            public int gridPaths(int m, int n) {
                int[] row = new int[n];
                Arrays.fill(row, 1);
                for (int r = 1; r < m; r++)
                    for (int c = 1; c < n; c++) row[c] += row[c - 1]; //>
                return row[n - 1];
            }
        }
        ''',
    )],
)
