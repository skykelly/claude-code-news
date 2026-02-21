# Claude Code Newsletter

매주 일요일 오전 8시(KST)에 **Claude Code 활용 사례 뉴스레터**를 자동으로 생성하고 이메일로 발송하는 파이프라인입니다.

Reddit, Hacker News, GitHub 등 주요 커뮤니티에서 지난 7일간의 콘텐츠를 수집·분류·요약하여 HTML 이메일로 변환합니다.

---

## 워크플로

```
[수집] Reddit / HN / GitHub
    ↓
[필터링] 중복 제거 · 카테고리 분류
    ↓
[본문 생성] 뉴스레터 마크다운 작성
    ↓
[포맷 변환] HTML · TXT · summary.json 생성
    ↓
[발송] Gmail SMTP → 수신자
```

각 단계는 독립 모듈로 분리되어 있어 특정 단계만 단독 실행할 수 있습니다.

---

## 폴더 구조

```
.
├── CLAUDE.md                        # 에이전트 공통 규칙 (Claude Code 전용)
├── plan.md                          # 전체 태스크 목록 및 에이전트 담당 분배
├── progress.md                      # 실시간 진행 상태 추적
├── requirements.txt                 # Python 의존 패키지
├── .env.example                     # 환경 변수 템플릿
│
├── src/                             # 파이프라인 핵심 모듈
│   ├── main.py                      # 진입점 — 4단계 파이프라인 오케스트레이션
│   ├── collect.py                   # 1단계: 콘텐츠 수집 (HN, Reddit RSS)
│   ├── filter.py                    # 2단계: 필터링 & 카테고리 분류
│   ├── generate.py                  # 3단계: 뉴스레터 본문 생성
│   ├── format.py                    # 4단계: HTML / TXT 포맷 변환
│   └── send.py                      # Gmail SMTP 이메일 발송
│
├── templates/
│   └── email.html.j2                # Jinja2 HTML 이메일 템플릿
│
├── knowledge/                       # 에이전트 참조용 지식 베이스
│   ├── index.md                     # 파일 목록 및 사용 가이드
│   ├── claude-code-use-cases.md     # Claude Code 활용 사례 연구
│   ├── claude-code-architecture.md  # Claude Code 에이전트/스킬 구조
│   ├── content-sources.md           # 수집 소스 API 정보 및 rate limit
│   └── email-delivery.md            # 이메일 발송 도구 및 렌더링 주의사항
│
├── output/                          # 생성된 뉴스레터 저장 (gitignore)
│   └── YYYY-MM-DD/
│       ├── raw.json                 # 수집된 원시 데이터
│       ├── curated.json             # 필터링·분류된 데이터
│       ├── content.md               # 생성된 뉴스레터 마크다운
│       ├── email.html               # 발송용 HTML 본문
│       ├── email.txt                # 플레인텍스트 fallback
│       └── summary.json             # 수집 통계 요약
│
├── .github/
│   └── workflows/
│       └── newsletter.yml           # GitHub Actions 스케줄 워크플로우
│
└── .claude/                         # Claude Code 에이전트 & 스킬 정의
    ├── agents/
    │   ├── collector.md             # 수집 전문 에이전트
    │   ├── curator.md               # 필터링·분류 에이전트
    │   ├── writer.md                # 본문 작성 에이전트
    │   └── formatter.md             # 포맷 변환 에이전트
    └── skills/
        ├── generate-newsletter/     # /generate-newsletter 커맨드
        ├── check-progress/          # /check-progress 커맨드
        ├── preview/                 # /preview 커맨드
        ├── save-research/           # /save-research 커맨드
        └── search-knowledge/        # /search-knowledge 커맨드
```

---

## 주요 파일 설명

### `src/main.py` — 파이프라인 진입점

4단계를 순서대로 실행하고 결과를 `output/YYYY-MM-DD/`에 저장합니다.

```bash
python src/main.py                        # 전체 실행
python src/main.py --test                 # mock 데이터로 테스트
python src/main.py --step collect         # 수집 단계만 실행
python src/main.py --date 2026-02-23      # 특정 날짜 기준 실행
python src/main.py --send user@example.com  # 생성 후 이메일 발송
```

### `src/collect.py` — 콘텐츠 수집

| 소스 | 방식 | 수집 기준 |
|------|------|-----------|
| Hacker News | Algolia API | `claude code` 키워드, 최근 7일, 포인트 20+ |
| Reddit | RSS 피드 | `r/ClaudeAI`, `r/ClaudeCode`, 업보트 10+ |
| GitHub | (확장 가능) | `anthropics/claude-code` 이슈·디스커션 |

`--test` 플래그 또는 API 실패 시 내장 mock 데이터 7개로 fallback합니다.

### `src/filter.py` — 필터링 & 분류

수집된 항목을 아래 카테고리로 분류하고 중복·광고·무관 항목을 제거합니다.

