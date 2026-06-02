/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          900: '#0a1929',
          800: '#0d2137',
          700: '#1a3a5c',
          600: '#1e4a7a',
        },
        accent: {
          green: '#00ffab',
          cyan: '#00e5ff',
          pink: '#ff0066',
          pinkLight: '#ff4081',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
};
