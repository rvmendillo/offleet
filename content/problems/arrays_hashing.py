"""Arrays & Hashing problems (original statements)."""
from dsl import problem, approach, viz

problem(
    id="two-sum-any-order",
    title="Pair Sum in Any Order",
    difficulty="Easy",
    topics=["Array", "Hash Map", "Two Pointers"],
    statement="""
    Given an unsorted integer array `nums` and a `target`, return the indices `[i, j]` (with `i < j`) of the two
    numbers that add up to `target`. Exactly one answer exists.
    """,
    examples=[([[3, 8, 11, 5], 13], [1, 3], "8 + 5 = 13"), ([[4, 4], 8], [0, 1], None)],
    tests=[([[2, 7, 11, 15], 9], [0, 1]), ([[-3, 4, 3, 90], 0], [0, 2]), ([[1, 5, 9, 2], 11], [2, 3])],
    constraints=["2 ≤ nums.length ≤ 10^4", "exactly one answer"],
    hints=["For each number, the partner you need is target − number.", "A hash map finds a partner instantly."],
    approaches=[
        approach(
            name="Hash Map", pattern="hash-map", time="O(n)", space="O(n)",
            idea="""
            Walk through the numbers once. For each number x, the partner we need is target − x.

            If that partner was already seen, we're done. Otherwise remember x and its index for later numbers.
            """,
            viz=viz(arr="nums", ptr={"i": "i"}, maps=[("seen", "seen")], vars=["target"]),
            py='''
            def two_sum(nums, target):
                seen = {}
                for i, x in enumerate(nums):
                    if target - x in seen:
                        return [seen[target - x], i]  #> {target - x} was seen at index {seen[target - x]}, and {x} completes the pair!
                    seen[x] = i  #> We need {target - x}, which we haven't seen. Remember {x} at index {i}.
                return []
            ''',
            java='''
            class Solution {
                public int[] twoSum(int[] nums, int target) {
                    Map<Integer, Integer> seen = new HashMap<>();
                    for (int i = 0; i < nums.length; i++) {
                        Integer j = seen.get(target - nums[i]);
                        if (j != null) return new int[]{j, i}; //>
                        seen.put(nums[i], i); //>
                    }
                    return new int[0];
                }
            }
            ''',
        ),
        approach(
            name="Sort + Two Pointers", pattern="two-pointers", time="O(n log n)", space="O(n)",
            idea="""
            Sort the positions by their values, then run the classic two-pointer pair search from both ends of that sorted order.

            We sort positions, not values, so we can still return the original indices.
            """,
            viz=viz(arr="[nums[i] for i in idx]", label="values in sorted order", ptr={"L": "l", "R": "r"}, vars=["s", "target"]),
            py='''
            def two_sum(nums, target):
                idx = sorted(range(len(nums)), key=lambda i: nums[i])  #> Sort the positions by value.
                l, r = 0, len(nums) - 1
                while l < r:
                    s = nums[idx[l]] + nums[idx[r]]  #> {nums[idx[l]]} plus {nums[idx[r]]} is {s}.
                    if s == target:
                        return sorted([idx[l], idx[r]])  #> Found it at original indices {sorted([idx[l], idx[r]])}.
                    if s < target:
                        l += 1
                    else:
                        r -= 1
                return []
            ''',
            java='''
            class Solution {
                public int[] twoSum(int[] nums, int target) {
                    Integer[] idx = new Integer[nums.length];
                    for (int i = 0; i < idx.length; i++) idx[i] = i;
                    Arrays.sort(idx, (a, b) -> Integer.compare(nums[a], nums[b])); //>
                    int l = 0, r = nums.length - 1;
                    while (l < r) {
                        int s = nums[idx[l]] + nums[idx[r]]; //>
                        if (s == target) return new int[]{Math.min(idx[l], idx[r]), Math.max(idx[l], idx[r])}; //>
                        if (s < target) l++; else r--;
                    }
                    return new int[0];
                }
            }
            ''',
        ),
    ],
)

