import { useState, useEffect } from 'react'
import { api } from '../../services/api'
import { useAuth } from '../../contexts/AuthContext'
import UserSelectionModal from '../../components/UserSelectionModal'
import MLAnalyticsDashboard from '../../components/MLAnalyticsDashboard'

export default function SuperAdminDashboard() {
    const { user } = useAuth()
    const [stats, setStats] = useState<any>(null)
    const [cabinets, setCabinets] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [selectedCabinetId, setSelectedCabinetId] = useState<number | null>(null)
    const [activeTab, setActiveTab] = useState<'gestion' | 'mlops'>('gestion')

    const fetchSuperAdminData = async () => {
        try {
            setLoading(true)
            const [statsRes, cabinetsRes] = await Promise.all([
                api.get<any>('/superadmin/stats/'),
                api.get<any>('/superadmin/cabinets/')
            ])
            setStats(statsRes)
            setCabinets(Array.isArray(cabinetsRes) ? cabinetsRes : (cabinetsRes.results || []))
        } catch (err) {
            console.error('Failed to fetch super admin data', err)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchSuperAdminData()
    }, [])

    const handleImpersonate = async (userId: number) => {
        setIsModalOpen(false)
        try {
            const res = await api.post<any>('/superadmin/impersonate/', { user_id: userId })
            if (!res.access || !res.refresh) {
                alert("Erreur: L'API n'a pas retourné les tokens.")
                return
            }
            
            // Store admin tokens before overwriting
            const currentAccess = localStorage.getItem('access_token')
            const currentRefresh = localStorage.getItem('refresh_token')
            if (currentAccess && currentRefresh) {
                localStorage.setItem('admin_access_token', currentAccess)
                localStorage.setItem('admin_refresh_token', currentRefresh)
            }
            
            localStorage.setItem('access_token', res.access)
            localStorage.setItem('refresh_token', res.refresh)
            window.location.href = '/' // full reload to reset all contexts
        } catch (err) {
            alert("Erreur lors de l'impersonation")
        }
    }

    const handleAddCredits = async (cabinetId: number) => {
        const amountStr = prompt("Combien de crédits voulez-vous ajouter à ce cabinet ? (ex: 50)")
        if (!amountStr) return
        
        const amount = parseInt(amountStr)
        if (isNaN(amount) || amount <= 0) {
            alert("Veuillez entrer un montant valide supérieur à 0.")
            return
        }

        try {
            await api.post(`/superadmin/cabinets/${cabinetId}/add_credits/`, { amount })
            fetchSuperAdminData()
        } catch (err) {
            alert("Erreur lors de l'ajout de crédits")
        }
    }

    const handleCreateCabinet = async () => {
        const name = prompt("Nom du nouveau cabinet :")
        if (!name) return

        try {
            setLoading(true)
            const res = await api.post<any>('/superadmin/cabinets/create_cabinet/', { name })
            alert(`Cabinet créé avec succès !\nNom : ${res.name}\nAdmin : ${res.admin_username}\nMot de passe : password`)
            fetchSuperAdminData()
        } catch (err: any) {
            alert(`Erreur: ${err.message || "Échec de création"}`)
            setLoading(false)
        }
    }

    const handleDeleteCabinet = async (cabinetId: number, cabinetName: string) => {
        if (!confirm(`Voulez-vous vraiment supprimer le cabinet "${cabinetName}" et toutes ses données ? Cette action est IRRÉVERSIBLE.`)) return;
        
        try {
            setLoading(true)
            await api.delete(`/superadmin/cabinets/${cabinetId}/delete_cabinet/`)
            alert("Cabinet supprimé avec succès.")
            fetchSuperAdminData()
        } catch (err: any) {
            alert(`Erreur: ${err.message || "Échec de suppression"}`)
            setLoading(false)
        }
    }

    if (loading) return <div className="p-10 text-white">Chargement du God Mode...</div>

    return (
        <div className="p-8 pb-32">
            <div className="mb-8 flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
                        <span className="text-purple-500">⚡</span> God Mode
                    </h1>
                    <p className="text-gray-500 dark:text-gray-400 mt-2">
                        Bienvenue, {user?.username}. Vous avez le contrôle total.
                    </p>
                </div>
            </div>

            <div className="flex border-b border-gray-700 mb-8">
                <button
                    className={`px-4 py-2 font-medium text-sm focus:outline-none ${activeTab === 'gestion' ? 'text-purple-400 border-b-2 border-purple-400' : 'text-gray-400 hover:text-white'}`}
                    onClick={() => setActiveTab('gestion')}
                >
                    Gestion (Cabinets & KPIs)
                </button>
                <button
                    className={`px-4 py-2 font-medium text-sm focus:outline-none ${activeTab === 'mlops' ? 'text-purple-400 border-b-2 border-purple-400' : 'text-gray-400 hover:text-white'}`}
                    onClick={() => setActiveTab('mlops')}
                >
                    AI Analytics (MLOps)
                </button>
            </div>

            {activeTab === 'gestion' ? (
                <>
                    {/* KPIs */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                        <div className="bg-white/50 dark:bg-[#1A1F2E]/50 backdrop-blur-xl border border-purple-500/20 rounded-2xl p-6 shadow-lg shadow-purple-500/5">
                            <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">Santé Celery</h3>
                            <div className="flex items-baseline gap-2">
                                <span className="text-4xl font-bold text-gray-900 dark:text-white">{stats?.celery_health?.success_rate}%</span>
                                <span className="text-sm text-green-500">Success</span>
                            </div>
                            <p className="text-xs text-gray-400 mt-2">{stats?.celery_health?.completed_count} terminés / {stats?.celery_health?.failed_count} en échec</p>
                        </div>

                        <div className="bg-white/50 dark:bg-[#1A1F2E]/50 backdrop-blur-xl border border-blue-500/20 rounded-2xl p-6 shadow-lg shadow-blue-500/5">
                            <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">Crédits (Global)</h3>
                            <div className="flex items-baseline gap-2">
                                <span className="text-4xl font-bold text-gray-900 dark:text-white">{stats?.credits_total_balance}</span>
                                <span className="text-sm text-blue-500">En circulation</span>
                            </div>
                        </div>

                        <div className="bg-white/50 dark:bg-[#1A1F2E]/50 backdrop-blur-xl border border-indigo-500/20 rounded-2xl p-6 shadow-lg shadow-indigo-500/5">
                            <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">Rapports Générés</h3>
                            <div className="flex items-baseline gap-2">
                                <span className="text-4xl font-bold text-gray-900 dark:text-white">{stats?.usage?.total_reports}</span>
                                <span className="text-sm text-indigo-500">Total</span>
                            </div>
                        </div>
                    </div>

                    {/* Cabinets Table */}
                    <div className="bg-white/50 dark:bg-[#1A1F2E]/50 backdrop-blur-xl border border-gray-200 dark:border-gray-800 rounded-2xl overflow-hidden shadow-xl">
                        <div className="px-6 py-5 border-b border-gray-200 dark:border-gray-800 flex justify-between items-center">
                            <h2 className="text-lg font-bold text-gray-900 dark:text-white">Gestion des Cabinets</h2>
                            <button 
                                onClick={handleCreateCabinet}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg transition-colors"
                            >
                                + Nouveau Cabinet
                            </button>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="bg-gray-50/50 dark:bg-gray-800/30 text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">
                                        <th className="px-6 py-4 font-semibold">Cabinet</th>
                                        <th className="px-6 py-4 font-semibold">Plan</th>
                                        <th className="px-6 py-4 font-semibold text-right">Crédits</th>
                                        <th className="px-6 py-4 font-semibold text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
                                    {cabinets.map(cabinet => (
                                        <tr key={cabinet.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/20 transition-colors">
                                            <td className="px-6 py-4">
                                                <div className="text-sm font-bold text-gray-900 dark:text-white">{cabinet.name}</div>
                                                <div className="text-xs text-gray-500">{cabinet.user_count} utilisateurs</div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-700 dark:bg-blue-500/10 dark:text-blue-400">
                                                    {cabinet.plan}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <span className="text-sm font-bold text-gray-900 dark:text-white">{cabinet.credits_balance}</span>
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <button 
                                                    onClick={() => handleAddCredits(cabinet.id)}
                                                    className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-green-50 text-green-600 hover:bg-green-100 dark:bg-green-500/10 dark:text-green-400 dark:hover:bg-green-500/20 transition-colors mr-2"
                                                >
                                                    + Crédits
                                                </button>
                                                <button 
                                                    onClick={() => {
                                                        setSelectedCabinetId(cabinet.id)
                                                        setIsModalOpen(true)
                                                    }}
                                                    className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-purple-50 text-purple-600 hover:bg-purple-100 dark:bg-purple-500/10 dark:text-purple-400 dark:hover:bg-purple-500/20 transition-colors mr-2"
                                                >
                                                    Impersonate
                                                </button>
                                                <button 
                                                    onClick={() => handleDeleteCabinet(cabinet.id, cabinet.name)}
                                                    className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-red-50 text-red-600 hover:bg-red-100 dark:bg-red-500/10 dark:text-red-400 dark:hover:bg-red-500/20 transition-colors"
                                                >
                                                    Supprimer
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                    {cabinets.length === 0 && (
                                        <tr>
                                            <td colSpan={4} className="px-6 py-8 text-center text-gray-500">Aucun cabinet trouvé.</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </>
            ) : (
                <MLAnalyticsDashboard />
            )}

            <UserSelectionModal 
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSelect={handleImpersonate}
                cabinetId={selectedCabinetId}
            />
        </div>
    )
}
