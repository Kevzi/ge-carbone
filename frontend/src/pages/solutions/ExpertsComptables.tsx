import React from 'react';
import FeaturePageLayout from '../../components/FeaturePageLayout';

const ExpertsComptables: React.FC = () => {
  return (
    <FeaturePageLayout 
      title="Pour les Experts-Comptables" 
      subtitle="Transformez une contrainte réglementaire en une mission de conseil hautement rentable."
      heroBadge="💼 Le ROI le plus rapide du marché"
    >
      <div className="bg-gradient-to-r from-blue-900 to-indigo-900 rounded-3xl p-12 text-center text-white mb-24 shadow-2xl relative overflow-hidden">
         <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/20 rounded-full blur-3xl pointer-events-none"></div>
         <h2 className="text-3xl font-bold mb-10">La mathématique de la rentabilité</h2>
         
         <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white/10 backdrop-blur-md border border-white/20 p-6 rounded-2xl">
               <div className="text-4xl font-black text-blue-300 mb-2">90 €</div>
               <div className="text-sm uppercase tracking-wider text-blue-100/70 font-semibold mb-4">Votre Coût</div>
               <p className="text-sm text-blue-50">Vous achetez 1 crédit LedgerCarbon (Pack Découverte).</p>
            </div>
            
            <div className="bg-white/10 backdrop-blur-md border border-white/20 p-6 rounded-2xl">
               <div className="text-4xl font-black text-green-300 mb-2">20 min</div>
               <div className="text-sm uppercase tracking-wider text-green-100/70 font-semibold mb-4">Votre Temps</div>
               <p className="text-sm text-green-50">Temps nécessaire pour uploader le FEC et réviser la piste d'audit générée par l'IA.</p>
            </div>
            
            <div className="bg-white/10 backdrop-blur-md border border-white/20 p-6 rounded-2xl shadow-[0_0_30px_rgba(59,130,246,0.3)]">
               <div className="text-4xl font-black text-white mb-2">1 500 €</div>
               <div className="text-sm uppercase tracking-wider text-yellow-300/80 font-semibold mb-4">Prix de Vente Moyen</div>
               <p className="text-sm text-white">Vous refacturez la mission de bilan carbone à votre client PME.</p>
            </div>
         </div>
         
         <div className="mt-10 pt-10 border-t border-white/10">
            <h3 className="text-2xl font-light">
               Marge nette générée : <span className="font-bold text-green-400">1 410 €</span>
            </h3>
            <p className="text-blue-200 mt-2">Soit l'équivalent d'un taux horaire de <strong>4 000 € / heure</strong>.</p>
         </div>
      </div>

      <div className="grid md:grid-cols-2 gap-16 items-center">
        <div>
          <h2 className="text-3xl font-bold mb-6">Ne laissez pas ce marché aux cabinets de conseil</h2>
          <p className="text-lg text-[var(--text-secondary)] leading-relaxed mb-6">
            La directive CSRD et les pressions des donneurs d'ordres obligent des centaines de milliers de PME à réaliser leur premier bilan carbone. Actuellement, elles se tournent vers des cabinets de conseil RSE spécialisés qui facturent des jours de prestation pour de la simple collecte de données.
          </p>
          <p className="text-lg text-[var(--text-secondary)] leading-relaxed">
            <strong>Vous avez un avantage concurrentiel injuste : vous possédez déjà la donnée source (le FEC).</strong> LedgerCarbon vous permet de désintermédier les consultants et de conserver cette nouvelle source de revenus stratégique au sein de votre cabinet d'expertise comptable.
          </p>
        </div>
        
        <div className="space-y-6">
           <div className="flex gap-4 items-start bg-[var(--bg-card)] border border-[var(--border-color)] p-6 rounded-xl">
              <div className="w-12 h-12 bg-blue-500/20 text-blue-400 rounded-full flex items-center justify-center flex-shrink-0 font-bold">1</div>
              <div>
                 <h4 className="font-bold text-lg mb-1">Générez le FEC</h4>
                 <p className="text-[var(--text-secondary)] text-sm">Depuis Quadra, Cegid, Sage, Pennylane ou Tiime.</p>
              </div>
           </div>
           
           <div className="flex gap-4 items-start bg-[var(--bg-card)] border border-[var(--border-color)] p-6 rounded-xl">
              <div className="w-12 h-12 bg-purple-500/20 text-purple-400 rounded-full flex items-center justify-center flex-shrink-0 font-bold">2</div>
              <div>
                 <h4 className="font-bold text-lg mb-1">Upload sur LedgerCarbon</h4>
                 <p className="text-[var(--text-secondary)] text-sm">L'IA s'occupe de l'affectation des facteurs physiques et monétaires.</p>
              </div>
           </div>
           
           <div className="flex gap-4 items-start bg-[var(--bg-card)] border border-[var(--border-color)] p-6 rounded-xl">
              <div className="w-12 h-12 bg-green-500/20 text-green-400 rounded-full flex items-center justify-center flex-shrink-0 font-bold">3</div>
              <div>
                 <h4 className="font-bold text-lg mb-1">Livrable & Conseil</h4>
                 <p className="text-[var(--text-secondary)] text-sm">Exportez le rapport CSRD, et concentrez-vous sur l'analyse et la stratégie de réduction.</p>
              </div>
           </div>
        </div>
      </div>
    </FeaturePageLayout>
  );
};

export default ExpertsComptables;