problem(
    id="has-repeat",
    title="Any Value Twice?",
    difficulty="Easy",
    topics=["Array", "Hash Set", "Sorting"],
    statement="""
    Return `true` if any value appears at least twice in `nums`, and `false` if every value is distinct.
    """,
    examples=[([[1, 2, 3, 1]], True, None), ([[1, 2, 3, 4]], False, None)],
    tests=[([[7]], False), ([[1, 1, 1, 3, 3, 4, 3, 2, 4, 2]], True), ([[-1, 1]], False)],
    constraints=["1 ≤ nums.length ≤ 10^5"],
    hints=["A set remembers what you've already seen.", "After sorting, equal values sit side by side."],
    approaches=[
        approach(
            name="Hash Set", pattern="hash-map", time="O(n)", space="O(n)",
            idea="""
            Scan the numbers and keep a set of values seen so far. The first time a value is already in the set, we found a repeat.
            """,
            viz=viz(arr="nums", ptr={"i": "i"}, maps=[("seen", "seen")]),
            py='''
            def has_repeat(nums):
                seen = set()
                for i, x in enumerate(nums):
                    if x in seen:
                        return True  #> {x} is already in the set: a repeat!
                    seen.add(x)  #> {x} is new. Add it to the set.
                return False
            ''',
            java='''
            class Solution {
                public boolean hasRepeat(int[] nums) {
                    Set<Integer> seen = new HashSet<>();
                    for (int x : nums) {
                        if (seen.contains(x)) return true; //>
                        seen.add(x); //>
                    }
                    return false;
                }
            }
            ''',
        ),
        approach(
            name="Sort + Neighbour Pointers", pattern="two-pointers", time="O(n log n)", space="O(1) extra",
            idea="""
            Sort the numbers so equal values become neighbours. Then walk two adjacent pointers, i − 1 and i, and compare them.
            """,
            viz=viz(arr="nums", ptr={"i-1": "i - 1", "i": "i"}),
            py='''
            def has_repeat(nums):
                nums.sort()  #> Sort so equal values sit next to each other.
                for i in range(1, len(nums)):
                    if nums[i] == nums[i - 1]:
                        return True  #> Neighbours {nums[i - 1]} and {nums[i]} are equal!
                return False
            ''',
            java='''
            class Solution {
                public boolean hasRepeat(int[] nums) {
                    Arrays.sort(nums); //>
                    for (int i = 1; i < nums.length; i++) if (nums[i] == nums[i - 1]) return true; //>
                    return false;
                }
            }
            ''',
        ),
    ],
)

problem(
    id="same-letters",
    title="Same Letters, Different Order",
    difficulty="Easy",
    topics=["String", "Hash Map", "Counting"],
    statement="""
    Return `true` if lowercase strings `s` and `t` use exactly the same letters the same number of times
    (that is, `t` is an anagram of `s`).
    """,
    examples=[(["listen", "silent"], True, None), (["rat", "car"], False, None)],
    tests=[(["a", "ab"], False), (["", ""], True), (["aacc", "ccac"], False)],
    constraints=["0 ≤ s.length, t.length ≤ 5·10^4"],
    hints=["Count letters in s, subtract letters in t."],
    approaches=[approach(
        name="Counting", pattern="hash-map", time="O(n)", space="O(1)",
        idea="""
        Use 26 counters. Add one for every letter of `s` and subtract one for every letter of `t`. If all counters end at zero, the strings are anagrams.
        """,
        why="The counter array has a fixed size of 26, so extra space is constant.",
        viz=viz(maps=[("counts", "{chr(i + 97): c for i, c in enumerate(count) if c}")]),
        py='''
        def same_letters(s, t):
            if len(s) != len(t):
                return False
            count = [0] * 26
            for a, b in zip(s, t):
                count[ord(a) - 97] += 1
                count[ord(b) - 97] -= 1  #> Add {q(a)} and subtract {q(b)}.
            return all(c == 0 for c in count)  #> All counters are zero? {yn(all(c == 0 for c in count))}.
        ''',
        java='''
        class Solution {
            public boolean sameLetters(String s, String t) {
                if (s.length() != t.length()) return false;
                int[] count = new int[26];
                for (int i = 0; i < s.length(); i++) {
                    count[s.charAt(i) - 'a']++;
                    count[t.charAt(i) - 'a']--; //>
                }
                for (int c : count) if (c != 0) return false;
                return true; //>
            }
        }
        ''',
    )],
)

