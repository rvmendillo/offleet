"""Binary Tree problems (original statements). TreeNode has val, left, right; trees are given in level order."""
from dsl import problem, approach, viz

T = "ARGS['root']"

problem(
    id="tree-depth",
    title="How Deep Is the Tree?",
    difficulty="Easy",
    topics=["Tree", "DFS", "Recursion"],
    statement="""
    Return the maximum depth of a binary tree: the number of nodes on the longest path from the root down to a leaf.
    """,
    examples=[([[3, 9, 20, None, None, 15, 7]], 3, None), ([[1, None, 2]], 2, None)],
    tests=[([[]], 0), ([[1]], 1), ([[1, 2, None, 3, None, 4]], 4)],
    constraints=["0 ≤ number of nodes ≤ 10^4"],
    hints=["A tree's depth is 1 + the deeper of its two subtrees."],
    approaches=[approach(
        name="Recursive DFS", pattern="tree", time="O(n)", space="O(h)",
        idea="""
        An empty tree has depth 0. Otherwise a node's depth is one more than the deeper of its left and right subtrees.

        Recursion asks each child the same question and combines the answers on the way back up.
        """,
        why="Every node is visited once; the call stack is as deep as the tree's height h.",
        viz=viz(tree=(T, {"node": "root"})),
        py='''
        def max_depth(root):
            if not root:
                return 0
            left, right = max_depth(root.left), max_depth(root.right)
            return 1 + max(left, right)  #> Node {root.val}: left depth {left}, right depth {right}, so its depth is {ret}.
        ''',
        java='''
        class Solution {
            public int maxDepth(TreeNode root) {
                if (root == null) return 0;
                return 1 + Math.max(maxDepth(root.left), maxDepth(root.right)); //>
            }
        }
        ''',
    )],
)

problem(
    id="mirror-tree",
    title="Mirror a Binary Tree",
    difficulty="Easy",
    topics=["Tree", "DFS", "Recursion"],
    statement="""
    Mirror the tree: swap the left and right children of every node. Return the root.
    """,
    examples=[([[4, 2, 7, 1, 3, 6, 9]], [4, 7, 2, 9, 6, 3, 1], None), ([[2, 1, 3]], [2, 3, 1], None)],
    tests=[([[]], []), ([[1, 2]], [1, None, 2])],
    constraints=["0 ≤ number of nodes ≤ 100"],
    hints=["Mirror both subtrees, then swap them."],
    approaches=[approach(
        name="Recursive DFS", pattern="tree", time="O(n)", space="O(h)",
        idea="""
        To mirror a tree, mirror its left and right subtrees and then swap them. The recursion bottoms out at empty children.
        """,
        viz=viz(tree=(T, {"node": "root"})),
        py='''
        def mirror(root):
            if root:
                root.left, root.right = mirror(root.right), mirror(root.left)  #>^ Swap the children of node {root.val}.
            return root
        ''',
        java='''
        class Solution {
            public TreeNode mirror(TreeNode root) {
                if (root == null) return null;
                TreeNode l = mirror(root.left);
                root.left = mirror(root.right);
                root.right = l; //>
                return root;
            }
        }
        ''',
    )],
)

problem(
    id="same-tree",
    title="Are Two Trees Identical?",
    difficulty="Easy",
    topics=["Tree", "DFS", "Two Pointers"],
    statement="""
    Return `true` if trees `a` and `b` have the same shape and the same values in the same places.
    """,
    examples=[([[1, 2, 3], [1, 2, 3]], True, None), ([[1, 2], [1, None, 2]], False, None)],
    tests=[([[], []], True), ([[1, 2, 1], [1, 1, 2]], False), ([[5], []], False)],
    constraints=["0 ≤ number of nodes ≤ 100"],
    hints=["Walk both trees together with one pointer in each."],
    approaches=[approach(
        name="Paired DFS (two pointers)", pattern="tree", time="O(n)", space="O(h)",
        idea="""
        Move a pointer through each tree in lockstep. At every step both must be empty, or both must hold the same value with identical left and right subtrees.
        """,
        viz=viz(tree=("ARGS['a']", {"a": "a"})),
        py='''
        def same_tree(a, b):
            if not a or not b:
                return a is b
            return a.val == b.val and same_tree(a.left, b.left) and same_tree(a.right, b.right)  #> Compare {a.val} with {b.val}.
        ''',
        java='''
        class Solution {
            public boolean sameTree(TreeNode a, TreeNode b) {
                if (a == null || b == null) return a == b;
                return a.val == b.val && sameTree(a.left, b.left) && sameTree(a.right, b.right); //>
            }
        }
        ''',
    )],
)

