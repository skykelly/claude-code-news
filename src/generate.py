"""3단계: 콘텐츠 생성 - Claude API로 뉴스레터 본문을 작성한다."""

import os
from datetime import datetime, timezone
from pathlib import Path


def _build_prompt(curated: dict, lang: str = "ko") -> str:
    items = curated["items"]
    period_from = curated["period"]["from"]
    period_to = curated["period"]["to"]

    def group(cat):
        return [i for i in items if i["category"] == cat]

    featured = group("featured")
    use_cases = group("use-case")[:4]
    tips = group("tip")[:3]
    tools = group("tool")[:2]
    news = group("news")[:2]

    def fmt_item(item):
        return f"- 제목: {item['title']}\n  URL: {item['url']}\n  요약: {item.get('summary','')}"

    sections = []
    if featured:
        sections.append("=== 이번 주 하이라이트 (featured) ===\n" + fmt_item(featured[0]))
    if use_cases:
        sections.append("=== 실전 사례 (use-case) ===\n" + "\n".join(fmt_item(i) for i in use_cases))
    if tips:
        sections.append("=== 팁 & 트릭 (tip) ===\n" + "\n".join(fmt_item(i) for i in tips))
    if tools:
        sections.append("=== 새로운 도구 (tool) ===\n" + "\n".join(fmt_item(i) for i in tools))
    if news:
        sections.append("=== 공식 업데이트 (news) ===\n" + "\n".join(fmt_item(i) for i in news))

    content_block = "\n\n".join(sections)
    date_str = datetime.now(timezone.utc).strftime("%Y년 %m월 %d일")

    return f"""아래 수집된 Claude Code 관련 콘텐츠를 바탕으로 한국어 개발자 뉴스레터 본문을 마크다운으로 작성해줘.

기간: {period_from} ~ {period_to}
날짜: {date_str}

**작성 규칙:**
- 개발자 대상, 실용적이고 간결하게
- 과도한 홍보 문구 지양
- 각 항목에 반드시 원문 링크 포함
- 한국어로 자연스럽게 (영문 고유명사는 그대로)

**뉴스레터 구조 (이 순서 그대로):**
1. 헤더: "이번 주 Claude Code 뉴스레터 - {date_str}"
2. 이번 주 하이라이트: featured 항목 300~400자 심층 소개
3. 실전 사례 모음: use-case 항목 각 100~150자 요약 + 링크
4. 이번 주 팁: tip 항목 간결하게
5. 새로운 도구: tool 항목 (있을 경우)
6. 공식 업데이트: news 항목 (있을 경우)
7. 푸터: "다음 호는 다음 주 일요일에 찾아옵니다. | 구독 해지: {{{{UNSUBSCRIBE_URL}}}}"

---

{content_block}
"""


def _fallback_content(curated: dict) -> str:
    """Claude API 없을 때 템플릿 기반 본문 생성."""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y년 %m월 %d일")
    items = curated["items"]

    def group(cat):
        return [i for i in items if i["category"] == cat]

    featured = group("featured")
    use_cases = group("use-case")[:4]
    tips = group("tip")[:3]
    tools = group("tool")[:2]
    news_items = group("news")[:2]

    lines = [f"# 이번 주 Claude Code 뉴스레터 - {date_str}", ""]

    if featured:
        item = featured[0]
        lines += [
            "## 🌟 이번 주 하이라이트",
            "",
            f"**{item['title']}**",
            "",
            item.get("summary", "이번 주 가장 주목받은 Claude Code 활용 사례입니다."),
            "",
            f"👉 [원문 읽기]({item['url']})",
            "",
            "---",
            "",
        ]

    if use_cases:
        lines += ["## 💻 실전 사례 모음", ""]
        for item in use_cases:
            lines += [
                f"### {item['title']}",
                item.get("summary", ""),
                f"[원문 링크]({item['url']})",
                "",
            ]
        lines += ["---", ""]

    if tips:
        lines += ["## 💡 이번 주 팁", ""]
        for item in tips:
            lines += [f"- **{item['title']}** — [바로가기]({item['url']})"]
        lines += ["", "---", ""]

    if tools:
        lines += ["## 🛠 새로운 도구", ""]
        for item in tools:
            lines += [f"- **{item['title']}** — [바로가기]({item['url']})"]
        lines += ["", "---", ""]

    if news_items:
        lines += ["## 📢 공식 업데이트", ""]
        for item in news_items:
            lines += [f"- **{item['title']}** — [바로가기]({item['url']})"]
        lines += ["", "---", ""]

    lines += [
        "다음 호는 다음 주 일요일에 찾아옵니다.",
        "",
        "구독 해지: {{UNSUBSCRIBE_URL}}",
    ]

    return "\n".join(lines)


def generate(curated: dict, output_dir: Path, lang: str = "ko") -> str:
    """Claude API로 본문 생성. API 키 없으면 fallback 템플릿 사용."""
    output_dir.mkdir(parents=True, exist_ok=True)
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()

    if api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            print("  [generate] Claude API로 본문 생성 중...")
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2048,
                messages=[{"role": "user", "content": _build_prompt(curated, lang)}],
            )
            content = message.content[0].text
            print("  [generate] Claude API 생성 완료")
        except Exception as e:
            print(f"  [generate] Claude API 실패 ({e}) → fallback 사용")
            content = _fallback_content(curated)
    else:
        print("  [generate] ANTHROPIC_API_KEY 없음 → 템플릿 기반 생성")
        content = _fallback_content(curated)

    out_file = output_dir / "content.md"
    out_file.write_text(content)
    print(f"  [generate] 본문 저장 → {out_file}")
    return content
