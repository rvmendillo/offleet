"""Linked List problems (original statements). ListNode has fields val and next."""
from dsl import problem, approach, viz

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

problem(
    id="merge-sorted-lists",
    title="Merge Two Sorted Chains",
    difficulty="Easy",
    topics=["Linked List", "Two Pointers"],
    statement="""
    `a` and `b` are heads of two sorted linked lists. Splice their nodes together into one sorted list and return its head.
    """,
    examples=[([[1, 2, 4], [1, 3, 4]], [1, 1, 2, 3, 4, 4], None), ([[], [0]], [0], None)],
    tests=[([[], []], []), ([[5], [1, 2, 3]], [1, 2, 3, 5]), ([[2, 6, 9], [1, 7]], [1, 2, 6, 7, 9])],
    constraints=["0 ≤ length of each list ≤ 50"],
    hints=["A dummy node avoids special-casing the head.", "Always attach the smaller of the two front nodes."],
    approaches=[approach(
        name="Two Pointers + Dummy Head", pattern="two-pointers", time="O(n + m)", space="O(1)",
        idea="""
        Start from a dummy node and a `tail` pointer. Compare the front nodes of both lists, attach the smaller one to the tail, and advance that list's pointer.

        When one list runs out, attach the remainder of the other list in one step.
        """,
        viz=viz(linked=(["dummy", "a", "b"], {"a": "a", "b": "b", "tail": "tail"})),
        py='''
        def merge_lists(a, b):
            dummy = tail = ListNode()
            while a and b:
                if a.val <= b.val:
                    tail.next, a = a, a.next  #> {tail.next.val} from the first list is smaller. Attach it.
                else:
                    tail.next, b = b, b.next  #> {tail.next.val} from the second list is smaller. Attach it.
                tail = tail.next
            tail.next = a or b  #> One list is empty, so attach the rest of the other.
            return dummy.next
        ''',
        java='''
        class Solution {
            public ListNode mergeLists(ListNode a, ListNode b) {
                ListNode dummy = new ListNode(), tail = dummy;
                while (a != null && b != null) {
                    if (a.val <= b.val) { tail.next = a; a = a.next; } //>
                    else { tail.next = b; b = b.next; } //>
                    tail = tail.next;
                }
                tail.next = a != null ? a : b; //>
                return dummy.next;
            }
        }
        ''',
    )],
)

problem(
    id="has-loop",
    title="Does the Chain Loop?",
    difficulty="Easy",
    topics=["Linked List", "Fast & Slow Pointers"],
    cycle=True,
    statement="""
    Return `true` if the linked list starting at `head` contains a cycle (some node's `next` points back to an
    earlier node). In the examples, `pos` is the index the last node links back to (−1 means no cycle); it is not
    passed to your function. Use O(1) memory.
    """,
    examples=[([[3, 2, 0, -4], 1], True, "The tail links back to node 2."), ([[1], -1], False, None)],
    tests=[([[1, 2], 0], True), ([[], -1], False), ([[1, 2, 3, 4], -1], False)],
    constraints=["0 ≤ number of nodes ≤ 10^4"],
    hints=["Two runners on a circular track eventually meet."],
    approaches=[approach(
        name="Fast & Slow Pointers", pattern="fast-slow", time="O(n)", space="O(1)",
        idea="""
        Move `slow` one node at a time and `fast` two nodes at a time. If there's no cycle, `fast` reaches the end.

        If there is a cycle, `fast` laps around and must eventually land on the same node as `slow`.
        """,
        viz=viz(linked=("head", {"slow": "slow", "fast": "fast"})),
        py='''
        def has_loop(head):
            slow = fast = head
            while fast and fast.next:
                slow, fast = slow.next, fast.next.next  #> Slow moves to {slow.val}, fast jumps to {fast.val if fast else "the end"}.
                if slow is fast:
                    return True  #> They landed on the same node: there's a cycle!
            return False  #> Fast reached the end, so there is no cycle.
        ''',
        java='''
        class Solution {
            public boolean hasLoop(ListNode head) {
                ListNode slow = head, fast = head;
                while (fast != null && fast.next != null) {
                    slow = slow.next; fast = fast.next.next; //>
                    if (slow == fast) return true; //>
                }
                return false; //>
            }
        }
        ''',
    )],
)

