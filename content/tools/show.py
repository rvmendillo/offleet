#!/usr/bin/env python3
"""Print a problem's generated tutorial as text (for reviewing narration)."""
import json, os, sys
root = os.path.join(os.path.dirname(__file__), "..", "..", "Offleet", "Resources", "Content", "tutorials")
pid = sys.argv[1]
tut = json.load(open(os.path.join(root, pid + ".json")))
for aid, frames in tut.items():
    print("==", aid, len(frames), "frames")
    for f in frames:
        st = f.get("st", {})
        brief = []
        for a in st.get("arrays", []):
            brief.append(f"{a['n']}={a['v']} p={[(p['l'], p['i']) for p in a.get('p', [])]} w={a.get('w')}")
        for k in ("vars", "maps", "stacks"):
            if k in st: brief.append(f"{k}={st[k]}")
        for k in ("linked", "tree", "grid", "table", "graph", "out", "bits", "intervals"):
            if k in st: brief.append(f"{k}={json.dumps(st[k])[:160]}")
        print(f"[{f['k']}] {f['cap']}" + (f"\n     say: {f['say']}" if 'say' in f else "") + (f"\n     ln={f.get('ln')}" if f.get('ln') else ""))
        for b in brief: print("     ", b[:220])
