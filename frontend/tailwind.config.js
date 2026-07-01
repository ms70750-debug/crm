/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#090b0d",
        panel: "#101417",
        line: "#263036",
        lime: "#c7ff45",
        mint: "#4ade80"
      }
    },
  },
  plugins: [],
};
