/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // or 'media'
  content: [
    "./templates/**/*.html", // Path to your Flask templates
    "./src/**/*.js", // Any JavaScript files
  ],
  theme: {
    extend: {
      colors: {
        // Warm and Cozy Colors
        'leather-red-light': '#D2691E',
        'leather-red-dark': '#8B4513',
        'burnished-gold': '#B8860B',
        'mahogany': '#4A2C2A',
        
        // Muted Paper Tones
        'old-paper': '#F5DEB3',
        'ivory': '#FFFFF0',
        'parchment-beige': '#EAD2AC',
        'antique-white': '#FAEBD7',

        // Deep Library Colors
        'forest-green': '#228B22',
        'library-teal': '#008080',
        'midnight-blue': '#2C3E50',

        // Soft Pastel Shades
        'pastel-green-light': '#B4E197',
        'pastel-blue-light': '#CFE2F3',
        'pastel-pink-light': '#F3C4C6',

        // Accent Colors
        'golden-yellow': '#FFD700',
        'bronze': '#CD7F32',
        'brick-red': '#B22222',
      },
    },
  },
  plugins: [],
};