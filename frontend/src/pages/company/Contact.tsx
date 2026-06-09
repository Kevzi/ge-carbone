import React from 'react';
import StaticPageLayout from '../../components/StaticPageLayout';

const Contact: React.FC = () => {
  return (
    <StaticPageLayout 
      title="Nous Contacter" 
      subtitle="Une question technique, un partenariat ou une demande de démo ? L'équipe LedgerCarbon est à votre écoute."
    >
      <div className="not-prose">
        <div className="max-w-2xl mx-auto bg-[var(--bg-card)] border border-[var(--border-color)] p-8 rounded-2xl shadow-xl">
          <form className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">Prénom & Nom</label>
                <input type="text" className="w-full bg-[var(--bg-primary)] border border-[var(--border-color)] rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500" placeholder="Jean Dupont" />
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">Cabinet ou Société</label>
                <input type="text" className="w-full bg-[var(--bg-primary)] border border-[var(--border-color)] rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500" placeholder="Cabinet XYZ" />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">Email Professionnel</label>
              <input type="email" className="w-full bg-[var(--bg-primary)] border border-[var(--border-color)] rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500" placeholder="jean@cabinet.fr" />
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">Sujet</label>
              <select className="w-full bg-[var(--bg-primary)] border border-[var(--border-color)] rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500">
                 <option>Demande de démonstration</option>
                 <option>Partenariat API / Intégration</option>
                 <option>Achat de gros volumes de crédits</option>
                 <option>Presse & Médias</option>
                 <option>Autre question</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">Votre Message</label>
              <textarea rows={4} className="w-full bg-[var(--bg-primary)] border border-[var(--border-color)] rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500" placeholder="Bonjour, je souhaite intégrer votre technologie dans mon logiciel..."></textarea>
            </div>

            <button type="button" className="w-full py-4 rounded-xl text-white font-bold text-lg hover:scale-105 transition-all" style={{ background: 'var(--gradient-primary)' }}>
              Envoyer le message
            </button>
          </form>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mt-12">
          <div className="text-center p-6">
            <h4 className="font-bold text-white mb-2">Email</h4>
            <p className="text-[var(--text-secondary)] text-sm">contact@ledgercarbon.org</p>
          </div>
          <div className="text-center p-6 border-l border-r border-[var(--border-color)]">
            <h4 className="font-bold text-white mb-2">Sécurité (DPO)</h4>
            <p className="text-[var(--text-secondary)] text-sm">security@ledgercarbon.org</p>
          </div>
          <div className="text-center p-6">
            <h4 className="font-bold text-white mb-2">Bureaux</h4>
            <p className="text-[var(--text-secondary)] text-sm">Paris, France</p>
          </div>
        </div>
      </div>
    </StaticPageLayout>
  );
};

export default Contact;
