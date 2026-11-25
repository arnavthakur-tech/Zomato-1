import type { Config } from "tailwindcss";

export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: "#111319",
          dim: "#111319",
          bright: "#36393f",
          variant: "#32353a",
          container: {
            DEFAULT: "#1d2025",
            lowest: "#0b0e13",
            low: "#191c21",
            high: "#272a30",
            highest: "#32353a",
          },
        },
        "on-surface": {
          DEFAULT: "#e1e2e9",
          variant: "#e4bebc",
        },
        primary: {
          DEFAULT: "#ffb3b1",
          container: "#ff535a",
          fixed: "#ffdad8",
        },
        "on-primary": {
          DEFAULT: "#680011",
          container: "#5b000e",
        },
        secondary: {
          DEFAULT: "#bec7d2",
          container: "#414a53",
        },
        tertiary: {
          DEFAULT: "#aac7ff",
          container: "#418fff",
        },
        outline: {
          DEFAULT: "#ab8987",
          variant: "#5b403f",
        },
        error: {
          DEFAULT: "#ffb4ab",
          container: "#93000a",
        },
      },
      fontFamily: {
        headline: ["var(--font-plus-jakarta)", "system-ui", "sans-serif"],
        body: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains)", "ui-monospace", "monospace"],
      },
      borderRadius: {
        DEFAULT: "0.25rem",
        lg: "0.5rem",
        xl: "0.75rem",
      },
      maxWidth: {
        shell: "72rem",
      },
    },
  },
  plugins: [],
} satisfies Config;
