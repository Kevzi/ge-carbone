import React from 'react';
import StaticPageLayout from '../../components/StaticPageLayout';

const A47Format: React.FC = () => {
  return (
    <StaticPageLayout 
      title="Guide : Format FEC A47 A-1" 
      subtitle="Documentation technique sur le format d'importation requis par notre algorithme."
    >
      <h2>La norme de la DGFIP</h2>
      <p>
        Pour garantir un calcul carbone fiable, LedgerCarbon s'appuie strictement sur le standard national imposé par la Direction Générale des Finances Publiques (DGFIP) : l'Article A47 A-1 du Livre des Procédures Fiscales (LPF).
      </p>

      <h3>Les 18 colonnes obligatoires (Régime Général)</h3>
      <p>Votre fichier d'export doit comporter les colonnes suivantes dans l'ordre ou avec des en-têtes exactement similaires :</p>
      
      <div className="overflow-x-auto bg-[var(--bg-primary)] p-4 rounded-lg border border-[var(--border-color)]">
        <table className="w-full text-sm text-left">
          <thead className="text-xs text-gray-400 uppercase bg-[var(--bg-card)] border-b border-[var(--border-color)]">
            <tr>
              <th className="px-4 py-3">Code</th>
              <th className="px-4 py-3">Signification</th>
              <th className="px-4 py-3">Utilisation Carbone (IA)</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b border-[var(--border-color)]">
              <td className="px-4 py-3 font-mono">JournalCode</td>
              <td className="px-4 py-3">Code journal</td>
              <td className="px-4 py-3 text-gray-400">Filtrage (Ignorer les flux de trésorerie)</td>
            </tr>
            <tr className="border-b border-[var(--border-color)]">
              <td className="px-4 py-3 font-mono">CompteNum</td>
              <td className="px-4 py-3">Numéro de compte</td>
              <td className="px-4 py-3 text-green-400 font-bold">Essentiel : Classification PCA (Scope)</td>
            </tr>
            <tr className="border-b border-[var(--border-color)]">
              <td className="px-4 py-3 font-mono">CompteLib</td>
              <td className="px-4 py-3">Libellé de compte</td>
              <td className="px-4 py-3 text-gray-400">Désambiguïsation</td>
            </tr>
            <tr className="border-b border-[var(--border-color)]">
              <td className="px-4 py-3 font-mono text-blue-400">EcritureLib</td>
              <td className="px-4 py-3 text-blue-400 font-bold">Libellé d'écriture</td>
              <td className="px-4 py-3 text-green-400 font-bold">Le cœur du NLP (Désambiguïsation fournisseur)</td>
            </tr>
            <tr className="border-b border-[var(--border-color)]">
              <td className="px-4 py-3 font-mono">Debit / Credit</td>
              <td className="px-4 py-3">Montant</td>
              <td className="px-4 py-3 text-green-400 font-bold">Application du ratio monétaire</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h3>Encodage et Formats</h3>
      <ul>
        <li><strong>Extensions acceptées :</strong> .txt, .csv</li>
        <li><strong>Encodage :</strong> UTF-8 ou ANSI, détecté automatiquement.</li>
        <li><strong>Séparateur :</strong> Tabulation (\t), Point-virgule (;) ou Pipe (|), détecté automatiquement.</li>
        <li><strong>Volume maximum :</strong> Aucun (Architecture en streaming). Fichiers de +5 Go acceptés.</li>
      </ul>
    </StaticPageLayout>
  );
};

export default A47Format;
