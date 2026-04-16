"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function RouteVisualizer() {
  const [tokenA, setTokenA] = useState("ETH");
  const [tokenB, setTokenB] = useState("USDC");
  const [amount, setAmount] = useState("1.0");
  const [enabled, setEnabled] = useState(false);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["route", tokenA, tokenB, amount],
    queryFn: () => api.route(tokenA, tokenB, parseFloat(amount) || 1),
    enabled,
    retry: false,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setEnabled(true);
    refetch();
  };

  return (
    <div className="rounded-xl border border-border bg-surface p-4 space-y-4">
      <h2 className="font-semibold text-white">Swap Route Recommender</h2>
      <form onSubmit={handleSubmit} className="flex gap-2 flex-wrap items-end">
        <div className="flex flex-col gap-1">
          <label className="text-xs text-muted">From</label>
          <input
            className="bg-surface-alt border border-border rounded px-3 py-1.5 text-sm text-white w-24"
            value={tokenA}
            onChange={(e) => setTokenA(e.target.value.toUpperCase())}
          />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs text-muted">To</label>
          <input
            className="bg-surface-alt border border-border rounded px-3 py-1.5 text-sm text-white w-24"
            value={tokenB}
            onChange={(e) => setTokenB(e.target.value.toUpperCase())}
          />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs text-muted">Amount</label>
          <input
            type="number"
            min="0"
            step="any"
            className="bg-surface-alt border border-border rounded px-3 py-1.5 text-sm text-white w-28"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
        </div>
        <button
          type="submit"
          className="bg-accent hover:bg-accent-hover text-white px-4 py-1.5 rounded text-sm font-medium transition-colors"
        >
          Find Route
        </button>
      </form>

      {isLoading && <p className="text-muted text-sm">Searching routes…</p>}
      {isError && <p className="text-danger text-sm">No route found for {tokenA} → {tokenB}</p>}

      {data && (
        <div className="space-y-3">
          <div className="flex items-center gap-2 flex-wrap">
            {data.path.map((token, i) => (
              <span key={i} className="flex items-center gap-2">
                <span className="bg-surface-alt border border-border px-3 py-1 rounded-full text-sm font-mono">
                  {token}
                </span>
                {i < data.path.length - 1 && (
                  <span className="text-muted text-xs">{data.dexes[i]} →</span>
                )}
              </span>
            ))}
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <Stat label="Amount Out" value={data.amount_out.toFixed(4)} unit={tokenB} />
            <Stat label="Effective Price" value={data.effective_price.toFixed(4)} />
            <Stat label="Price Impact" value={`${(data.price_impact * 100).toFixed(3)}%`} />
            <Stat label="Gas Estimate" value={data.gas_estimate.toLocaleString()} unit="units" />
          </div>
        </div>
      )}
    </div>
  );
}

function Stat({ label, value, unit }: { label: string; value: string; unit?: string }) {
  return (
    <div className="bg-surface-alt rounded-lg p-3 border border-border">
      <p className="text-xs text-muted">{label}</p>
      <p className="font-mono text-white mt-1">{value} <span className="text-muted text-xs">{unit}</span></p>
    </div>
  );
}
