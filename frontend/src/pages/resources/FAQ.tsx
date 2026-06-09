import React from 'react';
import FeaturePageLayout from '../../components/FeaturePageLayout';

const FAQ: React.FC = () => {
  return (
    <FeaturePageLayout 
      title="Centre d'Aide & FAQ" 
      subtitle="Les réponses aux questions les plus fréquentes de nos utilisateurs."
      heroBadge="💡 Support Technique"
    >
      <div className="max-w-3xl mx-auto space-y-6">
        
        <div className="bg-[var(--bg-card)] border border-[var(--border-color)] p-6 rounded-xl">
           <h3 className="text-xl font-bold mb-3 flex items-center gap-2">
             <span className="text-blue-500">Q.</span> Qu'est-ce qu'un fichier FEC ?
           </h3>
           <p className="text-[var(--text-secondary)]">
             Le Fichier des Écritures Comptables (FEC) est un standard français obligatoire depuis 2014. Il regroupe l'ensemble des écritures comptables d'une entreprise sur un exercice donné. C'est ce fichier exhaustif que nous utilisons comme base de calcul pour le bilan carbone.
           </p>
        </div>

        <div className="bg-[var(--bg-card)] border border-[var(--border-color)] p-6 rounded-xl">
           <h3 className="text-xl font-bold mb-3 flex items-center gap-2">
             <span className="text-blue-500">Q.</span> Quel est le niveau de précision du bilan carbone généré ?
           </h3>
           <p className="text-[var(--text-secondary)]">
             Le calcul est hybride. Pour l'énergie ou les déplacements, l'IA détecte les quantités physiques (Litres, kWh), offrant la précision maximale. Pour les achats généraux de services, nous utilisons des ratios monétaires issus de la Base ADEME, générant une précision estimative tout à fait recevable dans le cadre réglementaire. La marge d'erreur (Data Quality Rating) est toujours documentée.
           </p>
        </div>

        <div className="bg-[var(--bg-card)] border border-[var(--border-color)] p-6 rounded-xl">
           <h3 className="text-xl font-bold mb-3 flex items-center gap-2">
             <span className="text-blue-500">Q.</span> Combien de temps prend le traitement d'un FEC ?
           </h3>
           <p className="text-[var(--text-secondary)]">
             En moyenne, notre moteur traite 100 000 lignes comptables en moins de 30 secondes. Pour un dossier extrêmement volumineux (+1 million de lignes), le traitement asynchrone peut prendre de 2 à 5 minutes maximum.
           </p>
        </div>

        <div className="bg-[var(--bg-card)] border border-[var(--border-color)] p-6 rounded-xl">
           <h3 className="text-xl font-bold mb-3 flex items-center gap-2">
             <span className="text-blue-500">Q.</span> Sommes-nous obligés de souscrire un abonnement ?
           </h3>
           <p className="text-[var(--text-secondary)]">
             Non. LedgerCarbon fonctionne avec un système de crédits (Pay-as-you-go). Vous achetez un "pack de crédits" valables à vie. Un rapport = Un crédit. 
           </p>
        </div>

      </div>
    </FeaturePageLayout>
  );
};

export default FAQ;
