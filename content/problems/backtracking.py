"""Backtracking problems (original statements)."""
from dsl import problem, approach, viz

problem(
    id="all-subsets",
    title="Every Subset",
    difficulty="Medium",
    topics=["Array", "Backtracking"],
    statement="""
    `nums` has distinct integers. Return every possible subset (the power set), in any order, with no duplicates.
    """,
    examples=[([[1, 2, 3]], [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]], None), ([[0]], [[], [0]], None)],
    tests=[([[]], [[]]), ([[5, 9]], [[], [5], [9], [5, 9]])],
    check="deep-unordered",
    constraints=["0 ≤ nums.length ≤ 10"],
    hints=["Each element is either in or out.", "Choose, explore, un-choose."],
    approaches=[approach(
        name="Backtracking", pattern="backtracking", time="O(n · 2ⁿ)", space="O(n)",
        idea="""
        Build subsets one decision at a time. At each step record the current subset, then try adding each remaining element, explore deeper, and remove it again (backtrack) before trying the next one.
        """,
        viz=viz(arr="nums", ptr={"start": "start"}, out=("current", "path")),
        demo=[[1, 2, 3]],
        py='''
        def subsets(nums):
            res, path = [], []

            def explore(start):
                res.append(path[:])  #> Record the subset {path}.
                for i in range(start, len(nums)):
                    path.append(nums[i])
                    explore(i + 1)
                    path.pop()

            explore(0)
            return res
        ''',
        java='''
        class Solution {
            public List<List<Integer>> subsets(int[] nums) {
                List<List<Integer>> res = new ArrayList<>();
                explore(nums, 0, new ArrayList<>(), res);
                return res;
            }

            private void explore(int[] nums, int start, List<Integer> path, List<List<Integer>> res) {
                res.add(new ArrayList<>(path)); //>
                for (int i = start; i < nums.length; i++) {
                    path.add(nums[i]);
                    explore(nums, i + 1, path, res);
                    path.remove(path.size() - 1);
                }
            }
        }
        ''',
    )],
)

problem(
    id="all-orderings",
    title="Every Ordering",
    difficulty="Medium",
    topics=["Array", "Backtracking"],
    statement="""
    `nums` has distinct integers. Return every permutation (ordering) of `nums`, in any order.
    """,
    examples=[([[1, 2, 3]], [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]], None), ([[0, 1]], [[0, 1], [1, 0]], None)],
    tests=[([[1]], [[1]])],
    check="unordered",
    constraints=["1 ≤ nums.length ≤ 6"],
    hints=["Fill positions left to right with numbers not used yet."],
    approaches=[approach(
        name="Backtracking with Swaps", pattern="backtracking", time="O(n · n!)", space="O(n)",
        idea="""
        Fix one position at a time. For position `first`, swap each candidate from the rest of the array into place, recurse on the next position, then swap it back. When all positions are fixed, record the ordering.
        """,
        viz=viz(arr="nums", ptr={"first": "first", "i": "i"}),
        demo=[[1, 2, 3]],
        py='''
        def permutations(nums):
            res = []

            def place(first):
                if first == len(nums):
                    res.append(nums[:])  #> Every position is fixed: record {nums}.
                    return
                for i in range(first, len(nums)):
                    nums[first], nums[i] = nums[i], nums[first]
                    place(first + 1)
                    nums[first], nums[i] = nums[i], nums[first]

            place(0)
            return res
        ''',
        java='''
        class Solution {
            public List<List<Integer>> permutations(int[] nums) {
                List<List<Integer>> res = new ArrayList<>();
                place(nums, 0, res);
                return res;
            }

            private void place(int[] nums, int first, List<List<Integer>> res) {
                if (first == nums.length) {
                    List<Integer> p = new ArrayList<>();
                    for (int x : nums) p.add(x);
                    res.add(p); //>
                    return;
                }
                for (int i = first; i < nums.length; i++) {
                    int t = nums[first]; nums[first] = nums[i]; nums[i] = t;
                    place(nums, first + 1, res);
                    t = nums[first]; nums[first] = nums[i]; nums[i] = t;
                }
            }
        }
        ''',
    )],
)

