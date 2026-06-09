import React from 'react';
import StaticPageLayout from '../../components/StaticPageLayout';

const CGV: React.FC = () => {
  return (
    <StaticPageLayout 
      title="Conditions Générales (CGV / CGU)" 
      subtitle="Les conditions régissant l'utilisation de la plateforme LedgerCarbon."
    >
      <div className="bg-yellow-500/10 border-l-4 border-yellow-500 p-4 mb-8">
        <p className="m-0 text-sm">
          Ceci est une version simplifiée des Conditions Générales de Vente et d'Utilisation. La version intégrale vous sera remise lors de la signature de votre contrat ou de l'achat de vos packs de crédits.
        </p>
      </div>

      <h2>1. Objet</h2>
      <p>
        Les présentes conditions générales ont pour objet de définir les modalités de mise à disposition de la plateforme logicielle en mode SaaS "LedgerCarbon", permettant la génération automatisée de bilans carbones à partir de Fichiers des Écritures Comptables (FEC).
      </p>

      <h2>2. Modèle de Facturation (Système de Crédits)</h2>
      <p>
        LedgerCarbon ne requiert <strong>aucun abonnement mensuel contraignant</strong>. L'utilisation de la plateforme est facturée via un système de "Crédits Bilan Carbone". 
        Un (1) crédit équivaut à la génération et l'export d'un (1) rapport de bilan carbone (tous scopes confondus) pour un SIREN donné sur un exercice fiscal donné.
      </p>
      <p>
        Les crédits sont valables sans limite de durée tant que le compte utilisateur est actif. Aucun remboursement de crédits non consommés ne pourra être exigé.
      </p>

      <h2>3. Responsabilité des données (FEC)</h2>
      <p>
        Le Client (Cabinet d'Expertise Comptable ou Entreprise) certifie avoir le droit légal de téléverser le Fichier des Écritures Comptables sur la plateforme. LedgerCarbon agit uniquement en tant que sous-traitant (au sens du RGPD) fournissant une puissance de calcul et un algorithme de conversion. LedgerCarbon ne saurait être tenu responsable de la qualité ou de la véracité des écritures comptables fournies.
      </p>

      <h2>4. Exactitude du calcul carbone</h2>
      <p>
        L'algorithme de LedgerCarbon s'appuie sur la base officielle de l'ADEME pour les facteurs d'émission monétaires et physiques. Bien que nous mettions tout en œuvre pour assurer un niveau de précision maximal via notre approche hybride, le résultat généré demeure une estimation basée sur les référentiels publics.
      </p>

    </StaticPageLayout>
  );
};

export default CGV;
