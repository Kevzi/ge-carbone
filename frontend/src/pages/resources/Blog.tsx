import React from 'react';
import FeaturePageLayout from '../../components/FeaturePageLayout';
import { Link } from 'react-router-dom';

const Blog: React.FC = () => {
  return (
    <FeaturePageLayout 
      title="Blog & Actualités CSRD" 
      subtitle="Décryptez les nouvelles réglementations extra-financières et découvrez les meilleures pratiques pour votre cabinet."
    >
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
         
         <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl overflow-hidden shadow-lg group hover:border-blue-500/50 transition-colors">
            <div className="h-48 bg-gradient-to-br from-blue-900 to-slate-900 flex items-center justify-center p-6 text-center">
               <h3 className="text-xl font-bold text-white group-hover:scale-105 transition-transform">CSRD : Ce qui change pour les PME en 2026</h3>
            </div>
            <div className="p-6">
               <div className="text-sm text-blue-400 font-bold mb-2">Réglementation</div>
               <p className="text-[var(--text-secondary)] text-sm mb-4 line-clamp-3">
                 Bien que la CSRD vise en priorité les grandes entreprises, l'effet de ruissellement touche déjà les fournisseurs PME. Comment s'y préparer ?
               </p>
               <button className="text-sm font-bold text-white hover:text-blue-400">Lire l'article →</button>
            </div>
         </div>

         <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl overflow-hidden shadow-lg group hover:border-green-500/50 transition-colors">
            <div className="h-48 bg-gradient-to-br from-green-900 to-slate-900 flex items-center justify-center p-6 text-center">
               <h3 className="text-xl font-bold text-white group-hover:scale-105 transition-transform">Monétiser la mission de Bilan Carbone</h3>
            </div>
            <div className="p-6">
               <div className="text-sm text-green-400 font-bold mb-2">Business Expert-Comptable</div>
               <p className="text-[var(--text-secondary)] text-sm mb-4 line-clamp-3">
                 Pourquoi facturer au temps passé est une erreur. Découvrez comment valoriser la donnée FEC pour générer de nouvelles missions à forte marge.
               </p>
               <button className="text-sm font-bold text-white hover:text-green-400">Lire l'article →</button>
            </div>
         </div>

         <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl overflow-hidden shadow-lg group hover:border-purple-500/50 transition-colors">
            <div className="h-48 bg-gradient-to-br from-purple-900 to-slate-900 flex items-center justify-center p-6 text-center">
               <h3 className="text-xl font-bold text-white group-hover:scale-105 transition-transform">Format A47 A-1 : Comprendre la norme</h3>
            </div>
            <div className="p-6">
               <div className="text-sm text-purple-400 font-bold mb-2">Technique & IT</div>
               <p className="text-[var(--text-secondary)] text-sm mb-4 line-clamp-3">
                 Plongée technique dans l'algorithme d'ingestion LedgerCarbon : comment nous validons les 18 colonnes obligatoires du LPF.
               </p>
               <Link to="/resources/a47" className="text-sm font-bold text-white hover:text-purple-400">Lire l'article →</Link>
            </div>
         </div>

      </div>
    </FeaturePageLayout>
  );
};

export default Blog;
