"""Authoring DSL for Offleet content.

Content modules (content/problems/*.py, content/frameworks/*.py,
content/reviewer/*.py, content/books/*.py) call these helpers; build.py
imports the modules in a fixed order, verifies everything and exports JSON
for the iOS app. See content/README.md for the full authoring guide.
"""
from __future__ import annotations

import textwrap

PROBLEMS: list[dict] = []
SUBJECTS: list[dict] = []
CHAPTERS: list[dict] = []

_state = {"category": "algorithms", "module": None}

# id, name, one-line summary, SF Symbol, hex colour
PATTERNS = [
    ("two-pointers", "Two Pointers", "Two indices walk toward each other (or the same way) so one pass replaces a nested loop.", "arrow.left.and.right", "#22D3EE"),
    ("sliding-window", "Sliding Window", "Grow the right edge, shrink the left edge, and keep a running summary of what is inside.", "rectangle.split.3x1", "#FBBF24"),
    ("fast-slow", "Fast & Slow Pointers", "One pointer moves twice as fast: they meet on a cycle or stop at the middle.", "hare", "#F472B6"),
    ("hash-map", "Hash Map", "Remember what you have seen for instant lookups.", "number.square", "#A78BFA"),
    ("prefix-sum", "Prefix Sum", "Running totals turn any range sum into one subtraction.", "sum", "#34D399"),
    ("binary-search", "Binary Search", "Throw away half of the search space every step.", "magnifyingglass", "#60A5FA"),
    ("stack", "Stack", "Last in, first out: perfect for matching pairs and undo.", "square.stack.3d.up", "#F59E0B"),
    ("monotonic-stack", "Monotonic Stack", "Keep the stack sorted to find the next bigger or smaller item.", "chart.bar", "#FB923C"),
    ("heap", "Heap", "Always grab the smallest or largest item quickly.", "triangle", "#E879F9"),
    ("intervals", "Intervals", "Sort by start time, then merge or sweep.", "calendar", "#2DD4BF"),
    ("linked-list", "Linked List", "Rewire next pointers carefully, often with a dummy head.", "link", "#38BDF8"),
    ("tree", "Trees", "Recursion for depth, a queue for levels.", "tree", "#4ADE80"),
    ("graph", "Graphs", "BFS for fewest steps, DFS to explore, topological order for dependencies.", "point.3.connected.trianglepath.dotted", "#818CF8"),
    ("backtracking", "Backtracking", "Choose, explore, un-choose.", "arrow.uturn.backward", "#F87171"),
    ("dp", "Dynamic Programming", "Solve each small subproblem once and build up the answer.", "square.grid.3x3", "#C084FC"),
    ("greedy", "Greedy", "Take the locally best step when you can prove it is safe.", "bolt", "#FACC15"),
    ("bits", "Bit Manipulation", "Binary tricks with XOR, AND and shifts.", "cpu", "#94A3B8"),
    ("math", "Math", "Number properties and clever arithmetic.", "function", "#FDA4AF"),
    ("trie", "Trie", "A tree of characters for fast prefix lookups.", "text.magnifyingglass", "#5EEAD4"),
    ("union-find", "Union-Find", "Track connected groups with near-constant-time merges.", "circle.grid.cross", "#93C5FD"),
    ("matrix", "Matrix", "Walk 2D grids by rows, columns and layers.", "tablecells", "#FCD34D"),
    ("sorting", "Sorting", "Sort first and the problem often becomes easy.", "arrow.up.arrow.down", "#A3E635"),
    ("design", "Design", "Combine data structures into a class with fast operations.", "cube", "#F0ABFC"),
    ("spring-boot", "Spring Boot", "Build production-style Java back ends with Spring Boot.", "leaf", "#6DB33F"),
    ("angular", "Angular", "Build modern front ends with Angular, signals and RxJS.", "a.circle", "#DD0031"),
]
PATTERN_IDS = {p[0] for p in PATTERNS}


def dedent(s: str | None) -> str | None:
    if s is None:
        return None
    return textwrap.dedent(s).strip("\n")


def category(name: str):
    """Set the category for problems defined after this call in a module."""
    _state["category"] = name


def problem(**kw):
    """Register a problem.

    Required: id, title, difficulty, topics, statement, approaches.
    Algorithms also need tests/examples; frameworks use walkthrough steps.
    """
    kw.setdefault("category", _state["category"])
    kw["statement"] = dedent(kw["statement"])
    PROBLEMS.append(kw)
    return kw


def approach(**kw):
    for key in ("py", "java", "ts", "html", "idea", "why"):
        if key in kw:
            kw[key] = dedent(kw[key])
    for f in kw.get("files", []):
        f["src"] = dedent(f["src"])
    return kw


def file(name, src, lang=None):
    """A source file for framework walkthroughs; language inferred from the extension."""
    ext = name.rsplit(".", 1)[-1]
    lang = lang or {"java": "java", "ts": "typescript", "html": "html", "yml": "yaml", "yaml": "yaml",
                    "properties": "properties", "json": "json", "py": "python"}.get(ext, ext)
    return {"name": name, "lang": lang, "src": src}


def viz(**kw):
    return kw


def subject(**kw):
    """Reviewer subject: id, title, icon, color, blurb, units=[unit(...)]"""
    SUBJECTS.append(kw)
    return kw


def unit(title, *bites, blurb=""):
    return {"title": title, "blurb": blurb, "bites": list(bites)}


def bite(id, title, tldr, points, *, formula=None, say_formula=None, example=None, tip=None, quiz=None, say=None,
         flow=None):
    """A bite-sized reviewer card.

    quiz = (question, [options...], correct_index, why)
    say  = optional full spoken script (otherwise generated from the fields)
    flow = optional architecture flows, e.g. ["Client → Load Balancer → API → Cache → DB"]
    """
    return dict(id=id, title=title, tldr=tldr, points=points, formula=formula, say_formula=say_formula,
                example=example, tip=tip, quiz=quiz, say=say, flow=flow)


def chapter(book, title, text, *, id=None):
    """Audiobook chapter for a hand-written book (e.g. the patterns handbook)."""
    CHAPTERS.append(dict(book=book, title=title, text=dedent(text), id=id))


# ------------------------------------------------------------------ career paths
PATHS: list[dict] = []


def career_path(**kw):
    """A roadmap: id, title, subtitle, icon, color, blurb, stages=[stage(...)]."""
    PATHS.append(kw)
    return kw


def stage(title, blurb, *items):
    return {"title": title, "blurb": blurb, "items": list(items)}


def P(*ids):
    """Problems by id."""
    return [{"kind": "problem", "id": i} for i in ids]


def B(*ids):
    """Reviewer bites by id."""
    return [{"kind": "bite", "id": i} for i in ids]


def S(subject_id):
    """A whole reviewer subject."""
    return [{"kind": "subject", "id": subject_id}]


def BOOK(book_id):
    return [{"kind": "book", "id": book_id}]


def TRACK(track_id):
    return [{"kind": "track", "id": track_id}]


def MOCK(focus, title):
    """Start a mock interview filtered by focus, e.g. 'pattern:sliding-window' or 'cat:ai-engineering'."""
    return [{"kind": "mock", "id": focus, "title": title}]


def TIP(text):
    return [{"kind": "tip", "id": "tip", "title": text}]
