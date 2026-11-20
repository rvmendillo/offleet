"""Interval problems (original statements)."""
from dsl import problem, approach, viz

problem(
    id="merge-intervals",
    title="Merge Overlapping Intervals",
    difficulty="Medium",
    topics=["Array", "Intervals", "Sorting"],
    statement="""
    Merge all overlapping intervals `[start, end]` and return the result sorted by start. Intervals that touch
    (one ends where the next starts) also merge.
    """,
    examples=[([[[1, 3], [2, 6], [8, 10], [15, 18]]], [[1, 6], [8, 10], [15, 18]], None), ([[[1, 4], [4, 5]]], [[1, 5]], None)],
    tests=[([[[5, 7]]], [[5, 7]]), ([[[2, 3], [1, 10]]], [[1, 10]]), ([[[1, 2], [3, 4]]], [[1, 2], [3, 4]])],
    constraints=["1 ≤ intervals.length ≤ 10^4"],
    hints=["Sort by start.", "Then each interval either extends the last merged one or starts a new one."],
    approaches=[approach(
        name="Sort + Sweep", pattern="intervals", time="O(n log n)", space="O(n)",
        idea="""
        Sort by start time. Walk through: if an interval starts before (or exactly when) the last merged interval ends, extend that one; otherwise start a new merged interval.
        """,
        viz=viz(intervals=["intervals", ("merged", "res")]),
        py='''
        def merge(intervals):
            intervals.sort()
            res = []
            for s, e in intervals:
                if res and s <= res[-1][1]:
                    res[-1][1] = max(res[-1][1], e)  #> [{s}, {e}] overlaps, so the last merged interval grows to {res[-1]}.
                else:
                    res.append([s, e])  #> [{s}, {e}] starts a new merged interval.
            return res
        ''',
        java='''
        class Solution {
            public int[][] merge(int[][] intervals) {
                Arrays.sort(intervals, (a, b) -> a[0] - b[0]);
                List<int[]> res = new ArrayList<>();
                for (int[] iv : intervals) {
                    if (!res.isEmpty() && iv[0] <= res.get(res.size() - 1)[1])
                        res.get(res.size() - 1)[1] = Math.max(res.get(res.size() - 1)[1], iv[1]); //>
                    else res.add(new int[]{iv[0], iv[1]}); //>
                }
                return res.toArray(new int[0][]);
            }
        }
        ''',
    )],
)

