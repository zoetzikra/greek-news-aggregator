/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#1d4ed8',  // Greek blue
          600: '#1e40af',
          700: '#1e3a8a',
          800: '#1e3a5f',
          900: '#172554',
        },
        accent: '#ffffff',  // White (Greek flag)
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        greek: ['"Noto Sans"', '"Noto Sans Greek"', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
