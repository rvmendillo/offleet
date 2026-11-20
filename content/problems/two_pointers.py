"""Two Pointers problems (original statements)."""
from dsl import problem, approach, viz

problem(
    id="pair-sum-sorted",
    title="Pair Sum in a Sorted List",
    difficulty="Easy",
    topics=["Array", "Two Pointers"],
    statement="""
    You get a list of integers `nums` sorted from smallest to largest, and a number `target`.
    Find the two different positions whose values add up to `target` and return them as `[i, j]` with `i < j`.

    Exactly one such pair exists.
    """,
    examples=[
        ([[1, 3, 4, 6, 8], 10], [2, 3], "4 + 6 = 10"),
        ([[-3, 0, 2, 6], 2], [1, 2], "0 + 2 = 2"),
    ],
    tests=[([[1, 2], 3], [0, 1]), ([[1, 2, 3, 9], 12], [2, 3]), ([[-5, -2, 0, 7, 12], 7], [0, 4])],
    constraints=["2 ≤ n ≤ 10^5", "nums is sorted ascending", "exactly one answer exists"],
    hints=["Because the list is sorted, a sum that is too small can only grow by moving the left side right.",
           "Start one pointer at each end."],
    approaches=[approach(
        name="Two Pointers", pattern="two-pointers", time="O(n)", space="O(1)",
        idea="""
        Put one pointer, L, on the smallest number and another, R, on the largest.

        If their sum is too small, the only way to grow it is to move L to the right. If it is too big, move R to the left. Each step throws away one number that can never be part of the answer.
        """,
        why="Each step moves one pointer inward, so we take at most n steps and only store two indexes.",
        viz=viz(arr="nums", ptr={"L": "l", "R": "r"}, vars=["s", "target"]),
        py='''
        def pair_sum(nums, target):
            l, r = 0, len(nums) - 1  #> L starts at index {l} and R starts at index {r}.
            while l < r:
                s = nums[l] + nums[r]  #> {nums[l]} plus {nums[r]} is {s}.
                if s == target:
                    return [l, r]  #> That equals the target {target}! Return [{l}, {r}].
                if s < target:
                    l += 1  #> {s} is too small, so L moves right to index {l}.
                else:
                    r -= 1  #> {s} is too big, so R moves left to index {r}.
            return []
        ''',
        java='''
        class Solution {
            public int[] pairSum(int[] nums, int target) {
                int l = 0, r = nums.length - 1; //>
                while (l < r) {
                    int s = nums[l] + nums[r]; //>
                    if (s == target) return new int[]{l, r}; //>
                    if (s < target) l++; //>
                    else r--; //>
                }
                return new int[0];
            }
        }
        ''',
    )],
)

problem(
    id="clean-palindrome",
    title="Palindrome After Cleanup",
    difficulty="Easy",
    topics=["String", "Two Pointers"],
    statement="""
    A phrase counts as a palindrome if, after you ignore everything that is not a letter or a digit and treat
    uppercase and lowercase as equal, it reads the same forwards and backwards.

    Given a string `s`, return `true` if it is a palindrome under these rules.
    """,
    examples=[(["Taco cat!"], True, "Cleaned up it is \"tacocat\"."), (["Was it a car?"], False, None)],
    tests=[([""], True), ([" "], True), (["0P"], False), (["ab_a"], True), (["No lemon, no melon"], True)],
    constraints=["0 ≤ s.length ≤ 2·10^5", "s contains printable ASCII characters"],
    hints=["Compare characters from both ends.", "Skip anything that is not a letter or digit before comparing."],
    approaches=[approach(
        name="Two Pointers", pattern="two-pointers", time="O(n)", space="O(1)",
        idea="""
        Put L at the start and R at the end. Skip over punctuation and spaces on either side.

        When both point at letters or digits, compare them ignoring case. Any mismatch means it is not a palindrome. If the pointers meet, it is.
        """,
        why="Every character is visited at most once by one of the two pointers, and we never build a cleaned copy.",
        viz=viz(arr="s", ptr={"L": "l", "R": "r"}),
        demo=["Taco cat!"],
        py='''
        def is_clean_palindrome(s):
            l, r = 0, len(s) - 1  #> L starts at the first character and R at the last.
            while l < r:
                if not s[l].isalnum():
                    l += 1  #> {q(s[l - 1])} is not a letter or digit, so L skips it.
                elif not s[r].isalnum():
                    r -= 1  #> {q(s[r + 1])} is not a letter or digit, so R skips it.
                elif s[l].lower() != s[r].lower():
                    return False  #> {q(s[l])} and {q(s[r])} differ, so it is not a palindrome.
                else:
                    l, r = l + 1, r - 1  #> {q(s[l - 1])} matches {q(s[r + 1])}. Both pointers step inward.
            return True  #> The pointers met without a mismatch. It's a palindrome!
        ''',
        java='''
        class Solution {
            public boolean isCleanPalindrome(String s) {
                int l = 0, r = s.length() - 1; //>
                while (l < r) {
                    if (!Character.isLetterOrDigit(s.charAt(l))) l++; //>
                    else if (!Character.isLetterOrDigit(s.charAt(r))) r--; //>
                    else if (Character.toLowerCase(s.charAt(l)) != Character.toLowerCase(s.charAt(r))) return false; //>
                    else { l++; r--; } //>
                }
                return true; //>
            }
        }
        ''',
    )],
)

problem(
    id="reverse-chars",
    title="Reverse Characters In Place",
    difficulty="Easy",
    topics=["String", "Two Pointers"],
    statement="""
    You are given an array of characters `chars`. Reverse it **in place**: modify the array itself and use only
    O(1) extra memory.
    """,
    examples=[([["h", "e", "l", "l", "o"]], ["o", "l", "l", "e", "h"], None), ([["a", "b"]], ["b", "a"], None)],
    tests=[([["x"]], ["x"]), ([["r", "a", "c", "e"]], ["e", "c", "a", "r"])],
    out="arg0",
    constraints=["1 ≤ chars.length ≤ 10^5"],
    hints=["Swap the first and last characters, then move inward."],
    approaches=[approach(
        name="Two Pointers", pattern="two-pointers", time="O(n)", space="O(1)",
        idea="""
        L starts at the front and R at the back. Swap the two characters, then step both pointers toward the middle.

        When they meet, every character has been swapped into its mirrored position.
        """,
        why="We do n/2 swaps and only keep two indexes.",
        viz=viz(arr="chars", ptr={"L": "l", "R": "r"}),
        py='''
        def reverse_chars(chars):
            l, r = 0, len(chars) - 1  #> L points at the first character, R at the last.
            while l < r:
                chars[l], chars[r] = chars[r], chars[l]  #> Swap {q(chars[r])} and {q(chars[l])}.
                l, r = l + 1, r - 1  #> Both pointers move one step inward.
        ''',
        java='''
        class Solution {
            public void reverseChars(char[] chars) {
                int l = 0, r = chars.length - 1; //>
                while (l < r) {
                    char t = chars[l]; chars[l] = chars[r]; chars[r] = t; //>
                    l++; r--; //>
                }
            }
        }
        ''',
    )],
)

