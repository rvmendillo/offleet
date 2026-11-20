"""Generate animated tutorial frames by actually running a solution.

Narration lives in the Python solution as end-of-line comments:

    l += 1  #> Too small, so L moves right to index {l}.

`#>` text is an f-string evaluated with the function's variables right
*after* that line runs (on `if`/`for`/`while` headers it is only spoken when
the body actually runs). A viz spec describes what to draw for every frame
(arrays with pointers and windows, maps, stacks, grids, linked lists, trees,
graphs, DP tables...). The result is a list of frames the iOS player animates
while the presenter speaks.
"""
from __future__ import annotations

import ast
import copy
import math
import re
import sys
from collections import deque

from runtime import ListNode, TreeNode, Node, reset_registries, convert_arg, build_list

FILENAME = "<offleet-solution>"
PY_MARK = re.compile(r"\s*#>\s?(.*)$")
JAVA_MARK = re.compile(r"\s*//>\s*([\d,\s]*)$")
TS_MARK = JAVA_MARK


class AuthoringError(Exception):
    pass


class TooManyFrames(Exception):
    pass


# ------------------------------------------------------------ marker parsing
def split_py(code: str):
    """Strip `#>` markers. Returns (display_code, {line: (idx, template)})."""
    out, marks, idx = [], {}, 0
    for i, line in enumerate(code.split("\n"), 1):
        m = PY_MARK.search(line)
        if m and not _in_string(line, m.start()):
            idx += 1
            marks[i] = (idx, m.group(1).strip())
            line = line[: m.start()].rstrip()
        out.append(line)
    return "\n".join(out), marks


def _in_string(line, pos):
    quote = None
    for ch in line[:pos]:
        if quote:
            if ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
    return quote is not None


def split_c_like(code: str):
    """Strip `//>` markers from Java/TypeScript. Returns (display, {marker_idx: line})."""
    out, mapping, auto = [], {}, 0
    for i, line in enumerate(code.split("\n"), 1):
        m = JAVA_MARK.search(line)
        if m:
            nums = [int(x) for x in m.group(1).replace(" ", "").split(",") if x]
            if not nums:
                auto += 1
                nums = [auto]
            else:
                auto = max(nums)
            for k in nums:
                mapping.setdefault(k, i)
            line = line[: m.start()].rstrip()
        out.append(line)
    return "\n".join(out), mapping


def compound_ranges(code: str):
    """Map header line of if/for/while -> (first body line, last body line)."""
    tree = ast.parse(code)
    ranges = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.For, ast.While, ast.With)):
            body = node.body
            ranges[node.lineno] = (body[0].lineno, max(getattr(b, "end_lineno", b.lineno) for b in body))
    return ranges


def entry_name(code: str, design=False):
    tree = ast.parse(code)
    for node in tree.body:
        if design and isinstance(node, ast.ClassDef):
            return node.name
        if not design and isinstance(node, ast.FunctionDef):
            return node.name
    raise AuthoringError("no entry point found")


def py_params(code: str):
    tree = ast.parse(code)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            return [a.arg for a in node.args.args if a.arg != "self"]
    return []


# ------------------------------------------------------------ value display
def fv(v, depth=0):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        if math.isinf(v):
            return "∞" if v > 0 else "-∞"
        if v == int(v) and abs(v) < 1e15:
            return str(int(v)) if abs(v) >= 1 or v == 0 else f"{v:g}"
        return f"{v:.3f}".rstrip("0").rstrip(".")
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return v
    if isinstance(v, (ListNode, TreeNode, Node)):
        return f"({v.val})"
    if depth > 2:
        return "…"
    if isinstance(v, (list, tuple, deque)):
        items = [fv(x, depth + 1) for x in list(v)[:10]]
        return "[" + ", ".join(items) + (", …" if len(v) > 10 else "") + "]"
    if isinstance(v, (set, frozenset)):
        items = sorted((fv(x, depth + 1) for x in v))[:10]
        return "{" + ", ".join(items) + (", …" if len(v) > 10 else "") + "}"
    if isinstance(v, dict):
        items = [f"{fv(k, depth + 1)}: {fv(x, depth + 1)}" for k, x in list(v.items())[:8]]
        return "{" + ", ".join(items) + (", …" if len(v) > 8 else "") + "}"
    return str(v)


