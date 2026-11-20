"""The Patterns Handbook: an original audiobook explaining every interview pattern from zero."""
from dsl import chapter

B = "handbook"

chapter(B, "Welcome: How to Use This Handbook", """
Welcome to the Patterns Handbook. This book is meant to be heard: on a walk, on the train, or while you cook. Each chapter explains one problem-solving pattern in plain words, tells you how to spot it, and gives you a template you can rebuild from memory.

Interview problems look endless, but most of them are a handful of ideas in disguise. Once you can name the pattern, the solution usually follows. Listen to a chapter, then open the Practice tab and solve two or three problems with that pattern while it's fresh.

A tip before we start: don't rush. Understanding why a pattern works beats memorising a hundred solutions.
""")

chapter(B, "Big-O in Plain Words", """
Big-O notation answers one question: when the input gets bigger, how much more work does my code do?

If doubling the input doubles the work, that's linear, O of n. If it quadruples the work, that's quadratic, O of n squared, which usually means two nested loops. If the work barely grows, like binary search, which only adds one step each time the input doubles, that's logarithmic, O of log n.

Here's a practical rule. If n is around a hundred thousand, quadratic is too slow, so aim for n log n or linear. Many of the patterns in this book exist precisely to turn a nested loop into a single pass.
""")

chapter(B, "Two Pointers", """
Two pointers means walking through data with two indexes instead of one, so one pass replaces a nested loop.

The first flavour starts the pointers at opposite ends. Picture a sorted list and a target sum. Put the left pointer on the smallest number and the right pointer on the largest. If their sum is too small, the only way to grow it is to move left forward. If it's too big, move right backward. Every step throws away a number that can never be part of the answer, so you finish in linear time.

The second flavour moves both pointers the same way: a read pointer scans everything, and a write pointer marks where the next kept value should go. That's how you remove duplicates or move zeros in place, with constant extra memory.

Spot it when you see words like sorted, pair, triple, palindrome, reverse, or in place.
""")

chapter(B, "Sliding Window", """
A sliding window is a stretch of consecutive elements with a left edge and a right edge. Instead of recomputing every possible subarray, you slide the window and update a running summary.

Here is the template to memorise. Loop the right edge across the array. First, add the element at right to your window: add it to a sum, or bump its count in a map. Then, while the window breaks the rule, shrink it from the left: remove the element at left and move left forward. In Java, this shrink step reads nicely as a for loop with an empty start: for, semicolon, while the sum is at least s, semicolon, subtract the left value and increment left.

For a shortest-window question, record the answer inside the shrink loop, while the window is still valid. For a longest-window question, shrink until the window is valid again, then record its length. Use a sentinel like n plus one to mean "not found yet".

Why is it fast? Each element enters the window once and leaves once, so even with a loop inside a loop, the total work is linear.

Spot it with words like contiguous, substring, subarray, longest, shortest, at most k, or window of size k.
""")

chapter(B, "Fast and Slow Pointers", """
Imagine two runners on a track: one runs twice as fast as the other. If the track is a loop, the fast runner eventually laps the slow one and they meet. If the track has an end, the fast runner simply reaches it.

That's the fast and slow pointer pattern. Move slow one step and fast two steps. If they meet, there's a cycle. To find where the cycle starts, send one pointer back to the beginning and move both one step at a time; they meet exactly at the entrance.

The same trick finds the middle of a linked list: when fast reaches the end, slow is halfway. It even works on number sequences, like detecting whether repeatedly summing the squares of digits loops forever.
""")

chapter(B, "Hash Maps and Counting", """
A hash map remembers what you've seen, with near-instant lookups. It's the most common way to trade a little memory for a lot of speed.

The classic move is the complement lookup. To find two numbers that add up to a target, walk the list once, and for each number ask: have I already seen target minus this number? If yes, you're done; if not, remember the current number.

Counting is the other big use: letter frequencies for anagrams, votes, or how many times each value appears. When the key space is small, like lowercase letters, a plain array of 26 counters is even faster.
""")

chapter(B, "Prefix Sums", """
A prefix sum is a running total: position i holds the sum of everything before it. With it, the sum of any range becomes one subtraction.

The deeper trick combines prefix sums with a hash map. To count subarrays that sum to k, keep the running total and a map of how many times each earlier total occurred. A subarray ending here sums to k exactly when an earlier total equals the current total minus k. This works even with negative numbers, where a sliding window would fail.

A cousin of this idea, the difference array, records only where values change, then rebuilds every total with one prefix sum.
""")

chapter(B, "Binary Search", """
Binary search halves the search space at every step, so a million items take only about twenty steps.

Beyond finding a value in a sorted array, learn the lower-bound form: find the first position where the condition becomes true. Keep a range from lo to hi; if the middle fails the condition, the answer is to the right; otherwise it's at the middle or to the left.

The most powerful use is searching over answers. If a speed, capacity or time works, then every larger one also works. Binary search the smallest value that passes a quick greedy check, such as the slowest eating speed or the smallest truck capacity.
""")

