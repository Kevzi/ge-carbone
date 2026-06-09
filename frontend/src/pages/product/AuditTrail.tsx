import React from 'react';
import FeaturePageLayout from '../../components/FeaturePageLayout';

const AuditTrail: React.FC = () => {
  return (
    <FeaturePageLayout 
      title="La Piste d'Audit (Boîte de Verre)" 
      subtitle="Fini les boîtes noires. Retracez chaque gramme de CO2 jusqu'à sa facture d'origine."
      heroBadge="🔍 100% Auditable par les CAC"
    >
      <div className="grid md:grid-cols-2 gap-16 items-center">
        <div>
          <h2 className="text-3xl font-bold mb-6">Le concept "Boîte de Verre"</h2>
          <p className="text-lg text-[var(--text-secondary)] leading-relaxed mb-6">
            La majorité des logiciels de bilan carbone grand public agissent comme des "boîtes noires" : vous entrez un chiffre d'affaires, il ressort une tonne de CO2, sans aucune possibilité de vérifier le calcul intermédiaire. 
          </p>
          <p className="text-lg text-[var(--text-secondary)] leading-relaxed mb-8">
            Pour répondre aux exigences de la CSRD et des audits financiers, LedgerCarbon inverse ce paradigme. Notre système offre une traçabilité verticale totale (Drill-down).
          </p>
          
          <div className="bg-[var(--bg-primary)] p-6 rounded-xl border border-[var(--border-color)]">
            <h3 className="text-xl font-bold text-white mb-3 flex items-center gap-2">
              <svg className="w-6 h-6 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
              L'argument choc pour les Commissaires aux Comptes
            </h3>
            <p className="text-[var(--text-secondary)] text-sm">
              Lors d'une vérification extra-financière, l'auditeur peut cliquer sur le total du Scope 3 (Catégorie 1 - Achats de services), et "descendre" la pyramide jusqu'à trouver le numéro de ligne exact de l'écriture comptable d'origine, le libellé, et le facteur d'émission ADEME qui a été appliqué. L'audit devient instantané.
            </p>
          </div>
        </div>
        
        <div className="bg-[var(--bg-card)] border border-[var(--border-color)] p-2 rounded-2xl shadow-xl overflow-hidden">
          <div className="bg-[#1e1e1e] rounded-xl p-4 font-mono text-xs overflow-x-auto">
            <div className="text-gray-400 mb-4">// Simulation Drill-down Piste d'Audit</div>
            
            <div className="pl-0 text-blue-300 hover:bg-white/5 p-1 rounded cursor-pointer transition-colors">▼ SCOPE 3 (Emissions Indirectes) - 1,245 tCO2e</div>
            <div className="pl-4 text-green-300 hover:bg-white/5 p-1 rounded cursor-pointer transition-colors">  ▼ Categorie 1 (Achats de biens et services) - 840 tCO2e</div>
            <div className="pl-8 text-yellow-300 hover:bg-white/5 p-1 rounded cursor-pointer transition-colors">    ▼ Compte 606100 (Fournitures non stockables) - 45 tCO2e</div>
            <div className="pl-12 text-gray-300 hover:bg-white/5 p-1 rounded border-l-2 border-red-500 ml-2 mt-2 bg-red-500/10">
              <span className="text-red-400">Ligne FEC : 45892</span><br/>
              Date : 12/04/2024<br/>
              EcritureLib : "ACHAT PAPIER REPRO A4"<br/>
              Debit : 1 200.00 €<br/>
              <span className="text-purple-400">→ Facteur Appliqué : Papier, carton (ADEME v23 - 0.94 kgCO2e/€)</span><br/>
              <span className="text-blue-400">→ DQR (Qualité) : 3/5</span>
            </div>
          </div>
        </div>
      </div>
    </FeaturePageLayout>
  );
};

export default AuditTrail;
