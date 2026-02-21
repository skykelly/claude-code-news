---
name: save-research
description: 조사한 내용을 knowledge/ 디렉토리에 마크다운 파일로 저장한다. 새로운 주제를 조사했을 때 사용한다.
argument-hint: "[topic-filename] [조사 내용 설명]"
disable-model-invocation: true
allowed-tools: Read, Write, WebSearch, WebFetch
---

# 조사 내용 저장

`$ARGUMENTS`에서 첫 번째 단어를 파일명으로, 나머지를 주제 설명으로 사용한다.

## 실행 절차

1. `knowledge/index.md`를 읽어 기존 파일 목록을 확인한다.
2. 동일 주제 파일이 있으면 내용을 추가(append)하고, 없으면 새 파일을 생성한다.
3. 새 파일 형식:

```markdown
# [주제 제목]

조사일: YYYY-MM-DD
소스: [출처 목록]

---

[조사 내용]

---

## 참고 소스

- [URL 목록]
```

4. `knowledge/index.md`의 파일 목록 테이블을 업데이트한다.
5. 저장 완료 후 파일 경로를 출력한다.

## 파일명 규칙

- 소문자, 하이픈 구분 (예: `claude-code-tips`, `reddit-api-guide`)
- 저장 경로: `knowledge/<filename>.md`
