import React from 'react';
import FeaturePageLayout from '../../components/FeaturePageLayout';

const IngestionFEC: React.FC = () => {
  return (
    <FeaturePageLayout 
      title="Ingestion FEC Automatique" 
      subtitle="Oubliez les collectes de données interminables et la double saisie. Glissez votre fichier comptable, on s'occupe du reste."
      heroBadge="🚀 Plus de 1 million de lignes traitées en 5 min"
    >
      <div className="grid md:grid-cols-2 gap-16 items-center mb-24">
        <div>
          <h2 className="text-3xl font-bold mb-6">Conformité Stricte A47 A-1</h2>
          <p className="text-lg text-[var(--text-secondary)] leading-relaxed mb-6">
            Dès l'importation, notre parseur natif vérifie la structure de votre fichier. LedgerCarbon identifie et valide automatiquement les 18 colonnes obligatoires fixées par l'Article A47 A-1 du Livre des Procédures Fiscales (LPF).
          </p>
          <ul className="space-y-4">
            <li className="flex gap-3 items-start">
              <span className="text-green-400 mt-1">✓</span>
              <span>Détection intelligente de l'encodage et des séparateurs.</span>
            </li>
            <li className="flex gap-3 items-start">
              <span className="text-green-400 mt-1">✓</span>
              <span>Mappage natif des codes journaux (Achats, Ventes, OD).</span>
            </li>
          </ul>
        </div>
        <div className="bg-[var(--bg-card)] border border-[var(--border-color)] p-8 rounded-2xl shadow-xl flex items-center justify-center min-h-[300px]">
          {/* Mockup UI / Schema */}
          <div className="flex flex-col items-center gap-4 text-center">
            <svg className="w-16 h-16 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
            <div className="font-mono text-sm bg-[var(--bg-primary)] px-4 py-2 rounded-lg border border-[var(--border-color)]">
              FEC_2024_SocieteX.txt (1.2 Go)
            </div>
            <div className="w-full bg-gray-700 h-2 rounded-full overflow-hidden mt-4">
              <div className="bg-blue-500 w-3/4 h-full animate-pulse"></div>
            </div>
            <span className="text-sm text-green-400">Validation A47 A-1 en cours...</span>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-16 items-center flex-row-reverse md:flex-row">
        <div className="order-2 md:order-1 bg-[var(--bg-card)] border border-[var(--border-color)] p-8 rounded-2xl shadow-xl">
           <div className="space-y-4 font-mono text-sm text-[var(--text-secondary)]">
              <div className="flex justify-between border-b border-[var(--border-color)] pb-2"><span className="text-blue-400">Stream chunks</span><span>Size: 64MB</span></div>
              <div className="flex justify-between border-b border-[var(--border-color)] pb-2"><span className="text-green-400">Memory usage</span><span>Stable (~150MB)</span></div>
              <div className="flex justify-between border-b border-[var(--border-color)] pb-2"><span className="text-purple-400">Garbage collection</span><span>Optimized</span></div>
           </div>
        </div>
        <div className="order-1 md:order-2">
          <h2 className="text-3xl font-bold mb-6">Haute Performance & Sécurité (Streaming)</h2>
          <p className="text-lg text-[var(--text-secondary)] leading-relaxed mb-6">
            Les fichiers FEC peuvent peser plusieurs gigaoctets. LedgerCarbon intègre une architecture de traitement en "streaming" (chunking) permettant d'analyser d'immenses volumes de données sans jamais saturer la mémoire vive (RAM) de nos serveurs.
          </p>
          <p className="text-lg text-[var(--text-secondary)] leading-relaxed">
            <strong>Sécurité absolue :</strong> Les fichiers uploadés sont traités à la volée de manière éphémère et sont soumis à notre politique de suppression stricte (effacement garanti sous 24h après calcul).
          </p>
        </div>
      </div>
    </FeaturePageLayout>
  );
};

export default IngestionFEC;
