/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0284c7',
          600: '#0369a1',
          700: '#075985',
        },
        qa: {
          pass: '#10b981',
          fail: '#ef4444',
          blocked: '#f59e0b',
          inconclusive: '#6b7280'
        }
      }
    },
  },
  plugins: [],
}