problem(
    id="group-anagrams",
    title="Group Words by Their Letters",
    difficulty="Medium",
    topics=["String", "Hash Map", "Sorting"],
    statement="""
    Group the lowercase words in `words` so that words made of exactly the same letters are together.
    Return the groups in any order (and words within a group in any order).
    """,
    examples=[([["eat", "tea", "tan", "ate", "nat", "bat"]], [["bat"], ["nat", "tan"], ["ate", "eat", "tea"]], None),
              ([[""]], [[""]], None)],
    tests=[([["a"]], [["a"]]), ([["ab", "ba", "abc"]], [["ab", "ba"], ["abc"]])],
    check="deep-unordered",
    constraints=["1 ≤ words.length ≤ 10^4", "0 ≤ words[i].length ≤ 100"],
    hints=["Anagrams become identical after sorting their letters.", "Use the sorted word as a map key."],
    approaches=[approach(
        name="Hash Map with a Signature", pattern="hash-map", time="O(n · k log k)", space="O(n · k)",
        idea="""
        Give every word a signature: its letters in sorted order. Anagrams share the same signature.

        Put each word into a map list under its signature; the map's lists are the groups.
        """,
        viz=viz(maps=[("groups", "groups")]),
        py='''
        def group_anagrams(words):
            groups = {}
            for w in words:
                key = "".join(sorted(w))
                groups.setdefault(key, []).append(w)  #> {q(w)} has signature {q(key)}.
            return list(groups.values())
        ''',
        java='''
        class Solution {
            public List<List<String>> groupAnagrams(String[] words) {
                Map<String, List<String>> groups = new HashMap<>();
                for (String w : words) {
                    char[] c = w.toCharArray();
                    Arrays.sort(c);
                    groups.computeIfAbsent(new String(c), x -> new ArrayList<>()).add(w); //>
                }
                return new ArrayList<>(groups.values());
            }
        }
        ''',
    )],
)

problem(
    id="top-k-frequent",
    title="The k Most Common Values",
    difficulty="Medium",
    topics=["Array", "Hash Map", "Bucket Sort", "Heap"],
    statement="""
    Return the `k` values that appear most often in `nums`, in any order. The answer is guaranteed to be unique.
    """,
    examples=[([[1, 1, 1, 2, 2, 3], 2], [1, 2], None), ([[4], 1], [4], None)],
    tests=[([[5, 5, 6, 6, 6, 7], 1], [6]), ([[1, 2, 2, 3, 3, 3], 3], [1, 2, 3])],
    check="unordered",
    constraints=["1 ≤ nums.length ≤ 10^5", "k is between 1 and the number of distinct values"],
    hints=["Count each value.", "A value appears at most n times, so bucket values by their count."],
    approaches=[approach(
        name="Count + Bucket Sort", pattern="hash-map", time="O(n)", space="O(n)",
        idea="""
        Count how often each value appears. Then make buckets where bucket c holds the values that appear exactly c times.

        Walk the buckets from the highest count down, collecting values until we have k of them.
        """,
        viz=viz(maps=[("counts", "count")], out="res"),
        py='''
        from collections import Counter

        def top_k_frequent(nums, k):
            count = Counter(nums)
            buckets = [[] for _ in range(len(nums) + 1)]
            for x, c in count.items():
                buckets[c].append(x)
            res = []
            for c in range(len(nums), 0, -1):
                for x in buckets[c]:
                    res.append(x)  #> {x} appears {c} times, so it joins the answer.
                    if len(res) == k:
                        return res
            return res
        ''',
        java='''
        class Solution {
            public int[] topKFrequent(int[] nums, int k) {
                Map<Integer, Integer> count = new HashMap<>();
                for (int x : nums) count.merge(x, 1, Integer::sum);
                List<List<Integer>> buckets = new ArrayList<>();
                for (int i = 0; i <= nums.length; i++) buckets.add(new ArrayList<>());
                count.forEach((x, c) -> buckets.get(c).add(x));
                int[] res = new int[k];
                int n = 0;
                for (int c = nums.length; c > 0 && n < k; c--)
                    for (int x : buckets.get(c)) if (n < k) res[n++] = x; //>
                return res;
            }
        }
        ''',
    )],
)