problem(
    id="loop-entrance",
    title="Where the Loop Begins",
    difficulty="Medium",
    topics=["Linked List", "Fast & Slow Pointers"],
    cycle=True,
    statement="""
    Return the node where the cycle in the list begins, or `null` if there is no cycle. `pos` in the examples is the
    index the tail links back to (−1 means none) and is not passed to your function. The output shows the list read
    from the returned node until it repeats.
    """,
    examples=[([[3, 2, 0, -4], 1], [2, 0, -4], "The loop starts at node 2."), ([[1, 2], 0], [1, 2], None)],
    tests=[([[1], -1], []), ([[5, 6, 7, 8, 9], 2], [7, 8, 9])],
    constraints=["0 ≤ number of nodes ≤ 10^4"],
    hints=["After slow and fast meet, a pointer from the head and one from the meeting point meet at the entrance."],
    approaches=[approach(
        name="Fast & Slow Pointers", pattern="fast-slow", time="O(n)", space="O(1)",
        idea="""
        First find a meeting point with slow and fast pointers. Then start one pointer at the head and one at the meeting point and move both one step at a time.

        The distances work out so that they meet exactly at the loop's entrance.
        """,
        viz=viz(linked=("head", {"slow": "slow", "fast": "fast"})),
        py='''
        def loop_entrance(head):
            slow = fast = head
            while fast and fast.next:
                slow, fast = slow.next, fast.next.next
                if slow is fast:
                    slow = head  #> They met at node {fast.val}. Send slow back to the head.
                    while slow is not fast:
                        slow, fast = slow.next, fast.next  #> Both step once: slow {slow.val}, fast {fast.val}.
                    return slow  #> They meet at node {slow.val}, the start of the loop.
            return None
        ''',
        java='''
        class Solution {
            public ListNode loopEntrance(ListNode head) {
                ListNode slow = head, fast = head;
                while (fast != null && fast.next != null) {
                    slow = slow.next; fast = fast.next.next;
                    if (slow == fast) {
                        slow = head; //>
                        while (slow != fast) { slow = slow.next; fast = fast.next; } //>
                        return slow; //>
                    }
                }
                return null;
            }
        }
        ''',
    )],
)

problem(
    id="middle-node",
    title="Middle of the Chain",
    difficulty="Easy",
    topics=["Linked List", "Fast & Slow Pointers"],
    statement="""
    Return the middle node of the linked list. If there are two middle nodes, return the second one.
    """,
    examples=[([[1, 2, 3, 4, 5]], [3, 4, 5], None), ([[1, 2, 3, 4, 5, 6]], [4, 5, 6], None)],
    tests=[([[1]], [1]), ([[1, 2]], [2])],
    constraints=["1 ≤ number of nodes ≤ 100"],
    hints=["When the fast pointer finishes, the slow one is halfway."],
    approaches=[approach(
        name="Fast & Slow Pointers", pattern="fast-slow", time="O(n)", space="O(1)",
        idea="""
        Move `fast` two steps for every one step of `slow`. When `fast` can't move any further, `slow` has covered half the distance and sits at the middle.
        """,
        viz=viz(linked=("head", {"slow": "slow", "fast": "fast"})),
        py='''
        def middle(head):
            slow = fast = head
            while fast and fast.next:
                slow, fast = slow.next, fast.next.next  #> Slow steps to {slow.val}; fast jumps to {fast.val if fast else "past the end"}.
            return slow  #> Fast is done, so slow, at {slow.val}, is the middle.
        ''',
        java='''
        class Solution {
            public ListNode middle(ListNode head) {
                ListNode slow = head, fast = head;
                while (fast != null && fast.next != null) { slow = slow.next; fast = fast.next.next; } //>
                return slow; //>
            }
        }
        ''',
    )],
)

