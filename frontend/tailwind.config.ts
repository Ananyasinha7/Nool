import type { Config } from "tailwindcss";

// Tokens from Doc 2 section 2. The default palette is replaced, not extended: there is no accent colour.
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    colors: {
      transparent: "transparent",
      current: "currentColor",
      paper: "var(--paper)",
      surface: "var(--surface)",
      ink: "var(--ink)",
      "ink-2": "var(--ink-2)",
      "ink-3": "var(--ink-3)",
      line: "var(--line)",
      "line-strong": "var(--line-strong)",
      green: "var(--green)",
      "green-text": "var(--green-text)",
      "red-text": "var(--red-text)",
      field: "var(--field)",
      "green-bg": "var(--green-bg)",
      amber: "var(--amber)",
      "amber-text": "var(--amber-text)",
      "amber-bg": "var(--amber-bg)",
      red: "var(--red)",
      "red-bg": "var(--red-bg)",
      grey: "var(--grey)",
    },
    borderRadius: { none: "0", sm: "8px", DEFAULT: "8px", md: "12px", full: "999px" },
    fontFamily: { sans: ['Inter', '"Noto Sans Tamil"', "system-ui", "sans-serif"] },
    extend: {
      fontSize: {
        display: ["44px", { lineHeight: "48px", fontWeight: "600" }],
        title: ["28px", { lineHeight: "34px", fontWeight: "600" }],
        heading: ["20px", { lineHeight: "28px", fontWeight: "600" }],
        label: ["12px", { lineHeight: "16px", fontWeight: "500", letterSpacing: "0.02em" }],
      },
      maxWidth: { page: "1200px" },
      transitionTimingFunction: { nool: "cubic-bezier(.23,1,.32,1)" },
    },
  },
  plugins: [],
} satisfies Config;
