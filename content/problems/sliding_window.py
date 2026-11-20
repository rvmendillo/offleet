"""Sliding Window problems (original statements).

House style (the learner's preferred template): `left`/`right` pointers, add the element at `right` first,
then shrink with `for (; <invalid>; <remove left>, left++)` in Java (a `while` loop in Python), and use an
`n + 1` sentinel for "minimum length" answers.
"""
from dsl import problem, approach, viz

# Window bounds that also work before the loop variable exists.
R_OR = "locals().get('right', {d})"

problem(
    id="shortest-sum-at-least",
    title="Shortest Run Reaching a Target",
    difficulty="Medium",
    topics=["Array", "Sliding Window", "Prefix Sum"],
    statement="""
    Given positive integers `nums` and a positive number `s`, return the length of the shortest contiguous run whose
    sum is **at least** `s`, or `0` if no run reaches it.
    """,
    examples=[([7, [2, 3, 1, 2, 4, 3]], 2, "[4, 3] sums to 7."), ([4, [1, 4, 4]], 1, None)],
    tests=[([11, [1, 1, 1, 1, 1]], 0), ([15, [1, 2, 3, 4, 5]], 5), ([3, [3]], 1)],
    constraints=["1 ≤ nums.length ≤ 10^5", "1 ≤ nums[i] ≤ 10^4"],
    hints=["All numbers are positive, so growing the window always raises the sum.",
           "Once the sum is big enough, shrink from the left as far as possible."],
    approaches=[approach(
        name="Sliding Window", pattern="sliding-window", time="O(n)", space="O(1)",
        idea="""
        This is the simplest sliding window template. Move `right` forward and add `nums[right]` to the sum first.

        Then, while the sum is at least `s`, record the window length and shrink from the left: subtract `nums[left]` and move `left` forward. The sentinel `n + 1` means "no window found yet".
        """,
        why="right and left each move forward at most n times, so the nested loop is still linear.",
        viz=viz(arr="nums", ptr={"left": "left", "right": "right"}, win=("left", R_OR.format(d="-1")), vars=["total", "s", "min_len"]),
        py='''
        def min_sub_array_len(s, nums):
            total, min_len, left = 0, len(nums) + 1, 0
            for right in range(len(nums)):
                total += nums[right]  #> Add {nums[right]}. The window sum is {total}.
                while total >= s:
                    min_len = min(min_len, right - left + 1)  #> {total} reaches {s} with length {right - left + 1}. Shortest so far: {min_len}.
                    total -= nums[left]
                    left += 1  #> Shrink from the left. The sum drops to {total}.
            return min_len if min_len <= len(nums) else 0
        ''',
        java='''
        class Solution {
            public int minSubArrayLen(int s, int[] nums) {
                int sum = 0, minLen = nums.length + 1, left = 0;
                for (int right = 0; right < nums.length; right++) {
                    sum += nums[right]; //>
                    for (; sum >= s; sum -= nums[left], left++) {
                        minLen = Math.min(minLen, right - left + 1); //>2,3
                    }
                }
                return minLen <= nums.length ? minLen : 0;
            }
        }
        ''',
    )],
)

problem(
    id="longest-unique-substring",
    title="Longest Stretch Without Repeats",
    difficulty="Medium",
    topics=["String", "Sliding Window", "Hash Map"],
    statement="""
    Given a string `s`, return the length of the longest contiguous piece of `s` in which no character appears twice.
    """,
    examples=[(["abcabcbb"], 3, "\"abc\" has no repeats and nothing longer works."), (["bbbb"], 1, None)],
    tests=[([""], 0), (["pwwkew"], 3), (["abba"], 2), (["dvdf"], 3)],
    constraints=["0 ≤ s.length ≤ 5·10^4", "s contains ASCII characters"],
    hints=["Keep a window with no repeats.", "When a repeat enters, shrink from the left until it's gone."],
    approaches=[
        approach(
            name="Sliding Window", pattern="sliding-window", time="O(n)", space="O(1)",
            idea="""
            Count the characters inside the window. Add `s[right]` first. If it now appears twice, shrink from the left until that character's count is back to one.

            The window never holds a repeat after shrinking, so its length is a candidate answer.
            """,
            why="Each character enters and leaves the window once; the count table has a fixed ASCII size.",
            viz=viz(arr="s", ptr={"left": "left", "right": "right"}, win=("left", R_OR.format(d="-1")),
                    maps=[("counts", "{k: v for k, v in count.items() if v}")], vars=["best"]),
            py='''
            def longest_unique(s):
                count, best, left = {}, 0, 0
                for right in range(len(s)):
                    c = s[right]
                    count[c] = count.get(c, 0) + 1  #> Add {q(c)}.
                    while count[c] > 1:
                        count[s[left]] -= 1
                        left += 1  #> {q(c)} appears twice, so shrink: left moves to {left}.
                    best = max(best, right - left + 1)  #> The window {q(s[left:right + 1])} has length {right - left + 1}. Best: {best}.
                return best
            ''',
            java='''
            class Solution {
                public int longestUnique(String s) {
                    int[] count = new int[128];
                    int best = 0, left = 0;
                    for (int right = 0; right < s.length(); right++) {
                        char c = s.charAt(right);
                        count[c]++; //>
                        for (; count[c] > 1; left++) count[s.charAt(left)]--; //>
                        best = Math.max(best, right - left + 1); //>
                    }
                    return best;
                }
            }
            ''',
        ),
        approach(
            name="Sliding Window with Jumps", pattern="sliding-window", time="O(n)", space="O(k)",
            idea="""
            Instead of shrinking one step at a time, remember the last index where each character was seen. When `s[right]` was seen inside the window, jump `left` just past that earlier copy in one move.
            """,
            viz=viz(arr="s", ptr={"left": "left", "right": "right"}, win=("left", R_OR.format(d="-1")), maps=[("last seen", "last")], vars=["best"]),
            py='''
            def longest_unique(s):
                last, best, left = {}, 0, 0
                for right in range(len(s)):
                    if last.get(s[right], -1) >= left:
                        left = last[s[right]] + 1  #> {q(s[right])} is already in the window, so left jumps to {left}.
                    last[s[right]] = right
                    best = max(best, right - left + 1)  #> The window {q(s[left:right + 1])} has length {right - left + 1}. Best: {best}.
                return best
            ''',
            java='''
            class Solution {
                public int longestUnique(String s) {
                    Map<Character, Integer> last = new HashMap<>();
                    int best = 0, left = 0;
                    for (int right = 0; right < s.length(); right++) {
                        char c = s.charAt(right);
                        if (last.getOrDefault(c, -1) >= left) left = last.get(c) + 1; //>
                        last.put(c, right);
                        best = Math.max(best, right - left + 1); //>
                    }
                    return best;
                }
            }
            ''',
        ),
    ],
)

