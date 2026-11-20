"""Matrix problems (original statements)."""
from dsl import problem, approach, viz

problem(
    id="rotate-square",
    title="Rotate an Image a Quarter Turn",
    difficulty="Medium",
    topics=["Matrix", "Two Pointers", "Math"],
    statement="""
    Rotate the `n × n` matrix 90 degrees clockwise **in place**.
    """,
    examples=[([[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], [[7, 4, 1], [8, 5, 2], [9, 6, 3]], None), ([[[1]]], [[1]], None)],
    tests=[([[[1, 2], [3, 4]]], [[3, 1], [4, 2]])],
    out="arg0",
    constraints=["1 ≤ n ≤ 20"],
    hints=["Transpose (swap across the diagonal), then reverse each row."],
    approaches=[approach(
        name="Transpose + Reverse Rows", pattern="two-pointers", time="O(n²)", space="O(1)",
        idea="""
        Swap every element across the main diagonal (rows become columns). Then reverse each row with two pointers. Together these two flips equal a clockwise quarter turn.
        """,
        viz=viz(grid=("m", {"cell": ("i", "j")}, None, "matrix")),
        demo=[[[1, 2, 3], [4, 5, 6], [7, 8, 9]]],
        py='''
        def rotate_square(m):
            n = len(m)
            for i in range(n):
                for j in range(i + 1, n):
                    m[i][j], m[j][i] = m[j][i], m[i][j]  #> Swap across the diagonal: positions ({i}, {j}) and ({j}, {i}).
            for row in m:
                row.reverse()
        ''',
        java='''
        class Solution {
            public void rotateSquare(int[][] m) {
                int n = m.length;
                for (int i = 0; i < n; i++)
                    for (int j = i + 1; j < n; j++) { int t = m[i][j]; m[i][j] = m[j][i]; m[j][i] = t; } //>
                for (int[] row : m)
                    for (int left = 0, right = n - 1; left < right; left++, right--) { int t = row[left]; row[left] = row[right]; row[right] = t; }
            }
        }
        ''',
    )],
)

problem(
    id="spiral-read",
    title="Read a Matrix in a Spiral",
    difficulty="Medium",
    topics=["Matrix", "Simulation"],
    statement="""
    Return all elements of the `m × n` matrix in clockwise spiral order, starting at the top-left.
    """,
    examples=[([[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], [1, 2, 3, 6, 9, 8, 7, 4, 5], None), ([[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]], [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7], None)],
    tests=[([[[7]]], [7]), ([[[1], [2], [3]]], [1, 2, 3])],
    constraints=["1 ≤ m, n ≤ 10"],
    hints=["Keep four boundaries: top, bottom, left, right. Shrink one after each edge."],
    approaches=[approach(
        name="Four Shrinking Boundaries", pattern="matrix", time="O(m · n)", space="O(1) extra",
        idea="""
        Keep four pointers: top, bottom, left and right. Read the top row left to right, then the right column downwards, then the bottom row right to left, then the left column upwards. Each edge read moves its boundary inward.
        """,
        viz=viz(grid=("matrix", {}), vars=["top", "bottom", "left", "right"], out="res"),
        py='''
        def spiral(matrix):
            res = []
            top, bottom, left, right = 0, len(matrix) - 1, 0, len(matrix[0]) - 1
            while top <= bottom and left <= right:
                res += [matrix[top][c] for c in range(left, right + 1)]
                top += 1  #> Read the top row. The top boundary moves down to {top}.
                res += [matrix[r][right] for r in range(top, bottom + 1)]
                right -= 1  #> Read the right column. The right boundary moves to {right}.
                if top <= bottom:
                    res += [matrix[bottom][c] for c in range(right, left - 1, -1)]
                    bottom -= 1  #> Read the bottom row backwards. The bottom boundary moves up to {bottom}.
                if left <= right:
                    res += [matrix[r][left] for r in range(bottom, top - 1, -1)]
                    left += 1  #> Read the left column upwards. The left boundary moves to {left}.
            return res
        ''',
        java='''
        class Solution {
            public List<Integer> spiral(int[][] matrix) {
                List<Integer> res = new ArrayList<>();
                int top = 0, bottom = matrix.length - 1, left = 0, right = matrix[0].length - 1;
                while (top <= bottom && left <= right) {
                    for (int c = left; c <= right; c++) res.add(matrix[top][c]);
                    top++; //>
                    for (int r = top; r <= bottom; r++) res.add(matrix[r][right]);
                    right--; //>
                    if (top <= bottom) { for (int c = right; c >= left; c--) res.add(matrix[bottom][c]); bottom--; } //>
                    if (left <= right) { for (int r = bottom; r >= top; r--) res.add(matrix[r][left]); left++; } //>
                }
                return res;
            }
        }
        ''',
    )],
)

problem(
    id="zero-rows-columns",
    title="Spread Zeros to Rows and Columns",
    difficulty="Medium",
    topics=["Matrix", "Hash Set"],
    statement="""
    If an element of the matrix is 0, set its whole row and column to 0. Do it **in place** with O(1) extra memory.
    """,
    examples=[([[[1, 1, 1], [1, 0, 1], [1, 1, 1]]], [[1, 0, 1], [0, 0, 0], [1, 0, 1]], None),
              ([[[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]], [[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]], None)],
    tests=[([[[1]]], [[1]]), ([[[1, 0]]], [[0, 0]])],
    out="arg0",
    constraints=["1 ≤ m, n ≤ 200"],
    hints=["Use the first row and column as markers.", "Remember separately whether the first row/column themselves had a zero."],
    approaches=[approach(
        name="First Row and Column as Markers", pattern="matrix", time="O(m · n)", space="O(1)",
        idea="""
        Use the first cell of each row and column as a "this line must become zero" flag. Remember separately whether the first row and first column contained a zero themselves.

        Then zero cells by checking their row and column flags, and finally handle the first row and column.
        """,
        viz=viz(grid=("m", {}, None, "matrix")),
        demo=[[[1, 2, 3], [4, 0, 6], [7, 8, 9]]],
        py='''
        def set_zeros(m):
            rows, cols = len(m), len(m[0])
            first_row = any(v == 0 for v in m[0])
            first_col = any(m[r][0] == 0 for r in range(rows))
            for r in range(1, rows):
                for c in range(1, cols):
                    if m[r][c] == 0:
                        m[r][0] = m[0][c] = 0  #> A zero at ({r}, {c}) flags row {r} and column {c}.
            for r in range(1, rows):
                for c in range(1, cols):
                    if m[r][0] == 0 or m[0][c] == 0:
                        m[r][c] = 0  #> Row {r} or column {c} is flagged, so cell ({r}, {c}) becomes 0.
            if first_row:
                m[0] = [0] * cols
            if first_col:
                for r in range(rows):
                    m[r][0] = 0
        ''',
        java='''
        class Solution {
            public void setZeros(int[][] m) {
                int rows = m.length, cols = m[0].length;
                boolean firstRow = false, firstCol = false;
                for (int c = 0; c < cols; c++) if (m[0][c] == 0) firstRow = true;
                for (int r = 0; r < rows; r++) if (m[r][0] == 0) firstCol = true;
                for (int r = 1; r < rows; r++)
                    for (int c = 1; c < cols; c++) if (m[r][c] == 0) { m[r][0] = 0; m[0][c] = 0; } //>
                for (int r = 1; r < rows; r++)
                    for (int c = 1; c < cols; c++) if (m[r][0] == 0 || m[0][c] == 0) m[r][c] = 0; //>
                if (firstRow) Arrays.fill(m[0], 0);
                if (firstCol) for (int r = 0; r < rows; r++) m[r][0] = 0;
            }
        }
        ''',
    )],
)

problem(
    id="staircase-search",
    title="Search a Row- and Column-Sorted Grid",
    difficulty="Medium",
    topics=["Matrix", "Two Pointers", "Binary Search"],
    patterns=["two-pointers"],
    statement="""
    Every row of `grid` is sorted left to right and every column top to bottom. Return `true` if `target` is in it.
    """,
    examples=[([[[1, 4, 7, 11], [2, 5, 8, 12], [3, 6, 9, 16], [10, 13, 14, 17]], 5], True, None),
              ([[[1, 4, 7, 11], [2, 5, 8, 12], [3, 6, 9, 16], [10, 13, 14, 17]], 15], False, None)],
    tests=[([[[1]], 1], True), ([[[1, 2], [3, 4]], 0], False)],
    constraints=["1 ≤ m, n ≤ 300"],
    hints=["Start at the top-right corner: left is smaller, down is bigger."],
    approaches=[approach(
        name="Staircase Walk (two pointers)", pattern="two-pointers", time="O(m + n)", space="O(1)",
        idea="""
        Start at the top-right corner with a row pointer and a column pointer. Everything to the left is smaller and everything below is bigger. If the value is too big, move left; if too small, move down. Each step rules out a whole row or column.
        """,
        viz=viz(grid=("grid", {"at": ("r", "c")}), vars=["target"]),
        py='''
        def staircase_search(grid, target):
            r, c = 0, len(grid[0]) - 1
            while r < len(grid) and c >= 0:
                if grid[r][c] == target:
                    return True  #> Found {target}!
                if grid[r][c] > target:
                    c -= 1  #> {grid[r][c + 1]} is too big, so step left.
                else:
                    r += 1  #> {grid[r - 1][c]} is too small, so step down.
            return False
        ''',
        java='''
        class Solution {
            public boolean staircaseSearch(int[][] grid, int target) {
                int r = 0, c = grid[0].length - 1;
                while (r < grid.length && c >= 0) {
                    if (grid[r][c] == target) return true; //>
                    if (grid[r][c] > target) c--; //>
                    else r++; //>
                }
                return false;
            }
        }
        ''',
    )],
)