problem(
    id="symmetric-tree",
    title="Is the Tree Symmetric?",
    difficulty="Easy",
    topics=["Tree", "DFS", "Two Pointers"],
    patterns=["two-pointers"],
    statement="""
    Return `true` if the tree is a mirror image of itself around its center.
    """,
    examples=[([[1, 2, 2, 3, 4, 4, 3]], True, None), ([[1, 2, 2, None, 3, None, 3]], False, None)],
    tests=[([[1]], True), ([[1, 2, 3]], False)],
    constraints=["1 ≤ number of nodes ≤ 1000"],
    hints=["Compare the left subtree with the mirror of the right subtree.", "Use two pointers that move in opposite directions."],
    approaches=[approach(
        name="Mirrored Two Pointers", pattern="tree", time="O(n)", space="O(h)",
        idea="""
        Use two pointers, one walking the left half and one the right half in mirror order. The outer pair (left.left, right.right) and the inner pair (left.right, right.left) must match at every level.
        """,
        viz=viz(tree=("root", {"a": "a", "b": "b"})),
        py='''
        def is_symmetric(root):
            def mirror(a, b):
                if not a or not b:
                    return a is b
                return a.val == b.val and mirror(a.left, b.right) and mirror(a.right, b.left)  #> Compare {a.val} with its mirror {b.val}.
            return mirror(root.left, root.right)
        ''',
        java='''
        class Solution {
            public boolean isSymmetric(TreeNode root) {
                return mirror(root.left, root.right);
            }

            private boolean mirror(TreeNode a, TreeNode b) {
                if (a == null || b == null) return a == b;
                return a.val == b.val && mirror(a.left, b.right) && mirror(a.right, b.left); //>
            }
        }
        ''',
    )],
)

problem(
    id="level-by-level",
    title="Read a Tree Level by Level",
    difficulty="Medium",
    topics=["Tree", "BFS", "Queue"],
    statement="""
    Return the node values grouped by level, from top to bottom and left to right within each level.
    """,
    examples=[([[3, 9, 20, None, None, 15, 7]], [[3], [9, 20], [15, 7]], None), ([[1]], [[1]], None)],
    tests=[([[]], []), ([[1, 2, 3, 4, None, None, 5]], [[1], [2, 3], [4, 5]])],
    constraints=["0 ≤ number of nodes ≤ 2000"],
    hints=["A queue processes nodes in the order they were discovered.", "Handle one whole level per round."],
    approaches=[approach(
        name="BFS with a Queue", pattern="tree", time="O(n)", space="O(n)",
        idea="""
        Put the root in a queue. Each round, the queue holds exactly one level: pop that many nodes, record their values, and push their children for the next round.
        """,
        viz=viz(tree=("root", {"node": "node"}), queues=[("queue", "[n.val for n in q]")], out="res"),
        py='''
        from collections import deque

        def levels(root):
            res, q = [], deque([root] if root else [])
            while q:
                level = []
                for _ in range(len(q)):
                    node = q.popleft()
                    level.append(node.val)
                    q.extend(c for c in (node.left, node.right) if c)
                res.append(level)  #> Level {len(res)} holds {level}.
            return res
        ''',
        java='''
        class Solution {
            public List<List<Integer>> levels(TreeNode root) {
                List<List<Integer>> res = new ArrayList<>();
                Deque<TreeNode> q = new ArrayDeque<>();
                if (root != null) q.add(root);
                while (!q.isEmpty()) {
                    List<Integer> level = new ArrayList<>();
                    for (int n = q.size(); n > 0; n--) {
                        TreeNode node = q.poll();
                        level.add(node.val);
                        if (node.left != null) q.add(node.left);
                        if (node.right != null) q.add(node.right);
                    }
                    res.add(level); //>
                }
                return res;
            }
        }
        ''',
    )],
)

