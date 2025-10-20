#!/usr/bin/env python3
"""
Backbone Tracer – zero-dependency call-graph printer
Usage: python backbone_tracer.py <component-name>
"""
import ast, sys, pathlib, csv, textwrap

ROOT = pathlib.Path(__file__).resolve().parent
COMPONENT = sys.argv[1] if len(sys.argv) > 1 else "singletons"

# ------------------------------------------------------------------
# 1. Find every file that mentions the component
# ------------------------------------------------------------------
hits = []
for py in ROOT.rglob("*.py"):
    try:
        txt = py.read_text(encoding="utf-8")
        if COMPONENT in txt:
            hits.append(py.relative_to(ROOT))
    except Exception:
        pass

# ------------------------------------------------------------------
# 2. AST-parse each hit to extract import edges
# ------------------------------------------------------------------
edges = []  # (from, to, line)
for py in hits:
    try:
        tree = ast.parse((ROOT / py).read_text(encoding="utf-8"), filename=str(py))
    except Exception:
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if COMPONENT in alias.name:
                    edges.append((str(py), alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.module and COMPONENT in node.module:
                for alias in node.names:
                    edges.append((str(py), f"{node.module}.{alias.name}", node.lineno))

# ------------------------------------------------------------------
# 3. Print human-friendly report
# ------------------------------------------------------------------
print(f"# Backbone X-Ray – {COMPONENT}\n")
print("## Files that reference it\n")
for h in sorted(hits):
    print(f"- `{h}`")
print(f"\n## Import edges (caller → imported symbol)\n")
for frm, to, ln in edges:
    print(f"`{frm}` line {ln}  →  `{to}`")
print("\n## Leaves (files that import but are never imported)\n")
imported_as = {e[1] for e in edges}
leaves = [f for f in hits if not any(e[0] == str(f) for e in edges)]
for leaf in leaves:
    print(f"- `{leaf}`")

# ------------------------------------------------------------------
# 4. Optional CSV for Excel / Pandas
# ------------------------------------------------------------------
csv_path = ROOT / f"backbone-{COMPONENT}-edges.csv"
with csv_path.open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["from_file", "imported_symbol", "line"])
    writer.writerows(edges)
print(f"\n📊 CSV saved: `{csv_path}`")

