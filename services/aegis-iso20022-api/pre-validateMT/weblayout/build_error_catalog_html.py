#!/usr/bin/env python3
"""Generate a static HTML view of the FIN error-code catalog."""
from __future__ import annotations

import sys
from pathlib import Path
from collections import defaultdict
import yaml

ROOT = Path(__file__).resolve().parent
CATALOG_PATH = ROOT / "error_catalog.yaml"
OUTPUT_PATH = ROOT / "error_catalog.html"

CATEGORY_TITLES = {
    "T": "Text / Format validation",
    "C": "Currency / Amount semantics",
    "D": "Network validated rules",
    "E": "Enumeration / combination rules",
}

def load_catalog(path: Path):
    data = yaml.safe_load(path.read_text())
    catalog = data.get("catalog", {})
    grouped = defaultdict(list)
    for code, entry in sorted(catalog.items()):
        cat = entry.get("category", "?")
        grouped[cat].append((code, entry))
    return grouped

def html_escape(text: str) -> str:
    import html
    return html.escape(text, quote=True)

def build_html(grouped):
    nav_items = []
    content_items = []
    for cat in sorted(grouped.keys()):
        codes = grouped[cat]
        cat_title = CATEGORY_TITLES.get(cat, f"Category {cat}")
        nav_items.append(f"<h3>{html_escape(cat)} — {html_escape(cat_title)}</h3>")
        nav_items.append("<ul>")
        for code, entry in codes:
            nav_items.append(f'<li><a href="#code-{code}">{html_escape(code)}</a></li>')
        nav_items.append("</ul>")

        for code, entry in codes:
            title = entry.get("title", "")
            description = entry.get("description", "")
            severity = entry.get("severity", "")
            sources = entry.get("sources", [])
            content_items.append(f'<section class="error-section" id="code-{code}">')
            content_items.append(f'<h2>{html_escape(code)} — {html_escape(title)}</h2>')
            if severity:
                content_items.append(f'<p class="severity">Severity: {html_escape(severity)}</p>')
            if description:
                paragraphs = description.split('\n')
                for para in paragraphs:
                    if para.strip():
                        content_items.append(f'<p>{html_escape(para)}</p>')
            if sources:
                content_items.append('<details class="sources"><summary>Sources</summary><ul>')
                for src in sources:
                    content_items.append(f'<li>{html_escape(src)}</li>')
                content_items.append('</ul></details>')
            content_items.append('</section>')
    nav_html = "\n".join(nav_items)
    content_html = "\n".join(content_items)
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <title>FIN Error Code Catalog</title>
  <style>
    body {{ margin:0; font-family: 'Segoe UI', sans-serif; color:#222; }}
    .layout {{ display:flex; min-height: 100vh; }}
    nav {{ width: 22rem; background:#f4f6f9; border-right:1px solid #d7dbe3; padding:1.5rem; overflow-y:auto; position:sticky; top:0; height:100vh; box-sizing:border-box; }}
    nav h1 {{ font-size:1.3rem; margin-top:0; }}
    nav h3 {{ margin:1.5rem 0 0.5rem; font-size:1rem; color:#394b6a; }}
    nav ul {{ list-style:none; padding-left:1rem; margin:0; }}
    nav li {{ margin:0.25rem 0; }}
    nav a {{ color:#2a4b8d; text-decoration:none; }}
    nav a:hover {{ text-decoration:underline; }}
    main {{ flex:1; padding:2rem 3rem; background:white; overflow-y:auto; }}
    .error-section {{ margin-bottom:2.5rem; padding-bottom:2rem; border-bottom:1px solid #e3e8f0; }}
    .error-section h2 {{ margin-top:0; color:#1b2a4b; }}
    .severity {{ font-weight:600; color:#b9472b; }}
    details.sources {{ margin-top:1rem; background:#f7f9fc; padding:0.75rem 1rem; border-radius:0.4rem; }}
    details.sources summary {{ cursor:pointer; font-weight:600; }}
    @media (max-width: 900px) {{ nav {{ position:relative; height:auto; width:100%; border-right:none; border-bottom:1px solid #d7dbe3; }} main {{ padding:1.5rem; }} }}
  </style>
</head>
<body>
  <div class=\"layout\">
    <nav>
      <h1>FIN Error Catalog</h1>
      <p>Categories</p>
      {nav_html}
    </nav>
    <main>
      {content_html}
    </main>
  </div>
</body>
</html>
"""


def main():
    if not CATALOG_PATH.exists():
        sys.exit(f"Catalog not found: {CATALOG_PATH}")
    grouped = load_catalog(CATALOG_PATH)
    html = build_html(grouped)
    OUTPUT_PATH.write_text(html, encoding='utf-8')
    print(f"Generated {OUTPUT_PATH.relative_to(Path.cwd())}")

if __name__ == '__main__':
    main()
