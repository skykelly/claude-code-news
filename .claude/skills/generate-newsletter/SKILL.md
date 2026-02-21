---
name: generate-newsletter
description: 뉴스레터 생성 파이프라인 전체 또는 특정 단계를 실행한다.
argument-hint: "[--step collect|filter|generate|format] [--date YYYY-MM-DD]"
disable-model-invocation: true
context: fork
agent: general-purpose
---

# 뉴스레터 생성 파이프라인

`plan.md`와 `progress.md`를 읽어 현재 상태를 파악하고, 미완료 태스크를 순서대로 실행한다.

## 인수 처리

`$ARGUMENTS`를 파싱해 아래 옵션을 처리한다:

- `--step collect` : 1단계(수집)만 실행
- `--step filter`  : 2단계(필터링)만 실행
- `--step generate`: 3단계(본문 생성)만 실행
- `--step format`  : 4단계(포맷 변환)만 실행
- `--date YYYY-MM-DD`: 특정 날짜 기준으로 실행 (기본값: 오늘)
- 인수 없음: 전체 파이프라인 실행

## 실행 절차

1. `plan.md`를 읽어 전체 태스크 구조를 파악한다.
2. `progress.md`를 읽어 완료된 태스크와 블로커를 확인한다.
3. 실행할 단계를 결정한다.
4. 각 단계를 순서대로 실행한다:
   - **collect**: `collector` 에이전트에 위임
   - **filter**: `curator` 에이전트에 위임 (collect 완료 후)
   - **generate**: `writer` 에이전트에 위임 (filter 완료 후)
   - **format**: `formatter` 에이전트에 위임 (generate 완료 후)
5. 각 단계 완료 시 `progress.md`가 업데이트됐는지 확인한다.
6. 최종 완료 후 `output/YYYY-MM-DD/` 디렉토리의 파일 목록을 출력한다.

## 완료 조건

`output/YYYY-MM-DD/` 에 다음 3개 파일이 존재해야 성공으로 간주한다:
- `email.html`
- `email.txt`
- `summary.json`
