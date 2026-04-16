import type { Metadata } from "next";
import "./globals.css";
import Providers from "./providers";
import Nav from "@/components/Nav";

export const metadata: Metadata = {
  title: "Base DEX Radar — AI-powered DEX Intelligence",
  description: "Real-time DEX price comparison, optimal routing, and opportunity detection on Base",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background text-gray-100">
        <Providers>
          <Nav />
          <main className="max-w-7xl mx-auto px-4 py-6">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