problem(
    id="move-zeros",
    title="Push Zeros to the End",
    difficulty="Easy",
    topics=["Array", "Two Pointers"],
    statement="""
    Rearrange the integer array `nums` **in place** so that every `0` ends up at the end, while all the
    non-zero numbers keep their original relative order.
    """,
    examples=[([[0, 1, 0, 3, 12]], [1, 3, 12, 0, 0], None), ([[0]], [0], None)],
    tests=[([[1, 2, 3]], [1, 2, 3]), ([[0, 0, 1]], [1, 0, 0]), ([[4, 0, 5, 0, 0, 6]], [4, 5, 6, 0, 0, 0])],
    out="arg0",
    constraints=["1 ≤ nums.length ≤ 10^4"],
    hints=["Keep a write pointer for where the next non-zero number belongs."],
    approaches=[approach(
        name="Two Pointers (read & write)", pattern="two-pointers", time="O(n)", space="O(1)",
        idea="""
        Use a read pointer R that scans every number, and a write pointer W that marks where the next non-zero number should go.

        Each time R finds a non-zero number, swap it into position W and move W forward. Zeros naturally drift to the end.
        """,
        why="R passes over the array once; each swap is constant work.",
        viz=viz(arr="nums", ptr={"W": "w", "R": "r"}),
        py='''
        def move_zeros(nums):
            w = 0  #> W marks where the next non-zero number goes.
            for r in range(len(nums)):  #> R reads index {r}: the number {nums[r]}.
                if nums[r] != 0:
                    nums[w], nums[r] = nums[r], nums[w]  #> It's not zero, so swap it into position {w}.
                    w += 1  #> W moves to {w}.
        ''',
        java='''
        class Solution {
            public void moveZeros(int[] nums) {
                int w = 0; //>
                for (int r = 0; r < nums.length; r++) { //>
                    if (nums[r] != 0) {
                        int t = nums[w]; nums[w] = nums[r]; nums[r] = t; //>
                        w++; //>
                    }
                }
            }
        }
        ''',
    )],
)

problem(
    id="dedupe-sorted",
    title="Remove Repeats From a Sorted List",
    difficulty="Easy",
    topics=["Array", "Two Pointers"],
    statement="""
    `nums` is sorted in non-decreasing order. Remove the repeated values **in place** so each distinct value appears
    once, keeping the order. Return `k`, the number of distinct values; the first `k` slots of `nums` must hold them.
    """,
    examples=[([[1, 1, 2]], [1, 2], "k = 2 and the array starts with 1, 2."), ([[0, 0, 1, 1, 1, 2, 3, 3]], [0, 1, 2, 3], None)],
    tests=[([[5]], [5]), ([[1, 2, 3]], [1, 2, 3]), ([[2, 2, 2, 2]], [2])],
    out="arg0-prefix",
    constraints=["1 ≤ nums.length ≤ 3·10^4", "nums is sorted"],
    hints=["Duplicates are next to each other in a sorted array.", "Write each new value at a write pointer."],
    approaches=[approach(
        name="Two Pointers (read & write)", pattern="two-pointers", time="O(n)", space="O(1)",
        idea="""
        The first value is always kept, so the write pointer W starts at 1. The read pointer R scans the rest.

        Whenever R sees a value different from the last kept one, copy it to W and move W forward. At the end, W is the count of distinct values.
        """,
        viz=viz(arr="nums", ptr={"W": "w", "R": "r"}),
        py='''
        def remove_repeats(nums):
            w = 1  #> The first number is always kept, so W starts at index 1.
            for r in range(1, len(nums)):  #> R looks at index {r}, value {nums[r]}.
                if nums[r] != nums[w - 1]:
                    nums[w] = nums[r]  #> {nums[r]} is new, so write it at index {w}.
                    w += 1
            return w  #> The first {w} slots hold the distinct values.
        ''',
        java='''
        class Solution {
            public int removeRepeats(int[] nums) {
                int w = 1; //>
                for (int r = 1; r < nums.length; r++) { //>
                    if (nums[r] != nums[w - 1]) {
                        nums[w] = nums[r]; //>
                        w++;
                    }
                }
                return w; //>
            }
        }
        ''',
    )],
)

problem(
    id="keep-at-most-two",
    title="Allow Each Value At Most Twice",
    difficulty="Medium",
    topics=["Array", "Two Pointers"],
    statement="""
    `nums` is sorted. Remove extra copies **in place** so every value appears at most twice, keeping the order.
    Return `k`, the new length; the first `k` slots of `nums` must hold the result.
    """,
    examples=[([[1, 1, 1, 2, 2, 3]], [1, 1, 2, 2, 3], None), ([[0, 0, 1, 1, 1, 1, 2, 3, 3]], [0, 0, 1, 1, 2, 3, 3], None)],
    tests=[([[1]], [1]), ([[4, 4, 4, 4]], [4, 4]), ([[1, 2, 3]], [1, 2, 3])],
    out="arg0-prefix",
    constraints=["1 ≤ nums.length ≤ 3·10^4"],
    hints=["Compare the new value with the one written two slots back."],
    approaches=[approach(
        name="Two Pointers (read & write)", pattern="two-pointers", time="O(n)", space="O(1)",
        idea="""
        Keep a write pointer W. A value may be written if fewer than two values are written so far, or if it differs from the value two slots behind W.

        That single comparison guarantees no value appears three times in a row.
        """,
        viz=viz(arr="nums", ptr={"W": "w"}, vars=["x"]),
        py='''
        def keep_two(nums):
            w = 0
            for x in nums:
                if w < 2 or x != nums[w - 2]:
                    nums[w] = x  #> {x} is allowed, so write it at index {w}.
                    w += 1
            return w  #> The answer is the first {w} slots.
        ''',
        java='''
        class Solution {
            public int keepTwo(int[] nums) {
                int w = 0;
                for (int x : nums) {
                    if (w < 2 || x != nums[w - 2]) {
                        nums[w] = x; //>
                        w++;
                    }
                }
                return w; //>
            }
        }
        ''',
    )],
)

