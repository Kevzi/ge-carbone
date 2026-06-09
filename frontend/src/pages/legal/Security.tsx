import React from 'react';
import StaticPageLayout from '../../components/StaticPageLayout';

const Security: React.FC = () => {
  return (
    <StaticPageLayout 
      title="Sécurité & Infrastructures" 
      subtitle="La protection de vos données financières et de vos Fichiers des Écritures Comptables (FEC) est au cœur de notre architecture technique."
    >
      <h2>Nos engagements stricts sur la donnée</h2>
      <p>
        Dans le cadre de la génération automatisée de bilans carbones, LedgerCarbon est amené à traiter des données hautement sensibles. Notre posture de sécurité est conçue nativement pour les exigences des experts-comptables et directeurs financiers.
      </p>

      <h3>1. Suppression garantie des FEC sous 24h</h3>
      <p>
        <strong>Nous ne stockons pas vos écritures comptables.</strong> Les fichiers FEC uploadés sur notre plateforme sont utilisés exclusivement de manière éphémère par notre moteur de calcul algorithmique. 
        Dès la génération du rapport iXBRL / Bilan Carbone (et au maximum dans un délai de 24 heures en cas de traitement asynchrone), le fichier FEC source est <strong>définitivement et irrémédiablement supprimé</strong> de nos serveurs.
      </p>

      <h3>2. Chiffrement de bout en bout</h3>
      <ul>
        <li><strong>Données en transit :</strong> Toutes les communications entre vos navigateurs et notre API transitent via des protocoles chiffrés <code>TLS 1.3</code>.</li>
        <li><strong>Données au repos :</strong> Les métadonnées et résultats consolidés sauvegardés dans nos bases de données sont chiffrés avec la norme <code>AES-256</code>, considérée comme le standard industriel le plus robuste.</li>
      </ul>

      <h3>3. Architecture Multi-Tenant isolée</h3>
      <p>
        Pour garantir une étanchéité parfaite entre les cabinets d'expertise comptable, notre architecture s'appuie sur une isolation forte au niveau de la base de données. Chaque locataire (tenant) bénéficie de son propre schéma PostgreSQL isolé. Il est techniquement impossible pour les données d'un cabinet de "fuiter" vers l'espace d'un autre cabinet.
      </p>

      <h3>4. Hébergement Souverain et Certifications</h3>
      <p>
        LedgerCarbon est une solution 100% française. 
        Toutes nos infrastructures (serveurs de calcul, bases de données, stockages temporaires) sont hébergées physiquement en France et au sein de l'Union Européenne. 
      </p>
      <p>
        Nous collaborons avec des prestataires cloud engagés dans une démarche de certification <strong>ISO 27001</strong> et qualifiés <strong>SecNumCloud</strong> (le visa de sécurité le plus élevé délivré par l'ANSSI en France), vous garantissant une souveraineté totale face aux lois extraterritoriales (comme le Cloud Act américain).
      </p>

      <div className="bg-blue-500/10 border-l-4 border-blue-500 p-4 mt-8 rounded-r-lg">
        <p className="m-0 text-sm">
          Pour toute question technique concernant l'architecture de sécurité, l'audit de nos systèmes, ou pour obtenir notre livre blanc sécurité (NDA requis), veuillez contacter notre DPO à l'adresse <code>security@ledgercarbon.org</code>.
        </p>
      </div>
    </StaticPageLayout>
  );
};

export default Security;
