"use client";
import { useQuery } from "@tanstack/react-query";
import { api, type PriceQuote } from "@/lib/api";

const PAIRS = [
  { a: "ETH", b: "USDC" },
  { a: "ETH", b: "USDT" },
  { a: "USDC", b: "USDT" },
];

function QuoteRow({ quote }: { quote: PriceQuote }) {
  return (
    <tr className="border-b border-border hover:bg-surface-alt transition-colors">
      <td className="py-2 px-3 text-accent">{quote.dex}</td>
      <td className="py-2 px-3">{quote.token_a}/{quote.token_b}</td>
      <td className="py-2 px-3 text-right font-mono">{quote.price.toLocaleString(undefined, { minimumFractionDigits: 4 })}</td>
      <td className="py-2 px-3 text-right text-muted">{(quote.fee * 100).toFixed(2)}%</td>
      <td className="py-2 px-3 text-right text-muted">${(quote.liquidity / 1_000_000).toFixed(2)}M</td>
    </tr>
  );
}

function PairSection({ tokenA, tokenB }: { tokenA: string; tokenB: string }) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["prices", tokenA, tokenB],
    queryFn: () => api.prices(tokenA, tokenB),
    refetchInterval: 10_000,
  });

  if (isLoading) return <tr><td colSpan={5} className="py-2 px-3 text-muted">Loading {tokenA}/{tokenB}…</td></tr>;
  if (isError || !data) return null;

  return (
    <>
      <tr className="bg-surface-alt">
        <td colSpan={5} className="py-1 px-3 text-xs text-muted uppercase tracking-wider">{data.pair}</td>
      </tr>
      {data.quotes.map((q) => <QuoteRow key={q.pool_address} quote={q} />)}
    </>
  );
}

export default function PriceTable() {
  return (
    <div className="rounded-xl border border-border bg-surface overflow-hidden">
      <div className="px-4 py-3 border-b border-border flex items-center justify-between">
        <h2 className="font-semibold text-white">DEX Price Comparison</h2>
        <span className="text-xs text-muted">Auto-refresh every 10s</span>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-muted text-xs uppercase border-b border-border">
            <th className="py-2 px-3 text-left">DEX</th>
            <th className="py-2 px-3 text-left">Pair</th>
            <th className="py-2 px-3 text-right">Price</th>
            <th className="py-2 px-3 text-right">Fee</th>
            <th className="py-2 px-3 text-right">Liquidity</th>
          </tr>
        </thead>
        <tbody>
          {PAIRS.map((p) => <PairSection key={`${p.a}-${p.b}`} tokenA={p.a} tokenB={p.b} />)}
        </tbody>
      </table>
    </div>
  );
}