problem(
    id="valid-search-tree",
    title="Is It a Valid Search Tree?",
    difficulty="Medium",
    topics=["Tree", "DFS", "Binary Search Tree"],
    statement="""
    A binary search tree keeps every value in a node's left subtree strictly smaller than the node, and every value in
    its right subtree strictly larger. Return `true` if the tree satisfies this everywhere.
    """,
    examples=[([[2, 1, 3]], True, None), ([[5, 1, 4, None, None, 3, 6]], False, "4 sits in the right subtree of 5.")],
    tests=[([[1, 1]], False), ([[5, 4, 6, None, None, 3, 7]], False), ([[-2147483648]], True)],
    constraints=["1 ≤ number of nodes ≤ 10^4", "values fit in a 32-bit int"],
    hints=["Checking only a node's direct children is not enough.", "Pass down the allowed (low, high) range."],
    approaches=[approach(
        name="DFS with Bounds", pattern="tree", time="O(n)", space="O(h)",
        idea="""
        Every node must lie strictly inside a range inherited from its ancestors. The root may be anything; going left tightens the upper bound to the parent's value, going right tightens the lower bound.
        """,
        viz=viz(tree=(T, {"node": "root"})),
        py='''
        def is_valid_bst(root, lo=float("-inf"), hi=float("inf")):
            if not root:
                return True
            if not lo < root.val < hi:
                return False  #> {root.val} breaks its allowed range ({fv(lo)}, {fv(hi)}).
            return is_valid_bst(root.left, lo, root.val) and is_valid_bst(root.right, root.val, hi)  #> {root.val} fits between {fv(lo)} and {fv(hi)}.
        ''',
        java='''
        class Solution {
            public boolean isValidBst(TreeNode root) {
                return valid(root, Long.MIN_VALUE, Long.MAX_VALUE);
            }

            private boolean valid(TreeNode node, long lo, long hi) {
                if (node == null) return true;
                if (node.val <= lo || node.val >= hi) return false; //>1
                return valid(node.left, lo, node.val) && valid(node.right, node.val, hi); //>2
            }
        }
        ''',
    )],
)

problem(
    id="bst-split-point",
    title="Lowest Common Ancestor in a Search Tree",
    difficulty="Medium",
    topics=["Tree", "Binary Search Tree"],
    statement="""
    Given a binary search tree and two values `p` and `q` that both exist in it, return the value of their lowest
    common ancestor: the deepest node that has both in its subtree (a node counts as its own ancestor).
    """,
    examples=[([[6, 2, 8, 0, 4, 7, 9, None, None, 3, 5], 2, 8], 6, None), ([[6, 2, 8, 0, 4, 7, 9, None, None, 3, 5], 2, 4], 2, None)],
    tests=[([[2, 1], 2, 1], 2), ([[6, 2, 8, 0, 4, 7, 9], 7, 9], 8)],
    constraints=["2 ≤ number of nodes ≤ 10^5", "values are distinct"],
    hints=["If both values are smaller than the node, the answer is on the left."],
    approaches=[approach(
        name="Walk Down the Search Tree", pattern="tree", time="O(h)", space="O(1)",
        idea="""
        Start at the root. If both values are smaller, the split happens in the left subtree; if both are bigger, in the right. Otherwise this node is where the paths to p and q split, so it is the answer.
        """,
        viz=viz(tree=("root", {"node": "node"})),
        demo=[[6, 2, 8, 0, 4, 7, 9, None, None, 3, 5], 3, 5],
        py='''
        def common_ancestor(root, p, q):
            node = root
            while True:
                if p < node.val and q < node.val:
                    node = node.left  #> Both values are smaller, so go left to {node.val}.
                elif p > node.val and q > node.val:
                    node = node.right  #> Both values are bigger, so go right to {node.val}.
                else:
                    return node.val  #> {p} and {q} split here, at {node.val}.
        ''',
        java='''
        class Solution {
            public int commonAncestor(TreeNode root, int p, int q) {
                TreeNode node = root;
                while (true) {
                    if (p < node.val && q < node.val) node = node.left; //>
                    else if (p > node.val && q > node.val) node = node.right; //>
                    else return node.val; //>
                }
            }
        }
        ''',
    )],
)