problem(
    id="best-k-window-sum",
    title="Best Sum of k in a Row",
    difficulty="Easy",
    topics=["Array", "Sliding Window"],
    statement="""
    Given an integer array `nums` and a window size `k`, return the largest sum of any `k` consecutive numbers.
    """,
    examples=[([[2, 1, 5, 1, 3, 2], 3], 9, "5 + 1 + 3 = 9"), ([[-1, -2, -3], 2], -3, None)],
    tests=[([[4], 1], 4), ([[1, 2, 3, 4], 4], 10), ([[5, -10, 6, 1], 2], 7)],
    constraints=["1 ≤ k ≤ nums.length ≤ 10^5"],
    hints=["Don't re-add k numbers for every window.", "Sliding by one adds one number and removes one."],
    approaches=[approach(
        name="Fixed Sliding Window", pattern="sliding-window", time="O(n)", space="O(1)",
        idea="""
        Same template with a fixed size: add `nums[right]` first. Once the window is longer than k, remove `nums[left]` and move `left`.

        As soon as the window holds exactly k numbers, compare its sum with the best.
        """,
        viz=viz(arr="nums", ptr={"left": "left", "right": "right"}, win=("left", R_OR.format(d="-1")), vars=["total", "best"]),
        py='''
        def best_window_sum(nums, k):
            total, best, left = 0, float("-inf"), 0
            for right in range(len(nums)):
                total += nums[right]  #> Add {nums[right]}. The window sum is {total}.
                if right - left + 1 > k:
                    total -= nums[left]
                    left += 1  #> The window is longer than {k}, so drop the left value. Sum: {total}.
                if right - left + 1 == k:
                    best = max(best, total)
            return best  #> The best window sum is {best}.
        ''',
        java='''
        class Solution {
            public int bestWindowSum(int[] nums, int k) {
                int sum = 0, best = Integer.MIN_VALUE, left = 0;
                for (int right = 0; right < nums.length; right++) {
                    sum += nums[right]; //>
                    for (; right - left + 1 > k; left++) sum -= nums[left]; //>
                    if (right - left + 1 == k) best = Math.max(best, sum);
                }
                return best; //>
            }
        }
        ''',
    )],
)

problem(
    id="longest-after-replacements",
    title="Longest Same-Letter Run With k Changes",
    difficulty="Medium",
    topics=["String", "Sliding Window", "Hash Map"],
    statement="""
    `s` contains uppercase letters. You may change at most `k` characters to any other uppercase letter.
    Return the length of the longest run of identical letters you can create.
    """,
    examples=[(["ABAB", 2], 4, "Change both A's (or both B's)."), (["AABABBA", 1], 4, None)],
    tests=[(["A", 0], 1), (["ABCDE", 1], 2), (["AAAA", 0], 4)],
    constraints=["1 ≤ s.length ≤ 10^5", "0 ≤ k ≤ s.length"],
    hints=["A window is fine if (window length − count of its most common letter) ≤ k."],
    approaches=[approach(
        name="Sliding Window", pattern="sliding-window", time="O(n)", space="O(1)",
        idea="""
        Inside a window, the letters we must change are all except the most common one. So a window is valid while its length minus the top count is at most k.

        Add `s[right]`, update the top count, and shrink from the left while the window needs more than k changes.
        """,
        viz=viz(arr="s", ptr={"left": "left", "right": "right"}, win=("left", R_OR.format(d="-1")), maps=[("counts", "count")], vars=["top", "best"]),
        py='''
        def longest_after_changes(s, k):
            count, top, best, left = {}, 0, 0, 0
            for right in range(len(s)):
                count[s[right]] = count.get(s[right], 0) + 1
                top = max(top, count[s[right]])  #> Add {q(s[right])}. The most common letter appears {top} times.
                while right - left + 1 - top > k:
                    count[s[left]] -= 1
                    left += 1  #> More than {k} changes needed, so shrink: left moves to {left}.
                best = max(best, right - left + 1)
            return best
        ''',
        java='''
        class Solution {
            public int longestAfterChanges(String s, int k) {
                int[] count = new int[26];
                int top = 0, best = 0, left = 0;
                for (int right = 0; right < s.length(); right++) {
                    top = Math.max(top, ++count[s.charAt(right) - 'A']); //>
                    for (; right - left + 1 - top > k; left++) count[s.charAt(left) - 'A']--; //>
                    best = Math.max(best, right - left + 1);
                }
                return best;
            }
        }
        ''',
    )],
)