problem(
    id="remove-kth-from-end",
    title="Remove the k-th Node From the End",
    difficulty="Medium",
    topics=["Linked List", "Two Pointers"],
    statement="""
    Remove the `k`-th node counting from the end of the list (k = 1 is the last node) in one pass, and return the head.
    """,
    examples=[([[1, 2, 3, 4, 5], 2], [1, 2, 3, 5], None), ([[1], 1], [], None)],
    tests=[([[1, 2], 1], [1]), ([[1, 2], 2], [2]), ([[4, 5, 6, 7], 4], [5, 6, 7])],
    constraints=["1 ≤ k ≤ number of nodes ≤ 30"],
    hints=["Give one pointer a head start of k nodes.", "When it reaches the end, the other is just before the target."],
    approaches=[approach(
        name="Two Pointers with a Gap", pattern="two-pointers", time="O(n)", space="O(1)",
        idea="""
        Start both pointers at a dummy node before the head, then move `fast` k steps ahead. Now walk both together until `fast` reaches the last node.

        The gap means `slow` stops right before the node to delete, so we just skip over it.
        """,
        viz=viz(linked=(["dummy"], {"slow": "slow", "fast": "fast"})),
        py='''
        def remove_kth_from_end(head, k):
            dummy = ListNode(0, head)
            slow = fast = dummy
            for _ in range(k):
                fast = fast.next  #> Fast gets a head start: it moves to {fast.val}.
            while fast.next:
                slow, fast = slow.next, fast.next  #> Move together: slow {slow.val}, fast {fast.val}.
            slow.next = slow.next.next  #> Fast is at the end, so skip the node after slow.
            return dummy.next
        ''',
        java='''
        class Solution {
            public ListNode removeKthFromEnd(ListNode head, int k) {
                ListNode dummy = new ListNode(0, head), slow = dummy, fast = dummy;
                for (int i = 0; i < k; i++) fast = fast.next; //>
                while (fast.next != null) { slow = slow.next; fast = fast.next; } //>
                slow.next = slow.next.next; //>
                return dummy.next;
            }
        }
        ''',
    )],
)

problem(
    id="palindrome-chain",
    title="Does the Chain Read the Same Backwards?",
    difficulty="Easy",
    topics=["Linked List", "Fast & Slow Pointers", "Two Pointers"],
    statement="""
    Return `true` if the values of the linked list read the same forwards and backwards. Aim for O(1) extra memory.
    """,
    examples=[([[1, 2, 2, 1]], True, None), ([[1, 2]], False, None)],
    tests=[([[1]], True), ([[1, 2, 1]], True), ([[1, 2, 3, 1]], False)],
    constraints=["1 ≤ number of nodes ≤ 10^5"],
    hints=["Find the middle, reverse the second half, then compare the halves."],
    approaches=[approach(
        name="Fast & Slow + Reverse + Two Pointers", pattern="fast-slow", time="O(n)", space="O(1)",
        idea="""
        Use slow and fast pointers to find the middle. Reverse the second half in place.

        Then walk one pointer from the head and one from the reversed half, comparing values.
        """,
        viz=viz(linked=("head", {"slow": "slow", "fast": "fast", "left": "left", "right": "right"})),
        py='''
        def is_palindrome_chain(head):
            slow = fast = head
            while fast and fast.next:
                slow, fast = slow.next, fast.next.next
            prev = None
            while slow:
                slow.next, prev, slow = prev, slow, slow.next
            left, right = head, prev  #> The second half is reversed. Compare from both ends.
            while right:
                if left.val != right.val:
                    return False  #> {left.val} differs from {right.val}.
                left, right = left.next, right.next  #> The values match, so both pointers move on.
            return True
        ''',
        java='''
        class Solution {
            public boolean isPalindromeChain(ListNode head) {
                ListNode slow = head, fast = head;
                while (fast != null && fast.next != null) { slow = slow.next; fast = fast.next.next; }
                ListNode prev = null;
                while (slow != null) { ListNode n = slow.next; slow.next = prev; prev = slow; slow = n; }
                ListNode left = head, right = prev; //>
                while (right != null) {
                    if (left.val != right.val) return false; //>
                    left = left.next; right = right.next; //>
                }
                return true;
            }
        }
        ''',
    )],
)

