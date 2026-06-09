import React from 'react';
import StaticPageLayout from '../../components/StaticPageLayout';

const Cookies: React.FC = () => {
  return (
    <StaticPageLayout 
      title="Politique des Cookies" 
      subtitle="Parce que nous respectons votre vie privée, voici comment nous gérons les traceurs."
    >
      <h2>Utilisation minimale des cookies</h2>
      <p>
        LedgerCarbon est une plateforme SaaS B2B. Nous n'utilisons aucun cookie publicitaire intrusif (pas de reciblage Facebook, pas de traceurs tiers obscurs).
      </p>

      <h3>1. Cookies strictement nécessaires (Techniques)</h3>
      <p>Ces cookies sont indispensables au bon fonctionnement de la plateforme. Ils ne requièrent pas votre consentement préalable :</p>
      <ul>
        <li><strong>Session d'authentification :</strong> Maintient votre connexion active lors de la navigation entre les pages.</li>
        <li><strong>Sécurité :</strong> Prévient les attaques de type CSRF (Cross-Site Request Forgery).</li>
        <li><strong>Préférences :</strong> Sauvegarde du choix de la langue et du thème (Sombre/Clair).</li>
      </ul>

      <h3>2. Cookies analytiques (Statistiques)</h3>
      <p>
        Nous utilisons des outils d'analyse respectueux de la vie privée (sans IP tracking complet) pour comprendre l'utilisation de notre moteur de calcul, dans l'unique but d'optimiser nos temps de réponse et de détecter les éventuelles erreurs système lors du traitement de gros fichiers FEC.
      </p>

      <h3>Modifier vos choix</h3>
      <p>
        Vous pouvez à tout moment révoquer votre consentement pour les cookies analytiques via le panneau de contrôle de votre navigateur ou directement depuis les paramètres de votre compte LedgerCarbon.
      </p>
    </StaticPageLayout>
  );
};

export default Cookies;