problem(
    id="product-except-self",
    title="Product of Everything Else",
    difficulty="Medium",
    topics=["Array", "Prefix Sum", "Two Pointers"],
    statement="""
    Return an array `res` where `res[i]` is the product of every element of `nums` except `nums[i]`.
    Do it in O(n) time **without division**.
    """,
    examples=[([[1, 2, 3, 4]], [24, 12, 8, 6], None), ([[-1, 1, 0, -3, 3]], [0, 0, 9, 0, 0], None)],
    tests=[([[2, 3]], [3, 2]), ([[0, 0]], [0, 0]), ([[5, 1, 1]], [1, 5, 5])],
    constraints=["2 ≤ nums.length ≤ 10^5"],
    hints=["res[i] = (product of everything left of i) × (product of everything right of i)."],
    approaches=[approach(
        name="Left & Right Running Products", pattern="prefix-sum", time="O(n)", space="O(1) extra",
        idea="""
        The answer at i is the product of everything to its left times everything to its right.

        First sweep left to right, writing the running product of the left side into the result. Then sweep right to left with a second running product for the right side, multiplying it in.
        """,
        why="Two passes; apart from the output array we only keep one running number.",
        viz=viz(arrays=[("nums", {"i": "i"}), ("res", {"i": "i"})], vars=["left", "right"]),
        py='''
        def product_except_self(nums):
            n = len(nums)
            res = [1] * n
            left = 1
            for i in range(n):
                res[i] = left  #> Everything left of index {i} multiplies to {left}.
                left *= nums[i]
            right = 1
            for i in range(n - 1, -1, -1):
                res[i] *= right  #> Times everything right of index {i} ({right}) gives {res[i]}.
                right *= nums[i]
            return res
        ''',
        java='''
        class Solution {
            public int[] productExceptSelf(int[] nums) {
                int n = nums.length;
                int[] res = new int[n];
                for (int i = 0, left = 1; i < n; left *= nums[i++]) res[i] = left; //>
                for (int i = n - 1, right = 1; i >= 0; right *= nums[i--]) res[i] *= right; //>
                return res;
            }
        }
        ''',
    )],
)

problem(
    id="longest-consecutive-run",
    title="Longest Run of Consecutive Values",
    difficulty="Medium",
    topics=["Array", "Hash Set"],
    statement="""
    Given an unsorted array `nums`, return the length of the longest sequence of consecutive integers
    (like 4, 5, 6, 7) whose values all appear in `nums`. Aim for O(n).
    """,
    examples=[([[100, 4, 200, 1, 3, 2]], 4, "1, 2, 3, 4"), ([[0, 3, 7, 2, 5, 8, 4, 6, 0, 1]], 9, None)],
    tests=[([[]], 0), ([[5]], 1), ([[1, 2, 0, 1]], 3)],
    constraints=["0 ≤ nums.length ≤ 10^5"],
    hints=["Only start counting at a value whose predecessor is missing."],
    approaches=[approach(
        name="Hash Set", pattern="hash-map", time="O(n)", space="O(n)",
        idea="""
        Put all values in a set. A value starts a run only if the value just below it is missing.

        From each start, count upward while the next value exists. Every value is counted at most once overall, so the total work is linear.
        """,
        viz=viz(maps=[("values", "s")], vars=["x", "length", "best"]),
        py='''
        def longest_run(nums):
            s, best = set(nums), 0
            for x in s:
                if x - 1 not in s:
                    length = 1
                    while x + length in s:
                        length += 1
                    best = max(best, length)  #> {x} starts a run of length {length}. Best: {best}.
            return best
        ''',
        java='''
        class Solution {
            public int longestRun(int[] nums) {
                Set<Integer> s = new HashSet<>();
                for (int x : nums) s.add(x);
                int best = 0;
                for (int x : s) {
                    if (s.contains(x - 1)) continue;
                    int length = 1;
                    while (s.contains(x + length)) length++;
                    best = Math.max(best, length); //>
                }
                return best;
            }
        }
        ''',
    )],
)

