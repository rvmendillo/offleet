"""Sliding Window problems (original statements)."""
from dsl import problem, approach, viz

# Window bounds that also work before the loop variable exists.
R_OR = "locals().get('r', {d})"

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
    constraints=["0 ≤ s.length ≤ 5·10^4"],
    hints=["Keep a window with no repeats.", "When a repeat enters, jump the left edge past the previous copy."],
    approaches=[approach(
        name="Sliding Window", pattern="sliding-window", time="O(n)", space="O(k)",
        idea="""
        Keep a window from L to R that never contains a repeat, and remember the last index where each character was seen.

        When the new character at R was already seen inside the window, jump L just past that earlier copy. The window is valid again, so we update the best length.
        """,
        why="R visits every character once and L only moves forward, so the work is linear. The map holds at most one entry per distinct character, k.",
        viz=viz(arr="s", ptr={"L": "l", "R": "r"}, win=("l", "r"), maps=[("last seen", "last")], vars=["best"]),
        py='''
        def longest_unique(s):
            last, l, best = {}, 0, 0
            for r, ch in enumerate(s):  #> R moves to index {r}, the letter {q(ch)}.
                if last.get(ch, -1) >= l:
                    l = last[ch] + 1  #> {q(ch)} is already in the window, so L jumps to index {l}.
                last[ch] = r
                best = max(best, r - l + 1)  #> The window is {q(s[l:r+1])}, length {r - l + 1}. Best so far: {best}.
            return best
        ''',
        java='''
        class Solution {
            public int longestUnique(String s) {
                Map<Character, Integer> last = new HashMap<>();
                int l = 0, best = 0;
                for (int r = 0; r < s.length(); r++) { //>
                    char ch = s.charAt(r);
                    if (last.getOrDefault(ch, -1) >= l) l = last.get(ch) + 1; //>
                    last.put(ch, r);
                    best = Math.max(best, r - l + 1); //>
                }
                return best;
            }
        }
        ''',
    )],
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
        Add up the first k numbers. To slide the window one step right, add the number that enters and subtract the number that leaves.

        Each new window sum takes constant work, so we can check every window in one pass.
        """,
        viz=viz(arr="nums", ptr={"R": "r"}, win=(R_OR.format(d="k - 1") + " - k + 1", R_OR.format(d="k - 1")), vars=["window", "best"]),
        py='''
        def best_window_sum(nums, k):
            window = sum(nums[:k])  #> The first window adds up to {window}.
            best = window
            for r in range(k, len(nums)):
                window += nums[r] - nums[r - k]  #> Slide right: add {nums[r]}, drop {nums[r - k]}. The sum is now {window}.
                best = max(best, window)
            return best  #> The best window sum is {best}.
        ''',
        java='''
        class Solution {
            public int bestWindowSum(int[] nums, int k) {
                int window = 0;
                for (int i = 0; i < k; i++) window += nums[i]; //>
                int best = window;
                for (int r = k; r < nums.length; r++) {
                    window += nums[r] - nums[r - k]; //>
                    best = Math.max(best, window);
                }
                return best; //>
            }
        }
        ''',
    )],
)

problem(
    id="shortest-sum-at-least",
    title="Shortest Run Reaching a Target",
    difficulty="Medium",
    topics=["Array", "Sliding Window", "Prefix Sum"],
    statement="""
    Given positive integers `nums` and a positive `target`, return the length of the shortest contiguous run whose
    sum is **at least** `target`, or `0` if no run reaches it.
    """,
    examples=[([7, [2, 3, 1, 2, 4, 3]], 2, "[4, 3] sums to 7."), ([4, [1, 4, 4]], 1, None)],
    tests=[([11, [1, 1, 1, 1, 1]], 0), ([15, [1, 2, 3, 4, 5]], 5), ([3, [3]], 1)],
    constraints=["1 ≤ nums.length ≤ 10^5", "1 ≤ nums[i] ≤ 10^4"],
    hints=["All numbers are positive, so growing the window always raises the sum.",
           "Once the sum is big enough, shrink from the left as far as possible."],
    approaches=[approach(
        name="Variable Sliding Window", pattern="sliding-window", time="O(n)", space="O(1)",
        idea="""
        Grow the window by moving R and adding numbers. As soon as the sum reaches the target, record the length, then shrink from the left to look for something shorter.

        Because every number is positive, shrinking only lowers the sum, so we stop shrinking as soon as it falls below the target.
        """,
        why="R and L each move forward at most n times.",
        viz=viz(arr="nums", ptr={"L": "l", "R": "r"}, win=("l", R_OR.format(d="-1")), vars=["total", "target", "best"]),
        py='''
        def shortest_at_least(target, nums):
            l, total, best = 0, 0, float("inf")
            for r, x in enumerate(nums):
                total += x  #> Grow: add {x}. The window sum is {total}.
                while total >= target:
                    best = min(best, r - l + 1)  #> {total} reaches {target} with length {r - l + 1}. Best is {best}.
                    total -= nums[l]
                    l += 1  #> Shrink from the left. The sum drops to {total}.
            return 0 if best == float("inf") else best
        ''',
        java='''
        class Solution {
            public int shortestAtLeast(int target, int[] nums) {
                int l = 0, total = 0, best = Integer.MAX_VALUE;
                for (int r = 0; r < nums.length; r++) {
                    total += nums[r]; //>
                    while (total >= target) {
                        best = Math.min(best, r - l + 1); //>
                        total -= nums[l++]; //>
                    }
                }
                return best == Integer.MAX_VALUE ? 0 : best;
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
        In a window, the letters we must change are all except the most common one. So a window is valid while its length minus the top count is at most k.

        Grow the window with R. If it becomes invalid, slide L forward by one. The window never needs to shrink further, because only a bigger top count could give a longer answer.
        """,
        viz=viz(arr="s", ptr={"L": "l", "R": "r"}, win=("l", R_OR.format(d="-1")), maps=[("counts", "count")], vars=["top", "best"]),
        py='''
        def longest_after_changes(s, k):
            count, l, top, best = {}, 0, 0, 0
            for r, ch in enumerate(s):
                count[ch] = count.get(ch, 0) + 1
                top = max(top, count[ch])  #> Add {q(ch)}. The most common letter appears {top} times.
                if r - l + 1 - top > k:
                    count[s[l]] -= 1
                    l += 1  #> More than {k} changes needed, so L slides to {l}.
                best = max(best, r - l + 1)
            return best
        ''',
        java='''
        class Solution {
            public int longestAfterChanges(String s, int k) {
                int[] count = new int[26];
                int l = 0, top = 0, best = 0;
                for (int r = 0; r < s.length(); r++) {
                    top = Math.max(top, ++count[s.charAt(r) - 'A']); //>
                    if (r - l + 1 - top > k) count[s.charAt(l++) - 'A']--; //>
                    best = Math.max(best, r - l + 1);
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
        Count the letters of `p`. Then slide a window of the same length over `s`, keeping letter counts for the window: add the letter entering on the right and remove the one leaving on the left.

        Whenever the two count tables match, the window is a permutation of `p`.
        """,
        why="Comparing two 26-slot tables is constant work per step.",
        viz=viz(arr="s", ptr={"R": "r"}, win=("max(0, " + R_OR.format(d="-1") + " - len(p) + 1)", R_OR.format(d="-1")), vars=["p"]),
        demo=["ab", "eidbaooo"],
        py='''
        def contains_permutation(p, s):
            if len(p) > len(s):
                return False
            need, have = [0] * 26, [0] * 26
            for ch in p:
                need[ord(ch) - 97] += 1
            for r, ch in enumerate(s):
                have[ord(ch) - 97] += 1  #> Add {q(ch)} on the right.
                if r >= len(p):
                    have[ord(s[r - len(p)]) - 97] -= 1  #> Drop {q(s[r - len(p)])} on the left to keep the size at {len(p)}.
                if have == need:
                    return True  #> {q(s[r - len(p) + 1:r + 1])} has exactly the letters of {q(p)}!
            return False
        ''',
        java='''
        class Solution {
            public boolean containsPermutation(String p, String s) {
                if (p.length() > s.length()) return false;
                int[] need = new int[26], have = new int[26];
                for (char c : p.toCharArray()) need[c - 'a']++;
                for (int r = 0; r < s.length(); r++) {
                    have[s.charAt(r) - 'a']++; //>
                    if (r >= p.length()) have[s.charAt(r - p.length()) - 'a']--; //>
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
        Slide a window of length `len(p)` across `s` while maintaining letter counts. After each slide, if the window counts equal the counts of `p`, the window's start index is an answer.
        """,
        viz=viz(arr="s", ptr={"R": "r"}, win=("max(0, " + R_OR.format(d="-1") + " - len(p) + 1)", R_OR.format(d="-1")), out="res"),
        py='''
        def anagram_starts(s, p):
            need, have, res = [0] * 26, [0] * 26, []
            for ch in p:
                need[ord(ch) - 97] += 1
            for r, ch in enumerate(s):
                have[ord(ch) - 97] += 1
                if r >= len(p):
                    have[ord(s[r - len(p)]) - 97] -= 1
                if have == need:
                    res.append(r - len(p) + 1)  #> {q(s[r - len(p) + 1:r + 1])} is an anagram, starting at {res[-1]}.
            return res
        ''',
        java='''
        class Solution {
            public List<Integer> anagramStarts(String s, String p) {
                int[] need = new int[26], have = new int[26];
                List<Integer> res = new ArrayList<>();
                for (char c : p.toCharArray()) need[c - 'a']++;
                for (int r = 0; r < s.length(); r++) {
                    have[s.charAt(r) - 'a']++;
                    if (r >= p.length()) have[s.charAt(r - p.length()) - 'a']--;
                    if (Arrays.equals(have, need)) res.add(r - p.length() + 1); //>
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
    hints=["Track how many required characters are still missing.", "When nothing is missing, shrink from the left while it stays covered."],
    approaches=[approach(
        name="Sliding Window", pattern="sliding-window", time="O(n + m)", space="O(1)",
        idea="""
        Keep a count of how many of each character we still need, and a single number `missing` for the total.

        Move R to grow the window. When `missing` hits zero the window covers `t`: record it, then move L to shrink until a needed character drops out. Repeat until R reaches the end.
        """,
        why="Each character enters and leaves the window at most once; the count table has a fixed alphabet size.",
        viz=viz(arr="s", ptr={"L": "l", "R": "r"}, win=("l", R_OR.format(d="-1")), vars=["missing", "best"]),
        demo=["ADOBECODEBANC", "ABC"],
        py='''
        from collections import Counter

        def min_window(s, t):
            need, missing = Counter(t), len(t)
            l = start = 0
            best = float("inf")
            for r, ch in enumerate(s):
                if need[ch] > 0:
                    missing -= 1  #> {q(ch)} was needed. Still missing: {missing}.
                need[ch] -= 1
                while missing == 0:
                    if r - l + 1 < best:
                        best, start = r - l + 1, l  #> {q(s[l:r + 1])} covers everything. New best length: {best}.
                    need[s[l]] += 1
                    if need[s[l]] > 0:
                        missing += 1  #> Dropping {q(s[l])} breaks the cover.
                    l += 1
            return "" if best == float("inf") else s[start:start + best]
        ''',
        java='''
        class Solution {
            public String minWindow(String s, String t) {
                int[] need = new int[128];
                for (char c : t.toCharArray()) need[c]++;
                int missing = t.length(), l = 0, start = 0, best = Integer.MAX_VALUE;
                for (int r = 0; r < s.length(); r++) {
                    if (need[s.charAt(r)]-- > 0) missing--; //>
                    while (missing == 0) {
                        if (r - l + 1 < best) { best = r - l + 1; start = l; } //>
                        if (++need[s.charAt(l++)] > 0) missing++; //>
                    }
                }
                return best == Integer.MAX_VALUE ? "" : s.substring(start, start + best);
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
        Rephrase: find the longest window that contains at most k zeros, because those zeros can all be flipped.

        Grow with R and count zeros. Whenever there are more than k, move L right until a zero leaves the window.
        """,
        viz=viz(arr="nums", ptr={"L": "l", "R": "r"}, win=("l", R_OR.format(d="-1")), vars=["zeros", "best"]),
        demo=[[1, 1, 0, 0, 1, 1, 1, 0, 1], 1],
        py='''
        def longest_ones(nums, k):
            l = zeros = best = 0
            for r, x in enumerate(nums):
                zeros += x == 0  #> Add {x}. Zeros in the window: {zeros}.
                while zeros > k:
                    zeros -= nums[l] == 0
                    l += 1  #> Too many zeros, so L moves to {l}.
                best = max(best, r - l + 1)
            return best
        ''',
        java='''
        class Solution {
            public int longestOnes(int[] nums, int k) {
                int l = 0, zeros = 0, best = 0;
                for (int r = 0; r < nums.length; r++) {
                    if (nums[r] == 0) zeros++; //>
                    while (zeros > k) if (nums[l++] == 0) zeros--; //>
                    best = Math.max(best, r - l + 1);
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

        When a third kind appears, move L forward and decrease counts until one kind disappears completely.
        """,
        viz=viz(arr="fruits", ptr={"L": "l", "R": "r"}, win=("l", R_OR.format(d="-1")), maps=[("basket", "count")], vars=["best"]),
        demo=[[1, 2, 3, 2, 2]],
        py='''
        def two_baskets(fruits):
            count, l, best = {}, 0, 0
            for r, f in enumerate(fruits):
                count[f] = count.get(f, 0) + 1  #> Pick fruit {f}. Kinds in the baskets: {len(count)}.
                while len(count) > 2:
                    count[fruits[l]] -= 1
                    if count[fruits[l]] == 0:
                        del count[fruits[l]]
                    l += 1  #> Three kinds is too many, so L moves to {l}.
                best = max(best, r - l + 1)
            return best
        ''',
        java='''
        class Solution {
            public int twoBaskets(int[] fruits) {
                Map<Integer, Integer> count = new HashMap<>();
                int l = 0, best = 0;
                for (int r = 0; r < fruits.length; r++) {
                    count.merge(fruits[r], 1, Integer::sum); //>
                    while (count.size() > 2) {
                        if (count.merge(fruits[l], -1, Integer::sum) == 0) count.remove(fruits[l]);
                        l++; //>
                    }
                    best = Math.max(best, r - l + 1);
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
        Grow the window with R and count each character. If more than k distinct characters are inside, shrink from L until one of them disappears. Track the longest valid window.
        """,
        viz=viz(arr="s", ptr={"L": "l", "R": "r"}, win=("l", R_OR.format(d="-1")), maps=[("counts", "count")], vars=["best"]),
        py='''
        def longest_k_distinct(s, k):
            count, l, best = {}, 0, 0
            for r, ch in enumerate(s):
                count[ch] = count.get(ch, 0) + 1
                while len(count) > k:
                    count[s[l]] -= 1
                    if count[s[l]] == 0:
                        del count[s[l]]
                    l += 1  #> More than {k} letters, so shrink: L moves to {l}.
                best = max(best, r - l + 1)  #> The window {q(s[l:r + 1])} is valid. Best: {best}.
            return best
        ''',
        java='''
        class Solution {
            public int longestKDistinct(String s, int k) {
                Map<Character, Integer> count = new HashMap<>();
                int l = 0, best = 0;
                for (int r = 0; r < s.length(); r++) {
                    count.merge(s.charAt(r), 1, Integer::sum);
                    while (count.size() > k) {
                        char c = s.charAt(l++);
                        if (count.merge(c, -1, Integer::sum) == 0) count.remove(c); //>
                    }
                    best = Math.max(best, r - l + 1); //>
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
    hints=["If a window has a small product, so does every window ending at R inside it.",
           "Each step adds r − l + 1 new subarrays."],
    approaches=[approach(
        name="Sliding Window", pattern="sliding-window", time="O(n)", space="O(1)",
        idea="""
        Keep the product of the window from L to R. When it reaches k, divide out numbers from the left until it is small again.

        Then every subarray that ends at R and starts anywhere from L to R qualifies: that's r − l + 1 new ones.
        """,
        viz=viz(arr="nums", ptr={"L": "l", "R": "r"}, win=("l", R_OR.format(d="-1")), vars=["prod", "count"]),
        py='''
        def count_small_products(nums, k):
            if k <= 1:
                return 0
            prod, l, count = 1, 0, 0
            for r, x in enumerate(nums):
                prod *= x
                while prod >= k:
                    prod //= nums[l]
                    l += 1
                count += r - l + 1  #> The window product is {prod}, adding {r - l + 1} subarrays. Total: {count}.
            return count
        ''',
        java='''
        class Solution {
            public int countSmallProducts(int[] nums, int k) {
                if (k <= 1) return 0;
                long prod = 1;
                int l = 0, count = 0;
                for (int r = 0; r < nums.length; r++) {
                    prod *= nums[r];
                    while (prod >= k) prod /= nums[l++];
                    count += r - l + 1; //>
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
        Keep a deque of indexes whose values are decreasing from front to back. The front is always the current window's maximum.

        When a new value arrives, pop smaller values off the back: they can never win again. Pop the front if it slid out of the window.
        """,
        why="Every index is pushed and popped at most once.",
        viz=viz(arr="nums", ptr={"R": "r"}, win=("max(0, " + R_OR.format(d="-1") + " - k + 1)", R_OR.format(d="-1")),
                queues=[("deque (indexes)", "dq")], out="res"),
        demo=[[1, 3, -1, -3, 5, 3, 6], 3],
        py='''
        from collections import deque

        def window_maxes(nums, k):
            dq, res = deque(), []
            for r, x in enumerate(nums):
                while dq and nums[dq[-1]] <= x:
                    dq.pop()
                dq.append(r)  #> Add index {r} (value {x}). Smaller values behind it are gone for good.
                if dq[0] <= r - k:
                    dq.popleft()  #> The front index slid out of the window.
                if r >= k - 1:
                    res.append(nums[dq[0]])  #> The window maximum is {res[-1]}.
            return res
        ''',
        java='''
        class Solution {
            public int[] windowMaxes(int[] nums, int k) {
                Deque<Integer> dq = new ArrayDeque<>();
                int[] res = new int[nums.length - k + 1];
                for (int r = 0; r < nums.length; r++) {
                    while (!dq.isEmpty() && nums[dq.peekLast()] <= nums[r]) dq.pollLast();
                    dq.addLast(r); //>
                    if (dq.peekFirst() <= r - k) dq.pollFirst(); //>
                    if (r >= k - 1) res[r - k + 1] = nums[dq.peekFirst()]; //>
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
        name="Two Pointers (buy & sell)", pattern="sliding-window", time="O(n)", space="O(1)",
        idea="""
        Keep a BUY pointer on the cheapest day so far and let SELL scan forward. Together they form a window from buy day to sell day.

        If SELL finds a cheaper price, it becomes the new buy day. Otherwise check the profit of selling today.
        """,
        viz=viz(arr="prices", ptr={"buy": "buy", "sell": "sell"}, win=("buy", "locals().get('sell', 0)"), vars=["best"]),
        py='''
        def max_profit(prices):
            buy, best = 0, 0
            for sell in range(1, len(prices)):
                if prices[sell] < prices[buy]:
                    buy = sell  #> {prices[sell]} is cheaper, so BUY moves to day {buy}.
                else:
                    best = max(best, prices[sell] - prices[buy])  #> Selling at {prices[sell]} earns {prices[sell] - prices[buy]}. Best: {best}.
            return best
        ''',
        java='''
        class Solution {
            public int maxProfit(int[] prices) {
                int buy = 0, best = 0;
                for (int sell = 1; sell < prices.length; sell++) {
                    if (prices[sell] < prices[buy]) buy = sell; //>
                    else best = Math.max(best, prices[sell] - prices[buy]); //>
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
        Keep a set with the last k values. If the current value is already in the set, its twin is at most k positions back.

        After adding the current value, remove the value that just fell out of the window.
        """,
        viz=viz(arr="nums", ptr={"R": "r"}, maps=[("window", "window")]),
        demo=[[1, 2, 3, 1, 2, 3], 2],
        py='''
        def nearby_duplicate(nums, k):
            window = set()
            for r, x in enumerate(nums):
                if x in window:
                    return True  #> {x} is already among the last {k} values!
                window.add(x)
                if len(window) > k:
                    window.remove(nums[r - k])  #> Keep only the last {k} values: remove {nums[r - k]}.
            return False
        ''',
        java='''
        class Solution {
            public boolean nearbyDuplicate(int[] nums, int k) {
                Set<Integer> window = new HashSet<>();
                for (int r = 0; r < nums.length; r++) {
                    if (!window.add(nums[r])) return true; //>
                    if (window.size() > k) window.remove(nums[r - k]); //>
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
        Count vowels in the first k letters. Then slide one step at a time: add one if the entering letter is a vowel, subtract one if the leaving letter is a vowel, and keep the best count.
        """,
        viz=viz(arr="s", ptr={"R": "r"}, win=("max(0, " + R_OR.format(d="-1") + " - k + 1)", R_OR.format(d="-1")), vars=["count", "best"]),
        demo=["abciiidef", 3],
        py='''
        def most_vowels(s, k):
            count = best = 0
            for r, ch in enumerate(s):
                count += ch in "aeiou"
                if r >= k:
                    count -= s[r - k] in "aeiou"
                best = max(best, count)  #> The window {q(s[max(0, r - k + 1):r + 1])} has {count} vowels. Best: {best}.
            return best
        ''',
        java='''
        class Solution {
            public int mostVowels(String s, int k) {
                String v = "aeiou";
                int count = 0, best = 0;
                for (int r = 0; r < s.length(); r++) {
                    if (v.indexOf(s.charAt(r)) >= 0) count++;
                    if (r >= k && v.indexOf(s.charAt(r - k)) >= 0) count--;
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
        Grow a window to the right and keep its sum. If the sum before adding the next number is negative, that prefix only drags things down, so restart the window at the current number.

        The best window sum seen at any point is the answer. This is Kadane's algorithm seen as a sliding window.
        """,
        viz=viz(arr="nums", ptr={"L": "l", "R": "r"}, win=("l", R_OR.format(d="-1")), vars=["cur", "best"]),
        py='''
        def best_contiguous(nums):
            best, cur, l = nums[0], 0, 0
            for r, x in enumerate(nums):
                if cur < 0:
                    cur, l = 0, r  #> The window sum went negative, so restart the window at index {r}.
                cur += x  #> Add {x}. The window sum is {cur}.
                best = max(best, cur)
            return best
        ''',
        java='''
        class Solution {
            public int bestContiguous(int[] nums) {
                int best = nums[0], cur = 0;
                for (int x : nums) {
                    if (cur < 0) cur = 0; //>
                    cur += x; //>
                    best = Math.max(best, cur);
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
    hints=["The cards you take are some from the left plus the rest from the right.",
           "Start with all k from the left, then trade one left card for one right card at a time."],
    approaches=[approach(
        name="Sliding Window over the ends", pattern="sliding-window", time="O(k)", space="O(1)",
        idea="""
        Start by taking all k cards from the left. Then, one at a time, give back the last left card and take one more from the right end.

        That slides a window of taken cards around the ends of the row; the best total along the way is the answer.
        """,
        viz=viz(arr="cards", vars=["total", "best"]),
        demo=[[1, 2, 3, 4, 5, 6, 1], 3],
        py='''
        def card_points(cards, k):
            total = sum(cards[:k])  #> Take all {k} cards from the left: {total} points.
            best = total
            for i in range(1, k + 1):
                total += cards[-i] - cards[k - i]  #> Give back {cards[k - i]} and take {cards[-i]} from the right: {total}.
                best = max(best, total)
            return best
        ''',
        java='''
        class Solution {
            public int cardPoints(int[] cards, int k) {
                int total = 0, n = cards.length;
                for (int i = 0; i < k; i++) total += cards[i]; //>
                int best = total;
                for (int i = 1; i <= k; i++) {
                    total += cards[n - i] - cards[k - i]; //>
                    best = Math.max(best, total);
                }
                return best;
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
           "A sorted window can be raised to its right end if right × length − sum ≤ k."],
    approaches=[approach(
        name="Sort + Sliding Window", pattern="sliding-window", time="O(n log n)", space="O(1) extra",
        idea="""
        After sorting, try to make every number in a window equal to the window's largest value, the one at R. The cost is that value times the window length, minus the window sum.

        If the cost exceeds k, shrink from the left. The widest affordable window is the answer.
        """,
        viz=viz(arr="nums", ptr={"L": "l", "R": "r"}, win=("l", R_OR.format(d="-1")), vars=["total", "best"]),
        py='''
        def max_frequency(nums, k):
            nums.sort()
            l = total = best = 0
            for r, x in enumerate(nums):
                total += x
                while x * (r - l + 1) - total > k:
                    total -= nums[l]
                    l += 1  #> Raising everything to {x} costs too much, so L moves to {l}.
                best = max(best, r - l + 1)  #> Raising the window to {x} costs {x * (r - l + 1) - total}. Best: {best}.
            return best
        ''',
        java='''
        class Solution {
            public int maxFrequency(int[] nums, int k) {
                Arrays.sort(nums);
                long total = 0;
                int l = 0, best = 0;
                for (int r = 0; r < nums.length; r++) {
                    total += nums[r];
                    while ((long) nums[r] * (r - l + 1) - total > k) total -= nums[l++]; //>
                    best = Math.max(best, r - l + 1); //>
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
        Counting windows with at most k odd numbers is a standard sliding window: every valid window ending at R adds r − l + 1 subarrays.

        Windows with exactly k odd numbers are those with at most k, minus those with at most k − 1.
        """,
        viz=viz(arr="nums", ptr={"L": "l", "R": "r"}, win=("l", R_OR.format(d="-1")), vars=["odd", "count"]),
        demo=[[1, 1, 2, 1, 1], 3],
        py='''
        def exactly_k_odd(nums, k):
            def at_most(k):
                l = count = odd = 0
                for r, x in enumerate(nums):
                    odd += x % 2
                    while odd > k:
                        odd -= nums[l] % 2
                        l += 1
                    count += r - l + 1  #> Windows ending at {r} with at most {k} odd numbers: {r - l + 1}. Total {count}.
                return count

            return at_most(k) - at_most(k - 1)  #> Exactly {k} odd = at most {k} minus at most {k - 1}.
        ''',
        java='''
        class Solution {
            public int exactlyKOdd(int[] nums, int k) {
                return atMost(nums, k) - atMost(nums, k - 1); //>2
            }

            private int atMost(int[] nums, int k) {
                int l = 0, count = 0, odd = 0;
                for (int r = 0; r < nums.length; r++) {
                    odd += nums[r] % 2;
                    while (odd > k) odd -= nums[l++] % 2;
                    count += r - l + 1; //>1
                }
                return count;
            }
        }
        ''',
    )],
)