| 카테고리 | 설명 |
|----------|------|
| `featured` | 이번 주 하이라이트 (1개) |
| `use-case` | 실제 개발 활용 사례 |
| `tip` | 팁, 트릭, 워크플로우 |
| `tool` | 관련 도구·플러그인·확장 |
| `news` | Anthropic 공식 업데이트 |

### `src/generate.py` — 본문 생성

`ANTHROPIC_API_KEY`가 설정된 경우 Claude API(`claude-sonnet-4-6`)로 본문을 생성합니다.
미설정 시 Jinja2 템플릿 기반 fallback으로 자동 전환되어 **API 비용 없이** 실행됩니다.

### `src/format.py` — 포맷 변환

마크다운 본문을 `templates/email.html.j2` 템플릿에 주입해 HTML을 생성하고, 태그를 제거한 플레인텍스트 버전도 함께 만듭니다.

### `src/send.py` — 이메일 발송

Gmail SMTP(포트 465, SSL)를 사용합니다. `GMAIL_USER`와 `GMAIL_APP_PASSWORD` 환경 변수가 필요합니다.

---

## 실행 환경 설정

### 1. 의존 패키지 설치

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 아래 값을 채웁니다.

| 변수 | 필수 | 설명 |
|------|------|------|
| `ANTHROPIC_API_KEY` | 선택 | Claude API 키 (없으면 템플릿 fallback) |
| `GMAIL_USER` | 발송 시 필수 | 발신 Gmail 주소 |
| `GMAIL_APP_PASSWORD` | 발송 시 필수 | Gmail 앱 비밀번호 (16자리) |
| `NEWSLETTER_TO` | 선택 | 기본 수신 이메일 주소 |
| `OUTPUT_DIR` | 선택 | 출력 경로 (기본: `output`) |
| `NEWSLETTER_LANG` | 선택 | 뉴스레터 언어 (기본: `ko`) |

> Gmail 앱 비밀번호는 Google 계정 → 보안 → 2단계 인증 → 앱 비밀번호에서 발급합니다.

### 3. 로컬 테스트

```bash
# mock 데이터로 이메일 생성 (발송 없음)
python src/main.py --test

# 생성 후 내 이메일로 발송
python src/main.py --test --send my@example.com
```

---

## GitHub Actions 자동화

### 스케줄

매주 **일요일 오전 8시 KST** (UTC 23:00)에 자동 실행됩니다.

```yaml
schedule:
  - cron: "0 23 * * 0"
```

### 수동 실행

GitHub 저장소 → Actions → **Claude Code Newsletter** → **Run workflow**

| 입력 | 설명 |
|------|------|
| `test_mode` | `true`로 설정 시 mock 데이터 사용 |
| `date` | 기준 날짜 지정 (기본: 실행 당일) |
| `recipient` | 수신 이메일 (비워두면 `NEWSLETTER_TO` Secret 사용) |

### GitHub Secrets 등록

저장소 Settings → Secrets and variables → Actions에서 아래 값을 등록합니다.

| Secret | 설명 |
|--------|------|
| `GMAIL_USER` | 발신 Gmail 주소 |
| `GMAIL_APP_PASSWORD` | Gmail 앱 비밀번호 |
| `NEWSLETTER_TO` | 수신 이메일 주소 |
| `ANTHROPIC_API_KEY` | (선택) Claude API 키 |

### 아티팩트

실행 후 생성된 파일(`email.html`, `email.txt`, `summary.json`)은 Actions 아티팩트로 30일간 보관됩니다.

---

## Claude Code 에이전트 구조

이 프로젝트는 Claude Code의 멀티 에이전트 기능을 활용해 파이프라인 각 단계를 전담 에이전트로 분리합니다.

| 에이전트 | 담당 | 사용 모델 |
|----------|------|-----------|
| `collector` | 콘텐츠 수집 | Haiku |
| `curator` | 필터링·분류 | Sonnet |
| `writer` | 본문 작성 | Sonnet |
| `formatter` | HTML/TXT 변환 | Haiku |

### 에이전트 간 조율

`plan.md`와 `progress.md`로 태스크 상태를 관리합니다. 새 세션을 시작하면 에이전트가 두 파일을 읽어 자신의 담당 태스크와 선행 조건을 파악합니다.

### Claude Code 스킬 (슬래시 커맨드)

| 커맨드 | 설명 |
|--------|------|
| `/generate-newsletter` | 전체 파이프라인 실행 |
| `/check-progress` | 현재 진행 상태 요약 출력 |
| `/preview [YYYY-MM-DD]` | 생성된 뉴스레터 미리보기 |
| `/save-research [topic]` | 조사 내용을 knowledge/에 저장 |
| `/search-knowledge [keyword]` | knowledge/ 디렉토리 키워드 검색 |

---

## 기술 스택

- **언어**: Python 3.11+
- **HTTP**: `httpx`
- **HTML 템플릿**: `jinja2`
- **이메일 발송**: `smtplib` (Gmail SMTP)
- **스케줄링**: GitHub Actions
- **AI 본문 생성**: Anthropic Claude API (선택)