problem(
    id="contains-permutation",
    title="Scrambled Copy Inside",
    difficulty="Medium",
    topics=["String", "Sliding Window", "Hash Map"],
    statement="""
    Given lowercase strings `p` and `s`, return `true` if some contiguous part of `s` is a rearrangement
    (permutation) of `p`.
    """,
    examples=[(["ab", "eidbaooo"], True, "\"ba\" appears in s."), (["ab", "eidboaoo"], False, None)],
    tests=[(["abc", "ab"], False), (["a", "a"], True), (["adc", "dcda"], True)],
    constraints=["1 ≤ p.length, s.length ≤ 10^4"],
    hints=["A permutation has exactly the same letter counts.", "Slide a window of length p.length over s."],
    approaches=[approach(
        name="Fixed Sliding Window", pattern="sliding-window", time="O(n)", space="O(1)",
        idea="""
        Count the letters of `p`. Slide a window of the same length over `s`: add `s[right]`, and once the window is too long, remove `s[left]` and move `left`.

        Whenever the window's counts equal `p`'s counts, the window is a permutation of `p`.
        """,
        why="Comparing two 26-slot tables is constant work per step.",
        viz=viz(arr="s", ptr={"left": "left", "right": "right"}, win=("left", R_OR.format(d="-1")), vars=["p"]),
        demo=["ab", "eidbaooo"],
        py='''
        def contains_permutation(p, s):
            need, have, left = [0] * 26, [0] * 26, 0
            for c in p:
                need[ord(c) - 97] += 1
            for right in range(len(s)):
                have[ord(s[right]) - 97] += 1  #> Add {q(s[right])}.
                if right - left + 1 > len(p):
                    have[ord(s[left]) - 97] -= 1
                    left += 1  #> Too long, so drop {q(s[left - 1])} from the left.
                if have == need:
                    return True  #> {q(s[left:right + 1])} has exactly the letters of {q(p)}!
            return False
        ''',
        java='''
        class Solution {
            public boolean containsPermutation(String p, String s) {
                int[] need = new int[26], have = new int[26];
                for (char c : p.toCharArray()) need[c - 'a']++;
                for (int right = 0, left = 0; right < s.length(); right++) {
                    have[s.charAt(right) - 'a']++; //>
                    for (; right - left + 1 > p.length(); left++) have[s.charAt(left) - 'a']--; //>
                    if (Arrays.equals(have, need)) return true; //>
                }
                return false;
            }
        }
        ''',
    )],
)

problem(
    id="anagram-starts",
    title="Every Anagram Position",
    difficulty="Medium",
    topics=["String", "Sliding Window", "Hash Map"],
    statement="""
    Given lowercase strings `s` and `p`, return all start indices (in increasing order) of substrings of `s` that
    are anagrams of `p`.
    """,
    examples=[(["cbaebabacd", "abc"], [0, 6], "\"cba\" starts at 0 and \"bac\" at 6."), (["abab", "ab"], [0, 1, 2], None)],
    tests=[(["a", "ab"], []), (["aaaa", "aa"], [0, 1, 2]), (["xyz", "zyx"], [0])],
    constraints=["1 ≤ s.length, p.length ≤ 3·10^4"],
    hints=["Same window as checking for one permutation, but keep going and collect every match."],
    approaches=[approach(
        name="Fixed Sliding Window", pattern="sliding-window", time="O(n)", space="O(1)",
        idea="""
        Slide a window of length `len(p)` across `s` while maintaining letter counts. Each time the counts match `p`, the window's `left` index is an answer.
        """,
        viz=viz(arr="s", ptr={"left": "left", "right": "right"}, win=("left", R_OR.format(d="-1")), out="res"),
        py='''
        def anagram_starts(s, p):
            need, have, res, left = [0] * 26, [0] * 26, [], 0
            for c in p:
                need[ord(c) - 97] += 1
            for right in range(len(s)):
                have[ord(s[right]) - 97] += 1
                if right - left + 1 > len(p):
                    have[ord(s[left]) - 97] -= 1
                    left += 1
                if have == need:
                    res.append(left)  #> {q(s[left:right + 1])} is an anagram, starting at {left}.
            return res
        ''',
        java='''
        class Solution {
            public List<Integer> anagramStarts(String s, String p) {
                int[] need = new int[26], have = new int[26];
                List<Integer> res = new ArrayList<>();
                for (char c : p.toCharArray()) need[c - 'a']++;
                for (int right = 0, left = 0; right < s.length(); right++) {
                    have[s.charAt(right) - 'a']++;
                    for (; right - left + 1 > p.length(); left++) have[s.charAt(left) - 'a']--;
                    if (Arrays.equals(have, need)) res.add(left); //>
                }
                return res;
            }
        }
        ''',
    )],
)

