# Claude Code 콘텐츠 수집 소스 목록

조사일: 2026-02-21

---

## 활성 소스

### Reddit

| 서브레딧 | 특징 | API |
|---------|------|-----|
| r/ClaudeCode | 주간 기여자 4,200+, 가장 활발 | Reddit RSS (인증 불필요) |
| r/ClaudeAI | 일반 Claude 관련 | Reddit RSS |
| r/ChatGPTCoding | AI 코딩 도구 전반 | Reddit RSS |

**수집 기준:** 업보트 10+ / 최근 7일 이내

**API 엔드포인트:**
```
GET https://www.reddit.com/r/{subreddit}/hot.json?limit=25
Headers: User-Agent: ClaudeCodeNewsletter/1.0
```

---

### Hacker News

**API (무료, 인증 불필요):**
```
GET https://hn.algolia.com/api/v1/search
?query=claude+code&tags=story&numericFilters=points>=20,created_at_i>={timestamp}
```

**수집 기준:** 포인트 20+ / 최근 7일 이내

---

### GitHub

**엔드포인트:**
```
GET https://api.github.com/repos/anthropics/claude-code/issues
GET https://api.github.com/repos/anthropics/claude-code/discussions
```

**주목 저장소:**
- https://github.com/hesreallyhim/awesome-claude-code (25k+ stars)
- https://github.com/ruvnet/claude-flow

---

### Dev.to / Medium

- Dev.to: `claude-code` 태그 RSS
- Medium: 검색 기반 (API 없음, 크롤링 필요)

---

## 미사용 소스 (향후 추가 가능)

| 소스 | 이유 |
|------|------|
| Twitter/X | API 유료화로 현재 미사용 |
| LinkedIn | API 제한적 |
| YouTube | 동영상 콘텐츠, 요약 어려움 |

---

## 수집 시 주의사항

- Reddit rate limit: 60 req/min
- GitHub rate limit: 5,000 req/hr (인증 시), 60 req/hr (미인증)
- HN Algolia API: 제한 없음 (공개 무료)
- 저작권: 요약 시 반드시 원문 출처 링크 포함
