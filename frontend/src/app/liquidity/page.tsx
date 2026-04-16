import LiquidityDepthChart from "@/components/LiquidityDepthChart";

export default function LiquidityPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Liquidity Depth</h1>
        <p className="text-muted text-sm mt-1">
          Bid/ask liquidity distribution across price levels for each DEX pool.
        </p>
      </div>
      <LiquidityDepthChart />
    </div>
  );
}