problem(
    id="combination-target",
    title="Combinations Reaching a Target",
    difficulty="Medium",
    topics=["Array", "Backtracking"],
    statement="""
    `candidates` are distinct positive integers. Return every unique combination that sums to `target`, where each
    candidate may be used any number of times. Order inside a combination doesn't matter.
    """,
    examples=[([[2, 3, 6, 7], 7], [[2, 2, 3], [7]], None), ([[2, 3, 5], 8], [[2, 2, 2, 2], [2, 3, 3], [3, 5]], None)],
    tests=[([[2], 1], []), ([[1], 2], [[1, 1]])],
    check="deep-unordered",
    constraints=["1 ≤ candidates.length ≤ 30", "1 ≤ target ≤ 40"],
    hints=["To avoid duplicates, only reuse candidates from the current index onward."],
    approaches=[approach(
        name="Backtracking", pattern="backtracking", time="O(n^(t/min))", space="O(t/min)",
        idea="""
        Pick candidates in non-decreasing index order so each combination is built exactly once. Keep subtracting from the remaining target; at zero record the combination, below zero stop exploring that branch.
        """,
        viz=viz(out=("current", "path"), vars=["remaining"]),
        demo=[[2, 3, 6, 7], 7],
        py='''
        def combinations(candidates, target):
            res, path = [], []

            def explore(start, remaining):
                if remaining == 0:
                    res.append(path[:])  #> {path} adds up exactly. Record it.
                    return
                for i in range(start, len(candidates)):
                    if candidates[i] <= remaining:
                        path.append(candidates[i])
                        explore(i, remaining - candidates[i])
                        path.pop()

            explore(0, target)
            return res
        ''',
        java='''
        class Solution {
            public List<List<Integer>> combinations(int[] candidates, int target) {
                List<List<Integer>> res = new ArrayList<>();
                explore(candidates, 0, target, new ArrayList<>(), res);
                return res;
            }

            private void explore(int[] c, int start, int remaining, List<Integer> path, List<List<Integer>> res) {
                if (remaining == 0) { res.add(new ArrayList<>(path)); return; } //>
                for (int i = start; i < c.length; i++) {
                    if (c[i] > remaining) continue;
                    path.add(c[i]);
                    explore(c, i, remaining - c[i], path, res);
                    path.remove(path.size() - 1);
                }
            }
        }
        ''',
    )],
)

problem(
    id="balanced-parentheses",
    title="Every Balanced Bracket String",
    difficulty="Medium",
    topics=["String", "Backtracking"],
    statement="""
    Return every string made of `n` pairs of parentheses that is correctly balanced, in any order.
    """,
    examples=[([3], ["((()))", "(()())", "(())()", "()(())", "()()()"], None), ([1], ["()"], None)],
    tests=[([2], ["(())", "()()"])],
    check="unordered",
    constraints=["1 ≤ n ≤ 8"],
    hints=["You may open while opens < n, and close while closes < opens."],
    approaches=[approach(
        name="Backtracking With Counts", pattern="backtracking", time="O(4ⁿ / √n)", space="O(n)",
        idea="""
        Build the string left to right. You may add `(` while fewer than n are open, and `)` only while it closes an unmatched `(`. Those two rules generate exactly the balanced strings.
        """,
        viz=viz(vars=["path", "opened", "closed"]),
        demo=[2],
        py='''
        def balanced(n):
            res = []

            def build(path, opened, closed):
                if len(path) == 2 * n:
                    res.append(path)  #> {q(path)} is complete and balanced.
                    return
                if opened < n:
                    build(path + "(", opened + 1, closed)
                if closed < opened:
                    build(path + ")", opened, closed + 1)

            build("", 0, 0)
            return res
        ''',
        java='''
        class Solution {
            public List<String> balanced(int n) {
                List<String> res = new ArrayList<>();
                build("", 0, 0, n, res);
                return res;
            }

            private void build(String path, int opened, int closed, int n, List<String> res) {
                if (path.length() == 2 * n) { res.add(path); return; } //>
                if (opened < n) build(path + "(", opened + 1, closed, n, res);
                if (closed < opened) build(path + ")", opened, closed + 1, n, res);
            }
        }
        ''',
    )],
)