problem(
    id="majority-vote",
    title="The Majority Value",
    difficulty="Easy",
    topics=["Array", "Counting"],
    statement="""
    A value appears in `nums` more than `n / 2` times. Return it, using O(1) extra memory.
    """,
    examples=[([[3, 2, 3]], 3, None), ([[2, 2, 1, 1, 1, 2, 2]], 2, None)],
    tests=[([[1]], 1), ([[6, 5, 5]], 5), ([[4, 4, 9, 4, 9]], 4)],
    constraints=["1 ≤ n ≤ 5·10^4", "a majority value always exists"],
    hints=["Pair off different values; the majority survives."],
    approaches=[approach(
        name="Boyer–Moore Voting", pattern="math", time="O(n)", space="O(1)",
        idea="""
        Keep a candidate and a counter. A matching value adds a vote; a different value removes one. When the counter hits zero, the next value becomes the new candidate.

        Every removed vote cancels one majority value with one other value, and the majority has more than half, so it survives as the final candidate.
        """,
        viz=viz(arr="nums", ptr={"i": "i"}, vars=["candidate", "votes"]),
        py='''
        def majority(nums):
            candidate, votes = None, 0
            for i, x in enumerate(nums):
                if votes == 0:
                    candidate = x  #> No votes left, so {x} becomes the candidate.
                votes += 1 if x == candidate else -1  #> {x} {"votes for" if x == candidate else "votes against"} the candidate. Votes: {votes}.
            return candidate
        ''',
        java='''
        class Solution {
            public int majority(int[] nums) {
                int candidate = 0, votes = 0;
                for (int x : nums) {
                    if (votes == 0) candidate = x; //>
                    votes += x == candidate ? 1 : -1; //>
                }
                return candidate;
            }
        }
        ''',
    )],
)

problem(
    id="first-unique-letter",
    title="First Letter That Appears Once",
    difficulty="Easy",
    topics=["String", "Hash Map", "Counting"],
    statement="""
    Return the index of the first character in lowercase string `s` that appears exactly once, or `-1` if there is none.
    """,
    examples=[(["swiss"], 1, "'w' is the first letter used once."), (["aabb"], -1, None)],
    tests=[(["z"], 0), (["loveleetcode"], 2), (["abcabd"], 2)],
    constraints=["1 ≤ s.length ≤ 10^5"],
    hints=["Count every letter first, then scan again."],
    approaches=[approach(
        name="Two-Pass Counting", pattern="hash-map", time="O(n)", space="O(1)",
        idea="""
        First pass: count every letter. Second pass: return the first index whose letter has a count of exactly one.
        """,
        viz=viz(arr="s", ptr={"i": "i"}, maps=[("counts", "count")]),
        py='''
        from collections import Counter

        def first_unique(s):
            count = Counter(s)
            for i, ch in enumerate(s):  #> {q(ch)} appears {plural(count[ch], "time")}.
                if count[ch] == 1:
                    return i  #> That's the first letter used once, at index {i}.
            return -1
        ''',
        java='''
        class Solution {
            public int firstUnique(String s) {
                int[] count = new int[26];
                for (char c : s.toCharArray()) count[c - 'a']++;
                for (int i = 0; i < s.length(); i++) //>
                    if (count[s.charAt(i) - 'a'] == 1) return i; //>
                return -1;
            }
        }
        ''',
    )],
)

problem(
    id="letter-pattern-match",
    title="Same Shape Strings",
    difficulty="Easy",
    topics=["String", "Hash Map"],
    statement="""
    Two strings have the same shape (they are isomorphic) if you can replace each character of `s` with another
    character, consistently and one-to-one, to obtain `t`. Return `true` if `s` and `t` have the same shape.
    """,
    examples=[(["egg", "add"], True, "e→a, g→d"), (["foo", "bar"], False, None)],
    tests=[(["paper", "title"], True), (["badc", "baba"], False), (["ab", "ab"], True)],
    constraints=["1 ≤ s.length = t.length ≤ 5·10^4"],
    hints=["Map characters both ways to prevent two letters mapping to the same one."],
    approaches=[approach(
        name="Two Hash Maps", pattern="hash-map", time="O(n)", space="O(1)",
        idea="""
        Keep a map from `s` letters to `t` letters and another map back. Walk both strings together; if either map already holds a different partner, the shapes differ.
        """,
        viz=viz(arrays=[("s", {"i": "i"}), ("t", {"i": "i"})], maps=[("s → t", "fwd"), ("t → s", "back")]),
        demo=["paper", "title"],
        py='''
        def same_shape(s, t):
            fwd, back = {}, {}
            for i, (a, b) in enumerate(zip(s, t)):
                if fwd.get(a, b) != b or back.get(b, a) != a:
                    return False  #> {q(a)} and {q(b)} would break the one-to-one pairing.
                fwd[a], back[b] = b, a  #> {q(a)} pairs with {q(b)}.
            return True
        ''',
        java='''
        class Solution {
            public boolean sameShape(String s, String t) {
                Map<Character, Character> fwd = new HashMap<>(), back = new HashMap<>();
                for (int i = 0; i < s.length(); i++) {
                    char a = s.charAt(i), b = t.charAt(i);
                    if (fwd.getOrDefault(a, b) != b || back.getOrDefault(b, a) != a) return false; //>
                    fwd.put(a, b); back.put(b, a); //>
                }
                return true;
            }
        }
        ''',
    )],
)

