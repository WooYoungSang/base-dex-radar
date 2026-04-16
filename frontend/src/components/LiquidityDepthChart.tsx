"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import {
  ComposedChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const KNOWN_POOLS = [
  { address: "0x4C36388bE6F416A29C8d8Eee81C771cE6bE14B5", label: "ETH/USDC (Uniswap V3)" },
  { address: "0x420DD381b31aEf6683db6B902084cB0FFECe40D", label: "ETH/USDC (Aerodrome)" },
];

interface ChartData {
  price: string;
  bid: number;
  ask: number;
}

function PoolChart({ address, label }: { address: string; label: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ["liquidity", address],
    queryFn: () => api.liquidity(address),
    refetchInterval: 30_000,
  });

  if (isLoading) return <p className="text-muted text-sm">Loading {label}…</p>;
  if (!data) return null;

  const chartData: ChartData[] = [
    ...data.bids.slice().reverse().map((b) => ({
      price: b.price.toFixed(2),
      bid: b.liquidity,
      ask: 0,
    })),
    ...data.asks.map((a) => ({
      price: a.price.toFixed(2),
      bid: 0,
      ask: a.liquidity,
    })),
  ];

  return (
    <div className="rounded-xl border border-border bg-surface p-4">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-sm font-semibold text-white">{label}</h3>
        <span className="text-xs text-muted">Price: ${data.current_price.toLocaleString()}</span>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <ComposedChart data={chartData} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
          <XAxis dataKey="price" tick={{ fontSize: 10, fill: "#6b7280" }} interval={2} />
          <YAxis tick={{ fontSize: 10, fill: "#6b7280" }} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
          <Tooltip
            contentStyle={{ backgroundColor: "#111118", border: "1px solid #2a2a3a", borderRadius: 8 }}
            labelStyle={{ color: "#e5e7eb" }}
            formatter={(v: number) => [`$${(v / 1000).toFixed(1)}k`, ""]}
          />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Bar dataKey="bid" name="Bids" fill="#22c55e" opacity={0.8} />
          <Bar dataKey="ask" name="Asks" fill="#ef4444" opacity={0.8} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function LiquidityDepthChart() {
  return (
    <div className="space-y-4">
      <h2 className="font-semibold text-white">Liquidity Depth</h2>
      {KNOWN_POOLS.map((p) => (
        <PoolChart key={p.address} address={p.address} label={p.label} />
      ))}
    </div>
  );
}