def _cell(v):
    s = fv(v, 1)
    return s if len(s) <= 6 else s[:5] + "…"


# ------------------------------------------------------------ viz components
def _ev(expr, g, ctx):
    if callable(expr):
        return expr(ctx)
    return eval(expr, g, ctx)


def _seq(v):
    if isinstance(v, str):
        return list(v)
    if isinstance(v, (list, tuple, deque)):
        return list(v)
    raise TypeError("not a sequence")


def build_state(spec: dict, g, ctx, seen_ok: set):
    st = {}

    def attempt(key, fn):
        try:
            res = fn()
        except Exception:
            return None
        if res is not None:
            seen_ok.add(key)
        return res

    arrays = []
    arr_specs = list(spec.get("arrays", []))
    if "arr" in spec:
        arr_specs.insert(0, (spec["arr"], spec.get("ptr", {}), spec.get("win"), spec.get("marks"), spec.get("label")))
    for k, a in enumerate(arr_specs):
        a = tuple(a) + (None,) * (5 - len(a))
        expr, ptrs, win, marks, label = a[:5]

        def one(expr=expr, ptrs=ptrs, win=win, marks=marks, label=label):
            vals = _seq(_ev(expr, g, ctx))
            comp = {"n": label or (expr if isinstance(expr, str) else "array"), "v": [_cell(x) for x in vals]}
            ps = []
            for lbl, pe in (ptrs or {}).items():
                try:
                    i = _ev(pe, g, ctx)
                except Exception:
                    continue
                if isinstance(i, int) and not isinstance(i, bool) and -1 <= i <= len(vals):
                    ps.append({"l": lbl, "i": i})
            if ps:
                comp["p"] = ps
            if win:
                try:
                    lo, hi = _ev(win[0], g, ctx), _ev(win[1], g, ctx)
                    if isinstance(lo, int) and isinstance(hi, int):
                        comp["w"] = [lo, hi]
                except Exception:
                    pass
            if marks:
                try:
                    ms = _ev(marks, g, ctx)
                    comp["m"] = sorted({int(i) for i in ms if 0 <= int(i) < len(vals)})
                except Exception:
                    pass
            return comp
        r = attempt(f"arr{k}", one)
        if r:
            arrays.append(r)
    if arrays:
        st["arrays"] = arrays

    vars_ = []
    for item in spec.get("vars", []):
        label, expr = (item, item) if isinstance(item, str) else item
        try:
            val = _ev(expr, g, ctx)
            vars_.append({"k": label, "v": fv(val) if not isinstance(val, str) else f'"{val}"'})
            seen_ok.add(f"var:{label}")
        except Exception:
            pass
    if vars_:
        st["vars"] = vars_

    maps = []
    for item in spec.get("maps", []):
        label, expr = (item, item) if isinstance(item, str) else item

        def one(expr=expr, label=label):
            m = _ev(expr, g, ctx)
            if isinstance(m, dict):
                entries = [{"k": fv(k, 1), "v": fv(v, 1)} for k, v in list(m.items())[:16]]
            elif isinstance(m, (set, frozenset)):
                entries = [{"k": fv(k, 1), "v": ""} for k in sorted(m, key=lambda x: (str(type(x)), x))[:16]]
            else:
                raise TypeError
            return {"n": label, "e": entries}
        r = attempt(f"map:{label}", one)
        if r:
            maps.append(r)
    if maps:
        st["maps"] = maps

    stacks = []
    for kind in ("stacks", "queues"):
        for item in spec.get(kind, []):
            label, expr = (item, item) if isinstance(item, str) else item

            def one(expr=expr, label=label, kind=kind):
                vals = list(_ev(expr, g, ctx))
                return {"n": label, "v": [fv(x, 1) for x in vals[-14:]], "t": "stack" if kind == "stacks" else "queue"}
            r = attempt(f"{kind}:{label}", one)
            if r:
                stacks.append(r)
    if stacks:
        st["stacks"] = stacks

    for key in ("grid", "table"):
        if key in spec:
            gs = tuple(spec[key]) + (None,) * 4
            expr, ptrs, marks, label = gs[0], gs[1], gs[2], gs[3]

            def one(expr=expr, ptrs=ptrs, marks=marks, label=label, key=key):
                val = _ev(expr, g, ctx)
                rows = val if val and isinstance(val[0], (list, tuple, str)) else [val]
                rows = [[_cell(c) for c in row] for row in rows]
                comp = {"n": label or (expr if isinstance(expr, str) else key), "v": rows}
                ps = []
                for lbl, pe in (ptrs or {}).items():
                    try:
                        pos = pe if isinstance(pe, tuple) else (None, pe)
                        r_ = 0 if pos[0] is None else _ev(pos[0], g, ctx)
                        c_ = _ev(pos[1], g, ctx)
                        if 0 <= r_ < len(rows) and 0 <= c_ < len(rows[r_]):
                            ps.append({"l": lbl, "r": r_, "c": c_})
                    except Exception:
                        continue
                if ps:
                    comp["p"] = ps
                if marks:
                    try:
                        cells = _ev(marks, g, ctx)
                        comp["m"] = [[int(a), int(b)] for a, b in cells][:200]
                    except Exception:
                        pass
                return comp
            r = attempt(key, one)
            if r:
                st[key] = r

    if "linked" in spec:
        ls = tuple(spec["linked"]) + (None,) * 2
        roots, ptrs = ls[0], ls[1] or {}

        def one(roots=roots, ptrs=ptrs):
            reg = ListNode.registry
            index = {id(n): k for k, n in enumerate(reg)}
            ps, reach_from = [], []
            for lbl, pe in ptrs.items():
                try:
                    node = _ev(pe, g, ctx)
                except Exception:
                    continue
                if isinstance(node, ListNode) and id(node) in index:
                    ps.append({"l": lbl, "id": index[id(node)]})
                    reach_from.append(node)
            for rexpr in ([roots] if isinstance(roots, str) else (roots or [])):
                try:
                    node = _ev(rexpr, g, ctx)
                    if isinstance(node, ListNode):
                        reach_from.append(node)
                    elif isinstance(node, list):
                        reach_from.extend(x for x in node if isinstance(x, ListNode))
                except Exception:
                    pass
            reach = set()
            for node in reach_from:
                while node is not None and id(node) not in reach:
                    reach.add(id(node))
                    node = node.next
            max_row = max([n._row for n in reg if n._row is not None] or [0])
            new_col = 0
            nodes = []
            for k, n in enumerate(reg):
                row, col = n._row, n._col
                if row is None:
                    row, col = max_row + 1, new_col
                    new_col += 1
                nodes.append({"id": k, "v": _cell(n.val), "nx": index.get(id(n.next), -1) if n.next is not None else -1,
                              "row": row, "col": col, "dim": id(n) not in reach})
            comp = {"nodes": nodes}
            if ps:
                comp["p"] = ps
            return comp
        r = attempt("linked", one)
        if r:
            st["linked"] = r

    if "tree" in spec:
        ts = tuple(spec["tree"]) + (None,) * 3
        rexpr, ptrs, marks = ts[0], ts[1] or {}, ts[2]

        def one(rexpr=rexpr, ptrs=ptrs, marks=marks):
            root = _ev(rexpr, g, ctx)
            reg = TreeNode.registry
            index = {id(n): k for k, n in enumerate(reg)}
            nodes, order = [], [0]

            def walk(n, d):
                if n is None or len(nodes) > 63:
                    return
                walk(n.left, d + 1)
                nodes.append({"id": index.get(id(n), -1), "v": _cell(n.val), "x": order[0], "y": d,
                              "l": index.get(id(n.left), -1) if n.left else -1,
                              "r": index.get(id(n.right), -1) if n.right else -1})
                order[0] += 1
                walk(n.right, d + 1)
            walk(root, 0)
            comp = {"nodes": nodes}
            ps = []
            for lbl, pe in ptrs.items():
                try:
                    node = _ev(pe, g, ctx)
                except Exception:
                    continue
                if isinstance(node, TreeNode) and id(node) in index:
                    ps.append({"l": lbl, "id": index[id(node)]})
            if ps:
                comp["p"] = ps
            if marks:
                try:
                    ms = _ev(marks, g, ctx)
                    comp["m"] = sorted({index[id(x)] for x in ms if isinstance(x, TreeNode) and id(x) in index})
                except Exception:
                    pass
            return comp
        r = attempt("tree", one)
        if r:
            st["tree"] = r

    if "graph" in spec:
        gs = tuple(spec["graph"]) + (None,) * 4
        aexpr, ptrs, visited, directed = gs[0], gs[1] or {}, gs[2], bool(gs[3])

        def one(aexpr=aexpr, ptrs=ptrs, visited=visited, directed=directed):
            adj = _ev(aexpr, g, ctx)
            items = list(adj.items()) if isinstance(adj, dict) else list(enumerate(adj))
            keys = [fv(k, 1) for k, _ in items]
            for _, nb in items:
                for v in nb:
                    if fv(v, 1) not in keys:
                        keys.append(fv(v, 1))
            edges, seen_e = [], set()
            for k, nb in items:
                for v in nb:
                    a, b = fv(k, 1), fv(v, 1)
                    if not directed and (b, a) in seen_e:
                        continue
                    seen_e.add((a, b))
                    edges.append({"a": a, "b": b})
            comp = {"nodes": keys, "edges": edges, "dir": directed}
            ps = []
            for lbl, pe in ptrs.items():
                try:
                    ps.append({"l": lbl, "k": fv(_ev(pe, g, ctx), 1)})
                except Exception:
                    continue
            if ps:
                comp["p"] = ps
            if visited:
                try:
                    comp["vis"] = sorted({fv(x, 1) for x in _ev(visited, g, ctx)})
                except Exception:
                    pass
            return comp
        r = attempt("graph", one)
        if r:
            st["graph"] = r

    ivs = []
    for item in spec.get("intervals", []):
        label, expr = (item, item) if isinstance(item, str) else item

        def one(expr=expr, label=label):
            vals = [[float(a), float(b)] for a, b in _ev(expr, g, ctx)]
            return {"n": label, "v": vals}
        r = attempt(f"iv:{label}", one)
        if r is not None:
            ivs.append(r)
    if ivs:
        st["intervals"] = ivs

    bits = []
    for item in spec.get("bits", []):
        label, expr = (item, item) if isinstance(item, str) else item
        try:
            v = int(_ev(expr, g, ctx))
            bits.append({"k": label, "v": str(v), "b": format(v & 0xFFFFFFFF if v < 0 else v, "b")})
            seen_ok.add(f"bits:{label}")
        except Exception:
            pass
    if bits:
        width = max(4, max(len(b["b"]) for b in bits))
        for b in bits:
            b["b"] = b["b"].rjust(width, "0")
        st["bits"] = bits

    if "out" in spec:
        item = spec["out"]
        label, expr = (item, item) if isinstance(item, str) else item

        def one(expr=expr, label=label):
            v = _ev(expr, g, ctx)
            vals = list(v) if isinstance(v, (list, tuple, deque, str)) else [v]
            return {"n": label, "v": [fv(x, 1) for x in vals[:24]]}
        r = attempt("out", one)
        if r:
            st["out"] = r
    return st