problem(
    id="merge-into-first",
    title="Merge Two Sorted Lists Into the First",
    difficulty="Easy",
    topics=["Array", "Two Pointers", "Sorting"],
    statement="""
    `a` has length `m + n`: its first `m` values are sorted and the last `n` slots are zeros (free space).
    `b` holds `n` sorted values. Merge `b` into `a` **in place** so that `a` becomes fully sorted.
    """,
    examples=[([[1, 4, 7, 0, 0, 0], 3, [2, 5, 6], 3], [1, 2, 4, 5, 6, 7], None), ([[0], 0, [3], 1], [3], None)],
    tests=[([[1], 1, [], 0], [1]), ([[4, 5, 0, 0], 2, [1, 2], 2], [1, 2, 4, 5]), ([[2, 0], 1, [2], 1], [2, 2])],
    out="arg0",
    constraints=["0 ≤ m, n ≤ 200", "a.length = m + n"],
    hints=["Filling from the front would overwrite values you still need.", "Fill from the back with the larger of the two tails."],
    approaches=[approach(
        name="Two Pointers from the back", pattern="two-pointers", time="O(m + n)", space="O(1)",
        idea="""
        The free space is at the end of `a`, so fill the result from the back. I points at the last real value of `a`, J at the last value of `b`, and K at the slot to fill.

        Put the larger of the two tails into slot K and move that pointer left. When `b` runs out, everything left in `a` is already in place.
        """,
        viz=viz(arrays=[("a", {"I": "i", "K": "k"}), ("b", {"J": "j"})]),
        py='''
        def merge_into(a, m, b, n):
            i, j, k = m - 1, n - 1, m + n - 1  #> Start at the back: I at {i}, J at {j}, and K writes at {k}.
            while j >= 0:
                if i >= 0 and a[i] > b[j]:
                    a[k] = a[i]  #> {a[i]} from the first list is bigger, so it fills slot {k}.
                    i -= 1
                else:
                    a[k] = b[j]  #> {b[j]} from the second list fills slot {k}.
                    j -= 1
                k -= 1
        ''',
        java='''
        class Solution {
            public void mergeInto(int[] a, int m, int[] b, int n) {
                int i = m - 1, j = n - 1, k = m + n - 1; //>
                while (j >= 0) {
                    if (i >= 0 && a[i] > b[j]) a[k--] = a[i--]; //>
                    else a[k--] = b[j--]; //>
                }
            }
        }
        ''',
    )],
)

problem(
    id="sorted-squares",
    title="Squares in Sorted Order",
    difficulty="Easy",
    topics=["Array", "Two Pointers", "Sorting"],
    statement="""
    `nums` is sorted ascending and may contain negative numbers. Return a new array of the squares of each number,
    also sorted ascending.
    """,
    examples=[([[-4, -1, 0, 3, 10]], [0, 1, 9, 16, 100], None), ([[-7, -3, 2, 3, 11]], [4, 9, 9, 49, 121], None)],
    tests=[([[1]], [1]), ([[-2, -1]], [1, 4]), ([[0, 0, 5]], [0, 0, 25])],
    constraints=["1 ≤ nums.length ≤ 10^4"],
    hints=["The biggest square comes from one of the two ends.", "Fill the answer from the back."],
    approaches=[approach(
        name="Two Pointers", pattern="two-pointers", time="O(n)", space="O(1) extra",
        idea="""
        The largest square is always at one of the two ends, because large negatives sit on the left and large positives on the right.

        Compare the two ends, put the bigger square at the back of the result, and move that pointer inward. Repeat until the result is full.
        """,
        why="One pass with two pointers; apart from the output we use constant space.",
        viz=viz(arrays=[("nums", {"L": "l", "R": "r"}), ("res", {"K": "k"})]),
        py='''
        def sorted_squares(nums):
            res = [0] * len(nums)
            l, r = 0, len(nums) - 1
            for k in range(len(nums) - 1, -1, -1):
                if abs(nums[l]) > abs(nums[r]):
                    res[k] = nums[l] * nums[l]  #> {nums[l]} is bigger in size, so {res[k]} goes into slot {k}.
                    l += 1
                else:
                    res[k] = nums[r] * nums[r]  #> {nums[r]} is at least as big, so {res[k]} goes into slot {k}.
                    r -= 1
            return res
        ''',
        java='''
        class Solution {
            public int[] sortedSquares(int[] nums) {
                int n = nums.length, l = 0, r = n - 1;
                int[] res = new int[n];
                for (int k = n - 1; k >= 0; k--) {
                    if (Math.abs(nums[l]) > Math.abs(nums[r])) { res[k] = nums[l] * nums[l]; l++; } //>
                    else { res[k] = nums[r] * nums[r]; r--; } //>
                }
                return res;
            }
        }
        ''',
    )],
)

problem(
    id="most-water",
    title="Biggest Water Tank",
    difficulty="Medium",
    topics=["Array", "Two Pointers", "Greedy"],
    statement="""
    `heights[i]` is the height of a vertical wall at position `i`. Choose two walls; together with the ground they
    form a tank whose water level is limited by the shorter wall. Return the largest amount of water any pair can hold
    (width × shorter height).
    """,
    examples=[([[1, 8, 6, 2, 5, 4, 8, 3, 7]], 49, "Walls at 1 and 8: width 7, height 7."), ([[1, 1]], 1, None)],
    tests=[([[4, 3, 2, 1, 4]], 16), ([[1, 2, 1]], 2), ([[2, 3, 10, 5, 7, 8, 9]], 36)],
    constraints=["2 ≤ n ≤ 10^5", "0 ≤ heights[i] ≤ 10^4"],
    hints=["Start with the widest tank.", "Moving the taller wall can never help, so move the shorter one."],
    approaches=[approach(
        name="Two Pointers", pattern="two-pointers", time="O(n)", space="O(1)",
        idea="""
        Start with the widest tank: L at the first wall and R at the last. The water is limited by the shorter wall.

        Moving the taller wall inward can only shrink the width without raising the limit, so always move the shorter wall. Track the best area as you go.
        """,
        why="Each step discards one wall forever, so there are at most n steps.",
        viz=viz(arr="heights", ptr={"L": "l", "R": "r"}, vars=["area", "best"]),
        demo=[[1, 8, 6, 2, 5, 4, 8, 3, 7]],
        py='''
        def max_water(heights):
            l, r, best = 0, len(heights) - 1, 0
            while l < r:
                area = min(heights[l], heights[r]) * (r - l)  #> Walls {heights[l]} and {heights[r]}, width {r - l}: area {area}.
                best = max(best, area)
                if heights[l] < heights[r]:
                    l += 1  #> The left wall is shorter, so L moves right.
                else:
                    r -= 1  #> The right wall is not taller, so R moves left.
            return best
        ''',
        java='''
        class Solution {
            public int maxWater(int[] heights) {
                int l = 0, r = heights.length - 1, best = 0;
                while (l < r) {
                    int area = Math.min(heights[l], heights[r]) * (r - l); //>
                    best = Math.max(best, area);
                    if (heights[l] < heights[r]) l++; //>
                    else r--; //>
                }
                return best;
            }
        }
        ''',
    )],
)

