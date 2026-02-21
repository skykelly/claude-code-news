# Claude Code Newsletter - 자동화 프로젝트

## 에이전트 시작 시 필수 절차

**새 세션을 시작할 때마다 반드시 아래 두 파일을 먼저 읽어라.**

```
plan.md      # 전체 작업 목록 및 각 에이전트의 담당 범위
progress.md  # 현재까지 완료된 작업, 진행 중인 작업, 블로커
```

1. `plan.md`를 읽어 전체 작업 구조와 내 담당 태스크를 파악한다.
2. `progress.md`를 읽어 현재 진행 상태와 이어서 해야 할 일을 확인한다.
3. 작업을 시작하면 `progress.md`의 해당 태스크 상태를 `in_progress`로 업데이트한다.
4. 작업이 완료되면 `progress.md`를 `completed`로 업데이트하고 결과를 기록한다.
5. 블로커가 생기면 `progress.md`에 `blocked` 상태와 이유를 기록한다.

---

## plan.md 형식

`plan.md`는 전체 작업을 에이전트별로 분리하여 관리한다.

```markdown
# 작업 계획

## Agent A - 콘텐츠 수집
- [ ] TASK-01: Reddit 수집 모듈 구현 (src/collect_reddit.py)
- [ ] TASK-02: GitHub 수집 모듈 구현 (src/collect_github.py)
- [ ] TASK-03: HN 수집 모듈 구현 (src/collect_hn.py)

## Agent B - 필터링 & 생성
- [ ] TASK-04: 필터링 로직 구현 (src/filter.py)  [depends: TASK-01~03]
- [ ] TASK-05: Claude API 연동 및 본문 생성 (src/generate.py)  [depends: TASK-04]

## Agent C - 포맷 & 인프라
- [ ] TASK-06: Jinja2 HTML 템플릿 작성 (templates/email.html.j2)
- [ ] TASK-07: 포맷 변환 모듈 구현 (src/format.py)  [depends: TASK-05, TASK-06]
- [ ] TASK-08: GitHub Actions 워크플로우 작성 (.github/workflows/newsletter.yml)
- [ ] TASK-09: main.py 진입점 구현 (src/main.py)  [depends: TASK-07]
```

---

## progress.md 형식

`progress.md`는 실시간 진행 상태를 기록한다.

```markdown
# 진행 상황

마지막 업데이트: YYYY-MM-DD HH:MM

## 완료 (completed)
- TASK-01: Reddit 수집 모듈 완료 (2026-02-21) - Agent A

## 진행 중 (in_progress)
- TASK-02: GitHub 수집 모듈 작업 중 - Agent A
  - 현재: GraphQL API 인증 구현 중

## 대기 (pending)
- TASK-03 ~ TASK-09

## 블로커 (blocked)
- 없음
```

---

## 작업 규칙

- 같은 파일을 동시에 수정하지 않는다. `plan.md`에서 담당 파일을 명확히 분리한다.
- 의존 관계(`depends`)가 있는 태스크는 선행 태스크 완료 후 시작한다.
- 작업 중 설계 변경이 필요하면 `plan.md`를 업데이트하고 `progress.md`에 변경 이유를 기록한다.
- 각 에이전트는 자신의 담당 태스크 외 파일은 읽기만 하고 수정하지 않는다.

---

## 프로젝트 개요

매주 일요일 오전 8시 발송할 **Claude Code 활용 사례 뉴스레터** 이메일 본문을 자동으로 생성하는 파이프라인.

플랫폼 발송은 별도 처리하며, 이 프로젝트의 범위는 **이메일 콘텐츠(HTML + 텍스트) 생성**까지다.

---

## 목표 산출물

매주 실행 시 다음 파일을 생성한다:

```
output/
  YYYY-MM-DD/
    email.html      # 발송용 HTML 본문
    email.txt       # 플레인텍스트 fallback
    summary.json    # 수집된 원본 데이터 요약
```

---

## 파이프라인 단계

### 1단계: 콘텐츠 수집 (Collect)

다음 소스에서 지난 7일간의 Claude Code 관련 콘텐츠를 수집한다.

**소스 목록:**
- Reddit: `r/ClaudeCode`, `r/ClaudeAI`, `r/ChatGPTCoding`
- GitHub: `anthropics/claude-code` 이슈 및 디스커션, trending repos
- Hacker News: `claude code` 키워드 검색
- Twitter/X: `#ClaudeCode`, `@AnthropicAI` 멘션
- Dev.to / Medium: `claude-code` 태그 기사

