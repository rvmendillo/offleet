"""Two Pointers problems."""
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
    tests=[([[1, 2], 3], [0, 1]), ([[1, 2, 3, 9], 12], [2, 3]), ([[-5, -2, 0, 7, 11], 6], [0, 4])],
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
    id="reverse-list",
    title="Reverse a Linked List",
    difficulty="Easy",
    topics=["Linked List", "Two Pointers"],
    statement="""
    Given the `head` of a singly linked list, reverse the list so the last node becomes the first, and return the new head.
    """,
    examples=[([[1, 2, 3, 4]], [4, 3, 2, 1], None), ([[7]], [7], None)],
    tests=[([[]], []), ([[1, 2]], [2, 1])],
    constraints=["0 ≤ number of nodes ≤ 5000"],
    hints=["Walk the list once, flipping each arrow to point backwards.", "Keep a pointer to the previous node."],
    approaches=[approach(
        name="Two Pointers (prev & cur)", pattern="two-pointers", time="O(n)", space="O(1)",
        idea="""
        Use two pointers: `prev` starts empty and `cur` starts at the head.

        At each node, remember the next node, flip `cur.next` to point back at `prev`, then slide both pointers one step forward. When `cur` falls off the end, `prev` is the new head.
        """,
        viz=viz(linked=("head", {"prev": "prev", "cur": "cur", "next": "nxt"})),
        py='''
        def reverse_list(head):
            prev, cur = None, head  #> prev starts empty and cur starts at the head.
            while cur:
                nxt = cur.next  #> Save the next node, {nxt.val if nxt else "nothing"}, so we don't lose the rest.
                cur.next = prev  #> Flip node {cur.val} to point back at {prev.val if prev else "nothing"}.
                prev, cur = cur, nxt  #> Slide forward: prev is now {prev.val}{", cur is " + str(cur.val) if cur else ", and cur fell off the end"}.
            return prev  #> prev, node {prev.val if prev else "none"}, is the new head.
        ''',
        java='''
        class Solution {
            public ListNode reverseList(ListNode head) {
                ListNode prev = null, cur = head; //>
                while (cur != null) {
                    ListNode nxt = cur.next; //>
                    cur.next = prev; //>
                    prev = cur; cur = nxt; //>
                }
                return prev; //>
            }
        }
        ''',
    )],
)