problem(
    id="kth-smallest-bst",
    title="k-th Smallest in a Search Tree",
    difficulty="Medium",
    topics=["Tree", "Binary Search Tree", "Stack"],
    statement="""
    Return the `k`-th smallest value (1-indexed) in a binary search tree.
    """,
    examples=[([[3, 1, 4, None, 2], 1], 1, None), ([[5, 3, 6, 2, 4, None, None, 1], 3], 3, None)],
    tests=[([[1], 1], 1), ([[2, 1, 3], 3], 3)],
    constraints=["1 ≤ k ≤ number of nodes ≤ 10^4"],
    hints=["An in-order walk of a search tree visits values in sorted order.", "Stop after k visits."],
    approaches=[approach(
        name="Iterative In-Order", pattern="tree", time="O(h + k)", space="O(h)",
        idea="""
        An in-order traversal (left, node, right) of a search tree produces values in sorted order. Do it iteratively with a stack, and stop at the k-th visited node.
        """,
        viz=viz(tree=("root", {"node": "node"}), stacks=[("stack", "[n.val for n in stack]")]),
        demo=[[5, 3, 6, 2, 4, None, None, 1], 4],
        py='''
        def kth_smallest(root, k):
            stack, node = [], root
            while True:
                while node:
                    stack.append(node)
                    node = node.left
                node = stack.pop()
                k -= 1  #> Visit {node.val} in sorted order. {k} more to go.
                if k == 0:
                    return node.val
                node = node.right
        ''',
        java='''
        class Solution {
            public int kthSmallest(TreeNode root, int k) {
                Deque<TreeNode> stack = new ArrayDeque<>();
                TreeNode node = root;
                while (true) {
                    for (; node != null; node = node.left) stack.push(node);
                    node = stack.pop();
                    if (--k == 0) return node.val; //>
                    node = node.right;
                }
            }
        }
        ''',
    )],
)

problem(
    id="tree-diameter",
    title="Longest Path Between Two Nodes",
    difficulty="Easy",
    topics=["Tree", "DFS"],
    statement="""
    Return the diameter of a binary tree: the number of edges on the longest path between any two nodes. The path
    need not pass through the root.
    """,
    examples=[([[1, 2, 3, 4, 5]], 3, "4 → 2 → 1 → 3"), ([[1, 2]], 1, None)],
    tests=[([[1]], 0), ([[1, 2, None, 3, 4, None, None, 5, None, None, 6]], 4)],
    constraints=["1 ≤ number of nodes ≤ 10^4"],
    hints=["The longest path through a node = left depth + right depth."],
    approaches=[approach(
        name="DFS Returning Depths", pattern="tree", time="O(n)", space="O(h)",
        idea="""
        A depth-first helper returns each subtree's depth. At each node, the longest path bending through it is left depth plus right depth, so update a global best while returning the depth upward.
        """,
        viz=viz(tree=(T, {"node": "node"}), vars=["best"]),
        py='''
        def diameter(root):
            best = 0

            def depth(node):
                nonlocal best
                if not node:
                    return 0
                left, right = depth(node.left), depth(node.right)
                best = max(best, left + right)  #> Through node {node.val}: {left} plus {right} edges. Best: {best}.
                return 1 + max(left, right)

            depth(root)
            return best
        ''',
        java='''
        class Solution {
            private int best = 0;

            public int diameter(TreeNode root) {
                depth(root);
                return best;
            }

            private int depth(TreeNode node) {
                if (node == null) return 0;
                int left = depth(node.left), right = depth(node.right);
                best = Math.max(best, left + right); //>
                return 1 + Math.max(left, right);
            }
        }
        ''',
    )],
)

