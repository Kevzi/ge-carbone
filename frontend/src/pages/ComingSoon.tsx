import React from 'react';
import StaticPageLayout from '../components/StaticPageLayout';
import { Link } from 'react-router-dom';

const ComingSoon: React.FC<{ pageName: string }> = ({ pageName }) => {
  return (
    <StaticPageLayout 
      title={pageName} 
      subtitle="Cette page est actuellement en cours de rédaction."
    >
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <svg className="w-20 h-20 text-blue-500 mb-6 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
        </svg>
        <h2 className="text-2xl mt-0">Bientôt disponible !</h2>
        <p className="text-[var(--text-secondary)]">
          Nous travaillons activement pour vous proposer ce contenu très prochainement.
        </p>
        <Link to="/landing" className="mt-8 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors no-underline">
          Retour à l'accueil
        </Link>
      </div>
    </StaticPageLayout>
  );
};

export default ComingSoon;
