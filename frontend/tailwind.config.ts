import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0a0a0f",
        surface: "#111118",
        "surface-alt": "#1a1a24",
        border: "#2a2a3a",
        accent: "#6366f1",
        "accent-hover": "#818cf8",
        success: "#22c55e",
        warning: "#f59e0b",
        danger: "#ef4444",
        muted: "#6b7280",
      },
    },
  },
  plugins: [],
};

export default config;
