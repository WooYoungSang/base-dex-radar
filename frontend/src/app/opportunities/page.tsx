import OpportunityFeed from "@/components/OpportunityFeed";

export default function OpportunitiesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Opportunity Feed</h1>
        <p className="text-muted text-sm mt-1">
          Price inefficiencies detected across DEXes — spread {">"} 0.1%, net of fees.
        </p>
      </div>
      <OpportunityFeed />
    </div>
  );
}
