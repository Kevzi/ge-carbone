import React from 'react';
import StaticPageLayout from '../../components/StaticPageLayout';

const Privacy: React.FC = () => {
  return (
    <StaticPageLayout 
      title="Politique de Confidentialité" 
      subtitle="Transparence totale sur la gestion de vos données personnelles (RGPD)."
    >
      <h2>Préambule</h2>
      <p>
        LedgerCarbon s'engage fermement à respecter la vie privée et à protéger les données personnelles de ses utilisateurs. Cette politique de confidentialité (mise à jour en Juin 2026) détaille la manière dont nous collectons, utilisons, et sécurisons vos données conformément au Règlement Général sur la Protection des Données (RGPD).
      </p>

      <h3>1. Données collectées</h3>
      <p>Nous collectons uniquement les données strictement nécessaires à l'utilisation du service :</p>
      <ul>
        <li><strong>Données de compte :</strong> Nom, prénom, adresse e-mail professionnelle, nom du cabinet ou de l'entreprise.</li>
        <li><strong>Données techniques de connexion :</strong> Adresses IP, logs de connexion sécurisés (conservés 1 an légalement).</li>
        <li><strong>Fichiers FEC :</strong> Traités de manière éphémère (voir page Sécurité) et jamais considérés comme des données personnelles au sens strict puisque relatifs à des entités morales (entreprises).</li>
      </ul>

      <h3>2. Finalité du traitement</h3>
      <p>Vos données personnelles sont utilisées pour :</p>
      <ul>
        <li>Vous fournir l'accès à la plateforme SaaS LedgerCarbon.</li>
        <li>Assurer le support technique et la facturation.</li>
        <li>Vous informer des évolutions réglementaires majeures (CSRD) et des mises à jour produit.</li>
      </ul>

      <h3>3. Non-revente des données</h3>
      <p>
        <strong>Nous ne vendons, ne louons, ni ne cédons jamais vos données personnelles ou financières à des tiers.</strong> Votre Fichier des Écritures Comptables ne sera jamais utilisé pour entraîner des modèles d'intelligence artificielle publics.
      </p>

      <h3>4. Vos droits (RGPD)</h3>
      <p>
        Conformément à la réglementation, vous disposez d'un droit d'accès, de rectification, d'effacement (droit à l'oubli), de limitation du traitement, et de portabilité de vos données. 
        Pour exercer ces droits, vous pouvez nous contacter à tout moment à l'adresse <code>dpo@ledgercarbon.org</code>.
      </p>

    </StaticPageLayout>
  );
};

export default Privacy;
