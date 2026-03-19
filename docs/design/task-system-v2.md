# MPM 태스크 시스템 v2 — 설계 문서

이 문서는 2603191300 세션에서 논의된 전체 설계를 정리한 것이다.

---

## 1. 배포 방식

### 결정: Standalone 패키지

MPM의 주 가치는 "대시보드로 여러 프로젝트를 모니터링하는 것"이므로 standalone 패키지가 메인.

- `mpm` CLI로 설치/실행 (npm or pip)
- `mpm init` → workspace 초기화
- `mpm add ./project` → 프로젝트 등록 + `.mpm/`, `.claude/` 구조 생성
- `mpm start` → 대시보드 서버 실행

### Claude Code 연동

`mpm add` 실행 시 프로젝트 디렉토리에 `.claude/` 파일들을 자동 주입:
- `.claude/rules/mpm-workflow.md` — 태스크 시스템 규칙
- `.claude/settings.json` — hooks (Stop, SessionStart 등)
- `.claude/skills/mpm-next/SKILL.md` — `/mpm-next` 커맨드

기존 `.claude/settings.json`이 있으면 **merge** (hooks 배열에 append). `__mpm__` 태그로 MPM hook을 식별하여 `mpm remove` 시 정리 가능.

---

## 2. 문서 구조

```
.mpm/
├── docs/
│   └── PROJECT.md              # 프로젝트 정체성 + 로드맵 (유일한 기본 파일)
│                                # 구조 강제 없음 — 유저 자율
│                                # 사용자가 원하는 .md 파일 추가 가능
└── data/
    ├── future.json             # [{task}, ...] — 앞이 높은 우선순위
    ├── current/                # 세션별 진행 중 태스크
    │   └── {session_id}.json   # 한 세션에 하나의 태스크
    └── past/
        └── YYMMDD.json         # 완료/보류/폐기된 태스크 (당일 기준)
```

### PROJECT.md
- 프로젝트의 목적, 정체성, 큰 틀의 로드맵
- 세부 구조 강제 없음 (phase 단위든 자유 형식이든 사용자 재량)
- 첫 세션 시작 시 비어있으면 Claude가 프로젝트 분석 후 질문하여 자동 작성

### 문서 탭 (UI)
- `.mpm/docs/` 안의 파일뿐 아니라 프로젝트 경로 내 모든 `.md` 파일을 수집
- 대시보드에서 열람/편집 가능

---

## 3. 통합 태스크 스키마

future, current, past 모든 위치에서 같은 스키마를 사용. 시간이 지나며 어트리뷰트가 채워진다.

```json
{
  "id": "abc123",
  "title": "OAuth 연동",
  "prompt": "Google OAuth를 연동해줘. 기존 인증 시스템과 병행 운영 가능하도록.",
  "goal": null,
  "approach": null,
  "verification": null,
  "result": null,
  "memo": null,
  "status": "queued",
  "created": "2603191200",
  "session_id": null,
  "parent_id": null
}
```

### 필드 설명

| 필드 | 작성 시점 | 설명 |
|------|----------|------|
| `id` | future 생성 시 | 고유 ID |
| `title` | future 생성 시 | 태스크 한줄 요약 |
| `prompt` | future 생성 시 | 구체적인 작업 지시 |
| `goal` | current 진입 시 | Claude가 prompt를 분석하여 정리한 목표 |
| `approach` | current 진입 시 | 접근 방법 |
| `verification` | current 진입 시 | 완료 검증 기준 |
| `result` | 작업 완료 시 | 실제 결과 |
| `memo` | 작업 완료 시 | 메모/비고 |
| `status` | 전이 시 변경 | `queued` → `active` → `success`/`postpone`/`modified`/`discard` |
| `created` | future 생성 시 | 생성 시각 (YYMMDDHHmm) |
| `session_id` | current 진입 시 | 작업 중인 Claude Code 세션 ID |
| `parent_id` | 재생성 시 | postpone/modified에서 새 카드 생성 시 원본 ID |

---

## 4. 태스크 라이프사이클

### 기본 흐름

```
future.json (queued)
│  title, prompt 존재. 나머지 null.
│
│  pick up (유저 지시 또는 /mpm-next)
▼
current/{session_id}.json (active)
│  Claude가 goal, approach, verification 채움.
│  작업 수행.
│
│  작업 완료 → Claude가 result 채움 → 멈춤 시도
▼
Stop hook 발동
│  [1] prompt: 셀프리뷰 (verification 대조, 진짜 끝인지 확인)
│      → 아직 할 일 있으면 block → Claude 계속 작업
│      → 진짜 끝이면 통과
│  [2] http: 대시보드에 "답변 완료" 신호
│
▼
Claude: "verification 결과: ... 다음 작업으로 넘어갈까요?"
│
│  유저 응답으로 분기:
├─ "ㅇㅇ" / "넘어가" → success → past/YYMMDD.json
├─ "좀 더 손봐" → current 유지, 계속 작업
├─ "나중에 하자" → postpone → past로 + 새 카드 future에
├─ "이거 안 해" → discard → past로
```

### postpone / modified 처리

기존 카드는 **그대로 past로 이동** (기록 보존). 새 카드를 생성하여 future에 추가.

```
예시: postpone

기존 카드 (past/260319.json에 추가):
  status: "postpone"
  result: "API 키 발급 대기중"
  memo: "키 받으면 재시도"

새 카드 (future.json에 추가):
  id: "abc124"
  title: "OAuth 연동 재시도"
  prompt: "OAuth 연동 재시도. API 키 발급 완료 후 진행. 이전 시도에서 goal: ..., approach: ... 까지 정리됨"
  parent_id: "abc123"
```