problem(
    id="phone-letters",
    title="Letters From Phone Digits",
    difficulty="Medium",
    topics=["String", "Backtracking"],
    statement="""
    On a phone keypad 2→abc, 3→def, 4→ghi, 5→jkl, 6→mno, 7→pqrs, 8→tuv, 9→wxyz. Given `digits` (2–9), return every
    letter string they could spell, in any order (empty input gives an empty list).
    """,
    examples=[(["23"], ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"], None), ([""], [], None)],
    tests=[(["2"], ["a", "b", "c"]), (["79"], [a + b for a in "pqrs" for b in "wxyz"])],
    check="unordered",
    constraints=["0 ≤ digits.length ≤ 4"],
    hints=["One level of recursion per digit."],
    approaches=[approach(
        name="Backtracking", pattern="backtracking", time="O(4ⁿ · n)", space="O(n)",
        idea="""
        Handle one digit per level: for each letter of the current digit, append it and recurse into the next digit. When every digit has a letter, record the word.
        """,
        viz=viz(vars=["path", "i"]),
        demo=["23"],
        py='''
        def letter_combos(digits):
            keys = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}
            res = []

            def build(i, path):
                if i == len(digits):
                    res.append(path)  #> Spelled {q(path)}.
                    return
                for ch in keys[digits[i]]:
                    build(i + 1, path + ch)

            if digits:
                build(0, "")
            return res
        ''',
        java='''
        class Solution {
            private static final String[] KEYS = {"", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"};

            public List<String> letterCombos(String digits) {
                List<String> res = new ArrayList<>();
                if (!digits.isEmpty()) build(digits, 0, "", res);
                return res;
            }

            private void build(String digits, int i, String path, List<String> res) {
                if (i == digits.length()) { res.add(path); return; } //>
                for (char ch : KEYS[digits.charAt(i) - '0'].toCharArray()) build(digits, i + 1, path + ch, res);
            }
        }
        ''',
    )],
)

problem(
    id="grid-word-search",
    title="Find a Word in a Letter Grid",
    difficulty="Medium",
    topics=["Matrix", "Backtracking", "DFS"],
    statement="""
    Return `true` if `word` can be traced in `board` through horizontally or vertically adjacent cells, using each
    cell at most once.
    """,
    examples=[([[["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCCED"], True, None),
              ([[["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCB"], False, "The B can't be reused.")],
    tests=[([[["a"]], "a"], True), ([[["a", "b"], ["c", "d"]], "abdc"], True)],
    constraints=["1 ≤ m, n ≤ 6", "1 ≤ word.length ≤ 15"],
    hints=["Try every starting cell.", "Mark a cell as used while exploring from it, then unmark it."],
    approaches=[approach(
        name="DFS Backtracking", pattern="backtracking", time="O(m · n · 4^L)", space="O(L)",
        idea="""
        From each cell that matches the first letter, explore neighbours that match the next letter. Temporarily mark the current cell as used so the path never revisits it, and restore it when you backtrack.
        """,
        viz=viz(grid=("board", {"at": ("r", "c")}), vars=["k"]),
        py='''
        def word_search(board, word):
            m, n = len(board), len(board[0])

            def dfs(r, c, k):
                if k == len(word):
                    return True
                if not (0 <= r < m and 0 <= c < n) or board[r][c] != word[k]:
                    return False
                board[r][c] = "#"  #> Row {r}, column {c} matches letter {k + 1}, {q(word[k])}. Mark it used.
                found = dfs(r + 1, c, k + 1) or dfs(r - 1, c, k + 1) or dfs(r, c + 1, k + 1) or dfs(r, c - 1, k + 1)
                board[r][c] = word[k]
                return found

            return any(dfs(r, c, 0) for r in range(m) for c in range(n))
        ''',
        java='''
        class Solution {
            public boolean wordSearch(char[][] board, String word) {
                for (int r = 0; r < board.length; r++)
                    for (int c = 0; c < board[0].length; c++)
                        if (dfs(board, word, r, c, 0)) return true;
                return false;
            }

            private boolean dfs(char[][] b, String w, int r, int c, int k) {
                if (k == w.length()) return true;
                if (r < 0 || c < 0 || r >= b.length || c >= b[0].length || b[r][c] != w.charAt(k)) return false;
                b[r][c] = '#'; //>
                boolean found = dfs(b, w, r + 1, c, k + 1) || dfs(b, w, r - 1, c, k + 1) || dfs(b, w, r, c + 1, k + 1) || dfs(b, w, r, c - 1, k + 1);
                b[r][c] = w.charAt(k);
                return found;
            }
        }
        ''',
    )],
)

problem(
    id="queens-count",
    title="Peaceful Queens",
    difficulty="Hard",
    topics=["Backtracking"],
    statement="""
    Count the ways to place `n` queens on an `n × n` chessboard so that no two attack each other (no shared row,
    column or diagonal).
    """,
    examples=[([4], 2, None), ([1], 1, None)],
    tests=[([2], 0), ([6], 4), ([8], 92)],
    constraints=["1 ≤ n ≤ 9"],
    hints=["Place one queen per row.", "Track used columns and both diagonal directions in sets."],
    approaches=[approach(
        name="Row-by-Row Backtracking", pattern="backtracking", time="O(n!)", space="O(n)",
        idea="""
        Put exactly one queen in each row. For row r, try every column whose column, `r − c` diagonal and `r + c` anti-diagonal are all free. Record them, recurse to the next row, and free them on the way back.
        """,
        viz=viz(vars=["row", "count"], maps=[("columns used", "cols")]),
        demo=[4],
        py='''
        def count_queens(n):
            cols, diag, anti = set(), set(), set()
            count = 0

            def place(row):
                nonlocal count
                if row == n:
                    count += 1  #> All {n} queens placed safely: solution {count}.
                    return
                for c in range(n):
                    if c in cols or row - c in diag or row + c in anti:
                        continue
                    cols.add(c), diag.add(row - c), anti.add(row + c)
                    place(row + 1)
                    cols.remove(c), diag.remove(row - c), anti.remove(row + c)

            place(0)
            return count
        ''',
        java='''
        class Solution {
            private int count;

            public int countQueens(int n) {
                count = 0;
                place(0, n, new boolean[n], new boolean[2 * n], new boolean[2 * n]);
                return count;
            }

            private void place(int row, int n, boolean[] cols, boolean[] diag, boolean[] anti) {
                if (row == n) { count++; return; } //>
                for (int c = 0; c < n; c++) {
                    if (cols[c] || diag[row - c + n] || anti[row + c]) continue;
                    cols[c] = diag[row - c + n] = anti[row + c] = true;
                    place(row + 1, n, cols, diag, anti);
                    cols[c] = diag[row - c + n] = anti[row + c] = false;
                }
            }
        }
        ''',
    )],
)