problem(
    id="balanced-tree",
    title="Is the Tree Balanced?",
    difficulty="Easy",
    topics=["Tree", "DFS"],
    statement="""
    A tree is height-balanced if, at every node, the heights of the left and right subtrees differ by at most one.
    Return `true` if the tree is balanced.
    """,
    examples=[([[3, 9, 20, None, None, 15, 7]], True, None), ([[1, 2, 2, 3, 3, None, None, 4, 4]], False, None)],
    tests=[([[]], True), ([[1, None, 2, None, 3]], False)],
    constraints=["0 ≤ number of nodes ≤ 5000"],
    hints=["Return −1 from the height helper as soon as something is unbalanced."],
    approaches=[approach(
        name="DFS with an Early Exit", pattern="tree", time="O(n)", space="O(h)",
        idea="""
        A helper returns a subtree's height, or −1 if it found an imbalance anywhere below. Each node checks its children's heights once, so the whole check is a single pass.
        """,
        viz=viz(tree=(T, {"node": "node"})),
        py='''
        def is_balanced(root):
            def height(node):
                if not node:
                    return 0
                left, right = height(node.left), height(node.right)
                if left < 0 or right < 0 or abs(left - right) > 1:
                    return -1  #> Node {node.val} is unbalanced: heights {left} and {right}.
                return 1 + max(left, right)  #> Node {node.val} is balanced, with height {ret}.

            return height(root) >= 0
        ''',
        java='''
        class Solution {
            public boolean isBalanced(TreeNode root) {
                return height(root) >= 0;
            }

            private int height(TreeNode node) {
                if (node == null) return 0;
                int left = height(node.left), right = height(node.right);
                if (left < 0 || right < 0 || Math.abs(left - right) > 1) return -1; //>
                return 1 + Math.max(left, right); //>
            }
        }
        ''',
    )],
)

problem(
    id="right-side-view",
    title="What You See From the Right",
    difficulty="Medium",
    topics=["Tree", "BFS"],
    statement="""
    Imagine standing to the right of the tree. Return the values you can see, from top to bottom: the rightmost node
    of every level.
    """,
    examples=[([[1, 2, 3, None, 5, None, 4]], [1, 3, 4], None), ([[1, 2]], [1, 2], None)],
    tests=[([[]], []), ([[1, 2, 3, 4]], [1, 3, 4])],
    constraints=["0 ≤ number of nodes ≤ 100"],
    hints=["Do a level-order walk and keep the last node of each level."],
    approaches=[approach(
        name="BFS, Last of Each Level", pattern="tree", time="O(n)", space="O(n)",
        idea="""
        Walk the tree level by level with a queue. The last node popped in each level is the one visible from the right.
        """,
        viz=viz(tree=("root", {"node": "node"}), queues=[("queue", "[n.val for n in q]")], out="res"),
        py='''
        from collections import deque

        def right_view(root):
            res, q = [], deque([root] if root else [])
            while q:
                for i in range(len(q)):
                    node = q.popleft()
                    q.extend(c for c in (node.left, node.right) if c)
                res.append(node.val)  #> The rightmost node on this level is {node.val}.
            return res
        ''',
        java='''
        class Solution {
            public List<Integer> rightView(TreeNode root) {
                List<Integer> res = new ArrayList<>();
                Deque<TreeNode> q = new ArrayDeque<>();
                if (root != null) q.add(root);
                while (!q.isEmpty()) {
                    TreeNode node = null;
                    for (int n = q.size(); n > 0; n--) {
                        node = q.poll();
                        if (node.left != null) q.add(node.left);
                        if (node.right != null) q.add(node.right);
                    }
                    res.add(node.val); //>
                }
                return res;
            }
        }
        ''',
    )],
)