problem(
    id="interleave-halves",
    title="Weave the Chain From Both Ends",
    difficulty="Medium",
    topics=["Linked List", "Fast & Slow Pointers", "Two Pointers"],
    out="arg0",
    statement="""
    Reorder the list `L0 → L1 → … → Ln` **in place** into `L0 → Ln → L1 → Ln−1 → L2 → …`.
    """,
    examples=[([[1, 2, 3, 4]], [1, 4, 2, 3], None), ([[1, 2, 3, 4, 5]], [1, 5, 2, 4, 3], None)],
    tests=[([[1]], [1]), ([[1, 2]], [1, 2]), ([[1, 2, 3]], [1, 3, 2])],
    constraints=["1 ≤ number of nodes ≤ 5·10^4"],
    hints=["Split at the middle, reverse the second half, then merge alternately."],
    approaches=[approach(
        name="Middle + Reverse + Merge", pattern="fast-slow", time="O(n)", space="O(1)",
        idea="""
        Find the middle with slow and fast pointers and cut the list there. Reverse the second half.

        Now weave: take one node from the front half, then one from the reversed back half, and repeat.
        """,
        viz=viz(linked=("head", {"a": "a", "b": "b"})),
        py='''
        def weave(head):
            slow = fast = head
            while fast and fast.next:
                slow, fast = slow.next, fast.next.next
            prev, cur = None, slow.next
            slow.next = None
            while cur:
                cur.next, prev, cur = prev, cur, cur.next
            a, b = head, prev  #> The second half is reversed. Now weave a and b together.
            while b:
                a.next, b.next, a, b = b, a.next, a.next, b.next  #> Weave in the next back-half node. The list reads {lst(chain(head))}.
        ''',
        java='''
        class Solution {
            public void weave(ListNode head) {
                ListNode slow = head, fast = head;
                while (fast != null && fast.next != null) { slow = slow.next; fast = fast.next.next; }
                ListNode prev = null, cur = slow.next;
                slow.next = null;
                while (cur != null) { ListNode n = cur.next; cur.next = prev; prev = cur; cur = n; }
                ListNode a = head, b = prev; //>
                while (b != null) {
                    ListNode an = a.next, bn = b.next;
                    a.next = b; b.next = an; a = an; b = bn; //>
                }
            }
        }
        ''',
    )],
)

