const BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

export interface PriceQuote {
  token_a: string;
  token_b: string;
  dex: string;
  price: number;
  pool_address: string;
  liquidity: number;
  fee: number;
  timestamp: number;
}

export interface PricesResponse {
  pair: string;
  quotes: PriceQuote[];
}

export interface RouteResponse {
  token_in: string;
  token_out: string;
  amount_in: number;
  amount_out: number;
  path: string[];
  pools: string[];
  dexes: string[];
  gas_estimate: number;
  price_impact: number;
  effective_price: number;
}

export interface LiquidityLevel {
  price: number;
  liquidity: number;
}

export interface LiquidityResponse {
  pool_address: string;
  dex: string;
  token_a: string;
  token_b: string;
  current_price: number;
  bids: LiquidityLevel[];
  asks: LiquidityLevel[];
}

export interface GasResponse {
  base_fee_gwei: number;
  priority_fee_gwei: number;
  estimated_swap_usd: number;
  source: string;
}

export interface Opportunity {
  token_a: string;
  token_b: string;
  buy_dex: string;
  sell_dex: string;
  buy_price: number;
  sell_price: number;
  spread_pct: number;
  estimated_profit_pct: number;
  buy_pool: string;
  sell_pool: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  pools_loaded: number;
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

export const api = {
  prices: (tokenA: string, tokenB: string) =>
    get<PricesResponse>(`/api/prices?token_a=${tokenA}&token_b=${tokenB}`),

  route: (tokenA: string, tokenB: string, amount: number) =>
    get<RouteResponse>(`/api/route?token_a=${tokenA}&token_b=${tokenB}&amount=${amount}`),

  liquidity: (poolAddress: string) =>
    get<LiquidityResponse>(`/api/liquidity/${poolAddress}`),

  gas: () => get<GasResponse>("/api/gas"),

  opportunities: () => get<Opportunity[]>("/api/opportunities"),

  health: () => get<HealthResponse>("/api/health"),
};
