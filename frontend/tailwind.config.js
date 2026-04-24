/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        maroon: '#800000',
        'maroon-dark': '#600000',
        gold: '#FFD700',
        ivory: '#FFFFF0',
        'warm-gray': '#d7d7d7',
        charcoal: '#36454F',
        navy: '#000080',
      }
    },
  },
  plugins: [
    require('daisyui'),
  ],
}
