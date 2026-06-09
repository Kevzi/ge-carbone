import React from 'react';
import FeaturePageLayout from '../../components/FeaturePageLayout';

const Engine: React.FC = () => {
  return (
    <FeaturePageLayout 
      title="Moteur de Calcul Hybride & IA" 
      subtitle="La synergie parfaite entre comptabilité analytique (PCG) et Intelligence Artificielle (NLP) pour un bilan carbone précis."
      heroBadge="🧠 Propulsé par CamemBERTv2"
    >
      <div className="grid md:grid-cols-3 gap-8 mb-24">
        <div className="bg-[var(--bg-card)] border border-[var(--border-color)] p-8 rounded-2xl shadow-lg relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl group-hover:bg-blue-500/20 transition-all"></div>
          <h3 className="text-xl font-bold mb-4 text-blue-400">1. Intelligence Artificielle (NLP)</h3>
          <p className="text-[var(--text-secondary)]">
            Notre moteur analyse sémantiquement les libellés comptables (EcritureLib) grâce au modèle <strong>CamemBERTv2</strong>. Il est capable de désambiguïser les fournisseurs et de comprendre précisément la nature physique de l'achat.
          </p>
        </div>

        <div className="bg-[var(--bg-card)] border border-[var(--border-color)] p-8 rounded-2xl shadow-lg relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-green-500/10 rounded-full blur-3xl group-hover:bg-green-500/20 transition-all"></div>
          <h3 className="text-xl font-bold mb-4 text-green-400">2. Hybridation ADEME</h3>
          <p className="text-[var(--text-secondary)]">
            Les données sont connectées en temps réel avec les facteurs d'émission officiels de la <strong>Base Empreinte® v1.1</strong> et de la <strong>Base Carbone® v23.10</strong> de l'ADEME, croisant ratios monétaires et données physiques.
          </p>
        </div>

        <div className="bg-[var(--bg-card)] border border-[var(--border-color)] p-8 rounded-2xl shadow-lg relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-3xl group-hover:bg-purple-500/20 transition-all"></div>
          <h3 className="text-xl font-bold mb-4 text-purple-400">3. Transparence Totale (DQR)</h3>
          <p className="text-[var(--text-secondary)]">
            Le vrai différenciateur : pour chaque ligne, notre moteur calcule un <strong>Data Quality Rating (DQR)</strong> de 1 à 5. Nous ne masquons jamais l'incertitude inhérente aux ratios monétaires.
          </p>
        </div>
      </div>

      <div className="bg-[var(--bg-card)] border border-[var(--border-color)] p-12 rounded-3xl text-center max-w-4xl mx-auto shadow-2xl">
        <h2 className="text-3xl font-bold mb-6">Comment fonctionne l'hybridation ?</h2>
        <p className="text-lg text-[var(--text-secondary)] leading-relaxed mb-8">
          Un ratio purement monétaire (ex: "X euros dépensés en transport = Y kg CO2") génère d'énormes incertitudes. L'algorithme de LedgerCarbon extrait d'abord les quantités physiques (litres, kWh) depuis les comptes 60xxx, avant d'appliquer les ratios monétaires (Ratios d'intensité) uniquement en dernier recours sur les achats généraux.
        </p>
        
        <div className="flex flex-col md:flex-row justify-center items-center gap-6">
           <div className="px-6 py-3 bg-[var(--bg-primary)] rounded-lg font-mono text-sm border border-[var(--border-color)]">Compte 60221 (Carburants)</div>
           <svg className="w-6 h-6 text-gray-500 hidden md:block" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" /></svg>
           <div className="px-6 py-3 bg-blue-900/30 text-blue-300 rounded-lg font-bold border border-blue-500/30">NLP : Extraction Litres</div>
           <svg className="w-6 h-6 text-gray-500 hidden md:block" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" /></svg>
           <div className="px-6 py-3 bg-green-900/30 text-green-300 rounded-lg font-bold border border-green-500/30">Facteur Physique ADEME</div>
        </div>
      </div>
    </FeaturePageLayout>
  );
};

export default Engine;
