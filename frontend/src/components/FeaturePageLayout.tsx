import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import logoUrl from '../assets/logo.png';

interface FeaturePageLayoutProps {
  title: string;
  subtitle: string;
  heroBadge?: string;
  children: React.ReactNode;
}

const FeaturePageLayout: React.FC<FeaturePageLayoutProps> = ({ title, subtitle, heroBadge, children }) => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] font-sans text-[var(--text-primary)]">
      {/* Header */}
      <header className="flex justify-between items-center py-4 px-10 border-b border-[var(--border-color)] bg-[var(--bg-card)] sticky top-0 z-50 shadow-sm">
        <Link to="/" className="flex items-center gap-3">
          <img src={logoUrl} alt="LedgerCarbon" className="w-8 h-8 object-contain" />
          <span className="text-xl font-bold brand-text">LedgerCarbon</span>
        </Link>
        <Link to="/landing" className="px-5 py-2 rounded-lg border border-[var(--border-color)] text-sm font-medium hover:bg-[var(--bg-primary)] transition-all">
          Retour à l'accueil
        </Link>
      </header>

      {/* Hero Section */}
      <div className="relative overflow-hidden bg-[var(--bg-card)] border-b border-[var(--border-color)] pt-24 pb-32 px-6 text-center">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-4xl h-full bg-gradient-to-b from-blue-500/10 to-transparent blur-3xl rounded-full opacity-50 pointer-events-none"></div>
        <div className="relative z-10 max-w-4xl mx-auto">
          {heroBadge && (
            <div className="inline-block px-4 py-1.5 rounded-full bg-blue-500/10 text-blue-400 font-bold text-sm mb-6 border border-blue-500/20 shadow-[0_0_15px_rgba(59,130,246,0.2)]">
              {heroBadge}
            </div>
          )}
          <h1 className="text-5xl md:text-6xl font-extrabold mb-6 tracking-tight text-transparent bg-clip-text" style={{ backgroundImage: 'var(--gradient-primary)' }}>
            {title}
          </h1>
          <p className="text-xl md:text-2xl text-[var(--text-secondary)] leading-relaxed max-w-3xl mx-auto">
            {subtitle}
          </p>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-6xl mx-auto py-20 px-6">
        {children}
      </main>

      {/* Call To Action */}
      <div className="border-t border-[var(--border-color)] bg-gradient-to-b from-[var(--bg-card)] to-[var(--bg-primary)] py-20 px-6 text-center">
        <h2 className="text-3xl font-bold mb-6">Prêt à moderniser vos missions de conseil ?</h2>
        <p className="text-[var(--text-secondary)] mb-8 max-w-2xl mx-auto">
          Découvrez par vous-même la puissance du premier moteur de calcul carbone nativement conçu pour s'interfacer avec les données comptables.
        </p>
        <Link to="/login" className="inline-block px-8 py-4 rounded-xl text-white font-bold text-lg shadow-[0_0_20px_rgba(59,130,246,0.3)] hover:scale-105 transition-all" style={{ background: 'var(--gradient-primary)' }}>
          Démarrer gratuitement
        </Link>
      </div>

      {/* Simple Footer */}
      <footer className="border-t border-[var(--border-color)] bg-[var(--bg-card)] py-12 text-center text-[var(--text-secondary)] text-sm">
        <div className="flex items-center justify-center gap-3 mb-4">
          <img src={logoUrl} alt="LedgerCarbon" className="w-6 h-6 opacity-50 grayscale" />
          <span className="font-bold">LedgerCarbon © 2026</span>
        </div>
        <p>Solution hébergée en France (SecNumCloud).</p>
      </footer>
    </div>
  );
};

export default FeaturePageLayout;
