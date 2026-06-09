import React from 'react';
import FeaturePageLayout from '../../components/FeaturePageLayout';

const Partners: React.FC = () => {
  return (
    <FeaturePageLayout 
      title="Devenir Partenaire Technologique" 
      subtitle="Intégrez la technologie LedgerCarbon directement dans vos logiciels (ERP, SIRH, Outils de gestion)."
      heroBadge="🤝 API Restful disponible"
    >
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-3xl font-bold mb-6">Développez la "Feature" Climat en 1 semaine</h2>
        <p className="text-lg text-[var(--text-secondary)] leading-relaxed mb-12">
          Vous développez un ERP, un logiciel comptable, ou une solution RH ? Vos clients vous demandent d'ajouter des indicateurs carbones ? Ne réinventez pas la roue. Intégrez notre moteur de calcul par API et offrez à vos utilisateurs une estimation instantanée de l'empreinte CO2 liée à leurs achats, sans quitter votre interface.
        </p>

        <div className="bg-[var(--bg-card)] border border-[var(--border-color)] p-8 rounded-2xl shadow-xl text-left font-mono text-sm mb-12">
           <div className="text-gray-400 mb-4">// POST /api/v1/engine/calculate</div>
           <div className="text-blue-300">
             {"{"}<br/>
             &nbsp;&nbsp;"amount": 1200.00,<br/>
             &nbsp;&nbsp;"currency": "EUR",<br/>
             &nbsp;&nbsp;"description": "Achat 20 ordinateurs portables",<br/>
             &nbsp;&nbsp;"accountCode": "606400"<br/>
             {"}"}
           </div>
           <div className="text-gray-400 mt-4 mb-2">// Response (200 OK)</div>
           <div className="text-green-300">
             {"{"}<br/>
             &nbsp;&nbsp;"co2_kg": 3380.0,<br/>
             &nbsp;&nbsp;"factor_id": "ademe_it_001",<br/>
             &nbsp;&nbsp;"dqr_score": 3<br/>
             {"}"}
           </div>
        </div>

        <button className="px-8 py-4 bg-white text-black font-bold rounded-xl hover:bg-gray-200 transition-colors">
          Contacter l'équipe Partenariat
        </button>
      </div>
    </FeaturePageLayout>
  );
};

export default Partners;
