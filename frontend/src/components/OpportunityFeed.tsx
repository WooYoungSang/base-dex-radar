"use client";
import { useQuery } from "@tanstack/react-query";
import { api, type Opportunity } from "@/lib/api";

function OppCard({ opp }: { opp: Opportunity }) {
  const profitColor =
    opp.estimated_profit_pct > 0.5
      ? "text-success"
      : opp.estimated_profit_pct > 0.2
      ? "text-warning"
      : "text-muted";

  return (
    <div className="border border-border rounded-xl bg-surface-alt p-4 space-y-2">
      <div className="flex justify-between items-center">
        <span className="font-mono text-white font-semibold">
          {opp.token_a}/{opp.token_b}
        </span>
        <span className={`font-mono font-bold text-lg ${profitColor}`}>
          +{opp.estimated_profit_pct.toFixed(3)}%
        </span>
      </div>
      <div className="flex gap-4 text-sm">
        <div>
          <p className="text-xs text-muted">Buy on</p>
          <p className="text-success">{opp.buy_dex}</p>
          <p className="font-mono text-xs">${opp.buy_price.toLocaleString()}</p>
        </div>
        <div className="text-muted self-center">→</div>
        <div>
          <p className="text-xs text-muted">Sell on</p>
          <p className="text-danger">{opp.sell_dex}</p>
          <p className="font-mono text-xs">${opp.sell_price.toLocaleString()}</p>
        </div>
        <div className="ml-auto text-right">
          <p className="text-xs text-muted">Spread</p>
          <p className="font-mono text-xs">{opp.spread_pct.toFixed(3)}%</p>
        </div>
      </div>
    </div>
  );
}

export default function OpportunityFeed() {
  const { data, isLoading, dataUpdatedAt } = useQuery({
    queryKey: ["opportunities"],
    queryFn: api.opportunities,
    refetchInterval: 10_000,
  });

  const updatedAt = dataUpdatedAt ? new Date(dataUpdatedAt).toLocaleTimeString() : "-";

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="font-semibold text-white">Opportunity Feed</h2>
        <span className="text-xs text-muted">Updated: {updatedAt}</span>
      </div>
      {isLoading && <p className="text-muted text-sm">Scanning for opportunities…</p>}
      {data && data.length === 0 && (
        <div className="border border-border rounded-xl bg-surface p-6 text-center text-muted text-sm">
          No profitable opportunities detected — spreads too tight or fees exceed spread.
        </div>
      )}
      {data && data.map((opp, i) => <OppCard key={i} opp={opp} />)}
    </div>
  );
}
