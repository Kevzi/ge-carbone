import React from 'react';
import FeaturePageLayout from '../../components/FeaturePageLayout';

const CaseStudies: React.FC = () => {
  return (
    <FeaturePageLayout 
      title="Cas Clients & Témoignages" 
      subtitle="Découvrez comment les cabinets d'expertise comptable transforment la comptabilité de leurs clients en stratégie bas carbone."
    >
      <div className="max-w-4xl mx-auto">
        <div className="bg-[var(--bg-card)] border border-[var(--border-color)] p-8 md:p-12 rounded-3xl shadow-2xl relative overflow-hidden mb-12">
           <div className="absolute top-0 left-0 w-2 h-full bg-blue-500"></div>
           <svg className="w-12 h-12 text-blue-500/30 absolute top-8 right-8" fill="currentColor" viewBox="0 0 24 24"><path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" /></svg>
           
           <p className="text-xl md:text-2xl font-light text-white leading-relaxed mb-8 relative z-10 italic">
             "Avant LedgerCarbon, nous refusions les missions de Bilan Carbone car cela demandait trop de ressources internes. Aujourd'hui, on exporte le FEC de nos clients PME, on le glisse dans l'outil, et on génère le brouillon iXBRL en 10 minutes. C'est un gain de productivité incroyable qui nous permet de nous concentrer sur le conseil stratégique."
           </p>
           
           <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-blue-900 rounded-full flex items-center justify-center font-bold text-xl border-2 border-blue-500">M</div>
              <div>
                 <h4 className="font-bold text-lg text-white">Marc D.</h4>
                 <p className="text-[var(--text-secondary)] text-sm">Expert-Comptable Associé (Cabinet de 45 collaborateurs)</p>
              </div>
           </div>
        </div>

        <div className="bg-[var(--bg-card)] border border-[var(--border-color)] p-8 md:p-12 rounded-3xl shadow-2xl relative overflow-hidden">
           <div className="absolute top-0 left-0 w-2 h-full bg-green-500"></div>
           <svg className="w-12 h-12 text-green-500/30 absolute top-8 right-8" fill="currentColor" viewBox="0 0 24 24"><path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" /></svg>
           
           <p className="text-xl md:text-2xl font-light text-white leading-relaxed mb-8 relative z-10 italic">
             "L'argument décisif pour nous a été la piste d'audit 'Boîte de Verre'. Notre pôle audit (CAC) peut retracer chaque émission carbone jusqu'à la facture originelle. Le Data Quality Rating rassure énormément nos clients industriels."
           </p>
           
           <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-green-900 rounded-full flex items-center justify-center font-bold text-xl border-2 border-green-500">S</div>
              <div>
                 <h4 className="font-bold text-lg text-white">Sophie T.</h4>
                 <p className="text-[var(--text-secondary)] text-sm">Directrice Administrative et Financière (ETI Industrielle)</p>
              </div>
           </div>
        </div>
      </div>
    </FeaturePageLayout>
  );
};

export default CaseStudies;