problem(
    id="root-to-leaf-sum",
    title="Root-to-Leaf Path With a Target Sum",
    difficulty="Easy",
    topics=["Tree", "DFS"],
    statement="""
    Return `true` if some path from the root down to a leaf has node values adding up to `target`.
    """,
    examples=[([[5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1], 22], True, "5 + 4 + 11 + 2"), ([[1, 2, 3], 5], False, None)],
    tests=[([[], 0], False), ([[1, 2], 1], False), ([[-2, None, -3], -5], True)],
    constraints=["0 ≤ number of nodes ≤ 5000"],
    hints=["Subtract each node's value from the target as you go down."],
    approaches=[approach(
        name="DFS With a Shrinking Target", pattern="tree", time="O(n)", space="O(h)",
        idea="""
        Walk down, subtracting each node's value from the target. At a leaf, the path works if what's left is exactly zero.
        """,
        viz=viz(tree=(T, {"node": "root"}), vars=["target"]),
        py='''
        def has_path_sum(root, target):
            if not root:
                return False
            target -= root.val  #> At {root.val}, we still need {target} more.
            if not root.left and not root.right:
                return target == 0
            return has_path_sum(root.left, target) or has_path_sum(root.right, target)
        ''',
        java='''
        class Solution {
            public boolean hasPathSum(TreeNode root, int target) {
                if (root == null) return false;
                target -= root.val; //>
                if (root.left == null && root.right == null) return target == 0;
                return hasPathSum(root.left, target) || hasPathSum(root.right, target);
            }
        }
        ''',
    )],
)

problem(
    id="bst-pair-sum",
    title="Two Values in a Search Tree That Sum to k",
    difficulty="Easy",
    topics=["Tree", "Binary Search Tree", "Two Pointers"],
    patterns=["tree"],
    statement="""
    Return `true` if the binary search tree contains two different nodes whose values add up to `k`.
    """,
    examples=[([[5, 3, 6, 2, 4, None, 7], 9], True, "2 + 7 or 3 + 6"), ([[5, 3, 6, 2, 4, None, 7], 28], False, None)],
    tests=[([[1], 2], False), ([[2, 1, 3], 4], True)],
    constraints=["1 ≤ number of nodes ≤ 10^4"],
    hints=["An in-order walk gives a sorted list.", "Then it's the classic sorted pair search."],
    approaches=[approach(
        name="In-Order + Two Pointers", pattern="two-pointers", time="O(n)", space="O(n)",
        idea="""
        Walk the tree in order to get its values sorted. Then run two pointers from both ends: move `left` right when the sum is too small, `right` left when it is too big.
        """,
        viz=viz(arr="vals", ptr={"left": "left", "right": "right"}, vars=["k"]),
        py='''
        def bst_pair_sum(root, k):
            vals = []

            def inorder(node):
                if node:
                    inorder(node.left)
                    vals.append(node.val)
                    inorder(node.right)

            inorder(root)
            left, right = 0, len(vals) - 1  #> In order, the values are sorted: {vals}. Now use two pointers.
            while left < right:
                s = vals[left] + vals[right]
                if s == k:
                    return True  #> {vals[left]} plus {vals[right]} is {k}!
                if s < k:
                    left += 1  #> {s} is too small: left moves right.
                else:
                    right -= 1  #> {s} is too big: right moves left.
            return False
        ''',
        java='''
        class Solution {
            public boolean bstPairSum(TreeNode root, int k) {
                List<Integer> vals = new ArrayList<>();
                inorder(root, vals);
                int left = 0, right = vals.size() - 1; //>
                while (left < right) {
                    int s = vals.get(left) + vals.get(right);
                    if (s == k) return true; //>
                    if (s < k) left++; //>
                    else right--; //>
                }
                return false;
            }

            private void inorder(TreeNode node, List<Integer> vals) {
                if (node == null) return;
                inorder(node.left, vals);
                vals.add(node.val);
                inorder(node.right, vals);
            }
        }
        ''',
    )],
)