problem(
    id="smallest-covering-window",
    title="Smallest Window Covering All Letters",
    difficulty="Hard",
    topics=["String", "Sliding Window", "Hash Map"],
    statement="""
    Given strings `s` and `t`, return the shortest substring of `s` that contains every character of `t`
    (counting duplicates). If none exists return `""`. The answer is unique when it exists.
    """,
    examples=[(["ADOBECODEBANC", "ABC"], "BANC", None), (["a", "aa"], "", "s has only one 'a'.")],
    tests=[(["a", "a"], "a"), (["ab", "b"], "b"), (["aaflslflsldkalskaaa", "aaa"], "aaa")],
    constraints=["1 ≤ s.length, t.length ≤ 10^5"],
    hints=["Track how many required characters are still missing.", "While nothing is missing, record the window and shrink."],
    approaches=[approach(
        name="Sliding Window", pattern="sliding-window", time="O(n + m)", space="O(1)",
        idea="""
        Exactly the minimum-window template: `need` counts what `t` still requires and `missing` counts how many characters are outstanding.

        Add `s[right]`. While nothing is missing, record the window, then give back `s[left]` and move `left`; if that breaks the cover, the shrinking stops.
        """,
        why="Each character enters and leaves the window at most once; the count table has a fixed alphabet size.",
        viz=viz(arr="s", ptr={"left": "left", "right": "right"}, win=("left", R_OR.format(d="-1")), vars=["missing", "min_len"]),
        demo=["ADOBECODEBANC", "ABC"],
        py='''
        def min_window(s, t):
            need = {}
            for c in t:
                need[c] = need.get(c, 0) + 1
            missing, min_len, start, left = len(t), len(s) + 1, 0, 0
            for right in range(len(s)):
                if need.get(s[right], 0) > 0:
                    missing -= 1  #> {q(s[right])} was needed. Still missing: {missing}.
                need[s[right]] = need.get(s[right], 0) - 1
                while missing == 0:
                    if right - left + 1 < min_len:
                        min_len, start = right - left + 1, left  #> {q(s[left:right + 1])} covers everything. Shortest so far: {min_len}.
                    need[s[left]] += 1
                    if need[s[left]] > 0:
                        missing += 1  #> Giving back {q(s[left])} breaks the cover.
                    left += 1
            return s[start:start + min_len] if min_len <= len(s) else ""
        ''',
        java='''
        class Solution {
            public String minWindow(String s, String t) {
                int[] need = new int[128];
                for (char c : t.toCharArray()) need[c]++;
                int missing = t.length(), minLen = s.length() + 1, start = 0, left = 0;
                for (int right = 0; right < s.length(); right++) {
                    if (need[s.charAt(right)]-- > 0) missing--; //>
                    for (; missing == 0; left++) {
                        if (right - left + 1 < minLen) { minLen = right - left + 1; start = left; } //>
                        if (++need[s.charAt(left)] > 0) missing++; //>
                    }
                }
                return minLen <= s.length() ? s.substring(start, start + minLen) : "";
            }
        }
        ''',
    )],
)

problem(
    id="ones-after-flips",
    title="Longest Ones With k Flips",
    difficulty="Medium",
    topics=["Array", "Sliding Window"],
    statement="""
    `nums` contains only 0s and 1s. You may flip at most `k` zeros into ones. Return the length of the longest
    run of consecutive 1s you can get.
    """,
    examples=[([[1, 1, 0, 0, 1, 1, 1, 0, 1], 1], 5, "Flip the zero at index 3."), ([[0, 0, 1, 1], 0], 2, None)],
    tests=[([[0, 0, 0], 3], 3), ([[1, 1, 1], 0], 3), ([[0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1], 3], 10)],
    constraints=["1 ≤ nums.length ≤ 10^5", "0 ≤ k ≤ nums.length"],
    hints=["Find the longest window containing at most k zeros."],
    approaches=[approach(
        name="Sliding Window", pattern="sliding-window", time="O(n)", space="O(1)",
        idea="""
        Rephrase: find the longest window with at most k zeros, because those zeros can all be flipped.

        Add `nums[right]` and count zeros. While there are more than k, shrink from the left.
        """,
        viz=viz(arr="nums", ptr={"left": "left", "right": "right"}, win=("left", R_OR.format(d="-1")), vars=["zeros", "best"]),
        demo=[[1, 1, 0, 0, 1, 1, 1, 0, 1], 1],
        py='''
        def longest_ones(nums, k):
            zeros, best, left = 0, 0, 0
            for right in range(len(nums)):
                zeros += nums[right] == 0  #> Add {nums[right]}. Zeros in the window: {zeros}.
                while zeros > k:
                    zeros -= nums[left] == 0
                    left += 1  #> Too many zeros, so shrink: left moves to {left}.
                best = max(best, right - left + 1)
            return best
        ''',
        java='''
        class Solution {
            public int longestOnes(int[] nums, int k) {
                int zeros = 0, best = 0, left = 0;
                for (int right = 0; right < nums.length; right++) {
                    if (nums[right] == 0) zeros++; //>
                    for (; zeros > k; left++) if (nums[left] == 0) zeros--; //>
                    best = Math.max(best, right - left + 1);
                }
                return best;
            }
        }
        ''',
    )],
)

problem(
    id="two-kinds-longest",
    title="Two Baskets of Fruit",
    difficulty="Medium",
    topics=["Array", "Sliding Window", "Hash Map"],
    statement="""
    Trees stand in a row and `fruits[i]` is the kind of fruit on tree `i`. You have two baskets, each holding one
    kind of fruit (any amount). Starting at any tree and moving right, you pick one fruit per tree and must stop
    when a tree's fruit fits in neither basket. Return the most fruits you can pick.
    """,
    examples=[([[1, 2, 1]], 3, None), ([[0, 1, 2, 2]], 3, "Pick from trees 1 to 3: kinds 1 and 2.")],
    tests=[([[1, 2, 3, 2, 2]], 4), ([[3, 3, 3, 1, 2, 1, 1, 2, 3, 3, 4]], 5), ([[7]], 1)],
    constraints=["1 ≤ fruits.length ≤ 10^5"],
    hints=["This is the longest window with at most two distinct values."],
    approaches=[approach(
        name="Sliding Window", pattern="sliding-window", time="O(n)", space="O(1)",
        idea="""
        We want the longest window with at most two different kinds. Count kinds in the window with a map.

        Add `fruits[right]`; while three kinds are inside, shrink from the left until one kind disappears.
        """,
        viz=viz(arr="fruits", ptr={"left": "left", "right": "right"}, win=("left", R_OR.format(d="-1")), maps=[("basket", "count")], vars=["best"]),
        demo=[[1, 2, 3, 2, 2]],
        py='''
        def two_baskets(fruits):
            count, best, left = {}, 0, 0
            for right in range(len(fruits)):
                count[fruits[right]] = count.get(fruits[right], 0) + 1  #> Pick fruit {fruits[right]}. Kinds in the baskets: {len(count)}.
                while len(count) > 2:
                    count[fruits[left]] -= 1
                    if count[fruits[left]] == 0:
                        del count[fruits[left]]
                    left += 1  #> Three kinds is too many, so shrink: left moves to {left}.
                best = max(best, right - left + 1)
            return best
        ''',
        java='''
        class Solution {
            public int twoBaskets(int[] fruits) {
                Map<Integer, Integer> count = new HashMap<>();
                int best = 0, left = 0;
                for (int right = 0; right < fruits.length; right++) {
                    count.merge(fruits[right], 1, Integer::sum); //>
                    for (; count.size() > 2; left++) //>
                        if (count.merge(fruits[left], -1, Integer::sum) == 0) count.remove(fruits[left]);
                    best = Math.max(best, right - left + 1);
                }
                return best;
            }
        }
        ''',
    )],
)

