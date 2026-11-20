"""Bit Manipulation & Math problems (original statements)."""
from dsl import problem, approach, viz

problem(
    id="lone-number",
    title="The Number Without a Twin",
    difficulty="Easy",
    topics=["Array", "Bit Manipulation"],
    statement="""
    Every value in `nums` appears exactly twice, except one value that appears once. Return it using O(1) extra memory.
    """,
    examples=[([[4, 1, 2, 1, 2]], 4, None), ([[2, 2, 1]], 1, None)],
    tests=[([[7]], 7), ([[-3, 5, 5]], -3)],
    constraints=["1 ≤ nums.length ≤ 3·10^4"],
    hints=["x XOR x = 0 and x XOR 0 = x."],
    approaches=[approach(
        name="XOR Everything", pattern="bits", time="O(n)", space="O(1)",
        idea="""
        XOR has two handy rules: a value XOR itself is 0, and XOR with 0 changes nothing. XOR-ing every number cancels all the twins, leaving only the lone number.
        """,
        viz=viz(arr="nums", ptr={"i": "i"}, bits=[("x", "x"), ("acc", "acc")]),
        py='''
        def lone_number(nums):
            acc = 0
            for i, x in enumerate(nums):
                acc ^= x  #> XOR in {x}. The running value is {acc}.
            return acc
        ''',
        java='''
        class Solution {
            public int loneNumber(int[] nums) {
                int acc = 0;
                for (int x : nums) acc ^= x; //>
                return acc;
            }
        }
        ''',
    )],
)

problem(
    id="count-set-bits",
    title="Count the 1 Bits",
    difficulty="Easy",
    topics=["Bit Manipulation"],
    statement="""
    Return how many 1 bits the binary form of the non-negative integer `n` has.
    """,
    examples=[([11], 3, "11 is 1011 in binary."), ([128], 1, None)],
    tests=[([0], 0), ([2147483647], 31)],
    constraints=["0 ≤ n < 2^31"],
    hints=["n & (n − 1) clears the lowest 1 bit."],
    approaches=[approach(
        name="Clear the Lowest Bit", pattern="bits", time="O(number of 1 bits)", space="O(1)",
        idea="""
        Subtracting 1 flips the lowest 1 bit and every 0 below it, so `n & (n − 1)` removes exactly one 1 bit. Count how many times you can do that before n reaches 0.
        """,
        viz=viz(bits=["n"], vars=["count"]),
        py='''
        def count_bits(n):
            count = 0
            while n:
                n &= n - 1
                count += 1  #> Cleared the lowest 1 bit. {count} found so far.
            return count
        ''',
        java='''
        class Solution {
            public int countBits(int n) {
                int count = 0;
                for (; n != 0; n &= n - 1) count++; //>
                return count;
            }
        }
        ''',
    )],
)

problem(
    id="bit-counts-up-to-n",
    title="Bit Counts From 0 to n",
    difficulty="Easy",
    topics=["Bit Manipulation", "Dynamic Programming"],
    statement="""
    Return an array where entry `i` is the number of 1 bits in `i`, for every `i` from `0` to `n`.
    """,
    examples=[([2], [0, 1, 1], None), ([5], [0, 1, 1, 2, 1, 2], None)],
    tests=[([0], [0]), ([8], [0, 1, 1, 2, 1, 2, 2, 3, 1])],
    constraints=["0 ≤ n ≤ 10^5"],
    hints=["i has the same bits as i / 2, plus its last bit."],
    approaches=[approach(
        name="Reuse Smaller Answers", pattern="dp", time="O(n)", space="O(n)",
        idea="""
        Shifting i right by one drops its last bit, so bits(i) = bits(i ÷ 2) + (i's last bit). Every answer reuses one we already computed.
        """,
        viz=viz(table=("res", {"i": "i"}, None, "bits(i)")),
        demo=[6],
        py='''
        def bit_counts(n):
            res = [0] * (n + 1)
            for i in range(1, n + 1):
                res[i] = res[i >> 1] + (i & 1)  #> {i} has {res[i]} one bits: {res[i >> 1]} from {i >> 1}, plus its last bit {i & 1}.
            return res
        ''',
        java='''
        class Solution {
            public int[] bitCounts(int n) {
                int[] res = new int[n + 1];
                for (int i = 1; i <= n; i++) res[i] = res[i >> 1] + (i & 1); //>
                return res;
            }
        }
        ''',
    )],
)