problem(
    id="rebuild-tree",
    title="Rebuild a Tree From Two Walks",
    difficulty="Medium",
    topics=["Tree", "Hash Map", "Divide and Conquer"],
    statement="""
    `preorder` (node, left, right) and `inorder` (left, node, right) are two traversals of the same tree with distinct
    values. Rebuild the tree and return its root.
    """,
    examples=[([[3, 9, 20, 15, 7], [9, 3, 15, 20, 7]], [3, 9, 20, None, None, 15, 7], None), ([[-1], [-1]], [-1], None)],
    tests=[([[1, 2], [2, 1]], [1, 2]), ([[1, 2, 3], [1, 2, 3]], [1, None, 2, None, 3])],
    constraints=["1 ≤ number of nodes ≤ 3000"],
    hints=["The first preorder value is the root.", "Its position in inorder splits the left and right subtrees."],
    approaches=[approach(
        name="Divide and Conquer + Index Map", pattern="tree", time="O(n)", space="O(n)",
        idea="""
        Preorder lists each root before its subtrees, so we can take roots from it one by one. A root's position in the inorder list splits the remaining values into its left part and right part.

        A hash map from value to inorder index makes each split instant.
        """,
        viz=viz(arrays=[("inorder", {"lo": "lo", "hi": "hi"}, ("lo", "hi"))]),
        py='''
        def rebuild(preorder, inorder):
            pos = {v: i for i, v in enumerate(inorder)}
            it = iter(preorder)

            def build(lo, hi):
                if lo > hi:
                    return None
                val = next(it)
                node = TreeNode(val)  #> {val} is the next root. In the in-order list it splits positions {lo} to {hi}.
                node.left = build(lo, pos[val] - 1)
                node.right = build(pos[val] + 1, hi)
                return node

            return build(0, len(inorder) - 1)
        ''',
        java='''
        class Solution {
            private int next = 0;

            public TreeNode rebuild(int[] preorder, int[] inorder) {
                Map<Integer, Integer> pos = new HashMap<>();
                for (int i = 0; i < inorder.length; i++) pos.put(inorder[i], i);
                return build(preorder, pos, 0, inorder.length - 1);
            }

            private TreeNode build(int[] pre, Map<Integer, Integer> pos, int lo, int hi) {
                if (lo > hi) return null;
                TreeNode node = new TreeNode(pre[next++]); //>
                node.left = build(pre, pos, lo, pos.get(node.val) - 1);
                node.right = build(pre, pos, pos.get(node.val) + 1, hi);
                return node;
            }
        }
        ''',
    )],
)

problem(
    id="max-path-sum",
    title="Best Path Sum Anywhere in a Tree",
    difficulty="Hard",
    topics=["Tree", "DFS", "Dynamic Programming"],
    statement="""
    A path is any sequence of connected nodes (each used once); it need not pass through the root. Return the largest
    sum of values along any non-empty path.
    """,
    examples=[([[1, 2, 3]], 6, "2 → 1 → 3"), ([[-10, 9, 20, None, None, 15, 7]], 42, "15 → 20 → 7")],
    tests=[([[-3]], -3), ([[2, -1]], 2), ([[5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1]], 48)],
    constraints=["1 ≤ number of nodes ≤ 3·10^4"],
    hints=["Ask each child for the best downward path starting at it.", "Ignore a child whose best is negative."],
    approaches=[approach(
        name="DFS With Gains", pattern="tree", time="O(n)", space="O(h)",
        idea="""
        For every node, compute the best downward "gain" from each child, treating negative gains as zero (just don't take that branch). The best path that bends at this node is its value plus both gains.

        Return upward only one branch (value plus the better gain), because a path can't fork.
        """,
        viz=viz(tree=(T, {"node": "node"}), vars=["best"]),
        py='''
        def max_path_sum(root):
            best = root.val

            def gain(node):
                nonlocal best
                if not node:
                    return 0
                left, right = max(gain(node.left), 0), max(gain(node.right), 0)
                best = max(best, node.val + left + right)  #> Bending at {node.val}: {node.val + left + right}. Best: {best}.
                return node.val + max(left, right)

            gain(root)
            return best
        ''',
        java='''
        class Solution {
            private int best;

            public int maxPathSum(TreeNode root) {
                best = root.val;
                gain(root);
                return best;
            }

            private int gain(TreeNode node) {
                if (node == null) return 0;
                int left = Math.max(gain(node.left), 0), right = Math.max(gain(node.right), 0);
                best = Math.max(best, node.val + left + right); //>
                return node.val + Math.max(left, right);
            }
        }
        ''',
    )],
)

