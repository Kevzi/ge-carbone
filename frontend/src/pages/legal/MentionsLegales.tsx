import React from 'react';
import StaticPageLayout from '../../components/StaticPageLayout';

const MentionsLegales: React.FC = () => {
  return (
    <StaticPageLayout 
      title="Mentions Légales" 
    >
      <h2>Éditeur du Site</h2>
      <p>
        Le site <strong>LedgerCarbon</strong> (ledgercarbon.org) est édité par :
        <br />
        <strong>Société :</strong> LedgerCarbon SAS (en cours d'immatriculation)
        <br />
        <strong>Adresse :</strong> Paris, France
        <br />
        <strong>Email :</strong> contact@ledgercarbon.org
      </p>

      <h2>Directeur de la publication</h2>
      <p>
        Le directeur de la publication est Kévin, en qualité de Fondateur de LedgerCarbon.
      </p>

      <h2>Hébergement</h2>
      <p>
        Le site et les bases de données sont hébergés par des infrastructures conformes SecNumCloud, localisées en France (AWS Paris / OVHcloud).
      </p>

      <h2>Propriété Intellectuelle</h2>
      <p>
        L'ensemble de ce site relève de la législation française et internationale sur le droit d'auteur et la propriété intellectuelle. Tous les droits de reproduction sont réservés, y compris pour les documents téléchargeables et les représentations iconographiques et photographiques.
        La reproduction de tout ou partie de ce site sur un support électronique quel qu'il soit est formellement interdite sauf autorisation expresse du directeur de la publication.
      </p>
    </StaticPageLayout>
  );
};

export default MentionsLegales;
