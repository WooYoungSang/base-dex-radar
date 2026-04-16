import Link from "next/link";

const links = [
  { href: "/", label: "Prices" },
  { href: "/route", label: "Route" },
  { href: "/liquidity", label: "Liquidity" },
  { href: "/opportunities", label: "Opportunities" },
];

export default function Nav() {
  return (
    <nav className="border-b border-border bg-surface px-4 py-3">
      <div className="max-w-7xl mx-auto flex items-center gap-6">
        <span className="font-bold text-accent text-lg tracking-tight">⚡ DEX Radar</span>
        {links.map((l) => (
          <Link key={l.href} href={l.href} className="text-sm text-muted hover:text-white transition-colors">
            {l.label}
          </Link>
        ))}
        <span className="ml-auto text-xs text-muted">Powered by KAIROS CUDA PathFinder</span>
      </div>
    </nav>
  );
}