problem(
    id="add-digit-chains",
    title="Add Two Numbers Stored as Chains",
    difficulty="Medium",
    topics=["Linked List", "Math"],
    statement="""
    Two non-negative numbers are stored as linked lists of digits in **reverse** order (the head is the ones digit).
    Return their sum as a linked list in the same format.
    """,
    examples=[([[2, 4, 3], [5, 6, 4]], [7, 0, 8], "342 + 465 = 807"), ([[0], [0]], [0], None)],
    tests=[([[9, 9, 9, 9], [9, 9]], [8, 9, 0, 0, 1]), ([[5], [5]], [0, 1])],
    constraints=["1 ≤ digits per list ≤ 100", "no leading zeros except the number 0"],
    hints=["Add digit by digit like on paper, carrying the tens."],
    approaches=[approach(
        name="Digit-by-Digit with Carry", pattern="linked-list", time="O(n + m)", space="O(1) extra",
        idea="""
        Walk both lists together, adding the two digits and the carry. Write the ones digit into a new node and carry the tens to the next step.

        Keep going while either list has digits left or a carry remains.
        """,
        viz=viz(linked=(["dummy", "a", "b"], {"a": "a", "b": "b", "tail": "tail"}), vars=["carry"]),
        py='''
        def add_chains(a, b):
            dummy = tail = ListNode()
            carry = 0
            while a or b or carry:
                total = carry + (a.val if a else 0) + (b.val if b else 0)
                carry, digit = divmod(total, 10)
                tail.next = ListNode(digit)  #> The digits sum to {total}: write {digit}, carry {carry}.
                tail = tail.next
                a, b = a.next if a else None, b.next if b else None
            return dummy.next
        ''',
        java='''
        class Solution {
            public ListNode addChains(ListNode a, ListNode b) {
                ListNode dummy = new ListNode(), tail = dummy;
                int carry = 0;
                while (a != null || b != null || carry > 0) {
                    int total = carry + (a != null ? a.val : 0) + (b != null ? b.val : 0);
                    carry = total / 10;
                    tail.next = new ListNode(total % 10); //>
                    tail = tail.next;
                    a = a != null ? a.next : null;
                    b = b != null ? b.next : null;
                }
                return dummy.next;
            }
        }
        ''',
    )],
)

problem(
    id="dedupe-sorted-chain",
    title="Remove Repeats From a Sorted Chain",
    difficulty="Easy",
    topics=["Linked List"],
    statement="""
    The linked list is sorted. Delete nodes so each value appears once, and return the head.
    """,
    examples=[([[1, 1, 2]], [1, 2], None), ([[1, 1, 2, 3, 3]], [1, 2, 3], None)],
    tests=[([[]], []), ([[4, 4, 4]], [4])],
    constraints=["0 ≤ number of nodes ≤ 300"],
    hints=["Duplicates are adjacent; skip over them."],
    approaches=[approach(
        name="Single Pointer Skip", pattern="linked-list", time="O(n)", space="O(1)",
        idea="""
        Walk with `cur`. While the next node has the same value, bypass it by pointing `cur.next` one node further. Otherwise move on.
        """,
        viz=viz(linked=("head", {"cur": "cur"})),
        py='''
        def dedupe_chain(head):
            cur = head
            while cur and cur.next:
                if cur.next.val == cur.val:
                    cur.next = cur.next.next  #> The next node repeats {cur.val}, so skip it.
                else:
                    cur = cur.next  #> Move on to {cur.val}.
            return head
        ''',
        java='''
        class Solution {
            public ListNode dedupeChain(ListNode head) {
                ListNode cur = head;
                while (cur != null && cur.next != null) {
                    if (cur.next.val == cur.val) cur.next = cur.next.next; //>
                    else cur = cur.next; //>
                }
                return head;
            }
        }
        ''',
    )],
)

