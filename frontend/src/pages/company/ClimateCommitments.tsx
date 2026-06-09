import React from 'react';
import FeaturePageLayout from '../../components/FeaturePageLayout';

const ClimateCommitments: React.FC = () => {
  return (
    <FeaturePageLayout 
      title="Nos Engagements Climat" 
      subtitle="Parce qu'on ne peut pas aider nos clients à se décarboner si nous ne sommes pas nous-mêmes irréprochables."
      heroBadge="🌱 Stratégie Green AI"
    >
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold mb-8 text-center">L'Éco-conception logicielle au cœur de notre ADN</h2>
        
        <p className="text-lg text-[var(--text-secondary)] leading-relaxed mb-12 text-center">
          Mesurer l'empreinte carbone a paradoxalement un coût carbone. L'utilisation d'algorithmes d'Intelligence Artificielle (NLP) consomme d'énormes ressources CPU/GPU. Chez LedgerCarbon, nous appliquons une politique stricte de "Green AI".
        </p>

        <div className="grid md:grid-cols-2 gap-8 mb-16">
           <div className="bg-[var(--bg-card)] border border-green-500/30 p-8 rounded-2xl shadow-[0_0_15px_rgba(34,197,94,0.1)]">
              <div className="w-12 h-12 bg-green-500/20 text-green-500 rounded-xl flex items-center justify-center mb-6">
                 <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>
              </div>
              <h3 className="text-xl font-bold mb-3">Distillation & Quantification INT8</h3>
              <p className="text-[var(--text-secondary)]">
                Plutôt que d'utiliser des modèles LLM massifs et énergivores type GPT-4 pour lire des factures, nous utilisons un modèle CamemBERTv2 hautement spécialisé. Grâce à des techniques de "Quantification INT8", nous avons réduit sa taille en mémoire de 400% tout en gardant une précision sémantique identique.
              </p>
           </div>
           
           <div className="bg-[var(--bg-card)] border border-blue-500/30 p-8 rounded-2xl shadow-[0_0_15px_rgba(59,130,246,0.1)]">
              <div className="w-12 h-12 bg-blue-500/20 text-blue-500 rounded-xl flex items-center justify-center mb-6">
                 <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" /></svg>
              </div>
              <h3 className="text-xl font-bold mb-3">Datacenters Bas Carbone</h3>
              <p className="text-[var(--text-secondary)]">
                Le mix énergétique français étant l'un des plus décarbonés d'Europe (grâce au nucléaire et aux renouvelables), 100% de notre infrastructure de production est hébergée en France. Nous refusons de délocaliser notre puissance de calcul dans des pays où le kWh est plus carboné.
              </p>
           </div>
        </div>

        <div className="bg-[var(--bg-primary)] p-8 rounded-2xl border border-[var(--border-color)] text-center">
           <h3 className="text-2xl font-bold mb-4">Notre propre bilan carbone</h3>
           <p className="text-[var(--text-secondary)] mb-6">
             Fidèles à notre mission de transparence, nous publions annuellement l'empreinte carbone de la société LedgerCarbon, incluant nos scopes 1, 2 et 3.
           </p>
           <button className="px-6 py-2 bg-transparent border border-white hover:bg-white hover:text-black transition-colors rounded-lg font-bold">
             Télécharger le rapport 2025 (PDF)
           </button>
        </div>
      </div>
    </FeaturePageLayout>
  );
};

export default ClimateCommitments;
