---
id: CLAUDE-DEX-Radar
note_type: harness
title: "CLAUDE.md — Base DEX Radar (KAIROS)"
agent_platform: claude-code
status: active
---

# CLAUDE.md — Base DEX Radar (KAIROS)

> **Micro-Bet 기반. Phase 전환마다 구조화된 리포트 필수.**
> Grant 제출 기한: 2026-04-17 | 목표: 5 ETH

## Project Context

- **Project ID**: `grant-base-dex-radar`
- **Size / Appetite**: Big (1-2d)
- **Tech Stack**: Go + CUDA (KAIROS PathFinder, RTX 4090), Triton Inference Server (LightGBM), Base RPC + DEX subgraph, Next.js + Tailwind + Recharts, FastAPI, Vercel + GPU 서버
- **Language**: Go + Python + TypeScript
- **Grant Amount**: 5 ETH

## KAIROS 경로
- **Local**: `/home/jang/Workspace/wavis-kairos`
- **PathFinder module**: `wavis-kairos/cmd/` (public 분리 대상)
- **no_touch**: `cuda-engine/private/`, `.env`, `*.key`, `node_modules/`

---

## Build / Test / Lint

```bash
# Build
cd backend && pip install -r requirements.txt && cd ../cuda-engine && make build && cd ../frontend && npm run build

# Test
cd backend && pytest && cd ../cuda-engine && make test && cd ../frontend && npm test

# Lint
cd backend && ruff check . && cd ../frontend && eslint .
```

---

## Features (MVP)

- F1. 실시간 DEX 가격 비교 대시보드 (Uniswap V3, Aerodrome, BaseSwap, SushiSwap)
- F2. 최적 경로 추천 엔진 (CUDA PathFinder + 슬리피지+가스비 실질 비용)
- F3. 유동성 깊이 맵
- F4. Gas 효율 분석
- F5. 기회 피드 (Opportunity Feed)
- F6. Public API + Swagger

## Phase Protocol

### Phase 0: Shape (Preflight)
- 코드베이스 스캔 + no_touch 확인
- Scope 분해 (S1-Data, S2-API, S3-UI) + KAIROS PathFinder 분리 가능 여부 확인
- `📋 SHAPE REPORT` 생성

### Phase 1: Build
- S1 → S2 → S3 순서 구현
- 각 Scope 완료 시 `📋 BUILD REPORT` 생성

### Phase 2: Integrate & Test
- E2E + Acceptance 검증
- `📋 INTEGRATION REPORT` 생성

### Phase 3: Ship
- Vercel 배포 + 라이브 URL
- `📋 SHIP REPORT` 생성

### Phase 4: Reflect
- `📋 REFLECT REPORT` 생성

## Acceptance Criteria
- [ ] 실시간 DEX 가격 비교 대시보드 동작
- [ ] CUDA 최적 경로 추천 정확도 검증 (vs 기존 aggregator)
- [ ] 유동성 깊이 맵 시각화 정상 동작
- [ ] Opportunity Feed 실시간 업데이트 확인
- [ ] Public API 정상 응답 + Swagger 문서
- [ ] Vercel 배포 + 라이브 URL 확인

## Kill Condition
Day 3까지 PathFinder 모듈 분리가 완료되지 않으면 → 캐시된 가격 데이터 기반 비교 전용으로 스코프 축소

## No-Gos
- KAIROS private execution/차익거래 로직 노출
- 직접 스왑 실행 기능
- API 키 없는 무제한 접근

## Report Format

```markdown
📋 [PHASE] REPORT — Base DEX Radar (KAIROS)
Phase: [0-4]
Scope: [S1-Data | S2-API | S3-UI | ALL]
---
### Done
### Blockers
### Next
### Grant Readiness
- [ ] 라이브 URL
- [ ] GitHub repo (WooYoungSang/base-dex-radar)
- [ ] 임팩트 메트릭
```