problem(
    id="three-sum-zero",
    title="Triples That Sum to Zero",
    difficulty="Medium",
    topics=["Array", "Two Pointers", "Sorting"],
    statement="""
    Return every distinct triple of values `[a, b, c]` from `nums` (using three different positions) with
    `a + b + c = 0`. No triple may appear twice. Any order is accepted.
    """,
    examples=[([[-1, 0, 1, 2, -1, -4]], [[-1, -1, 2], [-1, 0, 1]], None), ([[0, 1, 1]], [], None)],
    tests=[([[0, 0, 0]], [[0, 0, 0]]), ([[-2, 0, 1, 1, 2]], [[-2, 0, 2], [-2, 1, 1]]), ([[3, -2, 1, 0]], [])],
    check="deep-unordered",
    constraints=["3 ≤ nums.length ≤ 3000"],
    hints=["Sort the numbers first.", "Fix the first value, then solve a two-pointer pair sum on the rest."],
    approaches=[approach(
        name="Sort + Two Pointers", pattern="two-pointers", time="O(n²)", space="O(1) extra",
        idea="""
        Sort the array. Fix the first number of the triple, then look for two numbers to its right that add up to minus that number, using L and R from both ends.

        Skip values equal to the previous one so the same triple is never reported twice.
        """,
        why="Sorting is O(n log n); for each of the n fixed values the two-pointer scan is O(n).",
        viz=viz(arr="nums", ptr={"i": "i", "L": "l", "R": "r"}, vars=["s"], out="res"),
        demo=[[-1, 0, 1, 2, -1, -4]],
        py='''
        def three_sum(nums):
            nums.sort()  #> First sort the numbers.
            res = []
            for i in range(len(nums) - 2):
                if i > 0 and nums[i] == nums[i - 1]:
                    continue
                l, r = i + 1, len(nums) - 1  #> Fix {nums[i]} and search the rest with L and R.
                while l < r:
                    s = nums[i] + nums[l] + nums[r]
                    if s < 0:
                        l += 1  #> The sum {s} is too small, so L moves right.
                    elif s > 0:
                        r -= 1  #> The sum {s} is too big, so R moves left.
                    else:
                        res.append([nums[i], nums[l], nums[r]])  #> Found {res[-1]}!
                        l += 1
                        while l < r and nums[l] == nums[l - 1]:
                            l += 1
            return res
        ''',
        java='''
        class Solution {
            public List<List<Integer>> threeSum(int[] nums) {
                Arrays.sort(nums); //>
                List<List<Integer>> res = new ArrayList<>();
                for (int i = 0; i < nums.length - 2; i++) {
                    if (i > 0 && nums[i] == nums[i - 1]) continue;
                    int l = i + 1, r = nums.length - 1; //>
                    while (l < r) {
                        int s = nums[i] + nums[l] + nums[r];
                        if (s < 0) l++; //>
                        else if (s > 0) r--; //>
                        else {
                            res.add(List.of(nums[i], nums[l], nums[r])); //>
                            l++;
                            while (l < r && nums[l] == nums[l - 1]) l++;
                        }
                    }
                }
                return res;
            }
        }
        ''',
    )],
)

problem(
    id="three-sum-closest",
    title="Triple Sum Closest to Target",
    difficulty="Medium",
    topics=["Array", "Two Pointers", "Sorting"],
    statement="""
    Pick three values at different positions of `nums` whose sum is as close as possible to `target`, and return
    that sum. Exactly one closest sum exists.
    """,
    examples=[([[-1, 2, 1, -4], 1], 2, "-1 + 2 + 1 = 2"), ([[0, 0, 0], 1], 0, None)],
    tests=[([[1, 1, 1, 0], 100], 3), ([[4, 0, 5, -5, 3, 3, 0, -4, -5], -2], -2)],
    constraints=["3 ≤ nums.length ≤ 500"],
    hints=["Same skeleton as the zero-sum triples.", "Move L or R depending on whether the sum is below or above target."],
    approaches=[approach(
        name="Sort + Two Pointers", pattern="two-pointers", time="O(n²)", space="O(1) extra",
        idea="""
        Sort, fix the first value, and use L and R on the remaining range. If the current sum is below the target, move L right to grow it; if above, move R left.

        Remember whichever sum has been closest so far, and stop early on an exact hit.
        """,
        viz=viz(arr="nums", ptr={"i": "i", "L": "l", "R": "r"}, vars=["s", "best", "target"]),
        demo=[[-4, -1, 1, 2], 1],
        py='''
        def three_sum_closest(nums, target):
            nums.sort()
            best = nums[0] + nums[1] + nums[2]
            for i in range(len(nums) - 2):
                l, r = i + 1, len(nums) - 1
                while l < r:
                    s = nums[i] + nums[l] + nums[r]  #> {nums[i]} plus {nums[l]} plus {nums[r]} is {s}.
                    if abs(s - target) < abs(best - target):
                        best = s  #> {s} is the closest to {target} so far.
                    if s < target:
                        l += 1
                    elif s > target:
                        r -= 1
                    else:
                        return s  #> Exactly {target}. It can't get closer!
            return best
        ''',
        java='''
        class Solution {
            public int threeSumClosest(int[] nums, int target) {
                Arrays.sort(nums);
                int best = nums[0] + nums[1] + nums[2];
                for (int i = 0; i < nums.length - 2; i++) {
                    int l = i + 1, r = nums.length - 1;
                    while (l < r) {
                        int s = nums[i] + nums[l] + nums[r]; //>
                        if (Math.abs(s - target) < Math.abs(best - target)) best = s; //>
                        if (s < target) l++;
                        else if (s > target) r--;
                        else return s; //>
                    }
                }
                return best;
            }
        }
        ''',
    )],
)

