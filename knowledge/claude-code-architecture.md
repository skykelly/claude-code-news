# Claude Code 에이전트/스킬/커맨드 구조

조사일: 2026-02-21
소스: code.claude.com/docs (agent-teams, sub-agents, slash-commands)

---

## 1. Subagents (서브에이전트)

독립된 컨텍스트 창에서 실행되는 특화 AI 어시스턴트.

### 정의 위치

| 범위 | 경로 |
|------|------|
| 프로젝트 전용 | `.claude/agents/<name>.md` |
| 개인 전역 | `~/.claude/agents/<name>.md` |
| 세션 한정 | `claude --agents '{...}'` CLI 플래그 |

### 주요 frontmatter 필드

```yaml
name: agent-name           # 필수
description: ...           # 필수 - Claude가 언제 위임할지 판단에 사용
tools: Read, Write, Bash   # 허용 도구 목록
model: haiku|sonnet|opus   # 사용 모델 (기본: inherit)
memory: project|user|local # 세션 간 메모리 유지
permissionMode: default|bypassPermissions|plan
maxTurns: 10               # 최대 턴 수
skills: [skill-name]       # 사전 로드할 스킬
```

### 내장 에이전트

- **Explore**: read-only, Haiku 모델, 코드베이스 탐색 특화
- **Plan**: read-only, 플랜 모드 리서치용
- **general-purpose**: 모든 도구, 복잡한 작업

---

## 2. Agent Teams (실험적)

여러 Claude Code 인스턴스가 공유 태스크 리스트로 협업.

```json
// settings.json에 활성화
{ "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }
```

### Subagents vs Agent Teams

| 항목 | Subagents | Agent Teams |
|------|-----------|-------------|
| 컨텍스트 | 독립적, 결과만 반환 | 독립적, 직접 통신 가능 |
| 통신 | 메인 에이전트에만 보고 | 팀원끼리 직접 메시지 |
| 태스크 관리 | 메인이 전부 관리 | 공유 태스크 리스트 |
| 비용 | 낮음 | 높음 (각자 컨텍스트) |
| 적합한 용도 | 결과만 필요한 독립 작업 | 토론·협업 필요한 복잡한 작업 |

---

## 3. Skills (슬래시 커맨드)

재사용 가능한 프롬프트 워크플로우.

### 정의 위치

| 범위 | 경로 |
|------|------|
| 프로젝트 전용 | `.claude/skills/<name>/SKILL.md` |
| 개인 전역 | `~/.claude/skills/<name>/SKILL.md` |
| 레거시 호환 | `.claude/commands/<name>.md` |

### 주요 frontmatter 필드

```yaml
name: skill-name
description: ...                    # Claude 자동 로드 판단 기준
argument-hint: "[arg1] [arg2]"      # 자동완성 힌트
disable-model-invocation: true      # 사용자만 호출 가능 (Claude 자동 호출 차단)
user-invocable: false               # Claude만 사용 (메뉴에서 숨김)
allowed-tools: Read, Grep           # 이 스킬 활성 시 허용 도구
context: fork                       # 별도 서브에이전트에서 실행
agent: Explore|Plan|general-purpose # context:fork 시 사용할 에이전트
model: haiku|sonnet|opus            # 스킬 실행 모델
```

### 변수 치환

| 변수 | 설명 |
|------|------|
| `$ARGUMENTS` | 전달된 전체 인수 |
| `$ARGUMENTS[N]` | N번째 인수 (0-index) |
| `$N` | `$ARGUMENTS[N]` 단축형 |
| `${CLAUDE_SESSION_ID}` | 현재 세션 ID |
| `` !`command` `` | 쉘 명령 실행 후 출력 삽입 |

---

## 4. Hooks

특정 이벤트 발생 시 자동 실행되는 쉘 명령.

```json
// settings.json
{
  "hooks": {
    "PreToolUse":   [{ "matcher": "Bash", "hooks": [{ "type": "command", "command": "..." }] }],
    "PostToolUse":  [{ "matcher": "Write|Edit", "hooks": [...] }],
    "Stop":         [{ "hooks": [...] }],
    "SubagentStop": [{ "matcher": "agent-name", "hooks": [...] }]
  }
}
```

### 이벤트 목록

| 이벤트 | 발생 시점 |
|--------|----------|
| `PreToolUse` | 도구 실행 전 (exit 2로 차단 가능) |
| `PostToolUse` | 도구 실행 후 |
| `Stop` | 에이전트 종료 시 |
| `SubagentStart/Stop` | 서브에이전트 시작/종료 시 |
| `TeammateIdle` | 팀원 유휴 상태 시 |
| `TaskCompleted` | 팀 태스크 완료 시 |

---

## 참고 소스

- https://code.claude.com/docs/en/agent-teams
- https://code.claude.com/docs/en/sub-agents
- https://code.claude.com/docs/en/slash-commands
- https://github.com/hesreallyhim/awesome-claude-code
