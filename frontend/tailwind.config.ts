import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        brand: {
          bg: "#060A13",
          surface: "#0B1324",
          sidebar: "#080E1C",
          card: "#0E182D",
          elevated: "#14223F",
          highlight: "#1E325A",
          border: "rgba(96, 165, 250, 0.12)",
          borderHover: "rgba(96, 165, 250, 0.35)",
          blue: "#3B82F6",
          electric: "#2563EB",
          sky: "#38BDF8",
          violet: "#8B5CF6",
          indigo: "#6366F1",
          purple: "#A855F7",
          text: "#F1F5F9",
          muted: "#94A3B8",
          subtle: "#64748B",
          success: "#10B981",
          warning: "#F59E0B",
          error: "#EF4444",
        },
      },
      borderRadius: {
        "2xl": "1rem",
        "3xl": "1.25rem",
        "card": "1.125rem",
      },
      boxShadow: {
        "glass": "0 8px 32px 0 rgba(0, 0, 0, 0.37)",
        "card": "0 4px 20px -2px rgba(3, 7, 18, 0.6), 0 2px 6px -1px rgba(3, 7, 18, 0.4)",
        "card-hover": "0 10px 25px -3px rgba(37, 99, 235, 0.15), 0 4px 10px -2px rgba(3, 7, 18, 0.5)",
        "glow-blue": "0 0 25px rgba(59, 130, 246, 0.25)",
        "glow-violet": "0 0 25px rgba(139, 92, 246, 0.20)",
      },
    },
  },
  plugins: [],
};

export default config;
