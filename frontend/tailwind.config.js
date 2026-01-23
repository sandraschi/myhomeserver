/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // We'll set this to 'dark' by default
  theme: {
    extend: {
      colors: {
        // Dark theme color palette - professional and beautiful
        background: {
          DEFAULT: '#0f172a', // slate-900
          secondary: '#1e293b', // slate-800
          tertiary: '#334155', // slate-700
          accent: '#475569', // slate-600
        },
        foreground: {
          DEFAULT: '#f8fafc', // slate-50
          secondary: '#cbd5e1', // slate-300
          muted: '#94a3b8', // slate-400
          accent: '#64748b', // slate-500
        },
        // Primary colors
        primary: {
          DEFAULT: '#3b82f6', // blue-500
          hover: '#2563eb', // blue-600
          active: '#1d4ed8', // blue-700
          muted: '#60a5fa', // blue-400
        },
        // Status colors
        success: {
          DEFAULT: '#10b981', // emerald-500
          hover: '#059669', // emerald-600
          background: '#dcfce7', // emerald-100
          foreground: '#065f46', // emerald-800
        },
        warning: {
          DEFAULT: '#f59e0b', // amber-500
          hover: '#d97706', // amber-600
          background: '#fef3c7', // amber-100
          foreground: '#92400e', // amber-800
        },
        error: {
          DEFAULT: '#ef4444', // red-500
          hover: '#dc2626', // red-600
          background: '#fee2e2', // red-100
          foreground: '#991b1b', // red-800
        },
        info: {
          DEFAULT: '#06b6d4', // cyan-500
          hover: '#0891b2', // cyan-600
          background: '#cffafe', // cyan-100
          foreground: '#164e63', // cyan-800
        },
        // Card and surface colors
        card: {
          DEFAULT: '#1e293b', // slate-800
          hover: '#334155', // slate-700
          border: '#475569', // slate-600
        },
        // Input colors
        input: {
          DEFAULT: '#334155', // slate-700
          border: '#475569', // slate-600
          focus: '#3b82f6', // blue-500
          placeholder: '#94a3b8', // slate-400
        },
        // Special device colors
        device: {
          online: '#10b981', // green
          offline: '#ef4444', // red
          warning: '#f59e0b', // amber
          camera: '#3b82f6', // blue
          light: '#fbbf24', // yellow
          energy: '#8b5cf6', // violet
          weather: '#06b6d4', // cyan
        }
      },
      // Custom shadows for dark theme
      boxShadow: {
        'card': '0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.3)',
        'card-hover': '0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -2px rgba(0, 0, 0, 0.4)',
        'modal': '0 20px 25px -5px rgba(0, 0, 0, 0.6), 0 10px 10px -5px rgba(0, 0, 0, 0.4)',
      },
      // Custom animations
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' },
        },
      },
      // Typography improvements
      fontFamily: {
        'sans': ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        'mono': ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
      },
    },
  },
  plugins: [],
}