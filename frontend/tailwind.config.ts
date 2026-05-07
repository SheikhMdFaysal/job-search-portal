import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#18201d",
        paper: "#f7f4ed",
        line: "#d8d2c4",
        mint: "#9bc9b7",
        coral: "#e6785f",
        steel: "#596d7a"
      },
      boxShadow: {
        soft: "0 12px 40px rgba(24, 32, 29, 0.10)"
      }
    }
  },
  plugins: []
};

export default config;
