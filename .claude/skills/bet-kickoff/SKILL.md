---
name: bet-kickoff
description: "Base DEX Radar (KAIROS) Bet 시작 시 Preflight + Shape 자동화"
allowed-tools: Read, Grep, Glob, Bash
---

## Process
1. 코드베이스 구조 스캔 (Go + Python + TypeScript)
2. KAIROS PathFinder 분리 가능 여부 확인: `ls /home/jang/Workspace/wavis-kairos/cmd/`
3. build baseline: `cd backend && pip install -r requirements.txt && cd ../cuda-engine && make build && cd ../frontend && npm run build`
4. no_touch 확인: `node_modules/`, `.env`, `*.key`, `cuda-engine/private/`
5. Scope 분해 (S1-Data, S2-API, S3-UI)
6. 📋 PREFLIGHT REPORT + SHAPE REPORT 생성
