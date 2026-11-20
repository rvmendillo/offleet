"""Sliding Window problems."""
from dsl import problem, approach, viz

problem(
    id="longest-unique-substring",
    title="Longest Stretch Without Repeats",
    difficulty="Medium",
    topics=["String", "Sliding Window", "Hash Map"],
    statement="""
    Given a string `s`, return the length of the longest contiguous piece of `s` in which no character appears twice.
    """,
    examples=[(["abcabcbb"], 3, "\"abc\" has no repeats and nothing longer works."), (["bbbb"], 1, None)],
    tests=[([""], 0), (["pwwkew"], 3), (["abba"], 2), (["dvdf"], 3)],
    constraints=["0 ≤ s.length ≤ 5·10^4"],
    hints=["Keep a window with no repeats.", "When a repeat enters, jump the left edge past the previous copy."],
    approaches=[approach(
        name="Sliding Window", pattern="sliding-window", time="O(n)", space="O(k)",
        idea="""
        Keep a window from L to R that never contains a repeat, and remember the last index where each character was seen.

        When the new character at R was already seen inside the window, jump L just past that earlier copy. The window is valid again, so we update the best length.
        """,
        why="R visits every character once and L only moves forward, so the work is linear. The map holds at most one entry per distinct character, k.",
        viz=viz(arr="s", ptr={"L": "l", "R": "r"}, win=("l", "r"), maps=[("last seen", "last")], vars=["best"]),
        py='''
        def longest_unique(s):
            last, l, best = {}, 0, 0
            for r, ch in enumerate(s):  #> R moves to index {r}, the letter {q(ch)}.
                if last.get(ch, -1) >= l:
                    l = last[ch] + 1  #> {q(ch)} is already in the window, so L jumps to index {l}.
                last[ch] = r
                best = max(best, r - l + 1)  #> The window is {q(s[l:r+1])}, length {r - l + 1}. Best so far: {best}.
            return best
        ''',
        java='''
        class Solution {
            public int longestUnique(String s) {
                Map<Character, Integer> last = new HashMap<>();
                int l = 0, best = 0;
                for (int r = 0; r < s.length(); r++) { //>
                    char ch = s.charAt(r);
                    if (last.getOrDefault(ch, -1) >= l) l = last.get(ch) + 1; //>
                    last.put(ch, r);
                    best = Math.max(best, r - l + 1); //>
                }
                return best;
            }
        }
        ''',
    )],
)
