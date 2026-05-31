import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["'Avenir Next'", "'Segoe UI'", "system-ui", "sans-serif"],
        display: [
          "'Space Grotesk'",
          "'Avenir Next'",
          "system-ui",
          "sans-serif",
        ],
      },
      colors: {
        ink: {
          50: "#eef6ff",
          100: "#dbeafe",
          200: "#bfdbfe",
          300: "#93c5fd",
          400: "#60a5fa",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
          800: "#1e40af",
          900: "#172554",
        },
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(96, 165, 250, 0.2), 0 24px 80px rgba(2, 6, 23, 0.45)",
      },
      backgroundImage: {
        "hero-radial":
          "radial-gradient(circle at top left, rgba(59, 130, 246, 0.24), transparent 34%), radial-gradient(circle at top right, rgba(14, 165, 233, 0.14), transparent 28%), linear-gradient(135deg, #020617 0%, #0f172a 45%, #111827 100%)",
      },
    },
  },
  plugins: [],
} satisfies Config;