problem(
    id="at-most-k-distinct",
    title="Longest Run With At Most k Letters",
    difficulty="Medium",
    topics=["String", "Sliding Window", "Hash Map"],
    statement="""
    Return the length of the longest substring of `s` that contains at most `k` distinct characters.
    """,
    examples=[(["eceba", 2], 3, "\"ece\""), (["aa", 1], 2, None)],
    tests=[(["a", 0], 0), (["abaccc", 2], 4), (["abcabc", 3], 6)],
    constraints=["1 ≤ s.length ≤ 5·10^4", "0 ≤ k ≤ 50"],
    hints=["Same as the two-baskets problem with k instead of 2."],
    approaches=[approach(
        name="Sliding Window", pattern="sliding-window", time="O(n)", space="O(k)",
        idea="""
        Add `s[right]` to the counts. While more than k distinct characters are inside, shrink from the left until one of them disappears. Track the longest valid window.
        """,
        viz=viz(arr="s", ptr={"left": "left", "right": "right"}, win=("left", R_OR.format(d="-1")), maps=[("counts", "count")], vars=["best"]),
        py='''
        def longest_k_distinct(s, k):
            count, best, left = {}, 0, 0
            for right in range(len(s)):
                count[s[right]] = count.get(s[right], 0) + 1
                while len(count) > k:
                    count[s[left]] -= 1
                    if count[s[left]] == 0:
                        del count[s[left]]
                    left += 1  #> More than {k} letters, so shrink: left moves to {left}.
                best = max(best, right - left + 1)  #> The window {q(s[left:right + 1])} is valid. Best: {best}.
            return best
        ''',
        java='''
        class Solution {
            public int longestKDistinct(String s, int k) {
                Map<Character, Integer> count = new HashMap<>();
                int best = 0, left = 0;
                for (int right = 0; right < s.length(); right++) {
                    count.merge(s.charAt(right), 1, Integer::sum);
                    for (; count.size() > k; left++) //>
                        if (count.merge(s.charAt(left), -1, Integer::sum) == 0) count.remove(s.charAt(left));
                    best = Math.max(best, right - left + 1); //>
                }
                return best;
            }
        }
        ''',
    )],
)

problem(
    id="small-product-subarrays",
    title="Count Runs With a Small Product",
    difficulty="Medium",
    topics=["Array", "Sliding Window"],
    statement="""
    Given positive integers `nums` and an integer `k`, return how many contiguous subarrays have a product
    strictly less than `k`.
    """,
    examples=[([[10, 5, 2, 6], 100], 8, None), ([[1, 2, 3], 0], 0, None)],
    tests=[([[1, 1, 1], 2], 6), ([[5], 5], 0), ([[2, 3, 4], 30], 6)],
    constraints=["1 ≤ nums.length ≤ 3·10^4", "1 ≤ nums[i] ≤ 1000", "0 ≤ k ≤ 10^6"],
    hints=["If a window has a small product, so does every window ending at right inside it.",
           "Each step adds right − left + 1 new subarrays."],
    approaches=[approach(
        name="Sliding Window", pattern="sliding-window", time="O(n)", space="O(1)",
        idea="""
        Multiply in `nums[right]`. While the product is at least k, divide out `nums[left]` and move `left`.

        Every subarray that ends at `right` and starts anywhere from `left` to `right` qualifies: that's right − left + 1 new ones.
        """,
        viz=viz(arr="nums", ptr={"left": "left", "right": "right"}, win=("left", R_OR.format(d="-1")), vars=["prod", "count"]),
        py='''
        def count_small_products(nums, k):
            prod, count, left = 1, 0, 0
            for right in range(len(nums)):
                prod *= nums[right]
                while prod >= k and left <= right:
                    prod //= nums[left]
                    left += 1
                count += right - left + 1  #> The window product is {prod}, adding {right - left + 1} subarrays. Total: {count}.
            return count
        ''',
        java='''
        class Solution {
            public int countSmallProducts(int[] nums, int k) {
                long prod = 1;
                int count = 0, left = 0;
                for (int right = 0; right < nums.length; right++) {
                    prod *= nums[right];
                    for (; prod >= k && left <= right; left++) prod /= nums[left];
                    count += right - left + 1; //>
                }
                return count;
            }
        }
        ''',
    )],
)

