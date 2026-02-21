"""2단계: 필터링 & 분류 - 수집된 항목을 카테고리별로 분류한다."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


CATEGORY_KEYWORDS = {
    "news": ["anthropic", "releases", "release", "update", "announces", "new feature", "sdk", "official"],
    "tool": ["tool", "plugin", "extension", "library", "framework", "cli", "vscode", "stars", "repo", "github"],
    "tip": ["tip", "trick", "workflow", "how to", "guide", "방법", "팁", "deep dive", "slash command", "skill", "hook"],
    "use-case": ["built", "made", "created", "saas", "app", "project", "production", "real", "사례", "활용", "구성"],
}


def classify(item: dict) -> str:
    """hint 또는 키워드 기반으로 카테고리를 결정한다."""
    hint = item.get("category_hint", "unknown")
    if hint != "unknown":
        return hint

    text = (item.get("title", "") + " " + item.get("summary", "")).lower()
    scores = {cat: 0 for cat in CATEGORY_KEYWORDS}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[cat] += 1

    best = max(scores, key=lambda c: scores[c])
    return best if scores[best] > 0 else "use-case"


def filter_and_curate(raw_items: list[dict], output_dir: Path) -> dict:
    """필터링 및 분류 후 curated.json 저장."""
    output_dir.mkdir(parents=True, exist_ok=True)
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    filtered = []
    seen_titles = set()

    for item in raw_items:
        # 7일 이내 확인
        try:
            pub = datetime.fromisoformat(item["published_at"])
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=timezone.utc)
            if pub < cutoff:
                continue
        except Exception:
            pass

        # 제목 중복 제거
        title_key = item["title"].lower().strip()
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)

        item["category"] = classify(item)
        filtered.append(item)

    # score 기준 정렬
    filtered.sort(key=lambda x: x.get("score", 0), reverse=True)

    # featured 선정: 가장 높은 score의 use-case 또는 전체 1위
    featured_id = None
    for item in filtered:
        if item["category"] == "use-case":
            featured_id = item["id"]
            break
    if not featured_id and filtered:
        featured_id = filtered[0]["id"]

    for item in filtered:
        if item["id"] == featured_id:
            item["category"] = "featured"
            break

    now = datetime.now(timezone.utc)
    curated = {
        "curated_at": now.isoformat(),
        "period": {
            "from": (now - timedelta(days=7)).strftime("%Y-%m-%d"),
            "to": now.strftime("%Y-%m-%d"),
        },
        "total_collected": len(raw_items),
        "total_curated": len(filtered),
        "items": filtered,
    }

    out_file = output_dir / "curated.json"
    out_file.write_text(json.dumps(curated, ensure_ascii=False, indent=2))
    print(f"  [filter] {len(filtered)}개 항목 큐레이션 완료 → {out_file}")
    return curated
