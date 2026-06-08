import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useReports } from '../contexts/ReportsContext'
import { api } from '../services/api'
import ConfirmModal from '../components/ConfirmModal'

interface Report {
    id: number
    fiscal_year: string
    status: string
    total_co2_kg: number | null
    created_at: string
    client_name?: string
    average_dqr?: string | number
}

interface CreditBalance {
    balance: number
    monthly_usage: number
}

export default function Dashboard() {
    const { user } = useAuth()
    const { reports, hasNoReports, loading: reportsLoading, error: reportsError, refreshReports } = useReports()
    const navigate = useNavigate()
    
    const [creditBalance, setCreditBalance] = useState<CreditBalance | null>(null)
    const [creditsLoading, setCreditsLoading] = useState(true)
    const [reportToDelete, setReportToDelete] = useState<Report | null>(null)

    useEffect(() => {
        loadCreditsData()
    }, [])

    const loadCreditsData = async () => {
        try {
            const credits = await api.get<CreditBalance>('/credits/balance/')
            setCreditBalance(credits)
        } catch {
            console.log('Credits API not available')
        } finally {
            setCreditsLoading(false)
        }
    }

    const recentReports = reports.slice(0, 5)

    const getStatusBadge = (status: string) => {
        const statusConfig: Record<string, { bg: string, text: string, label: string, icon: string, border: string }> = {
            'completed': { bg: 'bg-emerald-500/10', text: 'text-emerald-500', border: 'border-emerald-500/20', label: 'Terminé', icon: '✓' },
            'processing': { bg: 'bg-amber-500/10', text: 'text-amber-500', border: 'border-amber-500/20', label: 'En cours', icon: '⏳' },
            'failed': { bg: 'bg-red-500/10', text: 'text-red-500', border: 'border-red-500/20', label: 'Échec', icon: '✕' },
            'pending': { bg: 'bg-blue-500/10', text: 'text-blue-500', border: 'border-blue-500/20', label: 'En attente', icon: '🕒' }
        }
        const conf = statusConfig[status] || { bg: 'bg-gray-500/10', text: 'text-gray-500', border: 'border-gray-500/20', label: status, icon: '•' }
        return (
            <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium border ${conf.bg} ${conf.text} ${conf.border}`}>
                <span>{conf.icon}</span>
                {conf.label}
            </span>
        )
    }

    const getDQRColor = (dqr: number) => {
        if (dqr <= 2.0) return 'text-emerald-500'
        if (dqr <= 3.0) return 'text-amber-500'
        return 'text-red-500'
    }

    const formatCO2 = (kg: number | string | null) => {
        if (kg === null || kg === undefined) return '—'
        const numKg = typeof kg === 'string' ? parseFloat(kg) : kg;
        if (isNaN(numKg)) return '—'
        if (numKg >= 1000) {
            return `${(numKg / 1000).toLocaleString('fr-FR', { maximumFractionDigits: 2 })} t`
        }
        return `${numKg.toLocaleString('fr-FR', { maximumFractionDigits: 0 })} kg`
    }

    if (reportsLoading || creditsLoading) {
        return (
            <div className="min-h-full flex flex-col items-center justify-center p-8">
                <div className="w-12 h-12 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin mb-4"></div>
                <p className="text-gray-500 dark:text-gray-400 font-medium">Chargement de votre espace...</p>
            </div>
        )
    }

    const errorMessage = typeof reportsError === 'string' ? reportsError : (reportsError ? (reportsError as any).message || 'Une erreur est survenue' : null)

    return (
        <div className="min-h-full p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
            {/* Header */}
            <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
                        Bonjour, {user?.username} 👋
                    </h1>
                    <p className="text-gray-500 dark:text-gray-400 mt-1">
                        Voici un aperçu de vos bilans carbone et de votre activité
                    </p>
                </div>
                <div className="flex gap-3">
                    <Link to="/upload" className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium shadow-lg shadow-blue-500/25 transition-all hover:-translate-y-0.5">
                        <span className="text-xl">📤</span> Nouveau Rapport
                    </Link>
                </div>
            </header>

            {errorMessage && (
                <div className="p-4 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 flex justify-between items-center text-red-600 dark:text-red-400">
                    <div className="flex items-center gap-3">
                        <span>⚠️</span>
                        <span><strong>Erreur de synchronisation :</strong> {errorMessage}</span>
                    </div>
                    <button onClick={refreshReports} className="px-4 py-2 bg-red-100 dark:bg-red-500/20 rounded-lg hover:bg-red-200 dark:hover:bg-red-500/30 transition-colors font-medium">
                        Réessayer
                    </button>
                </div>
            )}

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white dark:bg-[#151b2b] p-6 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-sm relative overflow-hidden group hover:shadow-md transition-all">
                    <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-blue-500/10 rounded-full blur-2xl group-hover:bg-blue-500/20 transition-all"></div>
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-blue-50 dark:bg-blue-500/10 flex items-center justify-center text-2xl text-blue-500">📊</div>
                        <div>
                            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Rapports générés</p>
                            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{reports.length}</h3>
                        </div>
                    </div>
                </div>

                <div className="bg-white dark:bg-[#151b2b] p-6 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-sm relative overflow-hidden group hover:shadow-md transition-all">
                    <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-amber-500/10 rounded-full blur-2xl group-hover:bg-amber-500/20 transition-all"></div>
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-amber-50 dark:bg-amber-500/10 flex items-center justify-center text-2xl text-amber-500">🪙</div>
                        <div className="flex-1">
                            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">LedgerCoins</p>
                            <div className="flex items-end justify-between mt-1">
                                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{creditBalance?.balance || 0}</h3>
                                <Link to="/credits" className="text-sm font-medium text-amber-600 dark:text-amber-500 hover:underline">Recharger</Link>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="bg-white dark:bg-[#151b2b] p-6 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-sm relative overflow-hidden group hover:shadow-md transition-all">
                    <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-emerald-500/10 rounded-full blur-2xl group-hover:bg-emerald-500/20 transition-all"></div>
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-emerald-50 dark:bg-emerald-500/10 flex items-center justify-center text-2xl text-emerald-500">🌱</div>
                        <div>
                            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Dernier bilan CO₂</p>
                            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                                {recentReports.length > 0 && recentReports[0].total_co2_kg
                                    ? formatCO2(recentReports[0].total_co2_kg)
                                    : '—'}
                            </h3>
                        </div>
                    </div>
                </div>
            </div>

            {/* Rapports Récents */}
            <div className="bg-white dark:bg-[#151b2b] border border-gray-100 dark:border-gray-800 rounded-2xl shadow-sm overflow-hidden">
                <div className="px-6 py-5 border-b border-gray-100 dark:border-gray-800 flex justify-between items-center">
                    <h2 className="text-lg font-bold text-gray-900 dark:text-white">Rapports Récents</h2>
                    <Link to="/reports" className="text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300">
                        Voir l'historique complet →
                    </Link>
                </div>
                
                {recentReports.length === 0 ? (
                    <div className="p-12 text-center flex flex-col items-center">
                        <div className="w-20 h-20 rounded-full bg-blue-50 dark:bg-blue-500/10 flex items-center justify-center text-4xl mb-4">
                            🌱
                        </div>
                        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Prêt à mesurer votre impact ?</h3>
                        <p className="text-gray-500 dark:text-gray-400 max-w-md mb-6">
                            Importez votre premier fichier FEC pour générer instantanément un bilan conforme à la taxonomie EFRAG.
                        </p>
                        <Link to="/upload" className="btn btn-primary shadow-lg shadow-blue-500/25">
                            Créer mon premier rapport
                        </Link>
                    </div>
                ) : (
                    <div className="divide-y divide-gray-100 dark:divide-gray-800/60">
                        {recentReports.map(report => (
                            <div key={report.id} className="p-6 hover:bg-gray-50 dark:hover:bg-white/[0.02] transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-4 group">
                                <div className="flex items-center gap-5">
                                    <div className="w-12 h-12 rounded-xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center font-bold text-gray-500 dark:text-gray-400 group-hover:bg-blue-50 dark:group-hover:bg-blue-500/20 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                                        {report.fiscal_year}
                                    </div>
                                    <div>
                                        <Link to={`/reports/${report.id}`} className="text-lg font-semibold text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                                            {report.client_name || `Bilan ${report.fiscal_year}`}
                                        </Link>
                                        <div className="flex flex-wrap items-center gap-3 mt-1 text-sm">
                                            <span className="text-gray-500 dark:text-gray-400">
                                                {new Date(report.created_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}
                                            </span>
                                            {report.average_dqr && (
                                                <>
                                                    <span className="text-gray-300 dark:text-gray-600">•</span>
                                                    <span className="flex items-center gap-1 font-medium">
                                                        DQR: <span className={getDQRColor(Number(report.average_dqr))}>{Number(report.average_dqr).toFixed(2)}</span>
                                                    </span>
                                                </>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center gap-6 sm:justify-end">
                                    <div className="flex flex-col sm:items-end">
                                        <span className="text-sm text-gray-500 dark:text-gray-400">Émissions Totales</span>
                                        <span className="font-bold text-gray-900 dark:text-white">{formatCO2(report.total_co2_kg)}</span>
                                    </div>
                                    
                                    <div className="min-w-[120px] flex justify-end">
                                        {getStatusBadge(report.status)}
                                    </div>

                                    <div className="flex items-center gap-2">
                                        <Link to={`/reports/${report.id}`} className="p-2 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-500/10 transition-colors" title="Voir les détails">
                                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                                            </svg>
                                        </Link>
                                        <button 
                                            onClick={() => setReportToDelete(report)}
                                            className="p-2 text-gray-400 hover:text-red-600 dark:hover:text-red-400 rounded-lg hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors opacity-0 group-hover:opacity-100"
                                            title="Supprimer le rapport"
                                        >
                                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                                <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <ConfirmModal 
                isOpen={reportToDelete !== null}
                title="Supprimer le rapport"
                message={`Êtes-vous sûr de vouloir supprimer définitivement le rapport "${reportToDelete?.client_name || reportToDelete?.fiscal_year}" ? Cette action est irréversible.`}
                confirmLabel="Supprimer"
                onConfirm={async () => {
                    if (!reportToDelete) return;
                    try {
                        await api.delete(`/reports/${reportToDelete.id}/`);
                        refreshReports();
                    } catch (e) {
                        alert('Erreur lors de la suppression.');
                    } finally {
                        setReportToDelete(null);
                    }
                }}
                onCancel={() => setReportToDelete(null)}
            />
        </div>
    )
}