problem(
    id="sort-three-colors",
    title="Sort Three Colors",
    difficulty="Medium",
    topics=["Array", "Two Pointers", "Sorting"],
    statement="""
    `nums` contains only `0`, `1` and `2` (three colors). Sort it **in place** in one pass so all 0s come first,
    then the 1s, then the 2s, without using a library sort.
    """,
    examples=[([[2, 0, 2, 1, 1, 0]], [0, 0, 1, 1, 2, 2], None), ([[2, 0, 1]], [0, 1, 2], None)],
    tests=[([[0]], [0]), ([[1, 2, 0, 0]], [0, 0, 1, 2]), ([[2, 2, 1]], [1, 2, 2])],
    out="arg0",
    constraints=["1 ≤ nums.length ≤ 300"],
    hints=["Keep three regions: 0s on the left, 2s on the right, unknown in the middle."],
    approaches=[approach(
        name="Three Pointers", pattern="two-pointers", time="O(n)", space="O(1)",
        idea="""
        LO marks where the next 0 goes, HI where the next 2 goes, and MID scans the unknown middle.

        A 0 is swapped down to LO, a 2 is swapped up to HI, and a 1 is simply skipped. Every element is placed in a single pass.
        """,
        viz=viz(arr="nums", ptr={"lo": "lo", "mid": "mid", "hi": "hi"}),
        py='''
        def sort_colors(nums):
            lo, mid, hi = 0, 0, len(nums) - 1  #> LO and MID start at 0, HI starts at the end.
            while mid <= hi:
                if nums[mid] == 0:
                    nums[lo], nums[mid] = nums[mid], nums[lo]  #> A 0 belongs on the left, so swap it to LO at index {lo}.
                    lo, mid = lo + 1, mid + 1
                elif nums[mid] == 1:
                    mid += 1  #> A 1 already sits in the middle zone, so MID moves on.
                else:
                    nums[mid], nums[hi] = nums[hi], nums[mid]  #> A 2 belongs on the right, so swap it to HI at index {hi}.
                    hi -= 1
        ''',
        java='''
        class Solution {
            public void sortColors(int[] nums) {
                int lo = 0, mid = 0, hi = nums.length - 1; //>
                while (mid <= hi) {
                    if (nums[mid] == 0) { int t = nums[lo]; nums[lo++] = nums[mid]; nums[mid++] = t; } //>
                    else if (nums[mid] == 1) mid++; //>
                    else { int t = nums[hi]; nums[hi--] = nums[mid]; nums[mid] = t; } //>
                }
            }
        }
        ''',
    )],
)

problem(
    id="trapped-rain",
    title="Trapped Rainwater",
    difficulty="Hard",
    topics=["Array", "Two Pointers", "Dynamic Programming"],
    statement="""
    `height[i]` is the height of a bar of width 1. After rain, water collects between the bars. Return how many
    units of water are trapped.
    """,
    examples=[([[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]], 6, None), ([[4, 2, 0, 3, 2, 5]], 9, None)],
    tests=[([[1]], 0), ([[2, 0, 2]], 2), ([[5, 4, 1, 2]], 1)],
    constraints=["1 ≤ n ≤ 2·10^4", "0 ≤ height[i] ≤ 10^5"],
    hints=["Water above a bar = min(tallest on the left, tallest on the right) − its height.",
           "The lower side decides, so process the side with the lower wall."],
    approaches=[approach(
        name="Two Pointers", pattern="two-pointers", time="O(n)", space="O(1)",
        idea="""
        Water above a bar depends on the shorter of the tallest bar to its left and the tallest to its right.

        Keep L and R at the ends with the best height seen on each side. Whichever side is lower is the bottleneck, so its water is known right now: add it and move that pointer inward.
        """,
        why="Each bar is processed once by one pointer, with four integer variables.",
        viz=viz(arr="height", ptr={"L": "l", "R": "r"}, vars=["left_max", "right_max", "water"]),
        demo=[[4, 2, 0, 3, 2, 5]],
        py='''
        def trap(height):
            l, r = 0, len(height) - 1
            left_max = right_max = water = 0
            while l < r:
                if height[l] < height[r]:
                    left_max = max(left_max, height[l])
                    water += left_max - height[l]  #> The left side is lower. Index {l} holds {left_max - height[l]} water. Total {water}.
                    l += 1
                else:
                    right_max = max(right_max, height[r])
                    water += right_max - height[r]  #> The right side is lower. Index {r} holds {right_max - height[r]} water. Total {water}.
                    r -= 1
            return water
        ''',
        java='''
        class Solution {
            public int trap(int[] height) {
                int l = 0, r = height.length - 1, leftMax = 0, rightMax = 0, water = 0;
                while (l < r) {
                    if (height[l] < height[r]) {
                        leftMax = Math.max(leftMax, height[l]);
                        water += leftMax - height[l++]; //>
                    } else {
                        rightMax = Math.max(rightMax, height[r]);
                        water += rightMax - height[r--]; //>
                    }
                }
                return water;
            }
        }
        ''',
    )],
)

problem(
    id="is-subsequence",
    title="Hidden Inside Another String",
    difficulty="Easy",
    topics=["String", "Two Pointers"],
    statement="""
    Return `true` if you can obtain `s` from `t` by deleting some (or no) characters of `t` without reordering
    the rest — in other words, if `s` is a subsequence of `t`.
    """,
    examples=[(["ace", "abcde"], True, None), (["aec", "abcde"], False, None)],
    tests=[(["", "abc"], True), (["abc", ""], False), (["bb", "abab"], True)],
    constraints=["0 ≤ s.length ≤ 100", "0 ≤ t.length ≤ 10^4"],
    hints=["Walk through t once, matching characters of s in order."],
    approaches=[approach(
        name="Two Pointers", pattern="two-pointers", time="O(n)", space="O(1)",
        idea="""
        Pointer I tracks the next character of `s` we still need; pointer J scans `t`.

        Whenever `t[j]` equals the needed character, I moves forward. If I reaches the end of `s`, every character was found in order.
        """,
        viz=viz(arrays=[("s", {"i": "i"}), ("t", {"j": "j"})]),
        py='''
        def is_subsequence(s, t):
            i = 0
            for j in range(len(t)):  #> J reads {q(t[j])}.
                if i < len(s) and s[i] == t[j]:
                    i += 1  #> It matches the next needed letter, so I moves to {i}.
            return i == len(s)  #> I matched {i} of {len(s)} letters.
        ''',
        java='''
        class Solution {
            public boolean isSubsequence(String s, String t) {
                int i = 0;
                for (int j = 0; j < t.length(); j++) { //>
                    if (i < s.length() && s.charAt(i) == t.charAt(j)) i++; //>
                }
                return i == s.length(); //>
            }
        }
        ''',
    )],
)