problem(
    id="window-maximums",
    title="Maximum of Every Window",
    difficulty="Hard",
    topics=["Array", "Sliding Window", "Monotonic Queue"],
    statement="""
    A window of size `k` slides over `nums` from left to right, one position at a time. Return the maximum value
    inside the window at each position.
    """,
    examples=[([[1, 3, -1, -3, 5, 3, 6, 7], 3], [3, 3, 5, 5, 6, 7], None), ([[4], 1], [4], None)],
    tests=[([[9, 8, 7, 6], 2], [9, 8, 7]), ([[1, 2, 3, 4], 4], [4]), ([[2, 2, 2], 2], [2, 2])],
    constraints=["1 ≤ k ≤ nums.length ≤ 10^5"],
    hints=["A value smaller than a newer value can never be a window maximum again.",
           "Keep indexes in a deque with decreasing values."],
    approaches=[approach(
        name="Sliding Window + Monotonic Deque", pattern="sliding-window", time="O(n)", space="O(k)",
        idea="""
        Keep a deque of indexes whose values decrease from front to back. The front is always the current window's maximum.

        When `nums[right]` arrives, pop smaller values off the back: they can never win again. Pop the front once it slides out of the window.
        """,
        why="Every index is pushed and popped at most once.",
        viz=viz(arr="nums", ptr={"right": "right"}, win=("max(0, " + R_OR.format(d="-1") + " - k + 1)", R_OR.format(d="-1")),
                queues=[("deque (indexes)", "dq")], out="res"),
        demo=[[1, 3, -1, -3, 5, 3, 6], 3],
        py='''
        from collections import deque

        def window_maxes(nums, k):
            dq, res = deque(), []
            for right in range(len(nums)):
                while dq and nums[dq[-1]] <= nums[right]:
                    dq.pop()
                dq.append(right)  #> Add index {right} (value {nums[right]}). Smaller values behind it are gone for good.
                if dq[0] <= right - k:
                    dq.popleft()  #> The front index slid out of the window.
                if right >= k - 1:
                    res.append(nums[dq[0]])  #> The window maximum is {res[-1]}.
            return res
        ''',
        java='''
        class Solution {
            public int[] windowMaxes(int[] nums, int k) {
                Deque<Integer> dq = new ArrayDeque<>();
                int[] res = new int[nums.length - k + 1];
                for (int right = 0; right < nums.length; right++) {
                    while (!dq.isEmpty() && nums[dq.peekLast()] <= nums[right]) dq.pollLast();
                    dq.addLast(right); //>
                    if (dq.peekFirst() <= right - k) dq.pollFirst(); //>
                    if (right >= k - 1) res[right - k + 1] = nums[dq.peekFirst()]; //>
                }
                return res;
            }
        }
        ''',
    )],
)

problem(
    id="best-trade",
    title="Best Single Trade",
    difficulty="Easy",
    topics=["Array", "Sliding Window", "Two Pointers"],
    patterns=["two-pointers"],
    statement="""
    `prices[i]` is a stock's price on day `i`. Choose one day to buy and a **later** day to sell to maximise profit.
    Return the maximum profit, or `0` if no profitable trade exists.
    """,
    examples=[([[7, 1, 5, 3, 6, 4]], 5, "Buy at 1, sell at 6."), ([[7, 6, 4, 3, 1]], 0, None)],
    tests=[([[1]], 0), ([[2, 4, 1]], 2), ([[3, 2, 6, 5, 0, 3]], 4)],
    constraints=["1 ≤ prices.length ≤ 10^5"],
    hints=["Track the cheapest buying day seen so far."],
    approaches=[approach(
        name="Sliding Window (buy & sell)", pattern="sliding-window", time="O(n)", space="O(1)",
        idea="""
        `left` is the buy day and `right` is the sell day; together they form a window. Move `right` forward every day.

        If `right` finds a cheaper price than `left`, the window restarts there: `left` jumps to `right`. Otherwise check the profit of the window.
        """,
        viz=viz(arr="prices", ptr={"buy": "left", "sell": "right"}, win=("left", R_OR.format(d="0")), vars=["best"]),
        py='''
        def max_profit(prices):
            best, left = 0, 0
            for right in range(1, len(prices)):
                if prices[right] < prices[left]:
                    left = right  #> {prices[right]} is cheaper, so the buy day moves to day {left}.
                else:
                    best = max(best, prices[right] - prices[left])  #> Selling at {prices[right]} earns {prices[right] - prices[left]}. Best: {best}.
            return best
        ''',
        java='''
        class Solution {
            public int maxProfit(int[] prices) {
                int best = 0, left = 0;
                for (int right = 1; right < prices.length; right++) {
                    if (prices[right] < prices[left]) left = right; //>
                    else best = Math.max(best, prices[right] - prices[left]); //>
                }
                return best;
            }
        }
        ''',
    )],
)

problem(
    id="nearby-duplicate",
    title="Repeat Within Distance k",
    difficulty="Easy",
    topics=["Array", "Sliding Window", "Hash Set"],
    statement="""
    Return `true` if `nums` has two equal values at positions `i ≠ j` with `|i − j| ≤ k`.
    """,
    examples=[([[1, 2, 3, 1], 3], True, None), ([[1, 2, 3, 1, 2, 3], 2], False, None)],
    tests=[([[1, 0, 1, 1], 1], True), ([[5], 0], False), ([[4, 4], 0], False)],
    constraints=["1 ≤ nums.length ≤ 10^5", "0 ≤ k ≤ 10^5"],
    hints=["Only the last k values matter.", "Keep them in a set."],
    approaches=[approach(
        name="Sliding Window Set", pattern="sliding-window", time="O(n)", space="O(k)",
        idea="""
        The window holds the last k values in a set. Before adding `nums[right]`, drop `nums[left]` if the window would be longer than k.

        If `nums[right]` is already in the window, its twin is at most k positions back.
        """,
        viz=viz(arr="nums", ptr={"left": "left", "right": "right"}, win=("left", R_OR.format(d="-1")), maps=[("window", "window")]),
        demo=[[1, 2, 3, 1, 2, 3], 2],
        py='''
        def nearby_duplicate(nums, k):
            window, left = set(), 0
            for right in range(len(nums)):
                if right - left > k:
                    window.discard(nums[left])
                    left += 1  #> Keep only the last {k} values: drop {nums[left - 1]}.
                if nums[right] in window:
                    return True  #> {nums[right]} is already in the window!
                window.add(nums[right])
            return False
        ''',
        java='''
        class Solution {
            public boolean nearbyDuplicate(int[] nums, int k) {
                Set<Integer> window = new HashSet<>();
                for (int right = 0, left = 0; right < nums.length; right++) {
                    for (; right - left > k; left++) window.remove(nums[left]); //>
                    if (!window.add(nums[right])) return true; //>
                }
                return false;
            }
        }
        ''',
    )],
)