problem(
    id="good-nodes",
    title="Count Nodes Nobody Above Beats",
    difficulty="Medium",
    topics=["Tree", "DFS"],
    statement="""
    A node is "good" if no node on the path from the root to it has a larger value. Return the number of good nodes.
    """,
    examples=[([[3, 1, 4, 3, None, 1, 5]], 4, None), ([[3, 3, None, 4, 2]], 3, None)],
    tests=[([[1]], 1), ([[2, None, 4, 10, 8, None, None, 4]], 4)],
    constraints=["1 ≤ number of nodes ≤ 10^5"],
    hints=["Carry the largest value seen on the way down."],
    approaches=[approach(
        name="DFS Carrying the Max", pattern="tree", time="O(n)", space="O(h)",
        idea="""
        Walk down while carrying the biggest value seen on the path so far. A node is good if its value is at least that maximum; then update the maximum for its children.
        """,
        viz=viz(tree=(T, {"node": "root"})),
        py='''
        def good_nodes(root, high=float("-inf")):
            if not root:
                return 0
            good = 1 if root.val >= high else 0  #> {root.val} versus the biggest value above it ({fv(high)}): {"good" if good else "not good"}.
            high = max(high, root.val)
            return good + good_nodes(root.left, high) + good_nodes(root.right, high)
        ''',
        java='''
        class Solution {
            public int goodNodes(TreeNode root) {
                return count(root, Integer.MIN_VALUE);
            }

            private int count(TreeNode node, int high) {
                if (node == null) return 0;
                int good = node.val >= high ? 1 : 0; //>
                high = Math.max(high, node.val);
                return good + count(node.left, high) + count(node.right, high);
            }
        }
        ''',
    )],
)

problem(
    id="sorted-to-bst",
    title="Balanced Search Tree From a Sorted List",
    difficulty="Easy",
    topics=["Tree", "Binary Search Tree", "Divide and Conquer"],
    statement="""
    Build a height-balanced binary search tree from the sorted array `nums`. Always choose the middle element
    `(lo + hi) / 2` (rounding down) of the current range as the root, so the answer is unique.
    """,
    examples=[([[-10, -3, 0, 5, 9]], [0, -10, 5, None, -3, None, 9], None), ([[1, 3]], [1, None, 3], None)],
    tests=[([[1]], [1]), ([[1, 2, 3, 4]], [2, 1, 3, None, None, None, 4])],
    constraints=["1 ≤ nums.length ≤ 10^4"],
    hints=["The middle value becomes the root; recurse on each half."],
    approaches=[approach(
        name="Divide and Conquer", pattern="binary-search", time="O(n)", space="O(log n)",
        idea="""
        The middle value splits the list into two halves of almost equal size. Make it the root, then build the left half into the left subtree and the right half into the right subtree. Balanced halves give a balanced tree.
        """,
        viz=viz(arr="nums", ptr={"lo": "lo", "mid": "mid", "hi": "hi"}, win=("lo", "hi")),
        py='''
        def to_bst(nums):
            def build(lo, hi):
                if lo > hi:
                    return None
                mid = (lo + hi) // 2
                node = TreeNode(nums[mid])  #> The middle of positions {lo} to {hi} is {nums[mid]}: it becomes a root.
                node.left, node.right = build(lo, mid - 1), build(mid + 1, hi)
                return node

            return build(0, len(nums) - 1)
        ''',
        java='''
        class Solution {
            public TreeNode toBst(int[] nums) {
                return build(nums, 0, nums.length - 1);
            }

            private TreeNode build(int[] nums, int lo, int hi) {
                if (lo > hi) return null;
                int mid = (lo + hi) >>> 1;
                TreeNode node = new TreeNode(nums[mid]); //>
                node.left = build(nums, lo, mid - 1);
                node.right = build(nums, mid + 1, hi);
                return node;
            }
        }
        ''',
    )],
)
