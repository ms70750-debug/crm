/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0f2143",
        panel: "#ffffff",
        line: "#dbe5f2",
        lime: "#0b5ed7",
        mint: "#0a4fb4",
        gold: "#f8c545",
        graphite: "#263445",
        surface: "#f8fbff"
      }
    },
  },
  plugins: [],
};