problem(
    id="insert-interval",
    title="Insert Into a Sorted Schedule",
    difficulty="Medium",
    topics=["Array", "Intervals"],
    statement="""
    `intervals` are non-overlapping and sorted by start. Insert `new` and merge where needed, returning a sorted,
    non-overlapping list.
    """,
    examples=[([[[1, 3], [6, 9]], [2, 5]], [[1, 5], [6, 9]], None), ([[[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]], [[1, 2], [3, 10], [12, 16]], None)],
    tests=[([[], [5, 7]], [[5, 7]]), ([[[1, 5]], [6, 8]], [[1, 5], [6, 8]]), ([[[3, 4]], [1, 2]], [[1, 2], [3, 4]])],
    constraints=["0 ≤ intervals.length ≤ 10^4"],
    hints=["Three phases: intervals ending before `new`, ones overlapping it, and the rest."],
    approaches=[approach(
        name="Three-Phase Sweep", pattern="intervals", time="O(n)", space="O(n)",
        idea="""
        Copy every interval that ends before the new one starts. Then absorb every interval that overlaps, stretching the new interval. Finally add it, followed by the remaining intervals.
        """,
        viz=viz(intervals=["intervals", ("result", "res")], vars=["start", "end"]),
        demo=[[[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]],
        py='''
        def insert(intervals, new):
            res, i, n = [], 0, len(intervals)
            start, end = new
            while i < n and intervals[i][1] < start:
                res.append(intervals[i])  #> {intervals[i]} ends before the new interval starts, so keep it as is.
                i += 1
            while i < n and intervals[i][0] <= end:
                start, end = min(start, intervals[i][0]), max(end, intervals[i][1])  #> Absorb {intervals[i]}: the new interval becomes [{start}, {end}].
                i += 1
            res.append([start, end])
            return res + intervals[i:]
        ''',
        java='''
        class Solution {
            public int[][] insert(int[][] intervals, int[] add) {
                List<int[]> res = new ArrayList<>();
                int i = 0, n = intervals.length, start = add[0], end = add[1];
                for (; i < n && intervals[i][1] < start; i++) res.add(intervals[i]); //>
                for (; i < n && intervals[i][0] <= end; i++) {
                    start = Math.min(start, intervals[i][0]);
                    end = Math.max(end, intervals[i][1]); //>
                }
                res.add(new int[]{start, end});
                for (; i < n; i++) res.add(intervals[i]);
                return res.toArray(new int[0][]);
            }
        }
        ''',
    )],
)

problem(
    id="fewest-removals",
    title="Fewest Removals for No Overlaps",
    difficulty="Medium",
    topics=["Array", "Intervals", "Greedy", "Sorting"],
    statement="""
    Return the minimum number of intervals to remove so the rest don't overlap. Intervals that only touch at an end
    point are fine.
    """,
    examples=[([[[1, 2], [2, 3], [3, 4], [1, 3]]], 1, "Remove [1, 3]."), ([[[1, 2], [1, 2], [1, 2]]], 2, None)],
    tests=[([[[1, 2], [2, 3]]], 0), ([[[0, 10], [1, 2], [3, 4]]], 1)],
    constraints=["1 ≤ intervals.length ≤ 10^5"],
    hints=["Keep the interval that ends earliest: it leaves the most room."],
    approaches=[approach(
        name="Greedy by End Time", pattern="greedy", time="O(n log n)", space="O(1) extra",
        idea="""
        Sort by end time and keep greedily: an interval that starts at or after the last kept end is kept; otherwise it overlaps and is removed. Ending early always leaves the most room for the rest.
        """,
        viz=viz(intervals=["intervals"], vars=["last_end", "removed"]),
        py='''
        def fewest_removals(intervals):
            intervals.sort(key=lambda iv: iv[1])
            last_end, removed = float("-inf"), 0
            for s, e in intervals:
                if s >= last_end:
                    last_end = e  #> Keep [{s}, {e}]; it ends at {e}.
                else:
                    removed += 1  #> [{s}, {e}] overlaps the last kept interval: remove it.
            return removed
        ''',
        java='''
        class Solution {
            public int fewestRemovals(int[][] intervals) {
                Arrays.sort(intervals, (a, b) -> Integer.compare(a[1], b[1]));
                long lastEnd = Long.MIN_VALUE;
                int removed = 0;
                for (int[] iv : intervals) {
                    if (iv[0] >= lastEnd) lastEnd = iv[1]; //>
                    else removed++; //>
                }
                return removed;
            }
        }
        ''',
    )],
)

problem(
    id="attend-all-meetings",
    title="Can You Attend Every Meeting?",
    difficulty="Easy",
    topics=["Array", "Intervals", "Sorting"],
    statement="""
    Given meeting times `[start, end]`, return `true` if one person can attend all of them (a meeting may start exactly
    when another ends).
    """,
    examples=[([[[0, 30], [5, 10], [15, 20]]], False, None), ([[[7, 10], [2, 4]]], True, None)],
    tests=[([[]], True), ([[[1, 5], [5, 8]]], True)],
    constraints=["0 ≤ meetings.length ≤ 10^4"],
    hints=["Sort by start and compare neighbours."],
    approaches=[approach(
        name="Sort + Neighbour Check", pattern="intervals", time="O(n log n)", space="O(1) extra",
        idea="""
        Sort by start time. Any conflict must be between neighbours, so check that each meeting starts no earlier than the previous one ends.
        """,
        viz=viz(intervals=["meetings"]),
        demo=[[[9, 10], [1, 3], [4, 8], [7, 9]]],
        py='''
        def can_attend(meetings):
            meetings.sort()
            for i in range(1, len(meetings)):  #> Does {meetings[i]} start before {meetings[i - 1]} ends?
                if meetings[i][0] < meetings[i - 1][1]:
                    return False  #> {meetings[i]} starts before {meetings[i - 1]} ends: a clash.
            return True
        ''',
        java='''
        class Solution {
            public boolean canAttend(int[][] meetings) {
                Arrays.sort(meetings, (a, b) -> a[0] - b[0]);
                for (int i = 1; i < meetings.length; i++) if (meetings[i][0] < meetings[i - 1][1]) return false; //>1,2
                return true;
            }
        }
        ''',
    )],
)

problem(
    id="rooms-needed",
    title="How Many Meeting Rooms?",
    difficulty="Medium",
    topics=["Array", "Intervals", "Two Pointers", "Sorting"],
    patterns=["two-pointers"],
    statement="""
    Given meeting times `[start, end]`, return the minimum number of rooms needed so no two overlapping meetings share
    a room. A room freed at time t can be reused by a meeting starting at t.
    """,
    examples=[([[[0, 30], [5, 10], [15, 20]]], 2, None), ([[[7, 10], [2, 4]]], 1, None)],
    tests=[([[[1, 5], [5, 8], [8, 9]]], 1), ([[[1, 10], [2, 7], [3, 19], [8, 12], [10, 20], [11, 30]]], 4)],
    constraints=["1 ≤ meetings.length ≤ 10^4"],
    hints=["Sort start times and end times separately.", "Walk them with two pointers like a timeline."],
    approaches=[approach(
        name="Two Pointers Over Starts and Ends", pattern="two-pointers", time="O(n log n)", space="O(n)",
        idea="""
        Sort all start times and, separately, all end times. Walk the starts with one pointer; a second pointer tracks the earliest meeting still running.

        If the next meeting starts before that earliest end, we need a new room; otherwise a room frees up and we reuse it.
        """,
        viz=viz(arrays=[("starts", {"s": "i"}), ("ends", {"e": "j"})], vars=["rooms", "best"]),
        py='''
        def rooms_needed(meetings):
            starts = sorted(m[0] for m in meetings)
            ends = sorted(m[1] for m in meetings)
            rooms = best = j = 0
            for i in range(len(starts)):
                if starts[i] < ends[j]:
                    rooms += 1  #> A meeting starts at {starts[i]} before the earliest one ends ({ends[j]}): open a room. Rooms: {rooms}.
                else:
                    j += 1  #> A meeting ended at {ends[j - 1]}, so reuse its room for the one at {starts[i]}.
                best = max(best, rooms)
            return best
        ''',
        java='''
        class Solution {
            public int roomsNeeded(int[][] meetings) {
                int n = meetings.length, rooms = 0, best = 0;
                int[] starts = new int[n], ends = new int[n];
                for (int i = 0; i < n; i++) { starts[i] = meetings[i][0]; ends[i] = meetings[i][1]; }
                Arrays.sort(starts);
                Arrays.sort(ends);
                for (int i = 0, j = 0; i < n; i++) {
                    if (starts[i] < ends[j]) rooms++; //>
                    else j++; //>
                    best = Math.max(best, rooms);
                }
                return best;
            }
        }
        ''',
    )],
)

problem(
    id="interval-overlaps",
    title="Overlaps of Two Schedules",
    difficulty="Medium",
    topics=["Array", "Intervals", "Two Pointers"],
    patterns=["two-pointers"],
    statement="""
    `a` and `b` are lists of closed intervals, each list sorted and non-overlapping. Return the intersection of the two
    schedules: every overlap `[max start, min end]` between an interval of `a` and an interval of `b`.
    """,
    examples=[([[[0, 2], [5, 10], [13, 23], [24, 25]], [[1, 5], [8, 12], [15, 24], [25, 26]]],
               [[1, 2], [5, 5], [8, 10], [15, 23], [24, 24], [25, 25]], None),
              ([[[1, 3], [5, 9]], []], [], None)],
    tests=[([[[1, 7]], [[3, 10]]], [[3, 7]]), ([[[1, 2]], [[3, 4]]], [])],
    constraints=["0 ≤ a.length, b.length ≤ 1000"],
    hints=["Compare the current interval from each list.", "Advance whichever ends first."],
    approaches=[approach(
        name="Two Pointers", pattern="two-pointers", time="O(n + m)", space="O(1) extra",
        idea="""
        Point I at an interval in `a` and J at one in `b`. Their overlap, if any, runs from the later start to the earlier end.

        Then advance the pointer whose interval ends first, because it can't overlap anything later in the other list.
        """,
        viz=viz(intervals=[("a", "a"), ("b", "b"), ("overlaps", "res")], vars=["i", "j"]),
        py='''
        def overlaps(a, b):
            res, i, j = [], 0, 0
            while i < len(a) and j < len(b):
                lo, hi = max(a[i][0], b[j][0]), min(a[i][1], b[j][1])
                if lo <= hi:
                    res.append([lo, hi])  #> {a[i]} and {b[j]} overlap on [{lo}, {hi}].
                if a[i][1] < b[j][1]:
                    i += 1
                else:
                    j += 1
            return res
        ''',
        java='''
        class Solution {
            public int[][] overlaps(int[][] a, int[][] b) {
                List<int[]> res = new ArrayList<>();
                for (int i = 0, j = 0; i < a.length && j < b.length; ) {
                    int lo = Math.max(a[i][0], b[j][0]), hi = Math.min(a[i][1], b[j][1]);
                    if (lo <= hi) res.add(new int[]{lo, hi}); //>
                    if (a[i][1] < b[j][1]) i++; else j++;
                }
                return res.toArray(new int[0][]);
            }
        }
        ''',
    )],
)

problem(
    id="fewest-arrows",
    title="Fewest Arrows to Pop Every Balloon",
    difficulty="Medium",
    topics=["Array", "Intervals", "Greedy", "Sorting"],
    statement="""
    Balloons span horizontal ranges `[start, end]`. An arrow shot straight up at position x pops every balloon with
    `start ≤ x ≤ end`. Return the minimum number of arrows that pop all balloons.
    """,
    examples=[([[[10, 16], [2, 8], [1, 6], [7, 12]]], 2, "Shoot at 6 and 11."), ([[[1, 2], [3, 4], [5, 6], [7, 8]]], 4, None)],
    tests=[([[[1, 2], [2, 3], [3, 4], [4, 5]]], 2), ([[[-5, 5]]], 1)],
    constraints=["1 ≤ points.length ≤ 10^5"],
    hints=["Shoot at the end of the balloon that ends first."],
    approaches=[approach(
        name="Greedy by End", pattern="greedy", time="O(n log n)", space="O(1) extra",
        idea="""
        Sort balloons by their end. Shoot the first arrow at the end of the earliest-ending balloon; it pops every balloon that starts by then. The next balloon that starts after the arrow needs a new arrow at its own end.
        """,
        viz=viz(intervals=["points"], vars=["arrow", "arrows"]),
        py='''
        def fewest_arrows(points):
            points.sort(key=lambda p: p[1])
            arrows, arrow = 0, float("-inf")
            for s, e in points:
                if s > arrow:
                    arrow, arrows = e, arrows + 1  #> [{s}, {e}] isn't popped yet, so shoot arrow {arrows} at {e}.
            return arrows
        ''',
        java='''
        class Solution {
            public int fewestArrows(int[][] points) {
                Arrays.sort(points, (a, b) -> Integer.compare(a[1], b[1]));
                int arrows = 0;
                long arrow = Long.MIN_VALUE;
                for (int[] p : points) if (p[0] > arrow) { arrow = p[1]; arrows++; } //>
                return arrows;
            }
        }
        ''',
    )],
)

problem(
    id="common-free-slot",
    title="First Free Slot for Two Calendars",
    difficulty="Medium",
    topics=["Intervals", "Two Pointers", "Scheduling"],
    patterns=["two-pointers"],
    statement="""
    Two people's busy times `a` and `b` are sorted, non-overlapping intervals `[start, end)`. Within the working day
    `[day_start, day_end)`, return the earliest slot `[t, t + duration]` when both are free, or `[]` if none exists.
    """,
    examples=[([[[9, 10], [12, 13]], [[9, 11], [14, 15]], 9, 17, 1], [11, 12], None),
              ([[[9, 17]], [], 9, 17, 1], [], "The first person is busy all day.")],
    tests=[([[], [], 8, 9, 1], [8, 9]), ([[[10, 11]], [[11, 12]], 10, 14, 2], [12, 14]), ([[[9, 12]], [[13, 14]], 9, 14, 2], [])],
    constraints=["0 ≤ a.length, b.length ≤ 10^4"],
    hints=["Merge both busy lists with two pointers, in start order.", "Track the end of the busy time so far; a gap before the next start is free."],
    approaches=[approach(
        name="Two-Pointer Merge", pattern="two-pointers", time="O(n + m)", space="O(1)",
        idea="""
        Walk both busy lists like a merge, always taking the interval that starts first. Keep `free_from`, the moment everyone is free again.

        If the next busy interval starts at least `duration` after `free_from`, that gap is the answer. Otherwise push `free_from` past it. At the end, check the gap before the day ends.
        """,
        viz=viz(intervals=[("a busy", "a"), ("b busy", "b")], vars=["free_from", "i", "j"]),
        py='''
        def free_slot(a, b, day_start, day_end, duration):
            i = j = 0
            free_from = day_start
            while i < len(a) or j < len(b):
                if j == len(b) or (i < len(a) and a[i][0] <= b[j][0]):
                    s, e = a[i]
                    i += 1
                else:
                    s, e = b[j]
                    j += 1
                if min(s, day_end) - free_from >= duration:
                    return [free_from, free_from + duration]  #> The gap from {free_from} to {s} fits {duration}.
                free_from = max(free_from, e)  #> Busy [{s}, {e}): everyone is free again at {free_from}.
            return [free_from, free_from + duration] if day_end - free_from >= duration else []
        ''',
        java='''
        class Solution {
            public int[] freeSlot(int[][] a, int[][] b, int dayStart, int dayEnd, int duration) {
                int i = 0, j = 0, freeFrom = dayStart;
                while (i < a.length || j < b.length) {
                    int[] iv = (j == b.length || (i < a.length && a[i][0] <= b[j][0])) ? a[i++] : b[j++];
                    if (Math.min(iv[0], dayEnd) - freeFrom >= duration) return new int[]{freeFrom, freeFrom + duration}; //>
                    freeFrom = Math.max(freeFrom, iv[1]); //>
                }
                return dayEnd - freeFrom >= duration ? new int[]{freeFrom, freeFrom + duration} : new int[0];
            }
        }
        ''',
    )],
)