problem(
    id="odd-then-even",
    title="Odd Positions, Then Even Positions",
    difficulty="Medium",
    topics=["Linked List", "Two Pointers"],
    statement="""
    Regroup the list so all nodes at odd positions (1st, 3rd, …) come first, followed by the nodes at even positions,
    keeping the relative order within each group. Use O(1) extra space and return the head.
    """,
    examples=[([[1, 2, 3, 4, 5]], [1, 3, 5, 2, 4], None), ([[2, 1, 3, 5, 6, 4, 7]], [2, 3, 6, 7, 1, 5, 4], None)],
    tests=[([[]], []), ([[1]], [1]), ([[1, 2]], [1, 2])],
    constraints=["0 ≤ number of nodes ≤ 10^4"],
    hints=["Grow an odd chain and an even chain side by side, then join them."],
    approaches=[approach(
        name="Two Pointers (odd & even chains)", pattern="two-pointers", time="O(n)", space="O(1)",
        idea="""
        Keep two chains: `odd` starts at the first node and `even` at the second. Repeatedly link each to the node after the other, which leapfrogs them forward.

        Finally connect the end of the odd chain to the head of the even chain.
        """,
        viz=viz(linked=("head", {"odd": "odd", "even": "even"})),
        py='''
        def odd_even(head):
            if not head:
                return head
            odd, even = head, head.next
            even_head = even
            while even and even.next:
                odd.next = even.next
                odd = odd.next  #> The odd chain grows to {odd.val}.
                even.next = odd.next
                even = even.next  #> The even chain grows to {even.val if even else "the end"}.
            odd.next = even_head  #> Attach the even chain after the last odd node.
            return head
        ''',
        java='''
        class Solution {
            public ListNode oddEven(ListNode head) {
                if (head == null) return head;
                ListNode odd = head, even = head.next, evenHead = even;
                while (even != null && even.next != null) {
                    odd.next = even.next; odd = odd.next; //>
                    even.next = odd.next; even = even.next; //>
                }
                odd.next = evenHead; //>
                return head;
            }
        }
        ''',
    )],
)

problem(
    id="rotate-chain",
    title="Rotate a Chain to the Right",
    difficulty="Medium",
    topics=["Linked List", "Two Pointers"],
    statement="""
    Rotate the linked list to the right by `k` places: the last `k` nodes move to the front. Return the new head.
    """,
    examples=[([[1, 2, 3, 4, 5], 2], [4, 5, 1, 2, 3], None), ([[0, 1, 2], 4], [2, 0, 1], None)],
    tests=[([[], 3], []), ([[1], 9], [1]), ([[1, 2], 2], [1, 2])],
    constraints=["0 ≤ number of nodes ≤ 500", "0 ≤ k ≤ 2·10^9"],
    hints=["Only k mod length matters.", "Close the list into a ring, then cut it at the right place."],
    approaches=[approach(
        name="Ring and Cut", pattern="two-pointers", time="O(n)", space="O(1)",
        idea="""
        Find the length and the tail. Reduce k modulo the length, link the tail back to the head to form a ring, then walk to the node that should become the new tail and cut the ring after it.
        """,
        viz=viz(linked=("head", {"tail": "tail", "new tail": "new_tail"})),
        py='''
        def rotate_chain(head, k):
            if not head:
                return head
            n, tail = 1, head
            while tail.next:
                tail, n = tail.next, n + 1
            k %= n
            tail.next = head  #> Join the tail ({tail.val}) to the head to make a ring of {n} nodes.
            new_tail = head
            for _ in range(n - k - 1):
                new_tail = new_tail.next
            new_head = new_tail.next
            new_tail.next = None  #> Cut after {new_tail.val}. The new head is {new_head.val}.
            return new_head
        ''',
        java='''
        class Solution {
            public ListNode rotateChain(ListNode head, int k) {
                if (head == null) return head;
                int n = 1;
                ListNode tail = head;
                while (tail.next != null) { tail = tail.next; n++; }
                k %= n;
                tail.next = head; //>
                ListNode newTail = head;
                for (int i = 0; i < n - k - 1; i++) newTail = newTail.next;
                ListNode newHead = newTail.next;
                newTail.next = null; //>
                return newHead;
            }
        }
        ''',
    )],
)

