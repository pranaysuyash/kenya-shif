#!/usr/bin/env python3
"""
Builds an HTML version of STREAMLIT_USER_GUIDE.md with simple CSS.
Open the generated HTML in a browser and 'Print to PDF' for a polished PDF.
"""
from pathlib import Path

TEMPLATE = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>Streamlit User Guide</title>
  <style>
    :root { --text: #1a1a1a; --muted: #333840; --accent: #0b3d91; }
    body { font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif; color: var(--text); line-height: 1.6; max-width: 860px; margin: 2rem auto; padding: 0 1rem; }
    h1, h2, h3 { color: var(--muted); }
    code, pre { background: #f5f6f8; border-radius: 6px; padding: 0.2rem 0.4rem; }
    pre { padding: 1rem; overflow: auto; }
    a { color: var(--accent); }
    hr { margin: 2rem 0; }
    .callout { background: #eef4ff; border-left: 4px solid #0b3d91; padding: 0.8rem 1rem; border-radius: 6px; }
  </style>
  <script>
    document.addEventListener('DOMContentLoaded', () => {
      const headings = document.querySelectorAll('h2, h3');
      headings.forEach(h => { if (!h.id) h.id = h.textContent.toLowerCase().replace(/\s+/g,'-').replace(/[^a-z0-9\-]/g,''); });
    });
  </script>
  <link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github.min.css\">
</head>
<body>
  {body}
</body>
</html>
"""

def md_to_html(md: str) -> str:
    try:
        import markdown  # type: ignore
        return markdown.markdown(md, extensions=["tables", "fenced_code"]) 
    except Exception:
        html = md.replace('\n\n', '<br><br>')
        html = html.replace('\n', '<br>')
        return f"<pre>{html}</pre>"

def main():
    root = Path(__file__).resolve().parent
    md_path = root / "STREAMLIT_USER_GUIDE.md"
    out_path = root / "STREAMLIT_USER_GUIDE.html"
    if not md_path.exists():
        raise SystemExit(f"Missing {md_path}")
    md = md_path.read_text(encoding='utf-8')
    body = md_to_html(md)
    html = TEMPLATE.format(body=body)
    out_path.write_text(html, encoding='utf-8')
    print(f"✅ Wrote {out_path}")
    print("➡️  Open in a browser and use 'Print to PDF' to export a PDF.")

if __name__ == "__main__":
    main()