problem(
    id="rotate-right",
    title="Rotate an Array to the Right",
    difficulty="Medium",
    topics=["Array", "Two Pointers", "Math"],
    statement="""
    Rotate `nums` to the right by `k` steps **in place**: each value moves `k` positions right, wrapping around
    to the front. Use O(1) extra memory.
    """,
    examples=[([[1, 2, 3, 4, 5, 6, 7], 3], [5, 6, 7, 1, 2, 3, 4], None), ([[-1, -100, 3, 99], 2], [3, 99, -1, -100], None)],
    tests=[([[1], 5], [1]), ([[1, 2], 3], [2, 1]), ([[1, 2, 3], 0], [1, 2, 3])],
    out="arg0",
    constraints=["1 ≤ nums.length ≤ 10^5", "0 ≤ k ≤ 10^5"],
    hints=["Rotating by k is the same as rotating by k mod n.", "Three reversals do the trick."],
    approaches=[approach(
        name="Reverse Three Times", pattern="two-pointers", time="O(n)", space="O(1)",
        idea="""
        Reverse the whole array, then reverse the first k values, then reverse the rest. Each reversal is a classic two-pointer swap from both ends.

        The first reversal moves the last k values to the front (backwards); the next two put each part back in the right order.
        """,
        viz=viz(arr="nums", ptr={"L": "l", "R": "r"}),
        demo=[[1, 2, 3, 4, 5], 2],
        py='''
        def rotate(nums, k):
            k %= len(nums)

            def reverse(l, r):
                while l < r:
                    nums[l], nums[r] = nums[r], nums[l]  #> Swap positions {l} and {r}.
                    l, r = l + 1, r - 1

            reverse(0, len(nums) - 1)  #> Step 1: reverse the whole array.
            reverse(0, k - 1)  #> Step 2: reverse the first {k} numbers.
            reverse(k, len(nums) - 1)  #> Step 3: reverse the rest.
        ''',
        java='''
        class Solution {
            public void rotate(int[] nums, int k) {
                k %= nums.length;
                reverse(nums, 0, nums.length - 1); //>2
                reverse(nums, 0, k - 1); //>3
                reverse(nums, k, nums.length - 1); //>4
            }

            private void reverse(int[] a, int l, int r) {
                while (l < r) { int t = a[l]; a[l++] = a[r]; a[r--] = t; } //>1
            }
        }
        ''',
    )],
)

problem(
    id="rescue-boats",
    title="Fewest Rescue Boats",
    difficulty="Medium",
    topics=["Array", "Two Pointers", "Greedy", "Sorting"],
    statement="""
    `people[i]` is the weight of person `i`. Each boat carries at most two people and at most `limit` total weight.
    Return the minimum number of boats needed to carry everyone. Nobody is heavier than `limit`.
    """,
    examples=[([[3, 2, 2, 1], 3], 3, "(1, 2), (2) and (3)."), ([[1, 2], 3], 1, None)],
    tests=[([[3, 5, 3, 4], 5], 4), ([[5], 5], 1), ([[2, 2, 2, 2], 4], 2)],
    constraints=["1 ≤ people.length ≤ 5·10^4", "1 ≤ people[i] ≤ limit ≤ 3·10^4"],
    hints=["The heaviest person must leave on some boat; who can share it?", "Pair the heaviest with the lightest if possible."],
    approaches=[approach(
        name="Sort + Two Pointers", pattern="two-pointers", time="O(n log n)", space="O(1) extra",
        idea="""
        Sort the weights. The heaviest person, at R, always needs a boat. If the lightest person, at L, fits alongside, they ride together.

        Either way the heaviest leaves, so each step uses one boat and moves R left (and L right when they share).
        """,
        viz=viz(arr="people", ptr={"L": "l", "R": "r"}, vars=["boats", "limit"]),
        py='''
        def min_boats(people, limit):
            people.sort()  #> Sort the weights.
            l, r, boats = 0, len(people) - 1, 0
            while l <= r:
                if people[l] + people[r] <= limit:
                    l += 1  #> The lightest, {people[l - 1]}, can share with {people[r]}.
                boats += 1  #> {people[r]} leaves on boat number {boats}.
                r -= 1
            return boats
        ''',
        java='''
        class Solution {
            public int minBoats(int[] people, int limit) {
                Arrays.sort(people); //>
                int l = 0, r = people.length - 1, boats = 0;
                while (l <= r) {
                    if (people[l] + people[r] <= limit) l++; //>
                    boats++; //>
                    r--;
                }
                return boats;
            }
        }
        ''',
    )],
)

problem(
    id="almost-palindrome",
    title="Palindrome With One Deletion",
    difficulty="Easy",
    topics=["String", "Two Pointers", "Greedy"],
    statement="""
    Return `true` if the lowercase string `s` can become a palindrome after deleting **at most one** character.
    """,
    examples=[(["abca"], True, "Delete 'c' (or 'b')."), (["abc"], False, None)],
    tests=[(["aba"], True), (["deeee"], True), (["abcdba"], True), (["abccdba"], True), (["abcdef"], False)],
    constraints=["1 ≤ s.length ≤ 10^5"],
    hints=["Compare from both ends until the first mismatch.", "At a mismatch, try skipping the left or the right character."],
    approaches=[approach(
        name="Two Pointers", pattern="two-pointers", time="O(n)", space="O(1)",
        idea="""
        Walk inward from both ends while the characters match. At the first mismatch we must delete one of the two characters.

        So check whether the rest is a palindrome after skipping the left one, or after skipping the right one.
        """,
        viz=viz(arr="s", ptr={"L": "l", "R": "r"}),
        demo=["racecxar"],
        py='''
        def almost_palindrome(s):
            def is_pal(l, r):
                while l < r:
                    if s[l] != s[r]:
                        return False
                    l, r = l + 1, r - 1
                return True

            l, r = 0, len(s) - 1
            while l < r:
                if s[l] != s[r]:
                    return is_pal(l + 1, r) or is_pal(l, r - 1)  #> Mismatch: {q(s[l])} versus {q(s[r])}. Try deleting one of them.
                l, r = l + 1, r - 1  #> {q(s[l - 1])} matches {q(s[r + 1])}, so both pointers move inward.
            return True
        ''',
        java='''
        class Solution {
            public boolean almostPalindrome(String s) {
                int l = 0, r = s.length() - 1;
                while (l < r) {
                    if (s.charAt(l) != s.charAt(r)) return isPal(s, l + 1, r) || isPal(s, l, r - 1); //>
                    l++; r--; //>
                }
                return true;
            }

            private boolean isPal(String s, int l, int r) {
                while (l < r) if (s.charAt(l++) != s.charAt(r--)) return false;
                return true;
            }
        }
        ''',
    )],
)

