import React, { useEffect, useState } from 'react';
import SwaggerUI from 'swagger-ui-react';
import 'swagger-ui-react/swagger-ui.css';

const ApiPortal: React.FC = () => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <main className="min-h-screen bg-bgPrimary relative overflow-hidden pb-20">
      {/* Dynamic Background Elements */}
      <div className="absolute top-0 inset-x-0 h-96 bg-gradient-to-b from-indigo-50/50 to-transparent dark:from-indigo-950/20 -z-10 pointer-events-none" />
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-blue-400/10 blur-[100px] pointer-events-none" />
      <div className="absolute top-[20%] right-[-5%] w-[30%] h-[30%] rounded-full bg-purple-400/10 blur-[120px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12">
        <header className="mb-12 text-center relative z-10 transition-all duration-700 ease-out transform translate-y-0 opacity-100"
          style={{ opacity: mounted ? 1 : 0, transform: mounted ? 'translateY(0)' : 'translateY(20px)' }}
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-sm font-medium mb-6 shadow-sm border border-blue-200/50 dark:border-blue-800/50">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
            </span>
            API REST v1.0
          </div>
          <h1 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-700 to-indigo-600 dark:from-blue-400 dark:to-indigo-300 tracking-tight drop-shadow-sm mb-4">
            Portail Développeur
          </h1>
          <p className="mt-4 text-xl text-textSecondary max-w-3xl mx-auto leading-relaxed font-light">
            Automatisez la génération de vos bilans carbone. Intégrez LedgerCarbon directement à votre ERP ou votre système d'information via notre API REST interactive.
          </p>
        </header>

        {/* Swagger Container with Premium Glassmorphism and Light Background Enforcement */}
        <section 
          className="relative group transition-all duration-700 delay-150 ease-out"
          style={{ opacity: mounted ? 1 : 0, transform: mounted ? 'translateY(0)' : 'translateY(30px)' }}
        >
          <div className="absolute -inset-1 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-[2rem] blur-lg opacity-70 group-hover:opacity-100 transition duration-500"></div>
          <div className="relative bg-white rounded-3xl shadow-2xl overflow-hidden border border-gray-100">
            {/* 
              We force light mode inside the Swagger container because swagger-ui-react 
              doesn't have a native dark mode without extensive custom CSS hacking.
              This guarantees it looks perfect and readable regardless of the app's global theme.
            */}
            <div className="p-4 sm:p-8 md:p-10 bg-white" style={{ color: 'initial' }}>
              <div className="swagger-container" style={{ minHeight: '600px' }}>
                <SwaggerUI url="http://localhost:8000/api/schema/" />
              </div>
            </div>
          </div>
        </section>
        
        <section className="mt-16 relative z-10 grid grid-cols-1 md:grid-cols-3 gap-8 text-center"
          style={{ opacity: mounted ? 1 : 0, transform: mounted ? 'translateY(0)' : 'translateY(20px)', transitionDelay: '300ms' }}
        >
          <div className="bg-white/60 dark:bg-gray-800/40 backdrop-blur-md rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50 shadow-sm hover:shadow-md transition-all">
            <div className="w-12 h-12 mx-auto bg-blue-100 dark:bg-blue-900/50 rounded-xl flex items-center justify-center mb-4 text-blue-600 dark:text-blue-400 text-xl">
              🔐
            </div>
            <h3 className="text-lg font-bold text-textPrimary mb-2">Authentification Sécurisée</h3>
            <p className="text-sm text-textSecondary">
              L'API utilise des tokens JWT (Bearer). Récupérez votre token d'accès via le endpoint <code className="bg-gray-100 dark:bg-gray-900 px-1 py-0.5 rounded text-pink-500 text-xs">/api/v1/token/</code>.
            </p>
          </div>

          <div className="bg-white/60 dark:bg-gray-800/40 backdrop-blur-md rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50 shadow-sm hover:shadow-md transition-all">
            <div className="w-12 h-12 mx-auto bg-green-100 dark:bg-green-900/50 rounded-xl flex items-center justify-center mb-4 text-green-600 dark:text-green-400 text-xl">
              ⚡
            </div>
            <h3 className="text-lg font-bold text-textPrimary mb-2">Haute Performance</h3>
            <p className="text-sm text-textSecondary">
              Traitement asynchrone des fichiers FEC volumineux via Celery. Utilisez les webhooks ou le polling pour suivre l'état de génération.
            </p>
          </div>

          <div className="bg-white/60 dark:bg-gray-800/40 backdrop-blur-md rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50 shadow-sm hover:shadow-md transition-all">
            <div className="w-12 h-12 mx-auto bg-purple-100 dark:bg-purple-900/50 rounded-xl flex items-center justify-center mb-4 text-purple-600 dark:text-purple-400 text-xl">
              📖
            </div>
            <h3 className="text-lg font-bold text-textPrimary mb-2">Documentation Interactive</h3>
            <p className="text-sm text-textSecondary">
              Testez directement les endpoints depuis cette interface en utilisant le bouton "Try it out". Les schémas JSON sont automatiquement validés.
            </p>
          </div>
        </section>
      </div>

      {/* Tweaks to adapt Swagger's raw styles to look a bit more modern inside our white container */}
      <style>{`
        .swagger-container .swagger-ui {
          font-family: inherit !important;
        }
        .swagger-container .swagger-ui .info .title {
          font-weight: 800;
          color: #1e40af; /* Tailwind blue-800 */
        }
        .swagger-container .swagger-ui .scheme-container {
          background-color: transparent;
          box-shadow: none;
          padding: 10px 0;
          border-bottom: 1px solid #e5e7eb;
          margin-bottom: 20px;
        }
        .swagger-container .swagger-ui .opblock {
          border-radius: 12px;
          border: 1px solid #e5e7eb;
          box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
          transition: all 0.2s ease;
        }
        .swagger-container .swagger-ui .opblock:hover {
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        .swagger-container .swagger-ui .opblock .opblock-summary-method {
          border-radius: 6px;
        }
        .swagger-container .swagger-ui select {
          border-radius: 6px;
          border-color: #d1d5db;
        }
        .swagger-container .swagger-ui .btn {
          border-radius: 6px;
          font-weight: 600;
          box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        }
      `}</style>
    </main>
  );
};

export default ApiPortal;