problem(
    id="swap-neighbours",
    title="Swap Every Two Nodes",
    difficulty="Medium",
    topics=["Linked List", "Two Pointers"],
    statement="""
    Swap every two adjacent nodes of the list (by relinking nodes, not by changing values) and return the head.
    """,
    examples=[([[1, 2, 3, 4]], [2, 1, 4, 3], None), ([[1, 2, 3]], [2, 1, 3], None)],
    tests=[([[]], []), ([[1]], [1])],
    constraints=["0 ≤ number of nodes ≤ 100"],
    hints=["Use a dummy node and a pointer to the node before each pair."],
    approaches=[approach(
        name="Pointer Rewiring", pattern="two-pointers", time="O(n)", space="O(1)",
        idea="""
        Keep `prev` just before the next pair `a, b`. Rewire `prev → b → a → (rest)`, then move `prev` to `a`, which is now the second node of the swapped pair.
        """,
        viz=viz(linked=(["dummy"], {"prev": "prev", "a": "a", "b": "b"})),
        py='''
        def swap_pairs(head):
            dummy = ListNode(0, head)
            prev = dummy
            while prev.next and prev.next.next:
                a, b = prev.next, prev.next.next
                prev.next, a.next, b.next = b, b.next, a  #> Swap {a.val} and {b.val}.
                prev = a
            return dummy.next
        ''',
        java='''
        class Solution {
            public ListNode swapPairs(ListNode head) {
                ListNode dummy = new ListNode(0, head), prev = dummy;
                while (prev.next != null && prev.next.next != null) {
                    ListNode a = prev.next, b = a.next;
                    prev.next = b; a.next = b.next; b.next = a; //>
                    prev = a;
                }
                return dummy.next;
            }
        }
        ''',
    )],
)

problem(
    id="reverse-in-groups",
    title="Reverse Every k Nodes",
    difficulty="Hard",
    topics=["Linked List", "Two Pointers"],
    statement="""
    Reverse the nodes of the list `k` at a time and return the head. If fewer than `k` nodes remain at the end, leave
    them as they are. Only relink nodes; don't change values.
    """,
    examples=[([[1, 2, 3, 4, 5], 2], [2, 1, 4, 3, 5], None), ([[1, 2, 3, 4, 5], 3], [3, 2, 1, 4, 5], None)],
    tests=[([[1], 1], [1]), ([[1, 2, 3, 4], 4], [4, 3, 2, 1]), ([[1, 2], 3], [1, 2])],
    constraints=["1 ≤ k ≤ number of nodes ≤ 5000"],
    hints=["Check that k nodes exist before reversing a group.", "Reuse the prev/cur reversal inside each group."],
    approaches=[approach(
        name="Group Reversal with Two Pointers", pattern="two-pointers", time="O(n)", space="O(1)",
        idea="""
        Keep `group_prev`, the node before the current group. Check that k more nodes exist; if not, stop.

        Reverse those k nodes with the classic prev/cur two-pointer flip, then reconnect the reversed group between `group_prev` and the rest of the list.
        """,
        viz=viz(linked=(["dummy"], {"group prev": "group_prev", "cur": "cur", "prev": "prev"})),
        py='''
        def reverse_groups(head, k):
            dummy = ListNode(0, head)
            group_prev = dummy
            while True:
                kth = group_prev
                for _ in range(k):
                    kth = kth.next
                    if not kth:
                        return dummy.next
                group_next = kth.next
                prev, cur = group_next, group_prev.next
                while cur is not group_next:
                    cur.next, prev, cur = prev, cur, cur.next
                first = group_prev.next
                group_prev.next = prev
                group_prev = first  #> Reversed a group of {k}. The list is now {lst(chain(dummy.next))}.
        ''',
        java='''
        class Solution {
            public ListNode reverseGroups(ListNode head, int k) {
                ListNode dummy = new ListNode(0, head), groupPrev = dummy;
                while (true) {
                    ListNode kth = groupPrev;
                    for (int i = 0; i < k; i++) { kth = kth.next; if (kth == null) return dummy.next; }
                    ListNode groupNext = kth.next, prev = groupNext, cur = groupPrev.next;
                    while (cur != groupNext) { ListNode n = cur.next; cur.next = prev; prev = cur; cur = n; }
                    ListNode first = groupPrev.next;
                    groupPrev.next = prev;
                    groupPrev = first; //>
                }
            }
        }
        ''',
    )],
)