problem(
    id="reverse-vowels",
    title="Reverse Only the Vowels",
    difficulty="Easy",
    topics=["String", "Two Pointers"],
    statement="""
    Reverse the order of the vowels (`a, e, i, o, u` in either case) in the string `s`, leaving every other
    character where it is.
    """,
    examples=[(["hello"], "holle", None), (["Programming"], "Prigrammong", None)],
    tests=[(["xyz"], "xyz"), (["aA"], "Aa"), ([""], "")],
    constraints=["0 ≤ s.length ≤ 3·10^5"],
    hints=["Move pointers from both ends until each one sits on a vowel, then swap."],
    approaches=[approach(
        name="Two Pointers", pattern="two-pointers", time="O(n)", space="O(n)",
        idea="""
        L walks right and R walks left, each skipping consonants. When both sit on vowels, swap them and continue.

        Strings are immutable in Java and Python, so we work on a character array copy.
        """,
        viz=viz(arr="chars", ptr={"L": "l", "R": "r"}),
        demo=["education"],
        py='''
        def reverse_vowels(s):
            chars, vowels = list(s), set("aeiouAEIOU")
            l, r = 0, len(chars) - 1
            while l < r:
                if chars[l] not in vowels:
                    l += 1  #> {q(chars[l - 1])} is not a vowel, so L moves on.
                elif chars[r] not in vowels:
                    r -= 1  #> {q(chars[r + 1])} is not a vowel, so R moves on.
                else:
                    chars[l], chars[r] = chars[r], chars[l]  #> Both are vowels, so swap {q(chars[r])} and {q(chars[l])}.
                    l, r = l + 1, r - 1
            return "".join(chars)
        ''',
        java='''
        class Solution {
            public String reverseVowels(String s) {
                char[] c = s.toCharArray();
                String vowels = "aeiouAEIOU";
                int l = 0, r = c.length - 1;
                while (l < r) {
                    if (vowels.indexOf(c[l]) < 0) l++; //>
                    else if (vowels.indexOf(c[r]) < 0) r--; //>
                    else { char t = c[l]; c[l++] = c[r]; c[r--] = t; } //>
                }
                return new String(c);
            }
        }
        ''',
    )],
)

problem(
    id="backspace-equal",
    title="Equal After Backspaces",
    difficulty="Easy",
    topics=["String", "Two Pointers", "Stack"],
    statement="""
    In strings `s` and `t`, the character `#` means "backspace": it deletes the character typed before it (if any).
    Return `true` if both strings produce the same text once typed out.
    """,
    examples=[(["ab#c", "ad#c"], True, "Both become \"ac\"."), (["a#c", "b"], False, None)],
    tests=[(["ab##", "c#d#"], True), (["a##c", "#a#c"], True), (["xy#z", "xzz#"], True), (["bxj##tw", "bxo#j##tw"], True)],
    constraints=["1 ≤ s.length, t.length ≤ 200"],
    hints=["Read both strings from the end.", "Count pending backspaces to know which characters survive."],
    approaches=[approach(
        name="Two Pointers from the end", pattern="two-pointers", time="O(n + m)", space="O(1)",
        idea="""
        Scanning backwards, a `#` tells us to skip the next real character. So walk I down `s` and J down `t`, each time jumping to the next character that survives.

        Compare the two survivors; any difference, or one string running out first, means the texts differ.
        """,
        viz=viz(arrays=[("s", {"i": "i"}), ("t", {"j": "j"})]),
        py='''
        def backspace_equal(s, t):
            def survivor(x, i):
                skip = 0
                while i >= 0:
                    if x[i] == "#":
                        skip += 1
                    elif skip:
                        skip -= 1
                    else:
                        break
                    i -= 1
                return i

            i, j = len(s) - 1, len(t) - 1
            while True:
                i, j = survivor(s, i), survivor(t, j)  #>^ The next surviving characters are {q(s[i]) if i >= 0 else "nothing"} and {q(t[j]) if j >= 0 else "nothing"}.
                if i < 0 or j < 0:
                    return i < 0 and j < 0
                if s[i] != t[j]:
                    return False
                i, j = i - 1, j - 1
        ''',
        java='''
        class Solution {
            public boolean backspaceEqual(String s, String t) {
                int i = s.length() - 1, j = t.length() - 1;
                while (true) {
                    i = survivor(s, i); j = survivor(t, j); //>
                    if (i < 0 || j < 0) return i < 0 && j < 0;
                    if (s.charAt(i) != t.charAt(j)) return false;
                    i--; j--;
                }
            }

            private int survivor(String x, int i) {
                int skip = 0;
                for (; i >= 0; i--) {
                    if (x.charAt(i) == '#') skip++;
                    else if (skip > 0) skip--;
                    else break;
                }
                return i;
            }
        }
        ''',
    )],
)

