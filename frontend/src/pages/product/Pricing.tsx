import React from 'react';
import StaticPageLayout from '../../components/StaticPageLayout';

const Pricing: React.FC = () => {
  return (
    <StaticPageLayout 
      title="Tarifs & Packs de Crédits" 
      subtitle="Un modèle transparent, juste et sans abonnement caché, pensé pour la réalité des cabinets d'expertise comptable."
    >
      <h2>Payez uniquement pour ce que vous générez</h2>
      <p>
        Contrairement aux logiciels SaaS traditionnels qui imposent des abonnements mensuels coûteux même lorsque vous ne les utilisez pas, LedgerCarbon fonctionne avec un <strong>système de crédits prépayés</strong>.
      </p>

      <div className="flex justify-center items-center my-10">
        <div className="bg-[var(--bg-primary)] border border-[var(--border-color)] p-6 rounded-xl shadow-lg max-w-sm text-center">
          <h3 className="text-2xl font-bold mt-0">1 Crédit</h3>
          <p className="text-xl text-[var(--text-secondary)]">=</p>
          <h3 className="text-xl font-bold text-blue-400">1 Bilan Carbone (Annuel)</h3>
          <p className="text-sm mt-4 text-[var(--text-secondary)]">Export iXBRL, Tableaux de bord, Piste d'audit inclus.</p>
        </div>
      </div>

      <h2>Tarification dégressive</h2>
      <p>
        Le coût unitaire d'un crédit diminue en fonction du volume acheté par le cabinet, afin d'accompagner le déploiement de vos missions RSE :
      </p>
      <ul>
        <li><strong>Pack Découverte (1 à 5 crédits) :</strong> ~90 € H.T. / crédit</li>
        <li><strong>Pack Croissance (10 à 50 crédits) :</strong> ~70 € H.T. / crédit</li>
        <li><strong>Pack Entreprise (100+ crédits) :</strong> Jusqu'à 50 € H.T. / crédit</li>
      </ul>

      <h3>Pourquoi ce modèle est parfait pour les cabinets ?</h3>
      <p>
        Ce système de crédits vous permet de **refacturer directement** la mission à votre client avec une marge nette maîtrisée. Vous achetez un crédit 70 €, vous vendez la mission de Bilan Carbone automatisé entre 1 500 € et 3 000 € à votre client. Le retour sur investissement est immédiat et le risque financier pour le cabinet est nul.
      </p>

    </StaticPageLayout>
  );
};

export default Pricing;
