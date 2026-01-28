/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'race-sport': ['Race Sport', 'sans-serif'],
        'montserrat': ['Montserrat', 'sans-serif'],
      },
      colors: {
        'brand-green': '#0C2820',
        'brand-green-light': '#1A4A3E',
        'brand-gold': '#B7852A',
        'brand-gray': '#C2C2C2',
      }
    },
  },
  plugins: [],
}