/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        industrial: {
          900: '#090a0f',
          800: '#11131a',
          700: '#1a1d26',
          600: '#252936',
          500: '#34394a',
        },
        accent: {
          green: '#10b981',
          blue: '#38bdf8',
          amber: '#fbbf24',
          orange: '#fb923c',
          rose: '#f43f5e'
        }
      }
    },
  },
  plugins: [],
}
