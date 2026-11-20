"""Stack & Monotonic Stack problems (original statements)."""
from dsl import problem, approach, viz

problem(
    id="matching-brackets",
    title="Brackets That Match",
    difficulty="Easy",
    topics=["String", "Stack"],
    statement="""
    `s` contains only the characters `()[]{}`. Return `true` if every opening bracket is closed by the same kind of
    bracket, in the correct order.
    """,
    examples=[(["([]{})"], True, None), (["(]"], False, None)],
    tests=[(["("], False), (["]"], False), (["{[()()]}"], True), (["([)]"], False)],
    constraints=["1 ≤ s.length ≤ 10^4"],
    hints=["The most recent unclosed bracket must close first: last in, first out."],
    approaches=[approach(
        name="Stack", pattern="stack", time="O(n)", space="O(n)",
        idea="""
        Push every opening bracket onto a stack. A closing bracket must match the bracket on top of the stack, which we then pop.

        At the end the stack must be empty, otherwise some bracket was never closed.
        """,
        viz=viz(arr="s", ptr={"i": "i"}, stacks=["stack"]),
        demo=["{[()]}"],
        py='''
        def brackets_match(s):
            pairs = {")": "(", "]": "[", "}": "{"}
            stack = []
            for i, ch in enumerate(s):
                if ch not in pairs:
                    stack.append(ch)  #> {q(ch)} opens a bracket. Push it.
                elif stack and stack[-1] == pairs[ch]:
                    stack.pop()  #> {q(ch)} closes the {q(pairs[ch])} on top. Pop it.
                else:
                    return False  #> {q(ch)} has no matching open bracket.
            return not stack  #> Is the stack empty at the end? {yn(not stack)}.
        ''',
        java='''
        class Solution {
            public boolean bracketsMatch(String s) {
                Deque<Character> stack = new ArrayDeque<>();
                for (char ch : s.toCharArray()) {
                    char open = ch == ')' ? '(' : ch == ']' ? '[' : '{';
                    if (ch == '(' || ch == '[' || ch == '{') stack.push(ch); //>
                    else if (!stack.isEmpty() && stack.peek() == open) stack.pop(); //>
                    else return false; //>
                }
                return stack.isEmpty(); //>
            }
        }
        ''',
    )],
)

problem(
    id="min-stack",
    title="Stack With Instant Minimum",
    difficulty="Medium",
    topics=["Stack", "Design"],
    design=True,
    statement="""
    Design `MinStack` supporting `push(x)`, `pop()`, `top()` and `getMin()` (the smallest value currently in the
    stack), each in O(1). `pop`, `top` and `getMin` are only called on a non-empty stack.
    """,
    examples=[((["MinStack", "push", "push", "push", "getMin", "pop", "top", "getMin"], [[], [-2], [0], [-3], [], [], [], []]),
               [None, None, None, None, -3, None, 0, -2], None)],
    tests=[((["MinStack", "push", "getMin", "push", "getMin", "pop", "getMin"], [[], [5], [], [5], [], [], []]), [None, None, 5, None, 5, None, 5])],
    constraints=["up to 3·10^4 calls"],
    hints=["Store, next to each value, the minimum at the moment it was pushed."],
    approaches=[approach(
        name="Stack of (value, min) pairs", pattern="stack", time="O(1) per operation", space="O(n)",
        idea="""
        Each stack entry stores the value and the minimum of the stack at that moment, which is the smaller of the value and the previous entry's minimum.

        Popping removes both together, so the entry below always knows the correct minimum.
        """,
        viz=viz(stacks=[("stack (value, min)", "self.stack")]),
        py='''
        class MinStack:
            def __init__(self):
                self.stack = []

            def push(self, x):
                low = min(x, self.stack[-1][1]) if self.stack else x
                self.stack.append((x, low))  #> Push {x}. The minimum is now {low}.

            def pop(self):
                self.stack.pop()  #> Pop the top. The minimum goes back to {self.stack[-1][1] if self.stack else "nothing"}.

            def top(self):
                return self.stack[-1][0]

            def getMin(self):
                return self.stack[-1][1]  #> The minimum is stored right on top: {ret}.
        ''',
        java='''
        class MinStack {
            private final Deque<int[]> stack = new ArrayDeque<>();

            public void push(int x) {
                stack.push(new int[]{x, stack.isEmpty() ? x : Math.min(x, stack.peek()[1])}); //>
            }

            public void pop() { stack.pop(); } //>

            public int top() { return stack.peek()[0]; }

            public int getMin() { return stack.peek()[1]; } //>
        }
        ''',
    )],
)

