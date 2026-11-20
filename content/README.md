# Offleet content authoring guide

All app content is authored as Python modules and compiled by `content/tools/build.py` into JSON under
`Offleet/Resources/Content/` (bundled into the iOS app as a folder resource).

```
python3 content/tools/build.py                 # verify everything + write JSON
python3 content/tools/build.py --check         # verify only (used in CI)
python3 content/tools/build.py --only sliding_window --no-java   # quick iteration
python3 content/tools/show.py <problem-id>     # read a generated tutorial as text
```

The build **fails** if any Python or Java solution fails a test, a narration template errors, or a field is
missing. Problem statements, examples and explanations are original writing — never paste text from other sites.

## Modules (order = numbering in the app)

- `problems/*.py` — algorithm problems, listed in `PROBLEM_MODULES` in `build.py`.
- `frameworks/spring_boot.py`, `frameworks/angular.py` — framework exercises (code walkthroughs).
- `reviewer/{cs,ai,adv_math,calculus}.py` — bite-sized reviewer cards.
- `books/handbook.py` — hand-written audiobook chapters (The Patterns Handbook).

## Algorithm problem

```python
from dsl import problem, approach, viz

problem(
    id="pair-sum-sorted", title="...", difficulty="Easy|Medium|Hard",
    topics=["Array", "Two Pointers"],
    statement="""markdown, `code` and **bold** allowed""",
    examples=[(args, expected, "why (optional)"), ...],  # shown in the app AND used as tests
    tests=[(args, expected), ...],                         # extra hidden tests
    constraints=[...], hints=[...],
    eli5="optional plain-language restatement spoken in the tutorial",
    demo=args,            # optional tutorial input (default: first example) — keep it small
    check="exact",        # exact | unordered | deep-unordered | inner-sorted | float
    out="ret",            # ret | arg0 (in-place) | arg0-prefix (first `ret` items of arg0)
    design=False,         # True: args = (ops, op_args), expected = outputs (first is None)
    approaches=[approach(...), ...],   # first approach = default; prefer Sliding Window / Two Pointers first
)
```

`args` is the positional argument list. Types come from the Java signature: `ListNode` / `TreeNode` /
`Node` args are given as lists (level-order with `None` for trees) and converted automatically.

## Approach

```python
approach(
    name="Two Pointers", pattern="two-pointers",   # pattern id from dsl.PATTERNS
    time="O(n)", space="O(1)",
    idea="""1–3 short paragraphs for beginners (each paragraph = one tutorial frame)""",
    why="""why the complexity holds (spoken on the complexity frame)""",
    viz=viz(...),
    py='''python with #> narration markers''',
    java='''java `class Solution` with //> markers''',
)
```

### Narration markers

- Python: `code  #> text with {expressions}` — an f-string evaluated with the function's locals right
  **after** the line runs. On `if`/`for`/`while` headers it is spoken only when the body runs. On a line
  that calls another solution function it is spoken **before** the call (start the text with `^` to speak it
  after the call returns instead). On `return` lines `{ret}` is the
  returned value. Helpers: `q(x)` quotes strings, `lst(xs)`, `yn(b)`, `plural(n, "word")`, `fv(x)`, `chain(node)`
  (values of a linked list).
- Java: `code //>` marks the line matching the next Python marker (in order). `//>3` or `//>2,3` maps
  explicit Python marker numbers. Markers are stripped from displayed code.
- Keep narration friendly and concrete: say values, not variable syntax ("4 plus 6 is 10").

### viz spec (all optional; expressions are Python strings evaluated each frame)

```python
viz(
  arr="nums", ptr={"L": "l", "R": "r"}, win=("l", "r"), marks="[i for i in ...]", label="nums",
  arrays=[("expr", {"i": "i"}, ("lo", "hi"), "marks_expr", "label"), ...],
  vars=["best", ("window", "s[l:r+1]")],
  maps=[("seen", "seen")],            # dict / Counter / set
  stacks=["stack"], queues=["q"],
  grid=("grid", {"you": ("r", "c")}, "marks_expr_cells", "label"),
  table=("dp", {"i": "i"} or {"cell": ("i", "j")}, None, "dp"),
  linked=("head", {"prev": "prev", "cur": "cur"}),   # draws all ListNodes, dims unreachable ones
  tree=("root", {"node": "node"}, "marks_expr_nodes"),
  graph=("adj", {"at": "node"}, "visited_expr", directed_bool),
  intervals=["intervals", ("merged", "res")],
  bits=["n", ("result", "res")],
  out="res",
)
```

## Framework problem (Spring Boot / Angular)

```python
problem(id=..., title=..., difficulty=..., topics=[...], statement="...",
        examples=[("request/usage", "response/result", "why")],   # free text
        approaches=[approach(name="...", pattern="spring-boot", time="—", space="—", idea="...",
            files=[{"lang": "java", "name": "HelloController.java", "src": dedent('''...''')}],
            steps=[("needle in a code line", "narration", optional_file_index), ...])])
```

## Reviewer bite

```python
subject(id="calculus", title="Calculus", icon="function", color="#F472B6", blurb="...",
        units=[unit("Limits", bite("limit-def", "What is a limit?", "TL;DR", ["point", ...],
               formula="lim x→a f(x) = L", say_formula="the limit as x approaches a of f of x is L",
               example="...", tip="...", quiz=("Q?", ["A", "B", "C", "D"], 1, "why"))) ])
```
