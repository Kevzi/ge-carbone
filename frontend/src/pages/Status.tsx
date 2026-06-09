import React from 'react';
import FeaturePageLayout from '../../components/FeaturePageLayout';

const Status: React.FC = () => {
  return (
    <FeaturePageLayout 
      title="État des Services (Status)" 
      subtitle="Surveillance en temps réel de notre infrastructure."
      heroBadge="🟢 Tous les systèmes sont opérationnels"
    >
      <div className="max-w-4xl mx-auto">
         
         <div className="bg-[var(--bg-card)] border border-[var(--border-color)] p-8 rounded-2xl mb-8 shadow-xl">
            <div className="flex items-center justify-between border-b border-[var(--border-color)] pb-4 mb-4">
               <div className="font-bold text-lg">API d'Ingestion FEC</div>
               <div className="flex items-center gap-2 text-green-400 font-bold bg-green-500/10 px-3 py-1 rounded-full text-sm">
                 <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span> 100% Uptime
               </div>
            </div>
            
            <div className="flex items-center justify-between border-b border-[var(--border-color)] pb-4 mb-4">
               <div className="font-bold text-lg">Moteur de Calcul Carbone (IA)</div>
               <div className="flex items-center gap-2 text-green-400 font-bold bg-green-500/10 px-3 py-1 rounded-full text-sm">
                 <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span> 100% Uptime
               </div>
            </div>

            <div className="flex items-center justify-between border-b border-[var(--border-color)] pb-4 mb-4">
               <div className="font-bold text-lg">Générateur Export iXBRL</div>
               <div className="flex items-center gap-2 text-green-400 font-bold bg-green-500/10 px-3 py-1 rounded-full text-sm">
                 <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span> 100% Uptime
               </div>
            </div>

            <div className="flex items-center justify-between">
               <div className="font-bold text-lg">Tableau de bord Web (UI)</div>
               <div className="flex items-center gap-2 text-green-400 font-bold bg-green-500/10 px-3 py-1 rounded-full text-sm">
                 <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span> 100% Uptime
               </div>
            </div>
         </div>

         <p className="text-center text-[var(--text-secondary)] text-sm">
           La disponibilité est mesurée sur les 30 derniers jours civils. Les maintenances programmées sont annoncées 48h à l'avance.
         </p>
      </div>
    </FeaturePageLayout>
  );
};

export default Status;
