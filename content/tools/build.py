#!/usr/bin/env python3
"""Offleet content build: verify every solution, generate tutorials, export JSON.

    python3 content/tools/build.py            # verify + write Offleet/Resources/Content
    python3 content/tools/build.py --check    # verify only (CI)
    python3 content/tools/build.py --only two_pointers,sliding_window
    python3 content/tools/build.py --no-java  # skip the Java harness (faster)
"""
from __future__ import annotations

import argparse
import copy
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.dirname(HERE)
ROOT = os.path.dirname(CONTENT)
OUT = os.path.join(ROOT, "Offleet", "Resources", "Content")
BUILD = os.path.join(CONTENT, ".build")
sys.path.insert(0, HERE)
sys.path.insert(0, CONTENT)

import dsl  # noqa: E402
from runtime import (compare, convert_arg, normalize, reset_registries, select_output, with_timeout,  # noqa: E402
                     Timeout)
from speech import speakify  # noqa: E402
from tracer import (AuthoringError, entry_name, make_namespace, py_params, split_c_like, split_py, trace,  # noqa: E402
                    FILENAME, fv)

PROBLEM_MODULES = [
    "two_pointers", "sliding_window", "arrays_hashing", "prefix_sum", "binary_search", "stack",
    "linked_list", "trees", "heap", "intervals", "graphs", "backtracking", "dp", "greedy", "bits_math",
    "matrix", "design",
]
FRAMEWORK_MODULES = ["spring_boot", "angular"]
REVIEWER_MODULES = ["cs", "ai", "adv_math", "calculus"]
BOOK_MODULES = ["handbook"]

MAX_STEPS = 34