**수집 기준:**
- 최소 좋아요/업보트: Reddit 10+, HN 20+
- 게시일: 최근 7일 이내
- 언어: 영어, 한국어 모두 포함

### 2단계: 필터링 & 분류 (Filter)

수집된 항목을 다음 카테고리로 분류한다:

| 카테고리 | 설명 |
|----------|------|
| `featured` | 이번 주 메인 사례 (1개) |
| `use-case` | 실제 개발 활용 사례 |
| `tip` | 팁, 트릭, 워크플로우 |
| `tool` | 관련 도구/플러그인/확장 |
| `news` | Anthropic 공식 업데이트 |

중복 항목, 광고성 콘텐츠, 주제 무관 항목은 제거한다.

### 3단계: 콘텐츠 생성 (Generate)

Claude API를 사용해 이메일 본문을 작성한다.

**뉴스레터 구조:**
```
[헤더] 이번 주 Claude Code 뉴스레터 - YYYY년 MM월 DD일

[이번 주 하이라이트] featured 항목 심층 소개 (300~400자)

[실전 사례 모음] use-case 항목 3~5개 (각 100~150자 요약 + 원문 링크)

[이번 주 팁] tip 항목 2~3개 (간결한 포맷)

[새로운 도구] tool 항목 1~2개

[공식 업데이트] news 항목 (있을 경우)

[푸터] 구독 해지 링크, 발신자 정보
```

**작성 톤:**
- 개발자 대상, 실용적이고 간결하게
- 과도한 홍보 문구 지양
- 한국어 뉴스레터의 경우 자연스러운 한국어로 작성

### 4단계: 포맷 변환 (Format)

- HTML 템플릿에 생성된 콘텐츠 삽입
- 플레인텍스트 버전 별도 생성
- 링크 유효성 검증

---

## 기술 스택

- **언어**: Python 3.11+
- **Claude API**: `anthropic` SDK (`claude-sonnet-4-6` 모델 사용)
- **HTTP 요청**: `httpx` 또는 `requests`
- **HTML 생성**: `jinja2` 템플릿
- **스케줄링**: GitHub Actions (매주 일요일 23:00 UTC = 한국 시간 08:00)
- **환경 변수**: `.env` 파일 (로컬), GitHub Secrets (CI)

---

## 환경 변수

```
ANTHROPIC_API_KEY=      # Claude API 키 (필수)
REDDIT_CLIENT_ID=       # Reddit API (선택)
REDDIT_CLIENT_SECRET=   # Reddit API (선택)
OUTPUT_DIR=output       # 결과물 저장 경로
NEWSLETTER_LANG=ko      # 뉴스레터 언어 (ko / en)
```

---

## 파일 구조

```
.
├── CLAUDE.md                  # 이 파일 (에이전트 공통 규칙)
├── plan.md                    # 전체 작업 목록 및 에이전트 담당 분배
├── progress.md                # 실시간 진행 상태 추적
├── .env.example               # 환경 변수 템플릿
├── requirements.txt
├── src/
│   ├── collect.py             # 1단계: 콘텐츠 수집
│   ├── filter.py              # 2단계: 필터링 & 분류
│   ├── generate.py            # 3단계: Claude API로 본문 생성
│   ├── format.py              # 4단계: HTML/텍스트 변환
│   └── main.py                # 전체 파이프라인 실행 진입점
├── templates/
│   └── email.html.j2          # Jinja2 HTML 이메일 템플릿
├── output/                    # 생성된 이메일 저장 (gitignore)
└── .github/
    └── workflows/
        └── newsletter.yml     # GitHub Actions 스케줄 워크플로우
```

---

## 실행 방법

```bash
# 로컬 실행
python src/main.py

# 특정 날짜 기준으로 실행
python src/main.py --date 2026-02-23

# 수집만 실행 (디버깅)
python src/main.py --step collect
```

---

## 주의사항

- Reddit/Twitter API 호출 시 rate limit 준수
- Claude API 비용: 주당 1회 실행 기준 약 $0.01~0.05 예상
- 저작권: 외부 콘텐츠 요약 시 반드시 원문 출처 링크 포함
- 개인정보: 수집 데이터에 개인 식별 정보 포함 금지
