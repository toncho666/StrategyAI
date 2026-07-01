/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'apple-dark': '#1d1d1d',
        'apple-light': '#f5f5f7',
        'apple-gray': '#86868b',
        'apple-accent': '#0071e3',
        'profit': '#34c759',
        'loss': '#ff3b30',
      },
      fontFamily: {
        'apple': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      },
    },
  },
  plugins: [],
}
