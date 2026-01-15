from __future__ import annotations
from typing import Tuple, Dict, Set, List
import math


def _parse_csv_graph(s: str) -> Dict[str, Set[str]]:
    s = s.strip()
    if not s:
        return {}

    raw_edges: List[str] = []
    for part in s.replace('\n', ';').split(';'):
        part = part.strip()
        if part:
            raw_edges.append(part)

    graph: Dict[str, Set[str]] = {}

    for edge in raw_edges:
        parts = [p.strip() for p in edge.split(',')]
        if len(parts) != 2:
            raise ValueError(f"Некорректный формат ребра: {edge!r}, ожидается 'u,v'")
        u, v = parts
        if u not in graph:
            graph[u] = set()
        if v not in graph:
            graph[v] = set()
        graph[u].add(v)

    return graph


def _reachable_subgraph(graph: Dict[str, Set[str]], root: str) -> Dict[str, Set[str]]:
    if root not in graph:
        return {}

    visited: Set[str] = set()
    stack: List[str] = [root]

    while stack:
        u = stack.pop()
        if u in visited:
            continue
        visited.add(u)
        for v in graph[u]:
            if v not in visited:
                stack.append(v)

    subgraph: Dict[str, Set[str]] = {v: set() for v in visited}
    for u in visited:
        for v in graph[u]:
            if v in visited:
                subgraph[u].add(v)

    return subgraph


def _entropy_and_complexity(graph: Dict[str, Set[str]]) -> Tuple[float, float]:
    nodes = list(graph.keys())
    N = len(nodes)
    if N <= 1:
        return 0.0, 0.0

    out_degrees = [len(graph[v]) for v in nodes]
    M = sum(out_degrees)
    if M == 0:
        return 0.0, 0.0

    probs = [deg / M for deg in out_degrees if deg > 0]
    H = -sum(p * math.log2(p) for p in probs)

    max_entropy = math.log2(N)
    if max_entropy == 0:
        C_norm = 0.0
    else:
        C_norm = H / max_entropy

    return H, C_norm


def main(s: str, e: str) -> Tuple[float, float]:
    full_graph = _parse_csv_graph(s)
    subgraph = _reachable_subgraph(full_graph, e)
    H, C_norm = _entropy_and_complexity(subgraph)
    return round(H, 1), round(C_norm, 1)


if __name__ == "__main__":
    csv_str = "A,B;A,C;B,D;C,D"
    root = "A"
    print(main(csv_str, root))