problem(
    id="missing-from-range",
    title="The Missing Number",
    difficulty="Easy",
    topics=["Array", "Math", "Bit Manipulation"],
    statement="""
    `nums` contains `n` distinct numbers from the range `0..n`, so exactly one number of the range is missing. Return it.
    """,
    examples=[([[3, 0, 1]], 2, None), ([[9, 6, 4, 2, 3, 5, 7, 0, 1]], 8, None)],
    tests=[([[0]], 1), ([[1]], 0)],
    constraints=["1 ≤ n ≤ 10^4"],
    hints=["The sum of 0..n is n(n + 1) / 2."],
    approaches=[approach(
        name="Expected Sum", pattern="math", time="O(n)", space="O(1)",
        idea="""
        Every index 0 to n − 1 and the extra number n should cancel against the values. Add each index and subtract each value; whatever is left over is the missing number.

        This avoids computing a large sum, so it never overflows.
        """,
        viz=viz(arr="nums", ptr={"i": "i"}, vars=["missing"]),
        py='''
        def missing_number(nums):
            missing = len(nums)
            for i, x in enumerate(nums):
                missing += i - x  #> Add index {i} and subtract value {x}: the running total is {missing}.
            return missing
        ''',
        java='''
        class Solution {
            public int missingNumber(int[] nums) {
                int missing = nums.length;
                for (int i = 0; i < nums.length; i++) missing += i - nums[i]; //>
                return missing;
            }
        }
        ''',
    )],
)

problem(
    id="power-of-two",
    title="Is It a Power of Two?",
    difficulty="Easy",
    topics=["Bit Manipulation", "Math"],
    statement="""
    Return `true` if the integer `n` equals 2^k for some integer k ≥ 0.
    """,
    examples=[([16], True, None), ([6], False, None)],
    tests=[([1], True), ([0], False), ([-8], False), ([1073741824], True)],
    constraints=["-2^31 ≤ n < 2^31"],
    hints=["Powers of two have exactly one 1 bit."],
    approaches=[approach(
        name="One Bit Set", pattern="bits", time="O(1)", space="O(1)",
        idea="""
        A positive power of two has exactly one 1 bit. Clearing the lowest 1 bit with `n & (n − 1)` must therefore leave zero.
        """,
        viz=viz(bits=["n", ("n - 1", "n - 1")]),
        py='''
        def is_power_of_two(n):
            return n > 0 and n & (n - 1) == 0  #> {n} AND {n - 1} is {n & (n - 1)}, so the answer is {ret}.
        ''',
        java='''
        class Solution {
            public boolean isPowerOfTwo(int n) {
                return n > 0 && (n & (n - 1)) == 0; //>
            }
        }
        ''',
    )],
)

problem(
    id="add-without-plus",
    title="Add Without the Plus Sign",
    difficulty="Medium",
    topics=["Bit Manipulation", "Math"],
    statement="""
    Return `a + b` for 32-bit signed integers without using `+` or `-`.
    """,
    examples=[([1, 2], 3, None), ([-2, 3], 1, None)],
    tests=[([0, 0], 0), ([-5, -7], -12), ([1000, 24], 1024)],
    constraints=["-1000 ≤ a, b ≤ 1000"],
    hints=["XOR adds without carrying; AND finds the carries."],
    approaches=[approach(
        name="XOR + Carry", pattern="bits", time="O(32)", space="O(1)",
        idea="""
        XOR adds each bit pair while ignoring carries; AND shifted left by one gives exactly the carries. Keep adding the carries back in until none are left.

        Python integers are unbounded, so we mask to 32 bits and convert back to a signed number at the end.
        """,
        viz=viz(bits=[("a", "a & 0xFFFFFFFF"), ("carry", "b & 0xFFFFFFFF")]),
        demo=[5, 7],
        py='''
        def add(a, b):
            mask, max_int = 0xFFFFFFFF, 0x7FFFFFFF
            while b:
                a, b = (a ^ b) & mask, ((a & b) << 1) & mask  #> Partial sum {a}, carry {b}.
            return a if a <= max_int else ~(a ^ mask)
        ''',
        java='''
        class Solution {
            public int add(int a, int b) {
                while (b != 0) {
                    int carry = (a & b) << 1;
                    a ^= b;
                    b = carry; //>
                }
                return a;
            }
        }
        ''',
    )],
)

problem(
    id="reverse-digits",
    title="Reverse the Digits",
    difficulty="Medium",
    topics=["Math"],
    statement="""
    Reverse the digits of the 32-bit signed integer `x`. If the result falls outside the 32-bit signed range,
    return `0`.
    """,
    examples=[([123], 321, None), ([-120], -21, None)],
    tests=[([0], 0), ([1534236469], 0), ([-2147483412], -2143847412)],
    constraints=["-2^31 ≤ x < 2^31"],
    hints=["Pop the last digit with % 10 and push it onto the result with × 10.", "Check for overflow before it happens."],
    approaches=[approach(
        name="Pop and Push Digits", pattern="math", time="O(log x)", space="O(1)",
        idea="""
        Repeatedly take the last digit of x and append it to the result. Before appending, check that the result times 10 won't leave the 32-bit range.
        """,
        viz=viz(vars=["x", "res"]),
        py='''
        def reverse_digits(x):
            sign, x, res = (-1 if x < 0 else 1), abs(x), 0
            while x:
                x, digit = divmod(x, 10)
                res = res * 10 + digit  #> Move digit {digit} over: the result is {res}.
                if res > 2**31 - 1:
                    return 0
            return sign * res
        ''',
        java='''
        class Solution {
            public int reverseDigits(int x) {
                int res = 0;
                for (; x != 0; x /= 10) {
                    if (res > Integer.MAX_VALUE / 10 || res < Integer.MIN_VALUE / 10) return 0;
                    res = res * 10 + x % 10; //>
                }
                return res;
            }
        }
        ''',
    )],
)