problem(
    id="most-vowels-window",
    title="Most Vowels in a Window",
    difficulty="Medium",
    topics=["String", "Sliding Window"],
    statement="""
    Return the largest number of vowels (`a, e, i, o, u`) in any substring of `s` with length exactly `k`.
    """,
    examples=[(["abciiidef", 3], 3, "\"iii\""), (["leetcode", 3], 2, None)],
    tests=[(["rhythm", 2], 0), (["aeiou", 2], 2), (["tryhard", 4], 1)],
    constraints=["1 ≤ k ≤ s.length ≤ 10^5", "s is lowercase"],
    hints=["Fixed window: add the entering letter, remove the leaving letter."],
    approaches=[approach(
        name="Fixed Sliding Window", pattern="sliding-window", time="O(n)", space="O(1)",
        idea="""
        Add one if `s[right]` is a vowel. When the window grows past k, subtract one if `s[left]` was a vowel and move `left`. Keep the best count.
        """,
        viz=viz(arr="s", ptr={"left": "left", "right": "right"}, win=("left", R_OR.format(d="-1")), vars=["count", "best"]),
        demo=["abciiidef", 3],
        py='''
        def most_vowels(s, k):
            count, best, left = 0, 0, 0
            for right in range(len(s)):
                count += s[right] in "aeiou"
                if right - left + 1 > k:
                    count -= s[left] in "aeiou"
                    left += 1
                best = max(best, count)  #> The window {q(s[left:right + 1])} has {count} vowels. Best: {best}.
            return best
        ''',
        java='''
        class Solution {
            public int mostVowels(String s, int k) {
                String v = "aeiou";
                int count = 0, best = 0, left = 0;
                for (int right = 0; right < s.length(); right++) {
                    if (v.indexOf(s.charAt(right)) >= 0) count++;
                    for (; right - left + 1 > k; left++) if (v.indexOf(s.charAt(left)) >= 0) count--;
                    best = Math.max(best, count); //>
                }
                return best;
            }
        }
        ''',
    )],
)

problem(
    id="best-contiguous-sum",
    title="Best Contiguous Sum",
    difficulty="Medium",
    topics=["Array", "Sliding Window", "Dynamic Programming"],
    patterns=["dp"],
    statement="""
    Return the largest sum of any non-empty contiguous subarray of `nums`.
    """,
    examples=[([[-2, 1, -3, 4, -1, 2, 1, -5, 4]], 6, "[4, -1, 2, 1] sums to 6."), ([[5, 4, -1, 7, 8]], 23, None)],
    tests=[([[1]], 1), ([[-3, -1, -2]], -1), ([[2, -1, 2]], 3)],
    constraints=["1 ≤ nums.length ≤ 10^5"],
    hints=["A window whose sum turned negative only hurts what comes next."],
    approaches=[approach(
        name="Sliding Window (Kadane)", pattern="sliding-window", time="O(n)", space="O(1)",
        idea="""
        Grow the window to the right and keep its sum. If the sum before adding `nums[right]` is negative, that prefix only drags things down, so restart the window: `left` jumps to `right`.

        The best window sum seen at any point is the answer. This is Kadane's algorithm seen as a sliding window.
        """,
        viz=viz(arr="nums", ptr={"left": "left", "right": "right"}, win=("left", R_OR.format(d="-1")), vars=["total", "best"]),
        py='''
        def best_contiguous(nums):
            total, best, left = 0, nums[0], 0
            for right in range(len(nums)):
                if total < 0:
                    total, left = 0, right  #> The window sum went negative, so restart the window at index {right}.
                total += nums[right]  #> Add {nums[right]}. The window sum is {total}.
                best = max(best, total)
            return best
        ''',
        java='''
        class Solution {
            public int bestContiguous(int[] nums) {
                int sum = 0, best = nums[0];
                for (int right = 0; right < nums.length; right++) {
                    if (sum < 0) sum = 0; //>
                    sum += nums[right]; //>
                    best = Math.max(best, sum);
                }
                return best;
            }
        }
        ''',
    )],
)

problem(
    id="card-points",
    title="Take Cards From Both Ends",
    difficulty="Medium",
    topics=["Array", "Sliding Window", "Prefix Sum"],
    statement="""
    Cards lie in a row with point values `cards`. You must take exactly `k` cards, each time from the left end or the
    right end. Return the maximum total points.
    """,
    examples=[([[1, 2, 3, 4, 5, 6, 1], 3], 12, "Take 1, 6 and 5 from the right."), ([[9, 7, 7, 9, 7, 7, 9], 7], 55, None)],
    tests=[([[2, 2, 2], 2], 4), ([[1, 1000, 1], 1], 1), ([[100, 40, 17, 9, 73, 75], 3], 248)],
    constraints=["1 ≤ k ≤ cards.length ≤ 10^5"],
    hints=["The cards you leave behind form one contiguous window of length n − k.",
           "Minimise the sum of that window."],
    approaches=[approach(
        name="Sliding Window (cards left behind)", pattern="sliding-window", time="O(n)", space="O(1)",
        idea="""
        Whatever you take from the ends, the cards you leave form one contiguous window of length n − k. So find the window of that length with the smallest sum.

        The answer is the total of all cards minus that smallest window.
        """,
        viz=viz(arr="cards", ptr={"left": "left", "right": "right"}, win=("left", R_OR.format(d="-1")), vars=["window", "smallest"]),
        demo=[[1, 2, 3, 4, 5, 6, 1], 3],
        py='''
        def card_points(cards, k):
            size, total = len(cards) - k, sum(cards)
            window, smallest, left = 0, total, 0
            for right in range(len(cards)):
                window += cards[right]
                if right - left + 1 > size:
                    window -= cards[left]
                    left += 1
                if right - left + 1 == size:
                    smallest = min(smallest, window)  #> Leaving {cards[left:right + 1]} behind costs {window}. Smallest: {smallest}.
            return total - (smallest if size else 0)
        ''',
        java='''
        class Solution {
            public int cardPoints(int[] cards, int k) {
                int size = cards.length - k, total = 0, sum = 0, left = 0;
                for (int c : cards) total += c;
                int smallest = total;
                for (int right = 0; right < cards.length; right++) {
                    sum += cards[right];
                    for (; right - left + 1 > size; left++) sum -= cards[left];
                    if (right - left + 1 == size) smallest = Math.min(smallest, sum); //>
                }
                return total - (size == 0 ? 0 : smallest);
            }
        }
        ''',
    )],
)

