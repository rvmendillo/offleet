"""Shared runtime for verifying and tracing Offleet solutions.

Provides ListNode / TreeNode (with a creation registry so the tracer can lay
nodes out consistently), argument builders, output normalisers and the
comparison modes used by both the Python and Java verifiers.
"""
from __future__ import annotations

import json
import math
import signal
from collections import deque


# ---------------------------------------------------------------- data types
class ListNode:
    registry: list = []

    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
        self._row = None
        self._col = None
        ListNode.registry.append(self)

    def __repr__(self):
        return f"ListNode({self.val})"


class TreeNode:
    registry: list = []

    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
        TreeNode.registry.append(self)

    def __repr__(self):
        return f"TreeNode({self.val})"


class Node:
    """Graph node used by clone-graph style problems."""

    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []


def reset_registries():
    ListNode.registry = []
    TreeNode.registry = []


def build_list(values, row=0, cycle_pos=-1):
    dummy_nodes = []
    for i, v in enumerate(values):
        n = ListNode(v)
        n._row, n._col = row, i
        dummy_nodes.append(n)
    for a, b in zip(dummy_nodes, dummy_nodes[1:]):
        a.next = b
    if cycle_pos is not None and cycle_pos >= 0 and dummy_nodes:
        dummy_nodes[-1].next = dummy_nodes[cycle_pos]
    return dummy_nodes[0] if dummy_nodes else None


def list_to_py(node, limit=10000):
    out, seen = [], set()
    while node is not None and id(node) not in seen and len(out) < limit:
        seen.add(id(node))
        out.append(node.val)
        node = node.next
    return out


def build_tree(values):
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    q, i = deque([root]), 1
    while q and i < len(values):
        node = q.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            q.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            q.append(node.right)
        i += 1
    return root


def tree_to_py(root):
    if root is None:
        return []
    out, q = [], deque([root])
    while q:
        n = q.popleft()
        if n is None:
            out.append(None)
            continue
        out.append(n.val)
        q.append(n.left)
        q.append(n.right)
    while out and out[-1] is None:
        out.pop()
    return out


def build_graph(adj):
    """adj: list where adj[i] lists neighbours (1-indexed values) of node i+1."""
    if not adj:
        return None
    nodes = [Node(i + 1) for i in range(len(adj))]
    for i, nbrs in enumerate(adj):
        nodes[i].neighbors = [nodes[j - 1] for j in nbrs]
    return nodes[0]


def graph_to_py(node):
    if node is None:
        return []
    seen, order, q = {node.val: node}, [], deque([node])
    while q:
        n = q.popleft()
        order.append(n)
        for nb in n.neighbors:
            if nb.val not in seen:
                seen[nb.val] = nb
                q.append(nb)
    order.sort(key=lambda n: n.val)
    return [[nb.val for nb in n.neighbors] for n in order]


# ------------------------------------------------------- argument conversion
def convert_arg(value, jtype: str, row=0):
    """Convert a JSON test value into the runtime object for a Java type name."""
    t = jtype.replace(" ", "")
    if t == "ListNode":
        return build_list(value, row)
    if t == "TreeNode":
        return build_tree(value)
    if t == "Node":
        return build_graph(value)
    if t in ("ListNode[]", "List<ListNode>"):
        return [build_list(v, row + i) for i, v in enumerate(value)]
    return value


def normalize(value):
    """Turn any solution output into plain JSON-able data."""
    if isinstance(value, ListNode):
        return list_to_py(value)
    if isinstance(value, TreeNode):
        return tree_to_py(value)
    if isinstance(value, Node):
        return graph_to_py(value)
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, float):
        if math.isinf(value) or math.isnan(value):
            return str(value)
        return round(value, 5)
    if isinstance(value, (int, str)):
        return value
    if isinstance(value, (list, tuple, deque)):
        return [normalize(v) for v in value]
    if isinstance(value, (set, frozenset)):
        return sorted((normalize(v) for v in value), key=_key)
    if isinstance(value, dict):
        return {str(k): normalize(v) for k, v in value.items()}
    return value


def _key(v):
    return json.dumps(v, sort_keys=True)


def _deep_sort(v):
    if isinstance(v, list):
        return sorted((_deep_sort(x) for x in v), key=_key)
    return v


def compare(out, expected, mode: str) -> bool:
    """Compare a normalised output with the expected JSON value."""
    if mode in ("exact", "arg0", "ret"):
        return _eq(out, expected)
    if mode == "unordered":
        return isinstance(out, list) and sorted(out, key=_key) == sorted(expected, key=_key)
    if mode == "deep-unordered":
        return isinstance(out, list) and _deep_sort(out) == _deep_sort(expected)
    if mode == "inner-sorted":  # each inner list sorted, outer order kept
        return isinstance(out, list) and [sorted(x, key=_key) for x in out] == [sorted(x, key=_key) for x in expected]
    if mode == "float":
        return isinstance(out, (int, float)) and abs(out - expected) < 1e-4
    raise ValueError(f"unknown compare mode {mode}")


def _eq(a, b):
    if isinstance(a, float) or isinstance(b, float):
        try:
            return abs(float(a) - float(b)) < 1e-4
        except (TypeError, ValueError):
            return False
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_eq(x, y) for x, y in zip(a, b))
    return a == b


def select_output(mode_src: str, ret, args):
    """mode_src: 'ret' | 'arg0' | 'arg0-prefix' (first ret items of arg0)."""
    if mode_src == "arg0":
        return normalize(args[0])
    if mode_src == "arg0-prefix":
        return normalize(args[0])[:ret]
    return normalize(ret)


# ----------------------------------------------------------------- timeouts
class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def with_timeout(seconds, fn, *args):
    old = signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        return fn(*args)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)
