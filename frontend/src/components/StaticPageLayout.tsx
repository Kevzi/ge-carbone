import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import logoUrl from '../assets/logo.png';

interface StaticPageLayoutProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}

const StaticPageLayout: React.FC<StaticPageLayoutProps> = ({ title, subtitle, children }) => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] font-sans text-[var(--text-primary)]">
      {/* Mini Header */}
      <header className="flex justify-between items-center py-4 px-10 border-b border-[var(--border-color)] bg-[var(--bg-card)] sticky top-0 z-50">
        <Link to="/" className="flex items-center gap-3">
          <img src={logoUrl} alt="LedgerCarbon" className="w-8 h-8 object-contain" />
          <span className="text-xl font-bold brand-text">LedgerCarbon</span>
        </Link>
        <Link to="/landing" className="text-sm font-medium text-[var(--text-secondary)] hover:text-white transition-colors">
          Retour à l'accueil
        </Link>
      </header>

      {/* Hero Section */}
      <div className="bg-[var(--bg-card)] border-b border-[var(--border-color)] py-16 px-6 text-center">
        <h1 className="text-4xl md:text-5xl font-extrabold mb-4">{title}</h1>
        {subtitle && <p className="text-xl text-[var(--text-secondary)] max-w-2xl mx-auto">{subtitle}</p>}
      </div>

      {/* Content */}
      <main className="max-w-4xl mx-auto py-16 px-6 prose prose-invert prose-blue lg:prose-lg">
        {children}
      </main>

      {/* Simple Footer */}
      <footer className="border-t border-[var(--border-color)] bg-[var(--bg-card)] py-8 text-center text-[var(--text-secondary)] text-sm mt-auto">
        <p>LedgerCarbon © 2026. Tous droits réservés.</p>
      </footer>
    </div>
  );
};

export default StaticPageLayout;
