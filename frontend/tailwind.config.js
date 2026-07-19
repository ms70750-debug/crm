/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#020617",
        panel: "#ffffff",
        line: "#dbe4f0",
        lime: "#f97316",
        mint: "#0b5ed7"
      }
    },
  },
  plugins: [],
};