problem(
    id="ransom-letters",
    title="Build a Note From Magazine Letters",
    difficulty="Easy",
    topics=["String", "Hash Map", "Counting"],
    statement="""
    Can you write the lowercase string `note` using letters cut from `magazine`, using each magazine letter at most
    once? Return `true` or `false`.
    """,
    examples=[(["aa", "aab"], True, None), (["aa", "ab"], False, None)],
    tests=[(["", "x"], True), (["abc", "cba"], True), (["z", ""], False)],
    constraints=["0 ≤ note.length, magazine.length ≤ 10^5"],
    hints=["Count magazine letters, then spend them."],
    approaches=[approach(
        name="Counting", pattern="hash-map", time="O(n + m)", space="O(1)",
        idea="""
        Count the letters available in the magazine. Then spend one count for each letter of the note; if any count would go negative, the note can't be built.
        """,
        viz=viz(arr="note", maps=[("letters left", "{chr(i + 97): c for i, c in enumerate(count) if c}")]),
        demo=["aab", "baa"],
        py='''
        def can_build(note, magazine):
            count = [0] * 26
            for ch in magazine:
                count[ord(ch) - 97] += 1
            for ch in note:
                count[ord(ch) - 97] -= 1  #> Use one {q(ch)}. {count[ord(ch) - 97]} left.
                if count[ord(ch) - 97] < 0:
                    return False  #> We ran out of {q(ch)}.
            return True  #> Every letter of the note was available.
        ''',
        java='''
        class Solution {
            public boolean canBuild(String note, String magazine) {
                int[] count = new int[26];
                for (char c : magazine.toCharArray()) count[c - 'a']++;
                for (char c : note.toCharArray()) {
                    count[c - 'a']--; //>
                    if (count[c - 'a'] < 0) return false; //>
                }
                return true; //>
            }
        }
        ''',
    )],
)

problem(
    id="first-missing-positive",
    title="Smallest Missing Positive",
    difficulty="Hard",
    topics=["Array", "Hash Map", "In-place"],
    statement="""
    Return the smallest positive integer that does not appear in the unsorted array `nums`.
    Use O(n) time and O(1) extra memory (you may modify `nums`).
    """,
    examples=[([[3, 4, -1, 1]], 2, None), ([[7, 8, 9, 11, 12]], 1, None)],
    tests=[([[1, 2, 0]], 3), ([[1]], 2), ([[2, 2, 1, 1]], 3)],
    constraints=["1 ≤ nums.length ≤ 10^5"],
    hints=["The answer is between 1 and n + 1.", "Use the array itself as a hash table: put value v at index v − 1."],
    approaches=[approach(
        name="Index as Hash (cyclic placement)", pattern="hash-map", time="O(n)", space="O(1)",
        idea="""
        The answer must be between 1 and n + 1. So try to place every value v from 1 to n at index v − 1 by swapping it there.

        Afterwards, the first index i that doesn't hold i + 1 reveals the missing positive.
        """,
        why="Each swap puts one value in its final place, so there are at most n swaps in total.",
        viz=viz(arr="nums", ptr={"i": "i"}),
        py='''
        def first_missing_positive(nums):
            n = len(nums)
            for i in range(n):
                while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
                    j = nums[i] - 1
                    nums[i], nums[j] = nums[j], nums[i]  #> Send {nums[j]} to its home, index {j}.
            for i in range(n):
                if nums[i] != i + 1:
                    return i + 1  #> Index {i} doesn't hold {i + 1}, so {i + 1} is missing.
            return n + 1
        ''',
        java='''
        class Solution {
            public int firstMissingPositive(int[] nums) {
                int n = nums.length;
                for (int i = 0; i < n; i++) {
                    while (nums[i] >= 1 && nums[i] <= n && nums[nums[i] - 1] != nums[i]) {
                        int j = nums[i] - 1, t = nums[j]; nums[j] = nums[i]; nums[i] = t; //>
                    }
                }
                for (int i = 0; i < n; i++) if (nums[i] != i + 1) return i + 1; //>
                return n + 1;
            }
        }
        ''',
    )],
)
