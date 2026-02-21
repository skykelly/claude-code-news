"""1단계: 콘텐츠 수집 - Reddit, GitHub, Hacker News에서 Claude Code 관련 항목 수집."""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx


def _cutoff_dt(days: int = 7) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


# ---------------------------------------------------------------------------
# Mock 데이터 (API 키 없을 때 / --test 모드)
# ---------------------------------------------------------------------------

MOCK_ITEMS = [
    {
        "id": "reddit_001",
        "source": "reddit",
        "title": "I built a full SaaS in 3 days using Claude Code – here's how",
        "url": "https://reddit.com/r/ClaudeAI/comments/example1",
        "author": "dev_user_1",
        "published_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
        "score": 342,
        "summary": "Used Claude Code to scaffold a Next.js + FastAPI SaaS from scratch. Took 3 days solo. Sharing my workflow and prompts.",
        "category_hint": "use-case",
    },
    {
        "id": "reddit_002",
        "source": "reddit",
        "title": "Claude Code tip: use CLAUDE.md per-directory for monorepos",
        "url": "https://reddit.com/r/ClaudeCode/comments/example2",
        "author": "monorepo_fan",
        "published_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
        "score": 211,
        "summary": "Placing CLAUDE.md in each package directory gives agents focused context. Huge improvement for large codebases.",
        "category_hint": "tip",
    },
    {
        "id": "hn_001",
        "source": "hackernews",
        "title": "Ask HN: How are you using Claude Code in production?",
        "url": "https://news.ycombinator.com/item?id=example3",
        "author": "hn_user",
        "published_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        "score": 87,
        "summary": "Thread with 200+ developers sharing real production use cases: legacy refactoring, test generation, API scaffolding.",
        "category_hint": "use-case",
    },
    {
        "id": "github_001",
        "source": "github",
        "title": "awesome-claude-code reaches 25k stars",
        "url": "https://github.com/hesreallyhim/awesome-claude-code",
        "author": "hesreallyhim",
        "published_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
        "score": 156,
        "summary": "Curated list of Claude Code tools, skills, hooks, and workflows hits 25k GitHub stars.",
        "category_hint": "tool",
    },
    {
        "id": "devto_001",
        "source": "devto",
        "title": "Claude Code Agent Teams: 실전 멀티에이전트 워크플로우 구성법",
        "url": "https://dev.to/example/claude-code-agent-teams",
        "author": "kr_dev",
        "published_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
        "score": 64,
        "summary": "Agent Teams 실험 기능을 사용해 수집→필터→생성 파이프라인을 구성한 경험을 공유한다.",
        "category_hint": "use-case",
    },
    {
        "id": "reddit_003",
        "source": "reddit",
        "title": "Anthropic releases Claude Code SDK for programmatic access",
        "url": "https://reddit.com/r/ClaudeAI/comments/example4",
        "author": "ai_news_bot",
        "published_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        "score": 178,
        "summary": "Anthropic releases Claude Code SDK enabling CI/CD and headless automation without interactive sessions.",
        "category_hint": "news",
    },
    {
        "id": "hn_002",
        "source": "hackernews",
        "title": "Claude Code slash commands and skills – a deep dive",
        "url": "https://news.ycombinator.com/item?id=example5",
        "author": "power_user",
        "published_at": (datetime.now(timezone.utc) - timedelta(days=6)).isoformat(),
        "score": 45,
        "summary": "How to build reusable slash commands with SKILL.md files, frontmatter options, and context forking.",
        "category_hint": "tip",
    },
]


# ---------------------------------------------------------------------------
# 실제 수집 함수 (API 키 있을 때)
# ---------------------------------------------------------------------------

def collect_hackernews(cutoff: datetime) -> list[dict]:
    """HN Algolia API로 claude code 키워드 검색."""
    try:
        url = "https://hn.algolia.com/api/v1/search"
        params = {
            "query": "claude code",
            "tags": "story",
            "numericFilters": f"points>=20,created_at_i>={int(cutoff.timestamp())}",
            "hitsPerPage": 20,
        }
        resp = httpx.get(url, params=params, timeout=10)
        resp.raise_for_status()
        items = []
        for hit in resp.json().get("hits", []):
            items.append({
                "id": f"hn_{hit['objectID']}",
                "source": "hackernews",
                "title": hit.get("title", ""),
                "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit['objectID']}",
                "author": hit.get("author", ""),
                "published_at": datetime.fromtimestamp(
                    hit["created_at_i"], tz=timezone.utc
                ).isoformat(),
                "score": hit.get("points", 0),
                "summary": "",
                "category_hint": "unknown",
            })
        return items
    except Exception as e:
        print(f"  [HN] 수집 실패: {e}")
        return []


def collect_reddit_rss(subreddit: str, cutoff: datetime) -> list[dict]:
    """Reddit RSS (인증 불필요) 수집."""
    try:
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=25"
        headers = {"User-Agent": "ClaudeCodeNewsletter/1.0"}
        resp = httpx.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        items = []
        for post in resp.json()["data"]["children"]:
            d = post["data"]
            created = datetime.fromtimestamp(d["created_utc"], tz=timezone.utc)
            if created < cutoff or d["score"] < 10:
                continue
            items.append({
                "id": f"reddit_{d['id']}",
                "source": "reddit",
                "title": d["title"],
                "url": f"https://reddit.com{d['permalink']}",
                "author": d["author"],
                "published_at": created.isoformat(),
                "score": d["score"],
                "summary": d.get("selftext", "")[:300],
                "category_hint": "unknown",
            })
        return items
    except Exception as e:
        print(f"  [Reddit/{subreddit}] 수집 실패: {e}")
        return []


# ---------------------------------------------------------------------------
# 메인 수집 함수
# ---------------------------------------------------------------------------

def collect(output_dir: Path, test_mode: bool = False) -> list[dict]:
    """모든 소스에서 콘텐츠를 수집하고 raw JSON으로 저장한다."""
    cutoff = _cutoff_dt(days=7)
    output_dir.mkdir(parents=True, exist_ok=True)

    if test_mode:
        print("  [collect] 테스트 모드: mock 데이터 사용")
        items = MOCK_ITEMS
    else:
        print("  [collect] HN 수집 중...")
        items = collect_hackernews(cutoff)

        print("  [collect] Reddit 수집 중...")
        for sub in ["ClaudeCode", "ClaudeAI", "ChatGPTCoding"]:
            items.extend(collect_reddit_rss(sub, cutoff))

        if not items:
            print("  [collect] 실제 수집 결과 없음 → mock 데이터로 대체")
            items = MOCK_ITEMS

    # 중복 제거 (id 기준)
    seen = set()
    unique = []
    for item in items:
        if item["id"] not in seen:
            seen.add(item["id"])
            unique.append(item)

    out_file = output_dir / "raw.json"
    out_file.write_text(json.dumps(unique, ensure_ascii=False, indent=2))
    print(f"  [collect] {len(unique)}개 항목 저장 → {out_file}")
    return unique
