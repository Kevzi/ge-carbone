import React from 'react';
import FeaturePageLayout from '../../components/FeaturePageLayout';

const Export: React.FC = () => {
  return (
    <FeaturePageLayout 
      title="Export Réglementaire CSRD / iXBRL" 
      subtitle="Ne générez pas seulement un PDF. Générez un rapport lisible par les machines, nativement conforme à la taxonomie européenne."
      heroBadge="🇪🇺 Conforme EFRAG & ESRS E1"
    >
      <div className="grid md:grid-cols-2 gap-16 items-center">
        <div className="order-2 md:order-1 flex justify-center">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 blur-[50px] opacity-20"></div>
            <div className="relative bg-[var(--bg-card)] border border-[var(--border-color)] p-8 rounded-2xl shadow-xl w-full max-w-md">
              <div className="flex items-center gap-4 mb-6 border-b border-[var(--border-color)] pb-4">
                 <div className="w-12 h-12 bg-green-500/20 text-green-500 rounded-lg flex items-center justify-center font-bold text-xl">XML</div>
                 <div>
                   <h4 className="font-bold">rapport_esrs_e1.xhtml</h4>
                   <p className="text-sm text-[var(--text-secondary)]">Format iXBRL (ESEF)</p>
                 </div>
              </div>
              <div className="space-y-3 font-mono text-xs text-gray-400">
                <p>&lt;esrs:ClimateChangeMitigation contextRef="ctx1"&gt;</p>
                <p className="pl-4">&lt;esrs:GrossScope1Emissions decimals="0" unitRef="tCO2e"&gt;<span className="text-[var(--text-primary)] font-bold">145</span>&lt;/esrs:GrossScope1Emissions&gt;</p>
                <p>&lt;/esrs:ClimateChangeMitigation&gt;</p>
              </div>
            </div>
          </div>
        </div>

        <div className="order-1 md:order-2">
          <h2 className="text-3xl font-bold mb-6">La norme européenne EFRAG</h2>
          <p className="text-lg text-[var(--text-secondary)] leading-relaxed mb-6">
            La directive CSRD exige que les rapports de durabilité soient publiés dans un format numérique standardisé. L'export LedgerCarbon génère un fichier conforme à la norme environnementale <strong>ESRS E1</strong>.
          </p>
          
          <h3 className="text-xl font-bold mb-3 mt-8 text-blue-400">Prouesse technologique : le format iXBRL</h3>
          <p className="text-[var(--text-secondary)] mb-6">
            LedgerCarbon intègre nativement la taxonomie XBRL de l'EFRAG (format iXBRL / ESEF). Votre rapport de durabilité est généré sous forme de page web (XHTML) balisée informatiquement, rendant les données carbone instantanément lisibles par les machines, les banques et les algorithmes des investisseurs.
          </p>

          <h3 className="text-xl font-bold mb-3 mt-8 text-purple-400">Le "Plus" PME : Standard VSME v1.2.0</h3>
          <p className="text-[var(--text-secondary)]">
            Les PME non soumises directement à la CSRD reçoivent néanmoins la pression de leurs grands donneurs d'ordres. C'est pourquoi notre outil d'export intègre également le standard allégé de durabilité volontaire (VSME v1.2.0), parfaitement calibré pour protéger les PME de la surcharge administrative.
          </p>
        </div>
      </div>
    </FeaturePageLayout>
  );
};

export default Export;