problem(
    id="max-frequency-k-raises",
    title="Most Equal Values With k Raises",
    difficulty="Medium",
    topics=["Array", "Sliding Window", "Sorting", "Greedy"],
    statement="""
    In one operation you can add 1 to any element of `nums`. Using at most `k` operations in total, return the
    largest possible number of equal elements.
    """,
    examples=[([[1, 2, 4], 5], 3, "Raise 1 three times and 2 twice: all become 4."), ([[1, 4, 8, 13], 5], 2, None)],
    tests=[([[3, 9, 6], 2], 1), ([[5], 0], 1), ([[1, 1, 1, 2], 1], 3)],
    constraints=["1 ≤ nums.length ≤ 10^5", "0 ≤ k ≤ 10^5"],
    hints=["Sort first: it's best to raise the values just below a target.",
           "A sorted window can be raised to its right end if right value × length − sum ≤ k."],
    approaches=[approach(
        name="Sort + Sliding Window", pattern="sliding-window", time="O(n log n)", space="O(1) extra",
        idea="""
        After sorting, try to raise every number in the window up to `nums[right]`, the window's largest value. The cost is that value times the length, minus the window sum.

        While the cost exceeds k, shrink from the left. The widest affordable window is the answer.
        """,
        viz=viz(arr="nums", ptr={"left": "left", "right": "right"}, win=("left", R_OR.format(d="-1")), vars=["total", "best"]),
        py='''
        def max_frequency(nums, k):
            nums.sort()
            total, best, left = 0, 0, 0
            for right in range(len(nums)):
                total += nums[right]
                while nums[right] * (right - left + 1) - total > k:
                    total -= nums[left]
                    left += 1  #> Raising everything to {nums[right]} costs too much, so shrink: left moves to {left}.
                best = max(best, right - left + 1)  #> Raising the window to {nums[right]} costs {nums[right] * (right - left + 1) - total}. Best: {best}.
            return best
        ''',
        java='''
        class Solution {
            public int maxFrequency(int[] nums, int k) {
                Arrays.sort(nums);
                long sum = 0;
                int best = 0, left = 0;
                for (int right = 0; right < nums.length; right++) {
                    sum += nums[right];
                    for (; (long) nums[right] * (right - left + 1) - sum > k; left++) sum -= nums[left]; //>
                    best = Math.max(best, right - left + 1); //>
                }
                return best;
            }
        }
        ''',
    )],
)

problem(
    id="exactly-k-odd",
    title="Runs With Exactly k Odd Numbers",
    difficulty="Medium",
    topics=["Array", "Sliding Window", "Math"],
    statement="""
    Return the number of contiguous subarrays of `nums` that contain exactly `k` odd numbers.
    """,
    examples=[([[1, 1, 2, 1, 1], 3], 2, None), ([[2, 4, 6], 1], 0, None)],
    tests=[([[2, 2, 2, 1, 2, 2, 1, 2, 2, 2], 2], 16), ([[1], 1], 1), ([[1, 2, 1], 1], 4)],
    constraints=["1 ≤ nums.length ≤ 5·10^4", "1 ≤ k ≤ nums.length"],
    hints=["Counting 'at most k' with a sliding window is easy.", "Exactly k = at most k − at most (k − 1)."],
    approaches=[approach(
        name="Sliding Window (at most k trick)", pattern="sliding-window", time="O(n)", space="O(1)",
        idea="""
        Counting windows with at most k odd numbers is the standard template: after shrinking, every window ending at `right` adds right − left + 1 subarrays.

        Windows with exactly k odd numbers are those with at most k, minus those with at most k − 1.
        """,
        viz=viz(arr="nums", ptr={"left": "left", "right": "right"}, win=("left", R_OR.format(d="-1")), vars=["odd", "count"]),
        demo=[[1, 1, 2, 1, 1], 3],
        py='''
        def exactly_k_odd(nums, k):
            def at_most(k):
                odd, count, left = 0, 0, 0
                for right in range(len(nums)):
                    odd += nums[right] % 2
                    while odd > k:
                        odd -= nums[left] % 2
                        left += 1
                    count += right - left + 1  #> Windows ending at {right} with at most {k} odd numbers: {right - left + 1}. Total {count}.
                return count

            return at_most(k) - at_most(k - 1)  #> Exactly {k} odd = at most {k} minus at most {k - 1}.
        ''',
        java='''
        class Solution {
            public int exactlyKOdd(int[] nums, int k) {
                return atMost(nums, k) - atMost(nums, k - 1); //>2
            }

            private int atMost(int[] nums, int k) {
                int odd = 0, count = 0, left = 0;
                for (int right = 0; right < nums.length; right++) {
                    odd += nums[right] % 2;
                    for (; odd > k; left++) odd -= nums[left] % 2;
                    count += right - left + 1; //>1
                }
                return count;
            }
        }
        ''',
    )],
)