### 결과 판단 주체

**항상 유저 확인.** Claude는 verification을 수행하고 결과를 보여주지만, status 도장은 유저가 찍는다. 다만 유저는 "success"라고 타이핑하는 게 아니라 자연어로 응답하면 Claude가 매핑한다.

---

## 5. 강제 방식 — 3단 조합

### Rules (상시 컨텍스트 — 가이던스)

위치: `.claude/rules/mpm-workflow.md`

역할:
- `.mpm/` 구조가 뭔지 설명
- 태스크 라이프사이클 규칙
- 각 필드를 언제 채우는지
- PROJECT.md 참고 지시

강제력: 가이던스 (Claude가 참고하지만 까먹을 수 있음)

### Skills (실행 수단 — 확률적)

위치: `.claude/skills/mpm-next/SKILL.md`

역할:
- `/mpm-next` — future에서 pop, current에 생성, 작업 시작
- `/mpm-init-project` — PROJECT.md 자동 작성 (프로젝트 분석 + 유저 인터뷰)

강제력: 유저/Claude가 호출해야 동작

### Hooks (안전망 + 알림 — 결정론적)

위치: `.claude/settings.json`의 `hooks` 키

#### SessionStart hook
- `current/{session_id}.json` 존재 확인 → orphan 태스크 경고
- `PROJECT.md`가 비어있으면 `/mpm-init-project` 트리거

#### Stop hook (순서대로 실행)
1. **prompt 타입**: 셀프리뷰
   - current 태스크의 goal/verification 대조
   - 아직 할 일 남았으면 block → Claude 계속 작업
   - 진짜 끝났거나 유저 입력 필요하면 통과
2. **http 타입**: 대시보드 알림
   - prompt hook 통과 시에만 실행 (block되면 실행 안 됨)
   - `http://localhost:5000/api/hook/stop` 호출
   - 대시보드가 WebSocket으로 UI에 "답변 완료" 전달

#### 에이전트 상태 표시 (hook → HTTP → WebSocket)
```
SessionStart       → 🟢 활성
UserPromptSubmit   → ⏳ 작업중
Stop (통과)        → 💬 응답 완료
SessionEnd         → ⚫ 꺼짐
```

---

## 6. 유저 사용 플로우

### 최초 설치

```bash
npm install -g @mpm/mpm
cd ~/MyWorkspace
mpm init
mpm add ./my-project
```

`mpm add`가 하는 일:
1. `.mpm/docs/PROJECT.md` (빈 템플릿) 생성
2. `.mpm/data/future.json`, `current/`, `past/` 생성
3. `.claude/rules/mpm-workflow.md` 주입
4. `.claude/settings.json`에 hooks merge
5. `.claude/skills/mpm-next/SKILL.md` 주입

### 일상 사용 — 태스크 등록

대시보드 UI에서 직접 추가하거나, Claude Code에서 자연어로 등록.

### 일상 사용 — 태스크 실행

1. Claude Code 세션 시작
2. SessionStart hook → orphan 태스크 확인
3. 유저: "다음 할 거 해" 또는 `/mpm-next`
4. Claude: future에서 pop → current 생성 → goal/approach/verification 채움 → 작업
5. 작업 완료 → result 채움 → Stop hook (셀프리뷰 → 대시보드 알림)
6. Claude: "결과: ... 다음 작업으로 넘어갈까요?"
7. 유저 응답에 따라 분기

### 모니터링 (대시보드)

- 프로젝트별 현재 태스크 카드 (goal, approach, 상태)
- future 큐 (대기 중인 태스크 목록)
- 터미널 뷰 (Claude 실시간 출력)
- 에이전트 상태 인디케이터
- 문서 탭 (프로젝트 내 모든 .md 열람/편집)

### 중단 시나리오

- "나중에 하자" → postpone → past + 새 카드 future
- 세션 종료 → SessionEnd hook → 미완 태스크 기록 잔존
- 다음 SessionStart → "이전 세션에서 미완 태스크 있습니다" 경고

---

## 7. settings.json 충돌 방지

기존 `.claude/settings.json`이 있을 경우 덮어쓰지 않고 merge.

- hooks는 이벤트별 배열이므로 기존 hook 뒤에 append
- MPM hook은 `__mpm__` 태그로 식별
- `mpm remove` 시 `__mpm__` 태그가 있는 hook만 제거

---

## 8. 결정 사항 요약

| 항목 | 결정 |
|------|------|
| 배포 형태 | standalone 패키지 (메인) |
| AI Agent | Claude Code 전용 |
| 태스크 스키마 | 통합 (future/current/past 동일) |
| future 우선순위 | 앞이 높음 (pop from front, append to back) |
| current 구조 | `current/{session_id}.json` (복수 세션 지원) |
| past 기준 | 날짜가 아니라 결과 확정 시 즉시 이동 |
| postpone 처리 | past에 기록 보존 + future에 새 카드 생성 |
| 결과 판단 | 항상 유저 확인 (Claude는 제안만) |
| 유저 확인 방식 | 자연어 ("ㅇㅇ 다음" 등), Claude가 status 매핑 |
| 강제 방식 | Rules(인지) + Skills(실행) + Hooks(안전망+알림) |
| Stop hook | prompt(셀프리뷰) → http(대시보드 알림) 순서 |
| 에이전트 상태 | hook → HTTP → WebSocket 파이프라인 |
| settings 충돌 | merge + __mpm__ 태그 식별 |
