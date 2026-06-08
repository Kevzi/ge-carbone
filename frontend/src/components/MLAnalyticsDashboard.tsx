import { useState, useEffect } from 'react'
import { api } from '../services/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function MLAnalyticsDashboard() {
    const [data, setData] = useState<any>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchAnalytics = async () => {
            try {
                const res = await api.get('/superadmin/analytics/ai-accuracy/')
                setData(res)
            } catch (err) {
                console.error("Erreur lors du chargement des analytics MLOps", err)
            } finally {
                setLoading(false)
            }
        }
        fetchAnalytics()
    }, [])

    if (loading) return <div className="p-10 text-white">Chargement des analytics MLOps...</div>

    if (!data) return <div className="p-10 text-white">Aucune donnée disponible.</div>

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white/50 dark:bg-[#1A1F2E]/50 backdrop-blur-xl border border-blue-500/20 rounded-2xl p-6 shadow-lg shadow-blue-500/5">
                    <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">Accuracy NLP Globale</h3>
                    <div className="flex items-baseline gap-2">
                        <span className="text-4xl font-bold text-gray-900 dark:text-white">{data.global_accuracy}%</span>
                    </div>
                    <p className="text-xs text-gray-400 mt-2">Derniers 30 jours</p>
                </div>

                <div className="bg-white/50 dark:bg-[#1A1F2E]/50 backdrop-blur-xl border border-purple-500/20 rounded-2xl p-6 shadow-lg shadow-purple-500/5">
                    <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">Volume Classifié (NLP)</h3>
                    <div className="flex items-baseline gap-2">
                        <span className="text-4xl font-bold text-gray-900 dark:text-white">{data.total_nlp_volume}</span>
                    </div>
                    <p className="text-xs text-gray-400 mt-2">Lignes de FEC traitées</p>
                </div>

                <div className="bg-white/50 dark:bg-[#1A1F2E]/50 backdrop-blur-xl border border-red-500/20 rounded-2xl p-6 shadow-lg shadow-red-500/5">
                    <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">Erreurs Véritables (Feedback)</h3>
                    <div className="flex items-baseline gap-2">
                        <span className="text-4xl font-bold text-gray-900 dark:text-white">{data.total_errors}</span>
                    </div>
                    <p className="text-xs text-gray-400 mt-2">Corrections sémantiques (DQR 3)</p>
                </div>
            </div>

            <div className="bg-white/50 dark:bg-[#1A1F2E]/50 backdrop-blur-xl border border-gray-200 dark:border-gray-800 rounded-2xl p-6 shadow-xl">
                <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Évolution de l'Accuracy (30 Jours)</h2>
                <div className="h-80 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={data.chart_data}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
                            <XAxis dataKey="date" stroke="#9CA3AF" tick={{fill: '#9CA3AF'}} />
                            <YAxis domain={[0, 100]} stroke="#9CA3AF" tick={{fill: '#9CA3AF'}} />
                            <Tooltip 
                                contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: '#F3F4F6' }}
                                itemStyle={{ color: '#60A5FA' }}
                            />
                            <Line type="monotone" dataKey="accuracy" stroke="#3B82F6" strokeWidth={3} dot={{r: 4, fill: '#3B82F6'}} activeDot={{r: 8}} name="Accuracy (%)" />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>

            <div className="bg-white/50 dark:bg-[#1A1F2E]/50 backdrop-blur-xl border border-gray-200 dark:border-gray-800 rounded-2xl overflow-hidden shadow-xl">
                <div className="px-6 py-5 border-b border-gray-200 dark:border-gray-800">
                    <h2 className="text-lg font-bold text-gray-900 dark:text-white">Top 10 des erreurs fréquentes (Pour Fine-Tuning)</h2>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-gray-50/50 dark:bg-gray-800/30 text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">
                                <th className="px-6 py-4 font-semibold">Libellé Original</th>
                                <th className="px-6 py-4 font-semibold">Catégorie Corrigée (Ground Truth)</th>
                                <th className="px-6 py-4 font-semibold text-right">Occurrences</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
                            {data.top_errors.map((error: any, idx: number) => (
                                <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-800/20 transition-colors">
                                    <td className="px-6 py-4 text-sm text-gray-900 dark:text-white font-medium">{error.original_ecriture_lib}</td>
                                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{error.corrected_category}</td>
                                    <td className="px-6 py-4 text-sm text-gray-900 dark:text-white text-right font-bold">{error.count}</td>
                                </tr>
                            ))}
                            {data.top_errors.length === 0 && (
                                <tr>
                                    <td colSpan={3} className="px-6 py-8 text-center text-gray-500">Aucune erreur recensée pour le moment.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}