chapter(B, "Stacks and Monotonic Stacks", """
A stack is last in, first out. It's perfect whenever the most recent unfinished thing must be handled first: matching brackets, undo operations, evaluating expressions, or walking a tree without recursion.

A monotonic stack keeps its values in sorted order. When a new value arrives, pop every value it beats; for each popped item, the newcomer is its "next greater element". Each item is pushed once and popped once, so the whole pass is linear. That's how you answer "how many days until a warmer day" or find the largest rectangle in a bar chart.
""")

chapter(B, "Linked Lists", """
Linked list problems are about rewiring next pointers without losing the rest of the list.

Three habits make them easy. First, use a dummy node in front of the head, so you never special-case the first node. Second, when reversing, keep two pointers, previous and current, and save the next node before you flip the arrow. Third, use a gap: to remove the k-th node from the end, move one pointer k steps ahead, then walk both together until the leader reaches the end.

Draw the boxes and arrows on paper, and the code nearly writes itself.
""")

chapter(B, "Trees and Recursion", """
Most tree problems are solved by asking one question: what should each node report to its parent?

For the depth of a tree, a node reports one plus the deeper of its children. For the diameter, a node reports its depth upward while updating a global best with left depth plus right depth. For a valid search tree, pass down the allowed range instead.

Level-by-level questions use a queue instead: process one level at a time, and the rightmost node of each level is what you'd see from the right side. Remember that an in-order walk of a binary search tree visits values in sorted order, which turns many tree problems into array problems.
""")

chapter(B, "Graphs", """
Graphs are everywhere once you look: grids, course prerequisites, friendships, word ladders. Name the nodes and edges first.

Breadth-first search uses a queue and finds the fewest steps in unweighted graphs. Depth-first search dives deep and is great for exploring regions, like counting islands. For dependencies, topological sort repeatedly takes nodes with no remaining prerequisites; if some nodes never become free, there's a cycle.

Union-find tracks connected groups with near-constant merges. And when edges have weights, Dijkstra's algorithm always settles the closest unsettled node next, using a min-heap.
""")

chapter(B, "Heaps and Intervals", """
A heap hands you the smallest or largest item in logarithmic time. Whenever you hear top k, think of a min-heap of size k: push each value, and pop the smallest once the heap grows past k. Two heaps, one for the lower half and one for the upper half, track a running median.

Interval problems almost always start by sorting by start time. Then sweep: if the next interval overlaps the last one, merge; otherwise start a new one. To count meeting rooms, sort start times and end times separately and walk them with two pointers. To keep the most non-overlapping intervals, greedily keep the one that ends first.
""")

chapter(B, "Backtracking", """
Backtracking explores every possible choice, but abandons a path the moment it can't succeed.

The rhythm is choose, explore, un-choose. Add a candidate to the current path, recurse to decide the next position, then remove the candidate before trying the next one. That's how you generate subsets, permutations, combinations that hit a target, and solutions to puzzles like placing queens on a board.

Prune early: if a partial path already breaks a rule, stop. Good pruning turns impossible searches into fast ones.
""")

chapter(B, "Dynamic Programming", """
Dynamic programming is careful reuse. When a brute-force recursion keeps solving the same smaller problems, store each answer once.

Follow four steps. Define the state: what does a single cell mean, in words? Write the transition: how does a state come from smaller ones? Set the base cases. Then identify which cell holds the final answer.

Very often you only need the last one or two values, so the table shrinks to a sliding window of a few variables, like climbing stairs or robbing houses in constant space. For two strings, a two-dimensional table compares prefixes, and keeping just two rows is enough.
""")

chapter(B, "Greedy Choices", """
A greedy algorithm makes the best-looking choice right now and never looks back. It's fast and simple, but only correct when you can argue that the local choice is always safe.

Classic examples: to reach the end of an array of jumps, track the farthest index you can reach. To keep the most meetings, pick the one that ends first. To find a starting gas station, restart whenever the tank goes negative.

Before trusting a greedy idea, try hard to break it with a tiny counterexample. If you can, switch to dynamic programming.
""")

chapter(B, "Interview Day: Thinking Out Loud", """
Interviewers judge your process as much as your answer. Here is a reliable flow.

First, restate the problem and ask about edge cases: empty input, duplicates, negative numbers, huge sizes. Second, describe a brute-force solution and its complexity, even if it's slow. Third, look for the pattern: is this a window, two pointers, a map, a heap? Explain why it helps. Fourth, write clean code with good names. Fifth, dry-run a small example out loud and fix bugs calmly. Finally, state the time and space complexity.

If you get stuck, say what you're thinking. Silence is the only truly wrong answer. Good luck. You've got this.
""")
