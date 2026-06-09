import React from 'react';
import FeaturePageLayout from '../../components/FeaturePageLayout';

const DAF: React.FC = () => {
  return (
    <FeaturePageLayout 
      title="Pour les DAF & PME" 
      subtitle="Pilotez votre bilan carbone sans stress. Mettez fin aux questionnaires chronophages."
      heroBadge="📊 Réconcilié avec la liasse fiscale"
    >
      <div className="grid md:grid-cols-2 gap-16 items-center mb-24">
        <div>
          <h2 className="text-3xl font-bold mb-6">L'Approche "Ledger-First"</h2>
          <p className="text-lg text-[var(--text-secondary)] leading-relaxed mb-6">
            La méthode traditionnelle de bilan carbone est inefficace : on demande aux équipes opérationnelles de remplir d'immenses fichiers Excel approximatifs (kilométrage des commerciaux, tonnes de matières premières achetées, factures d'électricité manquantes...).
          </p>
          <div className="bg-blue-500/10 border-l-4 border-blue-500 p-6 mt-6 rounded-r-lg">
            <p className="text-xl italic font-serif text-blue-300">
              "Vous ne certifiez pas la chimie, vous certifiez la comptabilité."
            </p>
          </div>
          <p className="text-lg text-[var(--text-secondary)] leading-relaxed mt-6">
            Puisque toute activité économique de votre entreprise (achats, salaires, énergie, déplacements) laisse une trace financière, LedgerCarbon part directement de votre grand livre comptable (FEC) pour générer l'empreinte carbone.
          </p>
        </div>
        
        <div className="bg-[var(--bg-card)] border border-[var(--border-color)] p-8 rounded-2xl shadow-xl">
           <h3 className="text-xl font-bold text-center mb-8 border-b border-[var(--border-color)] pb-4">Zéro Double Saisie</h3>
           
           <div className="flex flex-col gap-6">
              <div className="flex items-center gap-4 text-[var(--text-secondary)]">
                 <svg className="w-8 h-8 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                 <span className="line-through decoration-red-500">Collecte des factures fournisseurs</span>
              </div>
              <div className="flex items-center gap-4 text-[var(--text-secondary)]">
                 <svg className="w-8 h-8 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                 <span className="line-through decoration-red-500">Estimation des notes de frais</span>
              </div>
              <div className="flex items-center gap-4 text-[var(--text-secondary)]">
                 <svg className="w-8 h-8 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                 <span className="line-through decoration-red-500">Oubli d'un poste de dépense</span>
              </div>
              <div className="flex items-center gap-4 font-bold text-white mt-4 pt-4 border-t border-[var(--border-color)]">
                 <svg className="w-8 h-8 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                 <span>Le FEC contient déjà 100% de l'information</span>
              </div>
           </div>
        </div>
      </div>

      <div className="text-center max-w-3xl mx-auto">
        <h2 className="text-3xl font-bold mb-6">Exhaustivité garantie</h2>
        <p className="text-lg text-[var(--text-secondary)] leading-relaxed">
          En liant mathématiquement l'empreinte carbone au compte de résultat financier, le DAF s'assure qu'absolument aucun flux physique ou monétaire n'a été "oublié" lors de la déclaration extra-financière. 
          Les commissaires aux comptes peuvent réconcilier les données carbone et financières sur un périmètre identique.
        </p>
      </div>
    </FeaturePageLayout>
  );
};

export default DAF;
