import React from 'react';
import StaticPageLayout from '../../components/StaticPageLayout';

const About: React.FC = () => {
  return (
    <StaticPageLayout 
      title="À propos de LedgerCarbon" 
      subtitle="Le moteur de calcul carbone universel qui tourne en arrière-plan de toute la comptabilité française."
    >
      <h2>Notre Mission</h2>
      <p>
        L'expertise comptable est à l'aube de sa plus grande transformation avec l'arrivée de la CSRD et de la facture électronique. 
        Pourtant, aujourd'hui, réaliser un bilan carbone pour une PME est un exercice fastidieux, manuel, et souvent facturé trop cher par des cabinets de conseil spécialisés.
      </p>
      <p>
        Notre mission est de **démocratiser la mesure de l'impact environnemental** en donnant le super-pouvoir du Bilan Carbone automatisé aux tiers de confiance absolus des entreprises : les Experts-Comptables.
      </p>

      <h2>Pourquoi le FEC ?</h2>
      <p>
        Toute entreprise française produit un Fichier des Écritures Comptables. Ce fichier contient déjà 80% des données nécessaires pour évaluer l'impact (achats de marchandises, dépenses d'énergie, déplacements professionnels, etc.).
        Plutôt que de demander aux PME de remplir de longs questionnaires, LedgerCarbon ingère la donnée financière brute et la traduit en impact carbone certifié (ADEME).
      </p>

      <h2>Nos Valeurs et notre Plan Climat</h2>
      <p>
        En tant que GreenTech, nous avons le devoir d'être irréprochables :
      </p>
      <ul>
        <li>**Hébergement bas carbone :** Nos serveurs sont localisés en France dans des datacenters alimentés par une électricité à très faible intensité carbone.</li>
        <li>**Sobriété numérique :** Notre algorithme est optimisé pour consommer le minimum de ressources de calcul (CPU/RAM) même sur des fichiers FEC de plusieurs millions de lignes.</li>
      </ul>
    </StaticPageLayout>
  );
};

export default About;
