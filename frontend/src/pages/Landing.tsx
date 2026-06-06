import React from 'react';
import { Link } from 'react-router-dom';
import logoUrl from '../assets/logo.png';
import ROISimulator from '../components/landing/ROISimulator';

const Landing: React.FC = () => {
  return (
    <div className="landing-page bg-[var(--bg-primary)] min-h-screen font-sans text-[var(--text-primary)]">
      
      {/* Header */}
      <header className="flex justify-between items-center py-6 px-10 border-b border-[var(--border-color)] bg-[var(--bg-card)] sticky top-0 z-50 shadow-sm">
        <div className="flex items-center gap-3">
          <img src={logoUrl} alt="LedgerCarbon Logo" className="w-10 h-10 object-contain" />
          <h1 className="text-2xl brand-text text-[var(--text-primary)]">
            LedgerCarbon
          </h1>
        </div>
        <nav className="flex items-center gap-6">
          <a href="#features" className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors font-medium">Fonctionnalités</a>
          <a href="#compliance" className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors font-medium">Conformité</a>
          <Link to="/login" className="px-6 py-2.5 rounded-lg border border-[var(--border-color)] hover:bg-[var(--bg-primary)] transition-all font-semibold">
            Espace Cabinet
          </Link>
          <Link to="/login" className="px-6 py-2.5 rounded-lg text-white font-semibold transition-all transform hover:scale-105 shadow-md" style={{ background: 'var(--gradient-primary)' }}>
            Demander une démo
          </Link>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="py-24 px-10 text-center max-w-5xl mx-auto flex flex-col items-center">
        <div className="inline-block px-4 py-1.5 rounded-full bg-blue-500/10 text-blue-400 font-semibold text-sm mb-6 border border-blue-500/20">
          ✨ La première solution automatisée pour Experts-Comptables
        </div>
        <h2 className="text-6xl md:text-7xl font-extrabold mb-8 leading-tight tracking-tight text-transparent bg-clip-text brand-text" style={{ backgroundImage: 'var(--gradient-primary)' }}>
          Transformez vos FEC en <br/> rapports CSRD auditables
        </h2>
        <p className="text-xl text-[var(--text-secondary)] max-w-3xl mb-12 leading-relaxed">
          Générez des bilans carbone certifiés et conformes (ESRS / iXBRL) en moins de 5 minutes, directement depuis vos écritures comptables. Sans formation préalable.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link to="/login" className="px-8 py-4 rounded-xl text-white font-bold text-lg transition-all transform hover:scale-105 hover:shadow-lg shadow-blue-500/20 flex items-center justify-center gap-2" style={{ background: 'var(--gradient-primary)' }}>
            Essayer gratuitement
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
          </Link>
          <a href="#features" className="px-8 py-4 rounded-xl font-bold text-lg border-2 border-[var(--border-color)] hover:border-gray-400 transition-colors bg-[var(--bg-card)] flex items-center justify-center gap-2">
            Voir la démo
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </a>
        </div>
      </section>

      {/* Social Proof / Compliance Badges */}
      <section id="compliance" className="py-16 bg-[var(--bg-card)] border-y border-[var(--border-color)]">
        <div className="max-w-6xl mx-auto px-10 text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-[var(--text-secondary)] mb-8">
            Conforme aux normes européennes les plus strictes
          </p>
          <div className="flex flex-wrap justify-center items-center gap-12 opacity-80 grayscale hover:grayscale-0 transition-all duration-500">
            <div className="flex items-center gap-3 bg-[var(--bg-primary)] px-6 py-3 rounded-lg border border-[var(--border-color)]">
              <span className="text-2xl font-black text-green-500">CSRD</span>
              <span className="text-sm font-medium">Ready</span>
            </div>
            <div className="flex items-center gap-3 bg-[var(--bg-primary)] px-6 py-3 rounded-lg border border-[var(--border-color)]">
              <span className="text-2xl font-black text-blue-500">ESRS</span>
              <span className="text-sm font-medium">Linkbase Arelle</span>
            </div>
            <div className="flex items-center gap-3 bg-[var(--bg-primary)] px-6 py-3 rounded-lg border border-[var(--border-color)]">
              <span className="text-2xl font-black text-purple-500">SecNumCloud</span>
              <span className="text-sm font-medium">Hébergement Souverain</span>
            </div>
            <div className="flex items-center gap-3 bg-[var(--bg-primary)] px-6 py-3 rounded-lg border border-[var(--border-color)]">
              <span className="text-2xl font-black text-gray-300">RGPD</span>
              <span className="text-sm font-medium">Conforme</span>
            </div>
          </div>
        </div>
      </section>

      {/* ROI Simulator */}
      <section id="roi-simulator" className="py-16 px-10 border-t border-[var(--border-color)]">
        <ROISimulator />
      </section>

      {/* Demo UI / Zero Learning / Features */}
      <section id="features" className="py-24 px-10 max-w-7xl mx-auto">
        <div className="grid md:grid-cols-2 gap-16 items-center">
          <div>
            <h3 className="text-4xl font-bold mb-6 tracking-tight brand-text">Interface "Zero-Learning"</h3>
            <p className="text-xl text-[var(--text-secondary)] mb-8 leading-relaxed">
              Pas de configuration complexe. Glissez-déposez simplement votre Fichier des Écritures Comptables (FEC) et notre IA se charge du reste.
            </p>
            <ul className="space-y-6">
              <li className="flex gap-4 items-start">
                <div className="bg-blue-500/20 p-3 rounded-lg text-blue-400 mt-1">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                </div>
                <div>
                  <h4 className="text-lg font-bold">Analyse IA ultra-rapide</h4>
                  <p className="text-[var(--text-secondary)]">1 million de lignes traitées en moins de 5 minutes grâce à notre moteur NLP propriétaire.</p>
                </div>
              </li>
              <li className="flex gap-4 items-start">
                <div className="bg-green-500/20 p-3 rounded-lg text-green-400 mt-1">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                </div>
                <div>
                  <h4 className="text-lg font-bold">Piste d'audit interactive</h4>
                  <p className="text-[var(--text-secondary)]">Remontez de la catégorie d'émission (Scope 3) jusqu'à la ligne comptable exacte.</p>
                </div>
              </li>
            </ul>
          </div>
          <div className="relative group perspective">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl blur-xl opacity-20 group-hover:opacity-40 transition-opacity duration-500"></div>
            <div className="relative bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-2 shadow-2xl transform rotate-y-3 group-hover:rotate-y-0 transition-transform duration-700 ease-out">
              {/* Fake UI mockup */}
              <div className="bg-[var(--bg-primary)] rounded-xl border border-[var(--border-color)] overflow-hidden">
                <div className="h-10 bg-[var(--bg-card)] border-b border-[var(--border-color)] flex items-center px-4 gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                </div>
                <div className="p-8 flex flex-col items-center justify-center min-h-[300px] border-2 border-dashed border-gray-600 rounded-lg m-6 bg-gray-800/30">
                  <svg className="w-16 h-16 text-blue-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
                  <p className="text-lg font-bold">Glissez-déposez le fichier FEC</p>
                  <p className="text-sm text-gray-400 mt-2">TXT, CSV acceptés. Jusqu'à 5Go.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[var(--border-color)] bg-[var(--bg-card)] py-12 px-10 text-center">
        <div className="flex flex-col md:flex-row justify-between items-center max-w-6xl mx-auto gap-6">
          <div className="flex items-center gap-3">
            <img src={logoUrl} alt="LedgerCarbon" className="w-8 h-8 opacity-50 grayscale" />
            <span className="font-bold text-gray-500">LedgerCarbon © 2026</span>
          </div>
          <div className="flex gap-6 text-sm text-gray-500">
            <a href="#" className="hover:text-[var(--text-primary)] transition-colors">Mentions légales</a>
            <a href="#" className="hover:text-[var(--text-primary)] transition-colors">Politique de confidentialité</a>
            <a href="#" className="hover:text-[var(--text-primary)] transition-colors">Contact</a>
          </div>
        </div>
      </footer>

    </div>
  );
};

export default Landing;
