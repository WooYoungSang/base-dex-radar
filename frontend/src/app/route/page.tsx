import RouteVisualizer from "@/components/RouteVisualizer";

export default function RoutePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Swap Route Recommender</h1>
        <p className="text-muted text-sm mt-1">
          Find the optimal multi-hop swap path powered by KAIROS CUDA PathFinder.
        </p>
      </div>
      <RouteVisualizer />
    </div>
  );
}