problem(
    id="next-arrangement",
    title="Next Bigger Arrangement",
    difficulty="Medium",
    topics=["Array", "Two Pointers"],
    statement="""
    Rearrange `nums` **in place** into the next arrangement that is larger in dictionary order (the next
    permutation). If `nums` is already the largest arrangement, rearrange it into the smallest one (sorted ascending).
    """,
    examples=[([[1, 2, 3]], [1, 3, 2], None), ([[3, 2, 1]], [1, 2, 3], None)],
    tests=[([[1, 1, 5]], [1, 5, 1]), ([[1, 3, 2]], [2, 1, 3]), ([[2, 4, 3, 1]], [3, 1, 2, 4])],
    out="arg0",
    constraints=["1 ≤ nums.length ≤ 100"],
    hints=["Find the first position from the right that is smaller than its right neighbour.",
           "Swap it with the next larger value to its right, then reverse the tail."],
    approaches=[approach(
        name="Scan + Two Pointers", pattern="two-pointers", time="O(n)", space="O(1)",
        idea="""
        From the right, find the first value that is smaller than the value after it; this is the digit we must bump up. Swap it with the smallest larger value on its right.

        The part after it is still in descending order, so reverse it with two pointers to make it as small as possible.
        """,
        viz=viz(arr="nums", ptr={"i": "i", "L": "l", "R": "r"}),
        demo=[[2, 4, 3, 1]],
        py='''
        def next_arrangement(nums):
            i = len(nums) - 2
            while i >= 0 and nums[i] >= nums[i + 1]:
                i -= 1
            if i >= 0:  #> Scanning from the right, {nums[i]} at index {i} is the first value smaller than its neighbour.
                j = len(nums) - 1
                while nums[j] <= nums[i]:
                    j -= 1
                nums[i], nums[j] = nums[j], nums[i]  #> Swap it with the next bigger value on its right.
            l, r = i + 1, len(nums) - 1  #> Now reverse everything after index {i} with L and R.
            while l < r:
                nums[l], nums[r] = nums[r], nums[l]  #> Swap positions {l} and {r}.
                l, r = l + 1, r - 1
        ''',
        java='''
        class Solution {
            public void nextArrangement(int[] nums) {
                int i = nums.length - 2;
                while (i >= 0 && nums[i] >= nums[i + 1]) i--;
                if (i >= 0) { //>
                    int j = nums.length - 1;
                    while (nums[j] <= nums[i]) j--;
                    int t = nums[i]; nums[i] = nums[j]; nums[j] = t; //>
                }
                for (int l = i + 1, r = nums.length - 1; l < r; l++, r--) { //>
                    int t = nums[l]; nums[l] = nums[r]; nums[r] = t; //>
                }
            }
        }
        ''',
    )],
)

problem(
    id="find-the-duplicate",
    title="The One Repeated Number",
    difficulty="Medium",
    topics=["Array", "Two Pointers", "Binary Search"],
    statement="""
    `nums` has `n + 1` integers, each between `1` and `n`, so at least one value repeats. Exactly one value is
    repeated (possibly many times). Return it without modifying `nums` and using only O(1) extra memory.
    """,
    examples=[([[1, 3, 4, 2, 2]], 2, None), ([[3, 1, 3, 4, 2]], 3, None)],
    tests=[([[1, 1]], 1), ([[2, 2, 2, 2]], 2), ([[1, 4, 4, 2, 4]], 4)],
    constraints=["1 ≤ n ≤ 10^5", "1 ≤ nums[i] ≤ n"],
    hints=["Treat each value as a pointer to an index: i → nums[i].", "A repeated value means two arrows enter the same index — a cycle."],
    approaches=[approach(
        name="Fast & Slow Pointers", pattern="fast-slow", time="O(n)", space="O(1)",
        idea="""
        Treat each value as an arrow to an index. Because two positions hold the same value, two arrows point at the same index, which creates a cycle whose entrance is the duplicate.

        Move a slow pointer one hop and a fast pointer two hops until they meet. Then restart slow from the beginning and move both one hop at a time: they meet exactly at the duplicate.
        """,
        why="Floyd's cycle detection takes linear time and just two variables.",
        viz=viz(arr="nums", ptr={"slow": "slow", "fast": "fast"}),
        py='''
        def find_duplicate(nums):
            slow = fast = nums[0]
            while True:
                slow, fast = nums[slow], nums[nums[fast]]  #> Slow hops to {slow}; fast hops twice to {fast}.
                if slow == fast:
                    break
            slow = nums[0]  #> They met inside the cycle. Restart slow from the beginning.
            while slow != fast:
                slow, fast = nums[slow], nums[fast]  #> Both hop once: slow is {slow}, fast is {fast}.
            return slow  #> They meet at the duplicate: {slow}.
        ''',
        java='''
        class Solution {
            public int findDuplicate(int[] nums) {
                int slow = nums[0], fast = nums[0];
                do { slow = nums[slow]; fast = nums[nums[fast]]; } while (slow != fast); //>
                slow = nums[0]; //>
                while (slow != fast) { slow = nums[slow]; fast = nums[fast]; } //>
                return slow; //>
            }
        }
        ''',
    )],
)

problem(
    id="sorted-intersection",
    title="Common Values of Two Sorted Lists",
    difficulty="Easy",
    topics=["Array", "Two Pointers"],
    statement="""
    `a` and `b` are sorted ascending. Return the values they have in common, in ascending order. If a value appears
    several times in both lists, include it as many times as it appears in both.
    """,
    examples=[([[1, 2, 2, 3, 5], [2, 2, 4, 5]], [2, 2, 5], None), ([[1, 3], [2, 4]], [], None)],
    tests=[([[], [1]], []), ([[1, 1, 1], [1, 1]], [1, 1]), ([[0, 4, 9], [4, 9, 9]], [4, 9])],
    constraints=["0 ≤ a.length, b.length ≤ 10^5"],
    hints=["Advance the pointer that sits on the smaller value."],
    approaches=[approach(
        name="Two Pointers", pattern="two-pointers", time="O(n + m)", space="O(1) extra",
        idea="""
        Put I at the start of `a` and J at the start of `b`. If the values are equal, it is a common value: record it and move both.

        Otherwise the smaller value can't appear in the other list any more, so move the pointer that sits on it.
        """,
        viz=viz(arrays=[("a", {"i": "i"}), ("b", {"j": "j"})], out="res"),
        py='''
        def common_values(a, b):
            i = j = 0
            res = []
            while i < len(a) and j < len(b):
                if a[i] == b[j]:
                    res.append(a[i])  #> Both lists have {a[i]}, so keep it.
                    i, j = i + 1, j + 1
                elif a[i] < b[j]:
                    i += 1  #> {a[i - 1]} is smaller, so I moves on.
                else:
                    j += 1  #> {b[j - 1]} is smaller, so J moves on.
            return res
        ''',
        java='''
        class Solution {
            public List<Integer> commonValues(int[] a, int[] b) {
                List<Integer> res = new ArrayList<>();
                int i = 0, j = 0;
                while (i < a.length && j < b.length) {
                    if (a[i] == b[j]) { res.add(a[i]); i++; j++; } //>
                    else if (a[i] < b[j]) i++; //>
                    else j++; //>
                }
                return res;
            }
        }
        ''',
    )],
)
