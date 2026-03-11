/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        pitwall: {
          bg: '#0A0A0F',
          surface: '#12121A',
          border: '#1E1E2E',
          accent: '#E10600',
          'accent-glow': '#FF1A1A',
          green: '#00D26A',
          yellow: '#FFD60A',
          blue: '#0A84FF',
          purple: '#BF5AF2',
          text: '#F5F5F7',
          'text-dim': '#86868B',
          'text-muted': '#48484A',
        },
      },
      fontFamily: {
        mono: ['"SF Mono"', '"JetBrains Mono"', 'monospace'],
        sans: ['"SF Pro Display"', '-apple-system', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(225, 6, 0, 0.3)' },
          '100%': { boxShadow: '0 0 20px rgba(225, 6, 0, 0.6)' },
        },
      },
    },
  },
  plugins: [],
};