# ------------------------------------------------------------ narration helpers
def _q(x):
    return f"'{x}'" if isinstance(x, str) else fv(x)


def _lst(xs):
    xs = list(xs)
    return ", ".join(fv(x, 1) for x in xs) if xs else "nothing"


def _yn(b):
    return "yes" if b else "no"


def _plural(n, word):
    return f"{n} {word}" + ("" if n == 1 else "s")


def _chain(node, limit=40):
    out, seen = [], set()
    while node is not None and id(node) not in seen and len(out) < limit:
        seen.add(id(node))
        out.append(node.val)
        node = node.next
    return out


HELPERS = {"q": _q, "lst": _lst, "yn": _yn, "plural": _plural, "fv": fv, "chain": _chain}


# ------------------------------------------------------------ the tracer
class _Tracer:
    def __init__(self, marks, ranges, spec, g, max_frames):
        self.marks, self.ranges, self.spec, self.g = marks, ranges, spec, g
        self.frames, self.pending = [], {}
        self.max_frames = max_frames
        self.seen_ok = set()

    def global_trace(self, frame, event, arg):
        if frame.f_code.co_filename != FILENAME:
            return None
        if event == "call" and not frame.f_code.co_name.startswith("<"):
            caller = frame.f_back
            if caller is not None and caller.f_code.co_filename == FILENAME:
                p = self.pending.get(id(caller))
                if p and p[0] not in self.ranges and not p[2].startswith("^"):
                    del self.pending[id(caller)]
                    self._emit(caller, p, None, False)
        return self.local_trace

    def local_trace(self, frame, event, arg):
        if event == "line":
            self._resolve(frame, frame.f_lineno, None, False)
            ln = frame.f_lineno
            if ln in self.marks:
                self.pending[id(frame)] = (ln,) + self.marks[ln]
        elif event == "return":
            self._resolve(frame, frame.f_lineno, arg, True)
        return self.local_trace

    def _resolve(self, frame, cur, retval, is_ret):
        p = self.pending.pop(id(frame), None)
        if not p:
            return
        rng = self.ranges.get(p[0])
        if rng and not (rng[0] <= cur <= rng[1]):
            return
        self._emit(frame, p, retval, is_ret)

    def _context(self, frame, retval, is_ret):
        chain, f = [], frame
        while f is not None and f.f_code.co_filename == FILENAME:
            chain.append(f)
            f = f.f_back
        ctx = {}
        for fr in reversed(chain):
            ctx.update(dict(fr.f_locals))
        ctx["ARGS"] = dict(chain[-1].f_locals)  # the outermost call's variables (e.g. the whole tree's root)
        if is_ret:
            ctx["__return__"] = retval
            ctx["ret"] = retval
        return ctx

    def _emit(self, frame, p, retval, is_ret):
        ln, idx, tpl = p
        tpl = tpl.lstrip("^").lstrip()
        ctx = self._context(frame, retval, is_ret)
        g = dict(self.g)
        g.update(HELPERS)
        try:
            text = eval("f" + repr(tpl), g, ctx)
        except Exception as e:  # noqa: BLE001
            raise AuthoringError(f"narration on line {ln} failed: {tpl!r}: {type(e).__name__}: {e}")
        state = build_state(self.spec, g, ctx, self.seen_ok)
        self.frames.append({"line": ln, "mark": idx, "say": text, "st": state})
        if len(self.frames) > self.max_frames:
            raise TooManyFrames()


