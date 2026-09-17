"""
Renders a simple entity-relationship diagram as a PNG using Pillow.

Layout: layered top-down — parents (the "1" side) sit above their children
(the "N" side). Within a layer, nodes are ordered by the average position of
their parents to reduce line crossings. Edges are straight lines labelled
1 / N (or N : N for many-to-many).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# All values in px at SCALE=1; rendered at 2x for crispness in Word.
SCALE = 2
NODE_H = 46
NODE_PAD_X = 18
H_GAP = 46
V_GAP = 110
MARGIN = 40
FONT_SIZE = 15
LABEL_SIZE = 12

FILL = (238, 243, 250)
BORDER = (54, 92, 141)
TEXT = (25, 35, 50)
LINE = (120, 135, 155)
LABEL = (80, 95, 115)


@dataclass
class DiagramEdge:
    parent: str   # logical name of the 1-side (or first entity for N:N)
    child: str    # logical name of the N-side (or second entity for N:N)
    many_to_many: bool = False


def _font(size: int):
    for name in ("segoeui.ttf", "arial.ttf", "calibri.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size * SCALE)
        except OSError:
            continue
    return ImageFont.load_default()


def render_er_diagram(
    nodes: dict[str, str],        # logical name -> display label
    edges: list[DiagramEdge],
    out_path: Path,
) -> Path | None:
    """Render the diagram to *out_path* (PNG). Returns the path, or None if
    there is nothing meaningful to draw."""
    # Keep only edges whose both ends are included, and nodes with edges
    edges = [e for e in edges if e.parent in nodes and e.child in nodes
             and e.parent != e.child]

    # Transitive reduction on the 1:N edges: drop a direct edge when a longer
    # path already implies it (e.g. Project→Submission is implied by
    # Project→Initiative→Form→Submission). Keeps the diagram uncluttered
    # without losing the shape of the model.
    adj: dict[str, set[str]] = {}
    for e in edges:
        if not e.many_to_many:
            adj.setdefault(e.parent, set()).add(e.child)

    def reachable_without(start: str, target: str, skip_edge: tuple[str, str]) -> bool:
        stack, seen = [start], {start}
        while stack:
            cur = stack.pop()
            for nxt in adj.get(cur, ()):
                if (cur, nxt) == skip_edge:
                    continue
                if nxt == target:
                    return True
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return False

    edges = [
        e for e in edges
        if e.many_to_many
        or not reachable_without(e.parent, e.child, (e.parent, e.child))
    ]

    connected = {e.parent for e in edges} | {e.child for e in edges}
    nodes = {k: v for k, v in nodes.items() if k in connected}
    if not nodes or not edges:
        return None

    # ── Layer assignment: child at least one layer below parent ──────────
    layer = {n: 0 for n in nodes}
    hierarchical = [e for e in edges if not e.many_to_many]
    for _ in range(len(nodes)):  # relaxation with cycle guard
        changed = False
        for e in hierarchical:
            if layer[e.child] < layer[e.parent] + 1:
                layer[e.child] = layer[e.parent] + 1
                changed = True
        if not changed:
            break

    layers: dict[int, list[str]] = {}
    for n, l in layer.items():
        layers.setdefault(l, []).append(n)
    n_layers = max(layers) + 1

    # ── Within-layer ordering by parent barycenter (2 passes) ────────────
    order = {n: i for l in layers.values() for i, n in enumerate(sorted(l))}
    parents_of: dict[str, list[str]] = {}
    for e in edges:
        parents_of.setdefault(e.child, []).append(e.parent)
    for _ in range(2):
        for l in range(n_layers):
            def key(n):
                ps = [order[p] for p in parents_of.get(n, []) if p in order]
                return sum(ps) / len(ps) if ps else order[n]
            layers[l] = sorted(layers[l], key=key)
            for i, n in enumerate(layers[l]):
                order[n] = i

    # ── Geometry ──────────────────────────────────────────────────────────
    font = _font(FONT_SIZE)
    label_font = _font(LABEL_SIZE)
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))

    def text_w(t, f):
        box = probe.textbbox((0, 0), t, font=f)
        return box[2] - box[0]

    node_w = {n: max(110 * SCALE, text_w(nodes[n], font) + 2 * NODE_PAD_X * SCALE)
              for n in nodes}
    layer_w = {l: sum(node_w[n] for n in ns) + H_GAP * SCALE * (len(ns) - 1)
               for l, ns in layers.items()}
    canvas_w = max(layer_w.values()) + 2 * MARGIN * SCALE
    canvas_h = (n_layers * NODE_H + (n_layers - 1) * V_GAP + 2 * MARGIN) * SCALE

    pos: dict[str, tuple[int, int, int, int]] = {}  # x0, y0, x1, y1
    for l, ns in layers.items():
        x = (canvas_w - layer_w[l]) // 2
        y0 = (MARGIN + l * (NODE_H + V_GAP)) * SCALE
        for n in ns:
            pos[n] = (x, y0, x + node_w[n], y0 + NODE_H * SCALE)
            x += node_w[n] + H_GAP * SCALE

    # ── Draw ──────────────────────────────────────────────────────────────
    img = Image.new("RGB", (canvas_w, canvas_h), "white")
    draw = ImageDraw.Draw(img)

    def anchor(n, towards_y):
        x0, y0, x1, y1 = pos[n]
        cx = (x0 + x1) // 2
        return (cx, y1) if towards_y > y1 else (cx, y0)

    def edge_label(text, x, y):
        draw.text((x, y), text, font=label_font, fill=LABEL,
                  stroke_width=3 * SCALE, stroke_fill="white", anchor="mm")

    for e in edges:
        py = (pos[e.parent][1] + pos[e.parent][3]) // 2
        cy = (pos[e.child][1] + pos[e.child][3]) // 2
        p = anchor(e.parent, cy)
        c = anchor(e.child, py)
        draw.line([p, c], fill=LINE, width=SCALE)
        if e.many_to_many:
            edge_label("N : N", (p[0] + c[0]) // 2, (p[1] + c[1]) // 2)
        else:
            edge_label("1", int(p[0] + (c[0] - p[0]) * 0.14), int(p[1] + (c[1] - p[1]) * 0.14))
            edge_label("N", int(p[0] + (c[0] - p[0]) * 0.86), int(p[1] + (c[1] - p[1]) * 0.86))

    for n, (x0, y0, x1, y1) in pos.items():
        draw.rounded_rectangle([x0, y0, x1, y1], radius=8 * SCALE,
                               fill=FILL, outline=BORDER, width=SCALE)
        draw.text(((x0 + x1) // 2, (y0 + y1) // 2), nodes[n],
                  font=font, fill=TEXT, anchor="mm")

    img.save(out_path, "PNG")
    return out_path
