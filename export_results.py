"""Save readable transition tables and diagrams without extra packages."""

import csv
from collections import deque
from html import escape

from automata import EPSILON, degrees


def stats(nfa):
    incoming, outgoing = degrees(nfa)
    return {
        "states": len(nfa.states),
        "transitions": len(nfa.edges),
        "symbol_transitions": sum(a != EPSILON for s, a, t in nfa.edges),
        "epsilon_transitions": sum(a == EPSILON for s, a, t in nfa.edges),
        "max_in_degree": max(incoming.values(), default=0),
        "max_out_degree": max(outgoing.values(), default=0),
    }


def write_csv(path, header, rows):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


def positions(nfa):
    # Use left-to-right layers for acyclic graphs (our two main examples).
    # A DFA dead state is drawn below the other states, away from the main path.
    dead = None
    for q in nfa.states:
        outgoing_edges = [(a, t) for s, a, t in nfa.edges if s == q]
        if q not in nfa.finals and outgoing_edges and all(t == q and a for a, t in outgoing_edges):
            dead = q
            break
    main_states = [q for q in nfa.states if q != dead]
    if not main_states:
        main_states = list(nfa.states)
        dead = None
    main_edges = [(s, a, t) for s, a, t in nfa.edges if s != dead and t != dead]
    pending = {q: 0 for q in main_states}
    for source, label, target in main_edges:
        pending[target] += 1
    level = {q: 0 for q in main_states}
    todo = deque(q for q in main_states if pending[q] == 0)
    visited = 0
    while todo:
        q = todo.popleft()
        visited += 1
        for source, label, target in main_edges:
            if source == q:
                level[target] = max(level[target], level[q] + 1)
                pending[target] -= 1
                if pending[target] == 0:
                    todo.append(target)

    # For graphs with loops, a simple breadth-first layout is enough.
    if visited != len(main_states):
        level = {nfa.start: 0}
        todo = deque([nfa.start])
        while todo:
            q = todo.popleft()
            for source, label, target in main_edges:
                if source == q and target not in level:
                    level[target] = level[q] + 1
                    todo.append(target)
        for q in main_states:
            level.setdefault(q, max(level.values()) + 1)

    layers = {}
    for q in main_states:
        layers.setdefault(level[q], []).append(q)
    rows = max(map(len, layers.values()))
    height = max(320, 140 + rows * 100)
    xy = {}
    for column, states in layers.items():
        for row, q in enumerate(states):
            xy[q] = (80 + column * 115,
                     height / 2 + (row - (len(states) - 1) / 2) * 100)
    width = 170 + max(layers) * 115
    if dead is not None:
        height += 180
        xy[dead] = (width / 2, height - 80)
    return xy, width, height


def write_svg(nfa, path, title, original_count=None):
    xy, width, height = positions(nfa)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b"/></marker></defs>',
        '<rect width="100%" height="100%" fill="white"/>',
        '<g font-family="Arial, sans-serif" font-size="13">',
        f'<text x="24" y="27" font-size="18" font-weight="bold">{escape(title)}</text>',
        '<text x="24" y="49" fill="#475569">ε consumes no input. Purple nodes are added routing states. Double circles accept.</text>',
    ]
    # Combining labels is only for drawing. CSV files count edges separately.
    connections = {}
    for source, label, target in nfa.edges:
        connections.setdefault((source, target), []).append(label or "ε")
    for (source, target), labels in connections.items():
        x1, y1 = xy[source]
        x2, y2 = xy[target]
        label = escape(", ".join(labels))
        if source == target:
            route = f'M {x1-10} {y1-17} C {x1-45} {y1-68}, {x1+45} {y1-68}, {x1+10} {y1-17}'
            tx, ty = x1, y1 - 55
        elif x2 > x1:
            route = f'M {x1+21} {y1} L {x2-23} {y2}'
            tx, ty = (x1 + x2) / 2, (y1 + y2) / 2 - 8
        else:
            bend = max(y1, y2) + 45
            route = f'M {x1} {y1+21} C {x1+35} {bend}, {x2-35} {bend}, {x2} {y2+23}'
            tx, ty = (x1 + x2) / 2, bend - 3
        parts.append(f'<path d="{route}" fill="none" stroke="#64748b" stroke-width="1.5" marker-end="url(#arrow)"/>')
        parts.append(f'<text x="{tx}" y="{ty}" text-anchor="middle" fill="#334155" stroke="white" stroke-width="4" paint-order="stroke">{label}</text>')
    sx, sy = xy[nfa.start]
    parts.append(f'<path d="M {sx-52} {sy} L {sx-23} {sy}" stroke="#64748b" marker-end="url(#arrow)"/>')
    for q, (x, y) in xy.items():
        added = original_count is not None and q >= original_count
        color = "#ede9fe" if added else "#e0f2fe"
        parts.append(f'<circle cx="{x}" cy="{y}" r="21" fill="{color}" stroke="#334155"/>')
        if q in nfa.finals:
            parts.append(f'<circle cx="{x}" cy="{y}" r="17" fill="none" stroke="#334155"/>')
        parts.append(f'<text x="{x}" y="{y+4}" text-anchor="middle">q{q}</text>')
    parts.append('</g></svg>')
    path.write_text("\n".join(parts), encoding="utf-8")


def save_machine(nfa, folder, name, title, original_count=None):
    write_csv(folder / f"{name}_transitions.csv", ["source", "label", "target"],
              ((f"q{s}", a or "ε", f"q{t}") for s, a, t in nfa.edges))
    incoming, outgoing = degrees(nfa)
    write_csv(folder / f"{name}_degrees.csv",
              ["state", "in_degree", "out_degree", "within_bound_2", "start", "accepting"],
              ((f"q{q}", incoming[q], outgoing[q], incoming[q] <= 2 and outgoing[q] <= 2,
                q == nfa.start, q in nfa.finals) for q in nfa.states))
    write_svg(nfa, folder / f"{name}.svg", title, original_count)