problem(
    id="postfix-calculator",
    title="Postfix Calculator",
    difficulty="Medium",
    topics=["Array", "Stack", "Math"],
    statement="""
    Evaluate an arithmetic expression written in postfix (reverse Polish) notation, given as a list of tokens.
    Operators are `+ - * /`; division truncates toward zero. The expression is always valid.
    """,
    examples=[([["2", "1", "+", "3", "*"]], 9, "(2 + 1) × 3"), ([["4", "13", "5", "/", "+"]], 6, "4 + 13 / 5")],
    tests=[([["7"]], 7), ([["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]], 22), ([["3", "-4", "/"]], 0)],
    constraints=["1 ≤ tokens.length ≤ 10^4"],
    hints=["Numbers wait on a stack until an operator needs them."],
    approaches=[approach(
        name="Stack", pattern="stack", time="O(n)", space="O(n)",
        idea="""
        Read tokens left to right. Push numbers. An operator pops the two most recent numbers, applies itself (the first popped is the right operand), and pushes the result.

        The single number left at the end is the answer.
        """,
        viz=viz(arr="tokens", ptr={"i": "i"}, stacks=["stack"]),
        py='''
        def postfix(tokens):
            ops = {"+": lambda a, b: a + b, "-": lambda a, b: a - b,
                   "*": lambda a, b: a * b, "/": lambda a, b: int(a / b)}
            stack = []
            for i, t in enumerate(tokens):
                if t in ops:
                    b, a = stack.pop(), stack.pop()
                    stack.append(ops[t](a, b))  #> Apply {a} {t} {b} = {stack[-1]}, and push the result.
                else:
                    stack.append(int(t))  #> Push the number {t}.
            return stack[0]
        ''',
        java='''
        class Solution {
            public int postfix(String[] tokens) {
                Deque<Integer> stack = new ArrayDeque<>();
                for (String t : tokens) {
                    if ("+-*/".contains(t) && t.length() == 1) {
                        int b = stack.pop(), a = stack.pop();
                        stack.push(t.equals("+") ? a + b : t.equals("-") ? a - b : t.equals("*") ? a * b : a / b); //>
                    } else stack.push(Integer.parseInt(t)); //>
                }
                return stack.pop();
            }
        }
        ''',
    )],
)

problem(
    id="days-until-warmer",
    title="Days Until a Warmer Day",
    difficulty="Medium",
    topics=["Array", "Monotonic Stack"],
    statement="""
    `temps[i]` is the temperature on day `i`. For each day, return how many days you must wait for a strictly warmer
    temperature, or `0` if no warmer day comes.
    """,
    examples=[([[73, 74, 75, 71, 69, 72, 76, 73]], [1, 1, 4, 2, 1, 1, 0, 0], None), ([[30, 60, 90]], [1, 1, 0], None)],
    tests=[([[50]], [0]), ([[90, 80, 70]], [0, 0, 0]), ([[40, 40, 41]], [2, 1, 0])],
    constraints=["1 ≤ temps.length ≤ 10^5"],
    hints=["Keep the days still waiting for a warmer day on a stack.", "Temperatures on the stack only go down."],
    approaches=[approach(
        name="Monotonic Stack", pattern="monotonic-stack", time="O(n)", space="O(n)",
        idea="""
        Keep a stack of days still waiting for a warmer day; their temperatures decrease from bottom to top.

        Each new day pops every waiting day that is colder, because today is their answer. Then today joins the stack and waits.
        """,
        why="Every day is pushed once and popped at most once.",
        viz=viz(arr="temps", ptr={"today": "i"}, stacks=[("waiting days", "stack")], out="res"),
        demo=[[73, 74, 75, 71, 69, 72, 76]],
        py='''
        def days_until_warmer(temps):
            res, stack = [0] * len(temps), []
            for i, t in enumerate(temps):
                while stack and temps[stack[-1]] < t:
                    j = stack.pop()
                    res[j] = i - j  #> Day {j} ({temps[j]}°) waited {i - j} days for {t}°.
                stack.append(i)  #> Day {i} ({t}°) starts waiting.
            return res
        ''',
        java='''
        class Solution {
            public int[] daysUntilWarmer(int[] temps) {
                int[] res = new int[temps.length];
                Deque<Integer> stack = new ArrayDeque<>();
                for (int i = 0; i < temps.length; i++) {
                    while (!stack.isEmpty() && temps[stack.peek()] < temps[i]) {
                        int j = stack.pop();
                        res[j] = i - j; //>
                    }
                    stack.push(i); //>
                }
                return res;
            }
        }
        ''',
    )],
)

problem(
    id="next-greater-circular",
    title="Next Bigger Value in a Circle",
    difficulty="Medium",
    topics=["Array", "Monotonic Stack"],
    statement="""
    `nums` is circular: after the last element comes the first. For each element, return the first strictly greater
    value you meet when walking forward around the circle, or `-1` if there is none.
    """,
    examples=[([[1, 2, 1]], [2, -1, 2], None), ([[1, 2, 3, 4, 3]], [2, 3, 4, -1, 4], None)],
    tests=[([[5]], [-1]), ([[3, 3]], [-1, -1]), ([[2, 1, 3]], [3, 3, -1])],
    constraints=["1 ≤ nums.length ≤ 10^4"],
    hints=["Walk the array twice to simulate the circle."],
    approaches=[approach(
        name="Monotonic Stack (two laps)", pattern="monotonic-stack", time="O(n)", space="O(n)",
        idea="""
        Walk the indexes twice around the circle. Keep a stack of indexes still waiting for a bigger value; when a bigger value arrives, it answers them.

        Only push indexes during the first lap, so each one waits at most one full circle.
        """,
        viz=viz(arr="nums", ptr={"i": "i % len(nums)"}, stacks=[("waiting", "stack")], out="res"),
        demo=[[2, 1, 3, 1]],
        py='''
        def next_greater_circular(nums):
            n = len(nums)
            res, stack = [-1] * n, []
            for i in range(2 * n):
                x = nums[i % n]
                while stack and nums[stack[-1]] < x:
                    res[stack.pop()] = x  #> {x} is the next bigger value for an index that was waiting.
                if i < n:
                    stack.append(i)
            return res
        ''',
        java='''
        class Solution {
            public int[] nextGreaterCircular(int[] nums) {
                int n = nums.length;
                int[] res = new int[n];
                Arrays.fill(res, -1);
                Deque<Integer> stack = new ArrayDeque<>();
                for (int i = 0; i < 2 * n; i++) {
                    int x = nums[i % n];
                    while (!stack.isEmpty() && nums[stack.peek()] < x) res[stack.pop()] = x; //>
                    if (i < n) stack.push(i);
                }
                return res;
            }
        }
        ''',
    )],
)

problem(
    id="biggest-rectangle-bars",
    title="Biggest Rectangle in a Bar Chart",
    difficulty="Hard",
    topics=["Array", "Monotonic Stack"],
    statement="""
    `heights` describes a bar chart with bars of width 1. Return the area of the largest rectangle that fits entirely
    inside the bars.
    """,
    examples=[([[2, 1, 5, 6, 2, 3]], 10, "Bars 5 and 6 give height 5 × width 2."), ([[2, 4]], 4, None)],
    tests=[([[1]], 1), ([[3, 3, 3]], 9), ([[6, 2, 5, 4, 5, 1, 6]], 12)],
    constraints=["1 ≤ heights.length ≤ 10^5"],
    hints=["For each bar, find how far it can stretch left and right.", "A bar stops stretching when a shorter bar appears."],
    approaches=[approach(
        name="Monotonic Stack", pattern="monotonic-stack", time="O(n)", space="O(n)",
        idea="""
        Keep a stack of bar indexes with increasing heights. When a shorter bar arrives, the taller bars on the stack can't extend past it, so pop them and compute their rectangles.

        A popped bar's rectangle stretches from just after the new stack top to just before the current index.
        """,
        why="Each bar is pushed and popped once. A zero-height sentinel at the end flushes the stack.",
        viz=viz(arr="heights", ptr={"i": "i"}, stacks=[("rising bars", "stack")], vars=["best"]),
        demo=[[2, 1, 5, 6, 2, 3]],
        py='''
        def largest_rectangle(heights):
            stack, best = [], 0
            for i, h in enumerate(heights + [0]):
                while stack and heights[stack[-1]] >= h:
                    top = stack.pop()
                    width = i if not stack else i - stack[-1] - 1
                    best = max(best, heights[top] * width)  #> Bar {heights[top]} stretches over width {width}: area {heights[top] * width}. Best: {best}.
                stack.append(i)
            return best
        ''',
        java='''
        class Solution {
            public int largestRectangle(int[] heights) {
                Deque<Integer> stack = new ArrayDeque<>();
                int best = 0, n = heights.length;
                for (int i = 0; i <= n; i++) {
                    int h = i == n ? 0 : heights[i];
                    while (!stack.isEmpty() && heights[stack.peek()] >= h) {
                        int top = stack.pop();
                        int width = stack.isEmpty() ? i : i - stack.peek() - 1;
                        best = Math.max(best, heights[top] * width); //>
                    }
                    stack.push(i);
                }
                return best;
            }
        }
        ''',
    )],
)

problem(
    id="decode-repeats",
    title="Expand Repeated Groups",
    difficulty="Medium",
    topics=["String", "Stack", "Recursion"],
    statement="""
    An encoded string uses the rule `k[text]`, meaning `text` repeated `k` times; groups can be nested. Return the
    fully expanded string. Input is always valid and digits only appear as repeat counts.
    """,
    examples=[(["3[a]2[bc]"], "aaabcbc", None), (["2[a2[c]]"], "accacc", None)],
    tests=[(["abc"], "abc"), (["10[x]"], "xxxxxxxxxx"), (["2[ab3[d]]e"], "abdddabddde")],
    constraints=["1 ≤ s.length ≤ 30", "counts are between 1 and 300"],
    hints=["On '[' save the current text and count; on ']' combine."],
    approaches=[approach(
        name="Stack", pattern="stack", time="O(output)", space="O(n)",
        idea="""
        Build the current text and current number as you read. At `[`, push the text-so-far and the repeat count, then start fresh.

        At `]`, pop them back and attach the current text repeated count times to the saved text.
        """,
        viz=viz(arr="s", ptr={"i": "i"}, stacks=[("saved (text, count)", "stack")], vars=["cur", "num"]),
        py='''
        def expand(s):
            stack, cur, num = [], "", 0
            for i, ch in enumerate(s):
                if ch.isdigit():
                    num = num * 10 + int(ch)
                elif ch == "[":
                    stack.append((cur, num))  #> Save {q(cur)} and the count {num}, then start fresh.
                    cur, num = "", 0
                elif ch == "]":
                    prev, k = stack.pop()
                    cur = prev + cur * k  #> Close a group: repeat it {k} times. Text is now {q(cur)}.
                else:
                    cur += ch
            return cur
        ''',
        java='''
        class Solution {
            public String expand(String s) {
                Deque<Object[]> stack = new ArrayDeque<>();
                StringBuilder cur = new StringBuilder();
                int num = 0;
                for (char ch : s.toCharArray()) {
                    if (Character.isDigit(ch)) num = num * 10 + (ch - '0');
                    else if (ch == '[') { stack.push(new Object[]{cur, num}); cur = new StringBuilder(); num = 0; } //>
                    else if (ch == ']') {
                        Object[] top = stack.pop();
                        StringBuilder prev = (StringBuilder) top[0];
                        prev.append(cur.toString().repeat((Integer) top[1]));
                        cur = prev; //>
                    } else cur.append(ch);
                }
                return cur.toString();
            }
        }
        ''',
    )],
)

problem(
    id="collapse-pairs",
    title="Collapse Adjacent Twins",
    difficulty="Easy",
    topics=["String", "Stack", "Two Pointers"],
    statement="""
    Repeatedly delete two adjacent equal letters from the lowercase string `s` until no such pair remains. Return the
    final string (it is unique).
    """,
    examples=[(["abbaca"], "ca", "Remove \"bb\", then \"aa\"."), (["azxxzy"], "ay", None)],
    tests=[(["a"], "a"), (["aa"], ""), (["abcd"], "abcd")],
    constraints=["1 ≤ s.length ≤ 10^5"],
    hints=["A new letter only ever cancels the letter just before it.", "That's exactly a stack, or a write pointer."],
    approaches=[
        approach(
            name="Two Pointers (write head)", pattern="two-pointers", time="O(n)", space="O(n)",
            idea="""
            Treat the front of a character array as a stack. The write pointer W is its top. Read each character: if it equals the character just below W, cancel the pair by moving W back; otherwise write it at W.
            """,
            viz=viz(arr="res", ptr={"W": "w"}, vars=["ch"]),
            py='''
            def collapse(s):
                res, w = list(s), 0
                for ch in s:
                    if w > 0 and res[w - 1] == ch:
                        w -= 1  #> {q(ch)} cancels the {q(ch)} before it. W steps back to {w}.
                    else:
                        res[w] = ch
                        w += 1  #> Write {q(ch)}. The kept text is {q("".join(res[:w]))}.
                return "".join(res[:w])
            ''',
            java='''
            class Solution {
                public String collapse(String s) {
                    char[] res = s.toCharArray();
                    int w = 0;
                    for (char ch : s.toCharArray()) {
                        if (w > 0 && res[w - 1] == ch) w--; //>
                        else res[w++] = ch; //>
                    }
                    return new String(res, 0, w);
                }
            }
            ''',
        ),
        approach(
            name="Stack", pattern="stack", time="O(n)", space="O(n)",
            idea="""
            Push letters onto a stack; if the incoming letter equals the top, pop instead. What remains, bottom to top, is the answer.
            """,
            viz=viz(arr="s", ptr={"i": "i"}, stacks=["stack"]),
            py='''
            def collapse(s):
                stack = []
                for i, ch in enumerate(s):
                    if stack and stack[-1] == ch:
                        stack.pop()  #> {q(ch)} matches the top, so they cancel.
                    else:
                        stack.append(ch)  #> Push {q(ch)}.
                return "".join(stack)
            ''',
            java='''
            class Solution {
                public String collapse(String s) {
                    StringBuilder stack = new StringBuilder();
                    for (char ch : s.toCharArray()) {
                        int n = stack.length();
                        if (n > 0 && stack.charAt(n - 1) == ch) stack.deleteCharAt(n - 1); //>
                        else stack.append(ch); //>
                    }
                    return stack.toString();
                }
            }
            ''',
        ),
    ],
)

problem(
    id="tidy-path",
    title="Tidy a File Path",
    difficulty="Medium",
    topics=["String", "Stack"],
    statement="""
    Given an absolute Unix-style path, return its simplest form: one `/` between folders, no trailing `/`,
    `.` means the current folder and `..` goes up one level (staying at `/` if already at the root).
    """,
    examples=[(["/home//docs/./../music/"], "/home/music", None), (["/../"], "/", None)],
    tests=[(["/a/./b/../../c/"], "/c"), (["/..."], "/..."), (["/"], "/")],
    constraints=["1 ≤ path.length ≤ 3000"],
    hints=["Split by '/', then use a stack of folder names."],
    approaches=[approach(
        name="Stack", pattern="stack", time="O(n)", space="O(n)",
        idea="""
        Split the path on `/`. Skip empty parts and `.`; for `..` pop the last folder if there is one; anything else is a folder name to push.

        Join the stack with `/` and add a leading slash.
        """,
        viz=viz(stacks=["stack"], vars=["part"]),
        py='''
        def tidy_path(path):
            stack = []
            for part in path.split("/"):
                if part == "..":
                    if stack:
                        stack.pop()  #> {q(part)} goes up one folder.
                elif part and part != ".":
                    stack.append(part)  #> Enter folder {q(part)}.
            return "/" + "/".join(stack)
        ''',
        java='''
        class Solution {
            public String tidyPath(String path) {
                Deque<String> stack = new ArrayDeque<>();
                for (String part : path.split("/")) {
                    if (part.equals("..")) { if (!stack.isEmpty()) stack.pollLast(); } //>
                    else if (!part.isEmpty() && !part.equals(".")) stack.addLast(part); //>
                }
                return "/" + String.join("/", stack);
            }
        }
        ''',
    )],
)

problem(
    id="rock-collisions",
    title="Colliding Rocks",
    difficulty="Medium",
    topics=["Array", "Stack", "Simulation"],
    statement="""
    Rocks move along a line. The size is `|rocks[i]|`; positive moves right, negative moves left, all at the same
    speed. When two meet, the smaller one shatters (both shatter if equal). Return the rocks that remain, in order.
    """,
    examples=[([[5, 10, -5]], [5, 10], "10 destroys −5."), ([[8, -8]], [], None)],
    tests=[([[10, 2, -5]], [10]), ([[-2, -1, 1, 2]], [-2, -1, 1, 2]), ([[1, -2, -2, -2]], [-2, -2, -2])],
    constraints=["2 ≤ rocks.length ≤ 10^4", "no rock has size 0"],
    hints=["Only a right-mover followed by a left-mover can collide.", "Keep survivors on a stack."],
    approaches=[approach(
        name="Stack", pattern="stack", time="O(n)", space="O(n)",
        idea="""
        Survivors wait on a stack. A left-moving rock collides with right-moving rocks on top of the stack: smaller right-movers shatter and are popped; if the top is bigger, the new rock shatters; if equal, both go.

        A rock that survives every collision is pushed.
        """,
        viz=viz(arr="rocks", ptr={"i": "i"}, stacks=[("survivors", "stack")]),
        demo=[[10, 2, -5]],
        py='''
        def collide(rocks):
            stack = []
            for i, r in enumerate(rocks):
                alive = True
                while alive and r < 0 and stack and stack[-1] > 0:
                    if stack[-1] < -r:
                        stack.pop()  #> {r} smashes the smaller rock on top.
                        continue
                    if stack[-1] == -r:
                        stack.pop()  #> Equal sizes: both rocks shatter.
                    alive = False
                if alive:
                    stack.append(r)  #> Rock {r} survives for now.
            return stack
        ''',
        java='''
        class Solution {
            public int[] collide(int[] rocks) {
                Deque<Integer> stack = new ArrayDeque<>();
                for (int r : rocks) {
                    boolean alive = true;
                    while (alive && r < 0 && !stack.isEmpty() && stack.peekLast() > 0) {
                        if (stack.peekLast() < -r) { stack.pollLast(); continue; } //>
                        if (stack.peekLast() == -r) stack.pollLast(); //>
                        alive = false;
                    }
                    if (alive) stack.addLast(r); //>
                }
                return stack.stream().mapToInt(Integer::intValue).toArray();
            }
        }
        ''',
    )],
)

problem(
    id="convoy-count",
    title="How Many Convoys Arrive",
    difficulty="Medium",
    topics=["Array", "Stack", "Sorting"],
    statement="""
    Cars drive toward a destination at mile `target`. Car `i` starts at `position[i]` with constant `speed[i]`.
    A faster car that catches a slower one ahead joins it and moves at the slower speed, forming a convoy. A convoy
    meeting exactly at the destination still counts as one. Return the number of convoys that arrive.
    """,
    examples=[([12, [10, 8, 0, 5, 3], [2, 4, 1, 1, 3]], 3, None), ([10, [3], [3]], 1, None)],
    tests=[([100, [0, 2, 4], [4, 2, 1]], 1), ([10, [6, 8], [3, 2]], 2)],
    constraints=["1 ≤ n ≤ 10^5", "positions are distinct"],
    hints=["Process cars from closest to the destination.", "Compare arrival times."],
    approaches=[approach(
        name="Sort + Stack", pattern="stack", time="O(n log n)", space="O(n)",
        idea="""
        Sort cars by position, closest to the destination first, and compute each car's arrival time if it drove alone.

        A car that would arrive no later than the convoy ahead of it catches up and merges. Otherwise it starts a new convoy; keep the convoys' arrival times on a stack.
        """,
        viz=viz(stacks=[("convoy arrival times", "stack")], vars=["t"]),
        py='''
        def convoys(target, position, speed):
            stack = []
            for p, s in sorted(zip(position, speed), reverse=True):
                t = (target - p) / s
                if not stack or t > stack[-1]:
                    stack.append(t)  #> The car at mile {p} needs {fv(t)} hours, slower than the convoy ahead: a new convoy.
            return len(stack)
        ''',
        java='''
        class Solution {
            public int convoys(int target, int[] position, int[] speed) {
                int n = position.length;
                Integer[] idx = new Integer[n];
                for (int i = 0; i < n; i++) idx[i] = i;
                Arrays.sort(idx, (a, b) -> position[b] - position[a]);
                Deque<Double> stack = new ArrayDeque<>();
                for (int i : idx) {
                    double t = (double) (target - position[i]) / speed[i];
                    if (stack.isEmpty() || t > stack.peek()) stack.push(t); //>
                }
                return stack.size();
            }
        }
        ''',
    )],
)