# ------------------------------------------------------------------ helpers
def jfmt(v):
    """Format a JSON-able value the way problem examples show it."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if v is None:
        return "null"
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, float):
        return fv(v)
    if isinstance(v, (list, tuple)):
        return "[" + ",".join(jfmt(x) for x in v) + "]"
    return str(v)


def parse_java_sig(java: str):
    """Return (return_type, method_name, [(type, name)]) of the first public method in class Solution."""
    m = re.search(r"class\s+Solution\b.*?public\s+(?:static\s+)?([\w<>\[\],.?\s]+?)\s+(\w+)\s*\(([^)]*)\)", java, re.S)
    if not m:
        return None
    ret, name, params = m.group(1).strip(), m.group(2), m.group(3)
    parts, depth, cur = [], 0, ""
    for ch in params:
        if ch == "<":
            depth += 1
        elif ch == ">":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)
    out = []
    for p in parts:
        p = p.strip().replace("final ", "")
        t, n = p.rsplit(None, 1)
        out.append((re.sub(r"\s+", "", t), n))
    return ret, name, out


def strip_md(s: str) -> str:
    s = re.sub(r"`([^`]*)`", r"\1", s)
    s = s.replace("**", "")
    return s


def paragraphs(text: str):
    return [re.sub(r"\s*\n\s*", " ", p.strip()) for p in re.split(r"\n\s*\n", text or "") if p.strip()]


def sentence(s: str) -> str:
    s = s.strip()
    return s if not s or s[-1] in ".!?:" else s + "."


def sentences(text: str):
    text = re.sub(r"\s+", " ", text.strip())
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])", text)
    return [p for p in parts if p]


def say_of(cap: str) -> str | None:
    s = speakify(strip_md(cap))
    return None if s == cap else s


def frame(kind, cap, *, say=None, **extra):
    f = {"k": kind, "cap": cap}
    s = say if say is not None else say_of(cap)
    if s and s != cap:
        f["say"] = s
    f.update({k: v for k, v in extra.items() if v is not None})
    return f


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def err(self, where, msg):
        self.errors.append(f"[{where}] {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"[{where}] {msg}")


# ------------------------------------------------------------------ loading
def load_modules(only=None):
    for pkg, mods in (("problems", PROBLEM_MODULES), ("frameworks", FRAMEWORK_MODULES),
                      ("reviewer", REVIEWER_MODULES), ("books", BOOK_MODULES)):
        for mod in mods:
            path = os.path.join(CONTENT, pkg, mod + ".py")
            if not os.path.exists(path):
                continue
            if only and mod not in only and pkg in ("problems", "frameworks"):
                continue
            dsl._state["category"] = {"problems": "algorithms", "frameworks": mod.replace("_", "-")}.get(pkg, "algorithms")
            dsl._state["module"] = mod
            before = len(dsl.PROBLEMS)
            importlib.import_module(f"{pkg}.{mod}")
            for p in dsl.PROBLEMS[before:]:
                p["_module"] = mod


# ------------------------------------------------------------------ problems
def prepare(p, num, rep: Report):
    pid = p["id"]
    for key in ("id", "title", "difficulty", "topics", "statement", "approaches"):
        if key not in p:
            rep.err(pid, f"missing field {key}")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", pid):
        rep.err(pid, "id must be a lowercase slug")
    if p.get("difficulty") not in ("Easy", "Medium", "Hard"):
        rep.err(pid, "difficulty must be Easy/Medium/Hard")
    p["num"] = num
    p["design"] = bool(p.get("design"))
    algo = p["category"] == "algorithms"
    for k, a in enumerate(p["approaches"], 1):
        a["aid"] = f"a{k}"
        if a.get("pattern") not in dsl.PATTERN_IDS:
            rep.err(pid, f"approach {a.get('name')}: unknown pattern {a.get('pattern')}")
        for key in ("name", "time", "space", "idea"):
            if not a.get(key):
                rep.err(pid, f"approach {a.get('name')}: missing {key}")
        if "py" in a:
            a["py_disp"], a["py_marks"] = split_py(a["py"])
        if "java" in a:
            a["java_disp"], a["java_map"] = split_c_like(a["java"])
        if "ts" in a:
            a["ts_disp"], a["ts_map"] = split_c_like(a["ts"])
        if algo and ("py" not in a or "java" not in a):
            rep.err(pid, f"approach {a['name']}: algorithms need both py and java")
    if algo and not p["design"]:
        first_java = next((a["java_disp"] for a in p["approaches"] if "java_disp" in a), None)
        sig = parse_java_sig(first_java) if first_java else None
        if not sig:
            rep.err(pid, "could not parse Java signature (need `class Solution` with a public method)")
            p["jtypes"], p["method"] = [], None
        else:
            p["jret"], p["method"], params = sig
            p["jtypes"] = [t for t, _ in params]
        p["pnames"] = py_params(p["approaches"][0]["py_disp"]) if "py_disp" in p["approaches"][0] else []
    tests = []
    for ex in p.get("examples", []):
        tests.append((ex[0], ex[1]))
    tests += [tuple(t) for t in p.get("tests", [])]
    p["_tests"] = tests
    if algo and len(tests) < 3:
        rep.warn(pid, f"only {len(tests)} tests")
    pats = []
    for a in p["approaches"]:
        if a.get("pattern") not in pats:
            pats.append(a["pattern"])
    for extra in p.get("patterns", []):
        if extra not in pats:
            pats.append(extra)
    p["_patterns"] = pats


def fix_null(p, got):
    """A null ListNode/TreeNode result means an empty list."""
    if got is None and p.get("jret") in ("ListNode", "TreeNode", "Node"):
        return []
    return got


def verify_python(p, rep: Report):
    pid = p["id"]
    for a in p["approaches"]:
        if "py_disp" not in a:
            continue
        ns = make_namespace()
        try:
            exec(compile(a["py_disp"], FILENAME, "exec"), ns)
        except Exception as e:  # noqa: BLE001
            rep.err(pid, f"{a['name']} (py): does not compile: {e}")
            continue
        for i, (args, expected) in enumerate(p["_tests"]):
            reset_registries()
            try:
                if p["design"]:
                    ops, oargs = copy.deepcopy(args)
                    obj = ns[ops[0]](*oargs[0])
                    outs = [None]
                    for op, av in zip(ops[1:], oargs[1:]):
                        outs.append(normalize(with_timeout(2, getattr(obj, op), *av)))
                    ok = compare(outs, expected, "exact")
                    got = outs
                else:
                    fn = ns[entry_name(a["py_disp"])]
                    conv = [convert_arg(copy.deepcopy(x), jt, row=j) for j, (x, jt) in enumerate(zip(args, p["jtypes"]))]
                    ret = with_timeout(2, fn, *conv)
                    got = fix_null(p, select_output(p.get("out", "ret"), ret, conv))
                    ok = compare(got, expected, p.get("check", "exact"))
                if not ok:
                    rep.err(pid, f"{a['name']} (py) test {i}: args={jfmt(args)[:120]} expected={jfmt(expected)[:80]} got={jfmt(got)[:80]}")
            except Timeout:
                rep.err(pid, f"{a['name']} (py) test {i}: timeout")
            except Exception as e:  # noqa: BLE001
                rep.err(pid, f"{a['name']} (py) test {i}: {type(e).__name__}: {e}")


def verify_java(problems, rep: Report):
    javac = shutil.which("javac")
    if not javac:
        rep.warn("java", "javac not found; skipping Java verification")
        return
    shutil.rmtree(os.path.join(BUILD, "java"), ignore_errors=True)
    src = os.path.join(BUILD, "java", "src")
    classes = os.path.join(BUILD, "java", "classes")
    os.makedirs(classes, exist_ok=True)
    files = []
    for sub in ("common", "harness"):
        for f in os.listdir(os.path.join(HERE, "java", sub)):
            files.append(os.path.join(HERE, "java", sub, f))
    jobs, owners = [], {}
    for p in problems:
        if p["category"] != "algorithms":
            continue
        for a in p["approaches"]:
            if "java_disp" not in a:
                continue
            pkg = f"p{p['num']:04d}{a['aid']}"
            d = os.path.join(src, pkg)
            os.makedirs(d, exist_ok=True)
            code = re.sub(r"(?m)^public\s+(class|interface|enum|record)\b", r"\1", a["java_disp"])
            header = (f"package {pkg};\nimport java.util.*;\nimport java.util.function.*;\nimport java.util.stream.*;\n"
                      f"import common.*;\n")
            path = os.path.join(d, "Solution.java")
            with open(path, "w") as fh:
                fh.write(header + code + "\n")
            files.append(path)
            owners[path] = (p["id"], a["name"], len(header.split("\n")) - 1)
            key = f"{p['id']}#{a['aid']}"
            job = {"key": key, "pkg": pkg, "design": p["design"], "tests": [t[0] for t in p["_tests"]]}
            if not p["design"]:
                job.update({"cls": "Solution", "method": p["method"]})
            jobs.append((job, p, a))
    res = subprocess.run([javac, "-nowarn", "-encoding", "UTF-8", "-d", classes] + files,
                         capture_output=True, text=True)
    if res.returncode != 0:
        for line in res.stderr.splitlines():
            m = re.match(r"(.+?\.java):(\d+): error: (.*)", line)
            if m and m.group(1) in owners:
                pid, name, off = owners[m.group(1)]
                rep.err(pid, f"{name} (java) line {int(m.group(2)) - off}: {m.group(3)}")
            elif m:
                rep.err("java", line)
        if not rep.errors:
            rep.err("java", res.stderr[-2000:])
        return
    tests_path = os.path.join(BUILD, "java", "tests.json")
    with open(tests_path, "w") as fh:
        json.dump([j for j, _, _ in jobs], fh)
    run = subprocess.run(["java", "-Xss64m", "-cp", classes, "harness.Harness", tests_path],
                         capture_output=True, text=True, timeout=900)
    results = {}
    for line in run.stdout.splitlines():
        if line.startswith("{"):
            r = json.loads(line)
            results[(r["key"], r["i"])] = r
    for job, p, a in jobs:
        for i, (args, expected) in enumerate(p["_tests"]):
            r = results.get((job["key"], i))
            if r is None:
                rep.err(p["id"], f"{a['name']} (java) test {i}: no result {run.stderr[-300:]}")
                continue
            if r.get("err"):
                rep.err(p["id"], f"{a['name']} (java) test {i}: {r['err']}")
                continue
            if p["design"]:
                got, ok = r["ret"], compare(r["ret"], expected, "exact")
            else:
                src_mode = p.get("out", "ret")
                if src_mode == "arg0":
                    got = r["args"][0]
                elif src_mode == "arg0-prefix":
                    got = r["args"][0][: r["ret"]]
                else:
                    got = fix_null(p, r["ret"])
                ok = compare(got, expected, p.get("check", "exact"))
            if not ok:
                rep.err(p["id"], f"{a['name']} (java) test {i}: expected={jfmt(expected)[:80]} got={jfmt(got)[:80]}")


# ------------------------------------------------------------------ tutorials
def demo_desc(p, args):
    if p["design"]:
        ops, oargs = args
        calls = [f"{op}({', '.join(jfmt(x) for x in av)})" for op, av in zip(ops, oargs)]
        return "the calls " + ", ".join(calls)
    names = p.get("pnames") or [f"arg{i}" for i in range(len(args))]
    return ", ".join(f"{n} = {jfmt(v)}" for n, v in zip(names, args))


def compress_steps(steps):
    if len(steps) <= MAX_STEPS:
        return steps
    head, tail = steps[:22], steps[-10:]
    skipped = len(steps) - 32
    bridge = dict(tail[0])
    bridge = {"k": "skip", "cap": f"Fast-forward: the same moves repeat for {skipped} more steps…",
              "st": tail[0].get("st"), "ln": tail[0].get("ln")}
    bridge["say"] = speakify(bridge["cap"])
    return head + [bridge] + tail


def build_algo_tutorial(p, a, rep: Report):
    pid = p["id"]
    title = p["title"]
    pname = dsl_pattern_name(a["pattern"])
    frames = [frame("title", title, card={"title": title, "sub": f"{a['name']} · {p['difficulty']}", "pattern": a["pattern"]},
                    say=speakify(f"Let's solve {strip_md(title)}, using the {a['name']} approach."))]
    plain = p.get("eli5") or paragraphs(p["statement"])[0]
    frames.append(frame("problem", strip_md(plain), card={"lines": [strip_md(x) for x in paragraphs(p["statement"])[:2]]}))
    if p.get("examples"):
        ex = p["examples"][0]
        inp = demo_desc(p, ex[0])
        why = sentence(ex[2]) if len(ex) > 2 and ex[2] else ""
        cap = f"For example, with {inp}, the answer is {jfmt(ex[1])}." + (f" {why}" if why else "")
        frames.append(frame("example", cap, card={"lines": [f"Input: {inp}", f"Output: {jfmt(ex[1])}"] + ([why] if why else [])}))
    for para in paragraphs(a["idea"]):
        frames.append(frame("idea", strip_md(para), card={"pattern": a["pattern"], "name": pname}))
    steps = []
    ret = None
    if a.get("py_marks"):
        demo = a.get("demo", p.get("demo"))
        if demo is None:
            demo = p["examples"][0][0] if p.get("examples") else p["_tests"][0][0]
        try:
            raw, ret, missing = trace(a["py"], a.get("viz", {}), copy.deepcopy(demo), p.get("jtypes", []), design=p["design"])
        except AuthoringError as e:
            rep.err(pid, f"{a['name']} tutorial: {e}")
            raw, missing = [], []
        except Exception as e:  # noqa: BLE001
            rep.err(pid, f"{a['name']} tutorial crashed: {type(e).__name__}: {e}\n{traceback.format_exc(limit=3)}")
            raw, missing = [], []
        for key in missing:
            rep.warn(pid, f"{a['name']} viz component '{key}' never rendered")
        if len(raw) < 2:
            rep.warn(pid, f"{a['name']}: tutorial has only {len(raw)} traced steps")
        jmap = a.get("java_map", {})
        for fr in raw:
            ln = {"python": fr["line"]}
            if fr["mark"] in jmap:
                ln["java"] = jmap[fr["mark"]]
            steps.append(frame("step", fr["say"], ln=ln, st=fr["st"]))
        if steps:
            intro = frame("trace", f"Let's walk through it with {demo_desc(p, demo)}.", st=steps[0].get("st"))
            frames.append(intro)
            frames.extend(compress_steps(steps))
            if not p["design"] and ret is not None:
                frames.append(frame("done", f"The answer is {jfmt(normalize(ret))}.", st=steps[-1].get("st")))
    cx = f"Time complexity is {a['time']} and extra space is {a['space']}."
    if a.get("why"):
        cx += " " + strip_md(a["why"])
    frames.append(frame("complexity", cx, card={"time": a["time"], "space": a["space"]}))
    frames.append(frame("outro", f"That's the {a['name']} approach. Now try writing it yourself, in Java or Python!"))
    return frames


def build_code_tutorial(p, a, rep: Report):
    """Framework walkthrough: steps = [(needle, narration[, file_index])]."""
    pid = p["id"]
    files = a["files"]
    frames = [frame("title", p["title"], card={"title": p["title"], "sub": f"{a['name']} · {p['difficulty']}", "pattern": a["pattern"]},
                    say=speakify(f"Let's build {strip_md(p['title'])}."))]
    frames.append(frame("problem", strip_md(p.get("eli5") or paragraphs(p["statement"])[0]),
                        card={"lines": [strip_md(x) for x in paragraphs(p["statement"])[:2]]}))
    for para in paragraphs(a["idea"]):
        frames.append(frame("idea", strip_md(para), card={"pattern": a["pattern"], "name": dsl_pattern_name(a["pattern"])}))
    cursor = {}
    for st in a.get("steps", []):
        needle, text = st[0], st[1]
        fi = st[2] if len(st) > 2 else None
        found = None
        order = [fi] if fi is not None else list(range(len(files)))
        for idx in order:
            lines = files[idx]["src"].split("\n")
            start = cursor.get(idx, 0)
            for ln in list(range(start, len(lines))) + list(range(0, start)):
                if needle in lines[ln]:
                    found = (idx, ln + 1)
                    break
            if found:
                break
        if not found:
            rep.err(pid, f"walkthrough step needle not found: {needle!r}")
            continue
        cursor[found[0]] = found[1]
        frames.append(frame("code", text, file=found[0], ln={"line": found[1]}))
    cx = f"Key idea recap: {strip_md(a.get('why') or a['idea'].split('.')[0])}."
    frames.append(frame("outro", "That's it! Read the full code below, then try building it yourself."))
    return frames


_PAT = {p[0]: p for p in dsl.PATTERNS}


def dsl_pattern_name(pid):
    return _PAT[pid][1] if pid in _PAT else pid


def export_problem(p):
    out = {
        "id": p["id"], "n": p["num"], "title": p["title"], "diff": p["difficulty"], "cat": p["category"],
        "topics": p["topics"], "patterns": p["_patterns"], "statement": p["statement"],
        "examples": [], "constraints": p.get("constraints", []), "hints": p.get("hints", []),
        "approaches": [],
    }
    if p.get("eli5"):
        out["eli5"] = p["eli5"]
    for ex in p.get("examples", []):
        if p["category"] == "algorithms":
            e = {"in": demo_desc(p, ex[0]) if not p["design"] else _design_in(ex[0]), "out": jfmt(ex[1])}
            if len(ex) > 2 and ex[2]:
                e["why"] = ex[2]
        else:
            e = {"in": ex[0], "out": ex[1]}
            if len(ex) > 2 and ex[2]:
                e["why"] = ex[2]
        out["examples"].append(e)
    for a in p["approaches"]:
        code = []
        if "py_disp" in a:
            code.append({"lang": "python", "name": "solution.py", "src": a["py_disp"]})
        if "java_disp" in a:
            code.append({"lang": "java", "name": "Solution.java", "src": a["java_disp"]})
        for f in a.get("files", []):
            code.append({"lang": f["lang"], "name": f["name"], "src": f["src"]})
        ea = {"id": a["aid"], "name": a["name"], "pattern": a["pattern"], "time": a["time"], "space": a["space"],
              "idea": a["idea"], "code": code}
        if a.get("why"):
            ea["why"] = a["why"]
        out["approaches"].append(ea)
    return out


def _design_in(args):
    ops, oargs = args
    return f"{jfmt(ops)}\n{jfmt(oargs)}"


# ------------------------------------------------------------------ reviewer & books
def bite_script(b):
    if b.get("say"):
        return speakify(b["say"])
    parts = [b["title"] + ".", b["tldr"]]
    parts += [pt if pt.endswith((".", "!", "?")) else pt + "." for pt in b["points"]]
    if b.get("say_formula"):
        parts.append(b["say_formula"] if b["say_formula"].endswith(".") else b["say_formula"] + ".")
    elif b.get("formula"):
        parts.append("In symbols: " + b["formula"] + ".")
    if b.get("example"):
        parts.append("Example: " + b["example"])
    if b.get("tip"):
        parts.append("Remember: " + b["tip"])
    return speakify(" ".join(parts))


def export_reviewer(rep: Report):
    subjects = []
    seen = set()
    for s in dsl.SUBJECTS:
        units = []
        for u in s["units"]:
            bites = []
            for b in u["bites"]:
                if b["id"] in seen:
                    rep.err("reviewer", f"duplicate bite id {b['id']}")
                seen.add(b["id"])
                eb = {k: b[k] for k in ("id", "title", "tldr", "points") if b.get(k)}
                for k in ("formula", "example", "tip"):
                    if b.get(k):
                        eb[k] = b[k]
                if b.get("quiz"):
                    q, opts, ans, why = b["quiz"]
                    if not 0 <= ans < len(opts):
                        rep.err("reviewer", f"{b['id']}: quiz answer index out of range")
                    eb["quiz"] = {"q": q, "opts": opts, "a": ans, "why": why}
                eb["say"] = bite_script(b)
                bites.append(eb)
            units.append({"title": u["title"], "blurb": u.get("blurb", ""), "bites": bites})
        subjects.append({k: s[k] for k in ("id", "title", "icon", "color", "blurb")} | {"units": units})
    return {"subjects": subjects}


def para_objs(text):
    out = []
    for para in paragraphs(text):
        cap = strip_md(para)
        o = {"t": cap}
        s = speakify(cap)
        if s != cap:
            o["s"] = s
        out.append(o)
    return out


def export_books(problems, reviewer):
    books = []
    hand = [c for c in dsl.CHAPTERS if c["book"] == "handbook"]
    if hand:
        books.append({"id": "handbook", "title": "The Patterns Handbook", "author": "Offleet",
                      "blurb": "Every interview pattern explained from zero, in plain words.",
                      "icon": "book.closed", "color": "#7C3AED",
                      "chapters": [{"id": c.get("id") or f"hb{i}", "title": c["title"], "paras": para_objs(c["text"])}
                                   for i, c in enumerate(hand, 1)]})

    def problem_chapter(p):
        text = [p["title"] + ".", strip_md(p.get("eli5") or p["statement"])]
        for a in p["approaches"]:
            text.append(f"Approach: {a['name']}.")
            text.append(strip_md(a["idea"]))
            text.append(f"Time {a['time']}, space {a['space']}." + (" " + strip_md(a["why"]) if a.get("why") else ""))
        return {"id": p["id"], "title": f"{p['num']}. {p['title']}", "paras": para_objs("\n\n".join(text))}

    algo = [p for p in problems if p["category"] == "algorithms"]
    if algo:
        books.append({"id": "walkthroughs", "title": "Problem Walkthroughs", "author": "Offleet",
                      "blurb": "Listen to every problem and its solution ideas, hands-free.",
                      "icon": "headphones", "color": "#0891B2", "chapters": [problem_chapter(p) for p in algo]})
    for cat, title, color, icon in (("spring-boot", "Spring Boot Essentials", "#6DB33F", "leaf"),
                                    ("angular", "Angular Essentials", "#DD0031", "a.circle")):
        ps = [p for p in problems if p["category"] == cat]
        if ps:
            books.append({"id": cat, "title": title, "author": "Offleet", "blurb": f"Hands-on {title.split()[0]} lessons as audio.",
                          "icon": icon, "color": color, "chapters": [problem_chapter(p) for p in ps]})
    for s in reviewer["subjects"]:
        chapters = []
        for u in s["units"]:
            paras = [{"t": u["title"] + ".", "s": speakify(u["title"]) + "."}]
            for b in u["bites"]:
                paras.append({"t": b["title"] + ": " + b["tldr"], "s": b["say"]})
            chapters.append({"id": f"{s['id']}-{len(chapters) + 1}", "title": u["title"], "paras": paras})
        books.append({"id": f"rev-{s['id']}", "title": f"{s['title']} Reviewer", "author": "Offleet",
                      "blurb": s["blurb"], "icon": s["icon"], "color": s["color"], "chapters": chapters})
    return {"books": books}


def export_tracks(problems):
    by_pat = {}
    for p in problems:
        for pat in p["_patterns"]:
            by_pat.setdefault(pat, []).append(p["id"])
    tracks = []
    for pid, name, summary, icon, color in dsl.PATTERNS:
        if by_pat.get(pid):
            tracks.append({"id": f"pat-{pid}", "title": name, "summary": summary, "icon": icon, "color": color,
                           "problems": by_pat[pid]})
    starter = [p["id"] for p in problems if p["category"] == "algorithms" and p["difficulty"] == "Easy"][:40]
    if starter:
        tracks.insert(0, {"id": "starter", "title": "Starter Path", "summary": "Gentle problems to build confidence.",
                          "icon": "flag.checkered", "color": "#34D399", "problems": starter})
    return {"tracks": tracks}


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify only, do not write output")
    ap.add_argument("--only", default="", help="comma separated module names")
    ap.add_argument("--no-java", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    only = {m for m in args.only.split(",") if m}
    t0 = time.time()
    load_modules(only or None)
    rep = Report()
    problems = dsl.PROBLEMS
    ids = set()
    for num, p in enumerate(problems, 1):
        if p["id"] in ids:
            rep.err(p["id"], "duplicate id")
        ids.add(p["id"])
        prepare(p, num, rep)
    for p in problems:
        if p["category"] == "algorithms":
            verify_python(p, rep)
    if not args.no_java:
        verify_java(problems, rep)
    tutorials = {}
    for p in problems:
        tut = {}
        for a in p["approaches"]:
            if p["category"] == "algorithms":
                tut[a["aid"]] = build_algo_tutorial(p, a, rep)
            elif a.get("files"):
                tut[a["aid"]] = build_code_tutorial(p, a, rep)
        tutorials[p["id"]] = tut
    reviewer = export_reviewer(rep)
    books = export_books(problems, reviewer)
    tracks = export_tracks(problems)

    if not args.quiet or rep.errors:
        for w in rep.warnings:
            print("WARN ", w)
    for e in rep.errors:
        print("ERROR", e)
    cats = {}
    for p in problems:
        cats[p["category"]] = cats.get(p["category"], 0) + 1
    sw = sum(1 for p in problems if "sliding-window" in p["_patterns"])
    tp = sum(1 for p in problems if {"two-pointers", "fast-slow"} & set(p["_patterns"]))
    nbites = sum(len(u["bites"]) for s in reviewer["subjects"] for u in s["units"])
    nframes = sum(len(f) for t in tutorials.values() for f in t.values())
    print(f"problems={len(problems)} {cats} sliding-window={sw} two-pointers={tp} bites={nbites} "
          f"tutorial-frames={nframes} books={len(books['books'])} errors={len(rep.errors)} "
          f"warnings={len(rep.warnings)} ({time.time() - t0:.1f}s)")
    if rep.errors:
        sys.exit(1)
    if args.check or only:
        return
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(os.path.join(OUT, "tutorials"), exist_ok=True)

    def dump(name, obj):
        with open(os.path.join(OUT, name), "w") as fh:
            json.dump(obj, fh, ensure_ascii=False, separators=(",", ":"))

    dump("problems.json", {"patterns": [{"id": a, "name": b, "summary": c, "icon": d, "color": e} for a, b, c, d, e in dsl.PATTERNS],
                           "problems": [export_problem(p) for p in problems]})
    for pid, tut in tutorials.items():
        if tut:
            dump(os.path.join("tutorials", pid + ".json"), tut)
    dump("reviewer.json", reviewer)
    dump("books.json", books)
    dump("tracks.json", tracks)
    dump("meta.json", {"version": 1, "built": time.strftime("%Y-%m-%d"), "problems": len(problems),
                       "categories": cats, "bites": nbites, "books": len(books["books"])})
    size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(OUT) for f in fs)
    print(f"wrote {OUT} ({size / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
