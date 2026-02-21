"""4단계: 포맷 변환 - 마크다운 본문을 HTML 및 플레인텍스트로 변환한다."""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def md_to_html_simple(md: str) -> str:
    """간단한 마크다운 → HTML 변환."""
    html = md
    # 헤더
    html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
    # 굵게
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    # 링크
    html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', html)
    # 목록
    html = re.sub(r"^- (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)
    html = re.sub(r"(<li>.*</li>\n?)+", r"<ul>\g<0></ul>", html, flags=re.DOTALL)
    # hr
    html = html.replace("---", "<hr>")
    # 단락
    paragraphs = []
    for block in html.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        if block.startswith(("<h", "<ul", "<hr", "<li")):
            paragraphs.append(block)
        else:
            paragraphs.append(f"<p>{block.replace(chr(10), '<br>')}</p>")
    return "\n".join(paragraphs)


def md_to_plain(md: str) -> str:
    """마크다운 → 플레인텍스트 변환."""
    text = md
    # 링크: [제목](URL) → 제목 (URL)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    # 마크다운 기호 제거
    text = re.sub(r"#{1,6}\s+", "", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"^- ", "• ", text, flags=re.MULTILINE)
    text = re.sub(r"^---$", "-" * 40, text, flags=re.MULTILINE)
    return text


def format_output(content_md: str, curated: dict, output_dir: Path, template_dir: Path) -> dict:
    """HTML, TXT, summary.json 생성."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- HTML ---
    html_body = md_to_html_simple(content_md)

    template_file = template_dir / "email.html.j2"
    if template_file.exists():
        env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=True)
        tmpl = env.get_template("email.html.j2")
        html_out = tmpl.render(content=html_body, unsubscribe_url="#unsubscribe")
    else:
        html_out = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Claude Code Newsletter</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f5f5; margin: 0; padding: 20px; color: #333; }}
    .wrapper {{ max-width: 600px; margin: 0 auto; background: #fff;
                border-radius: 8px; overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
    .header {{ background: #1a1a2e; color: #fff; padding: 32px 40px; }}
    .header h1 {{ margin: 0; font-size: 20px; font-weight: 600; }}
    .header p {{ margin: 8px 0 0; font-size: 13px; opacity: 0.7; }}
    .body {{ padding: 32px 40px; }}
    h1 {{ font-size: 22px; color: #1a1a2e; border-bottom: 2px solid #e8e8e8;
          padding-bottom: 10px; }}
    h2 {{ font-size: 18px; color: #2d2d44; margin-top: 32px; }}
    h3 {{ font-size: 15px; color: #444; }}
    a {{ color: #5b6af0; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    hr {{ border: none; border-top: 1px solid #e8e8e8; margin: 24px 0; }}
    ul {{ padding-left: 20px; }}
    li {{ margin: 6px 0; line-height: 1.6; }}
    p {{ line-height: 1.7; }}
    .footer {{ background: #f9f9f9; padding: 20px 40px;
               font-size: 12px; color: #999; text-align: center;
               border-top: 1px solid #e8e8e8; }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <h1>Claude Code Newsletter</h1>
      <p>매주 일요일 · Claude Code 활용 사례 모음</p>
    </div>
    <div class="body">
      {html_body}
    </div>
    <div class="footer">
      <a href="#unsubscribe">구독 해지</a> · Claude Code Newsletter
    </div>
  </div>
</body>
</html>"""

    html_file = output_dir / "email.html"
    html_file.write_text(html_out)
    print(f"  [format] HTML 저장 → {html_file}")

    # --- TXT ---
    txt_out = md_to_plain(content_md)
    txt_file = output_dir / "email.txt"
    txt_file.write_text(txt_out)
    print(f"  [format] TXT  저장 → {txt_file}")

    # --- summary.json ---
    items = curated.get("items", [])
    stats = {
        "total_collected": curated.get("total_collected", 0),
        "total_curated": len(items),
        "featured": sum(1 for i in items if i.get("category") == "featured"),
        "use_cases": sum(1 for i in items if i.get("category") == "use-case"),
        "tips": sum(1 for i in items if i.get("category") == "tip"),
        "tools": sum(1 for i in items if i.get("category") == "tool"),
        "news": sum(1 for i in items if i.get("category") == "news"),
    }
    sources = list({i.get("source") for i in items if i.get("source")})
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "period": curated.get("period", {}),
        "stats": stats,
        "sources": sources,
        "output_files": ["email.html", "email.txt", "summary.json"],
    }
    summary_file = output_dir / "summary.json"
    summary_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"  [format] JSON 저장 → {summary_file}")

    return summary
