export default function Academy() {
    return (
        <main className="page-container p-8 max-w-7xl mx-auto pb-12">
            <header className="page-header">
                <div>
                    <h1 className="text-2xl font-bold text-textPrimary">LedgerCarbon Academy</h1>
                    <p className="text-textSecondary mt-2">Documentation "Boîte de Verre" et méthodologie de calcul</p>
                </div>
            </header>

            <div className="card p-8 mt-6 leading-relaxed">
                <h2 className="text-xl font-bold mb-4 text-accentPrimary">1. Mapping PCG ➔ ADEME</h2>
                <p className="mb-4">
                    Notre moteur de calcul s'appuie sur une hiérarchie stricte pour associer une ligne d'écriture comptable (FEC) à un facteur d'émission de la Base Empreinte® de l'ADEME :
                </p>
                <ul className="list-disc pl-6 mb-6 text-textPrimary">
                    <li className="mb-2"><strong>Niveau 1 : Analyse Sémantique (NLP)</strong>. Notre intelligence artificielle éco-conçue (CamemBERTv2) analyse le libellé de l'écriture (<code>EcritureLib</code>) pour en déduire la nature exacte de la dépense. C'est la méthode la plus précise.</li>
                    <li className="mb-2"><strong>Niveau 2 : Code NAF (Sirétisation)</strong>. Si le NLP n'est pas concluant, nous croisons le Compte Auxiliaire du fournisseur avec la base Sirene de l'Insee pour récupérer son secteur d'activité (Code NAF), et nous appliquons le ratio sectoriel.</li>
                    <li className="mb-2"><strong>Niveau 3 : Plan Comptable Général (PCG)</strong>. En dernier recours, le numéro de compte (ex: 6061) permet d'affecter une catégorie générique.</li>
                </ul>

                <h2 className="text-xl font-bold mb-4 mt-8 text-accentPrimary">2. Le Score de Confiance (DQR)</h2>
                <p className="mb-4">
                    Le Data Quality Ratio (DQR) note la précision du calcul carbone de 1 (Excellent) à 5 (Médiocre). Il est crucial pour les auditeurs CSRD.
                </p>
                <div className="overflow-x-auto mb-6">
                    <table className="w-full text-left border-collapse mt-6">
                        <caption className="sr-only">Scores DQR et signification</caption>
                        <thead>
                            <tr className="border-b-2 border-borderSubtle text-textSecondary">
                                <th scope="col" className="py-2 pr-4 font-semibold">Score</th>
                                <th scope="col" className="py-2 pr-4 font-semibold">Type de Donnée</th>
                                <th scope="col" className="py-2 font-semibold">Description</th>
                            </tr>
                        </thead>
                        <tbody className="text-textPrimary">
                            <tr className="border-b border-borderSubtle">
                                <td className="py-3 font-bold text-green-500">1</td>
                                <td className="py-3">Physique primaire</td>
                                <td className="py-3">Quantité réelle mesurée (ex: 500 Litres de gazole).</td>
                            </tr>
                            <tr className="border-b border-borderSubtle">
                                <td className="py-3 font-bold text-green-400">2</td>
                                <td className="py-3">Monétaire (NLP précis)</td>
                                <td className="py-3">Facture très spécifique avec facteur physique déduit.</td>
                            </tr>
                            <tr className="border-b border-borderSubtle">
                                <td className="py-3 font-bold text-yellow-500">3</td>
                                <td className="py-3">Monétaire (NAF)</td>
                                <td className="py-3">Ratio sectoriel Insee basé sur l'activité du fournisseur.</td>
                            </tr>
                            <tr className="border-b border-borderSubtle">
                                <td className="py-3 font-bold text-orange-500">4</td>
                                <td className="py-3">Monétaire (PCG)</td>
                                <td className="py-3">Estimation globale basée sur le plan comptable.</td>
                            </tr>
                            <tr>
                                <td className="py-3 font-bold text-red-500">5</td>
                                <td className="py-3">Inconnue</td>
                                <td className="py-3">Donnée non mappable ou taux de marge d'erreur excessif.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <h2 className="text-xl font-bold mb-4 mt-8 text-accentPrimary">3. Application des Déflateurs Insee</h2>
                <p className="mb-4">
                    Les facteurs d'émission monétaires de l'ADEME (ex: kgCO2e / €) sont calculés pour une année de référence (souvent l'année de l'étude sectorielle). L'inflation fausse donc les calculs si on utilise les prix d'aujourd'hui.
                </p>
                <p className="mb-4">
                    Pour corriger ce biais, LedgerCarbon applique automatiquement les déflateurs monétaires annuels de l'Insee.
                </p>
                <div className="bg-bgTertiary p-4 rounded-lg border border-borderColor">
                    <pre className="text-sm overflow-x-auto text-textPrimary"><code>
<span className="text-textSecondary">// Formule de calcul avec correction d'inflation :</span><br/>
Empreinte = Montant_HT × (Indice_Année_Rapport / Indice_Année_Facteur) × Facteur_Monétaire
                    </code></pre>
                </div>
            </div>
        </main>
    );
}
