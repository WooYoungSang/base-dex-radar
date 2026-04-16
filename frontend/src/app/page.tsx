import PriceTable from "@/components/PriceTable";

export default function HomePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">DEX Price Dashboard</h1>
        <p className="text-muted text-sm mt-1">
          Real-time price comparison across Uniswap V3, Aerodrome, BaseSwap, and SushiSwap on Base.
        </p>
      </div>
      <PriceTable />
    </div>
  );
}