problem(
    id="happy-number",
    title="Does the Digit-Square Chain Reach 1?",
    difficulty="Easy",
    topics=["Math", "Fast & Slow Pointers"],
    statement="""
    Starting from `n`, repeatedly replace the number with the sum of the squares of its digits. Return `true` if this
    eventually reaches 1, and `false` if it loops forever without reaching 1.
    """,
    examples=[([19], True, "1² + 9² = 82 → 68 → 100 → 1"), ([2], False, None)],
    tests=[([1], True), ([7], True), ([4], False)],
    constraints=["1 ≤ n < 2^31"],
    hints=["The chain either reaches 1 or enters a cycle.", "Detect the cycle with slow and fast pointers."],
    approaches=[approach(
        name="Fast & Slow Pointers", pattern="fast-slow", time="O(log n)", space="O(1)",
        idea="""
        Treat the chain like a linked list. Move `slow` one step and `fast` two steps. If there's a cycle they meet; if the chain reaches 1, fast gets there first (1 maps to itself).
        """,
        viz=viz(vars=["slow", "fast"]),
        py='''
        def is_happy(n):
            def step(x):
                return sum(int(d) ** 2 for d in str(x))

            slow, fast = n, step(n)
            while fast != 1 and slow != fast:
                slow, fast = step(slow), step(step(fast))  #>^ Slow moves to {slow}, fast jumps to {fast}.
            return fast == 1
        ''',
        java='''
        class Solution {
            public boolean isHappy(int n) {
                int slow = n, fast = step(n);
                while (fast != 1 && slow != fast) { slow = step(slow); fast = step(step(fast)); } //>
                return fast == 1;
            }

            private int step(int x) {
                int s = 0;
                for (; x > 0; x /= 10) s += (x % 10) * (x % 10);
                return s;
            }
        }
        ''',
    )],
)

problem(
    id="number-palindrome",
    title="Does the Number Read the Same Backwards?",
    difficulty="Easy",
    topics=["Math", "Two Pointers"],
    statement="""
    Return `true` if the integer `x` reads the same forwards and backwards, without converting it to a string.
    """,
    examples=[([121], True, None), ([-121], False, "It reads 121- backwards.")],
    tests=[([10], False), ([0], True), ([12321], True), ([1221], True)],
    constraints=["-2^31 ≤ x < 2^31"],
    hints=["Reverse only the second half of the digits and compare."],
    approaches=[approach(
        name="Reverse Half the Digits", pattern="two-pointers", time="O(log x)", space="O(1)",
        idea="""
        Peel digits off the end into a reversed half until the reversed half is at least as big as what's left. Then the two halves meet in the middle, like two pointers: they must be equal (or equal after dropping the middle digit).
        """,
        viz=viz(vars=["x", "half"]),
        demo=[12321],
        py='''
        def is_palindrome_number(x):
            if x < 0 or (x % 10 == 0 and x != 0):
                return False
            half = 0
            while x > half:
                x, half = x // 10, half * 10 + x % 10  #> Left part {x}, reversed right part {half}.
            return x == half or x == half // 10
        ''',
        java='''
        class Solution {
            public boolean isPalindromeNumber(int x) {
                if (x < 0 || (x % 10 == 0 && x != 0)) return false;
                int half = 0;
                for (; x > half; x /= 10) half = half * 10 + x % 10; //>
                return x == half || x == half / 10;
            }
        }
        ''',
    )],
)

problem(
    id="fast-power",
    title="Raise to a Power Quickly",
    difficulty="Medium",
    topics=["Math", "Recursion"],
    statement="""
    Compute `x` raised to the integer power `n` (n may be negative) in O(log |n|) multiplications.
    """,
    examples=[([2.0, 10], 1024.0, None), ([2.0, -2], 0.25, None)],
    tests=[([1.5, 0], 1.0), ([-2.0, 3], -8.0), ([0.5, 4], 0.0625)],
    check="float",
    constraints=["-100 < x < 100", "-2^31 ≤ n < 2^31"],
    hints=["x^n = (x²)^(n/2), times one extra x when n is odd."],
    approaches=[approach(
        name="Binary Exponentiation", pattern="math", time="O(log n)", space="O(1)",
        idea="""
        Look at n in binary. Square the base each step; whenever the current bit of n is 1, multiply that power into the result. A negative exponent just means using 1/x.
        """,
        viz=viz(vars=["base", "e", "res"]),
        py='''
        def power(x, n):
            base, e, res = (x, n, 1.0) if n >= 0 else (1 / x, -n, 1.0)
            while e:
                if e & 1:
                    res *= base  #> The low bit is 1, so multiply in {fv(base)}: the result is {fv(res)}.
                base, e = base * base, e >> 1
            return res
        ''',
        java='''
        class Solution {
            public double power(double x, int n) {
                long e = Math.abs((long) n);
                double base = n >= 0 ? x : 1 / x, res = 1.0;
                for (; e > 0; e >>= 1, base *= base) if ((e & 1) == 1) res *= base; //>
                return res;
            }
        }
        ''',
    )],
)