def make_namespace():
    return {"ListNode": ListNode, "TreeNode": TreeNode, "Node": Node, "__name__": "offleet_solution"}


def build_args(args, jtypes, cycle=False):
    """Convert JSON test args to runtime objects (cycle: args = [values, pos] -> one list with a cycle)."""
    if cycle:
        return [build_list(args[0], 0, cycle_pos=args[1])]
    return [convert_arg(copy.deepcopy(x), jt, row=i) for i, (x, jt) in enumerate(zip(args, jtypes))]


def trace(code: str, spec: dict, demo_args, jtypes, design=False, max_frames=600, cycle=False):
    """Run `code` on demo args with tracing; returns (frames, return_value)."""
    disp, marks = split_py(code)
    ranges = {k: v for k, v in compound_ranges(disp).items() if k in marks}
    reset_registries()
    ns = make_namespace()
    exec(compile(disp, FILENAME, "exec"), ns)
    tr = _Tracer(marks, ranges, spec or {}, ns, max_frames)
    ret = None
    sys.settrace(tr.global_trace)
    try:
        if design:
            ops, args = demo_args
            cls = ns[ops[0]]
            obj = cls(*args[0])
            ret = [None]
            for op, a in zip(ops[1:], args[1:]):
                ret.append(getattr(obj, op)(*a))
        else:
            fn = ns[entry_name(disp)]
            conv = build_args(demo_args, jtypes, cycle)
            ret = fn(*conv)
    except TooManyFrames:
        pass
    finally:
        sys.settrace(None)
    missing = []
    for key in _spec_keys(spec or {}):
        if key not in tr.seen_ok:
            missing.append(key)
    return tr.frames, ret, missing


def _spec_keys(spec):
    keys = []
    n_arr = len(spec.get("arrays", [])) + (1 if "arr" in spec else 0)
    keys += [f"arr{k}" for k in range(n_arr)]
    for item in spec.get("vars", []):
        keys.append("var:" + (item if isinstance(item, str) else item[0]))
    for item in spec.get("maps", []):
        keys.append("map:" + (item if isinstance(item, str) else item[0]))
    for kind in ("stacks", "queues"):
        for item in spec.get(kind, []):
            keys.append(f"{kind}:" + (item if isinstance(item, str) else item[0]))
    for k in ("grid", "table", "linked", "tree", "graph", "out"):
        if k in spec:
            keys.append(k)
    return keys
