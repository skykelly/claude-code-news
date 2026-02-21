# 작업 계획

> 이 파일은 전체 태스크 목록과 에이전트별 담당 범위를 정의한다.
> 설계 변경 시 이 파일을 먼저 업데이트하고 progress.md에 변경 이유를 기록한다.

---

## Agent A - 콘텐츠 수집

| 태스크 | 설명 | 파일 | 의존 |
|--------|------|------|------|
| TASK-01 | Reddit 수집 모듈 구현 | `src/collect_reddit.py` | - |
| TASK-02 | GitHub 수집 모듈 구현 | `src/collect_github.py` | - |
| TASK-03 | Hacker News 수집 모듈 구현 | `src/collect_hn.py` | - |

---

## Agent B - 필터링 & 생성

| 태스크 | 설명 | 파일 | 의존 |
|--------|------|------|------|
| TASK-04 | 필터링 및 카테고리 분류 로직 구현 | `src/filter.py` | TASK-01~03 |
| TASK-05 | Claude API 연동 및 이메일 본문 생성 | `src/generate.py` | TASK-04 |

---

## Agent C - 포맷 & 인프라

| 태스크 | 설명 | 파일 | 의존 |
|--------|------|------|------|
| TASK-06 | Jinja2 HTML 이메일 템플릿 작성 | `templates/email.html.j2` | - |
| TASK-07 | HTML/텍스트 포맷 변환 모듈 구현 | `src/format.py` | TASK-05, TASK-06 |
| TASK-08 | GitHub Actions 워크플로우 작성 | `.github/workflows/newsletter.yml` | - |
| TASK-09 | 전체 파이프라인 진입점 구현 | `src/main.py` | TASK-07 |

---

## 공통 태스크 (어느 에이전트든 처리 가능)

| 태스크 | 설명 | 파일 | 의존 |
|--------|------|------|------|
| TASK-00 | 프로젝트 초기 셋업 | `requirements.txt`, `.env.example` | - |
