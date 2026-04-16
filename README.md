# Base DEX Radar — AI-powered DEX Intelligence Platform

> **Grant submission — Base Ecosystem Fund**
> Powered by KAIROS CUDA PathFinder | RTX 4090 GPU acceleration

## Problem

DeFi traders on Base face fragmented liquidity across Uniswap V3, Aerodrome, BaseSwap, and SushiSwap. Finding the best swap price, optimal route, and detecting arbitrage opportunities requires manual monitoring across multiple interfaces — a slow, error-prone process that leaves value on the table.

## Solution

Base DEX Radar is a real-time intelligence platform that:
- Aggregates prices across all major Base DEXes in a single dashboard
- Computes optimal multi-hop swap routes using GPU-accelerated pathfinding (KAIROS CUDA PathFinder)
- Visualizes liquidity depth at each price level
- Surfaces price inefficiencies as they emerge — before they disappear

## Features

| # | Feature | Description |
|---|---------|-------------|
| F1 | **Real-time Price Dashboard** | Live price comparison across Uniswap V3, Aerodrome, BaseSwap, SushiSwap — auto-refresh every 10s |
| F2 | **CUDA Path Finder** | Multi-hop swap route optimization with slippage + gas cost modeling, powered by KAIROS RTX 4090 |
| F3 | **Liquidity Depth Map** | Bid/ask depth visualization at ±5% price range for every pool |
| F4 | **Gas Efficiency Analysis** | Real-time Base L2 gas estimates for swap cost planning |
| F5 | **Opportunity Feed** | Detects price spreads >0.1% net of fees across all DEX pairs |
| F6 | **Public REST API + Swagger** | Fully documented API at `/docs` for builders and integrators |

## Quick Start

```bash
# Clone and launch
git clone https://github.com/WooYoungSang/base-dex-radar
cd base-dex-radar
docker-compose up
```

- Frontend: http://localhost:3000
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/prices?token_a=ETH&token_b=USDC` | Price quotes across all DEXes |
| GET | `/api/route?token_a=ETH&token_b=USDC&amount=1.0` | Optimal swap route |
| GET | `/api/liquidity/{pool_address}` | Liquidity depth for a pool |
| GET | `/api/gas` | Current Base L2 gas estimates |
| GET | `/api/opportunities` | Active price inefficiencies |
| GET | `/api/health` | Service health + pool count |

Full API docs: http://localhost:8000/docs

## Architecture

```
Frontend (Next.js 14 + Tailwind + Recharts)
    ↓ /api/* proxy
Backend (FastAPI + Python)
    ↓ httpx async RPC calls
Base RPC (https://mainnet.base.org)
    + KAIROS CUDA PathFinder (RTX 4090 GPU subprocess)
```

## Grant Submission

> This project is submitted to the Base Ecosystem Fund as a public-good DeFi intelligence tool.
> 
> - **Target**: 5 ETH
> - **Impact metrics**: Real-time aggregation of 4+ DEXes, sub-10s refresh, GPU-accelerated path finding
> - **Open source**: MIT licensed
> - **Powered by KAIROS CUDA PathFinder**: RTX 4090 acceleration for multi-hop route optimization

## Tech Stack

- **Backend**: Python 3.11, FastAPI, web3.py, httpx, Pydantic v2
- **Frontend**: Next.js 14 App Router, TypeScript, Tailwind CSS, TanStack Query, Recharts
- **Infrastructure**: Docker Compose, Vercel (frontend), Base L2 RPC

## License

MIT
