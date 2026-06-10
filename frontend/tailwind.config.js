/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  corePlugins: {
    preflight: false,
  },
  theme: {
    extend: {
      colors: {
        bgPrimary: 'var(--bg-primary)',
        bgSecondary: 'var(--bg-secondary)',
        bgTertiary: 'var(--bg-tertiary)',
        bgCard: 'var(--bg-card)',
        bgCardHover: 'var(--bg-card-hover)',
        textPrimary: 'var(--text-primary)',
        textSecondary: 'var(--text-secondary)',
        textMuted: 'var(--text-muted)',
        accentPrimary: 'var(--accent-primary)',
        accentPrimaryHover: 'var(--accent-primary-hover)',
        accentSecondary: 'var(--accent-secondary)',
        accentWarning: 'var(--accent-warning)',
        accentError: 'var(--accent-error)',
        borderSubtle: 'var(--border-subtle)',
        borderColor: 'var(--border-color)',
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}

