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

    // Redirection si aucun rapport
    useEffect(() => {
        if (!reportsLoading && hasNoReports && !reportsError) {
            navigate('/upload', { replace: true })
        }
    }, [hasNoReports, reportsLoading, reportsError, navigate])

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
        const statusClasses: Record<string, string> = {
            'completed': 'badge badge-success',
            'processing': 'badge badge-warning',
            'failed': 'badge badge-error',
            'pending': 'badge badge-info'
        }
        const statusLabels: Record<string, string> = {
            'completed': 'Terminé',
            'processing': 'En cours',
            'failed': 'Échec',
            'pending': 'En attente'
        }
        return (
            <span className={statusClasses[status] || 'badge'}>
                {statusLabels[status] || status}
            </span>
        )
    }

    const formatCO2 = (kg: number | string | null) => {
        if (kg === null || kg === undefined) return '—'
        const numKg = typeof kg === 'string' ? parseFloat(kg) : kg;
        if (isNaN(numKg)) return '—'
        
        if (numKg >= 1000) {
            return `${(numKg / 1000).toFixed(2)} t CO₂`
        }
        return `${numKg.toFixed(2)} kg CO₂`
    }

    if (reportsLoading || creditsLoading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Chargement...</p>
            </div>
        )
    }

    const errorMessage = typeof reportsError === 'string' ? reportsError : (reportsError ? (reportsError as any).message || 'Une erreur est survenue' : null)

    return (
        <div className="dashboard">
            <header className="page-header">
                <h1>Bonjour, {user?.username} 👋</h1>
                <p>Bienvenue sur votre tableau de bord LedgerCarbon</p>
            </header>

            {errorMessage && (
                <div className="alert alert-error mb-6 flex justify-between items-center">
                    <span><strong>Erreur :</strong> {errorMessage}</span>
                    <button onClick={refreshReports} className="btn btn-secondary btn-sm">Réessayer</button>
                </div>
            )}

            <div className="dashboard-grid">
                {/* Stats Cards */}
                <div className="stats-row">
                    <div className="stat-card">
                        <div className="stat-icon">📊</div>
                        <div className="stat-content">
                            <span className="stat-value">{recentReports.length}</span>
                            <span className="stat-label">Rapports générés</span>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon">💳</div>
                        <div className="stat-content">
                            <span className="stat-value">{creditBalance?.balance || 0}</span>
                            <span className="stat-label">Crédits disponibles</span>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon">🌱</div>
                        <div className="stat-content">
                            <span className="stat-value">
                                {recentReports.length > 0 && recentReports[0].total_co2_kg
                                    ? formatCO2(recentReports[0].total_co2_kg)
                                    : '—'}
                            </span>
                            <span className="stat-label">Dernier bilan</span>
                        </div>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="card">
                    <h2>Actions rapides</h2>
                    <div className="quick-actions">
                        <Link to="/upload" className="action-card">
                            <span className="action-icon">📤</span>
                            <span className="action-title">Nouveau rapport</span>
                            <span className="action-desc">Importer un fichier FEC</span>
                        </Link>
                        <Link to="/reports" className="action-card">
                            <span className="action-icon">📋</span>
                            <span className="action-title">Mes rapports</span>
                            <span className="action-desc">Voir l'historique</span>
                        </Link>
                        <Link to="/credits" className="action-card">
                            <span className="action-icon">💳</span>
                            <span className="action-title">Acheter des crédits</span>
                            <span className="action-desc">Recharger votre compte</span>
                        </Link>
                    </div>
                </div>

                {/* Recent Reports */}
                <div className="card">
                    <div className="card-header">
                        <h2>Rapports récents</h2>
                        <Link to="/reports" className="btn btn-secondary btn-sm">
                            Voir tout
                        </Link>
                    </div>

                    {recentReports.length === 0 ? (
                        <div className="empty-state">
                            <div className="empty-icon" style={{ fontSize: '3rem', marginBottom: '1rem' }}>🌱</div>
                            <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '8px', color: 'var(--text-main)' }}>Prêt à mesurer votre impact ?</h3>
                            <p style={{ color: 'var(--text-muted)', marginBottom: '24px', maxWidth: '400px', margin: '0 auto 24px auto' }}>
                                Commencez votre parcours carbone. Importez votre premier fichier FEC (Grand Livre) pour générer instantanément votre bilan CSRD conforme à la taxonomie EFRAG.
                            </p>
                            <Link to="/upload" className="btn btn-primary">
                                <span style={{ marginRight: '8px' }}>📤</span> Créer mon premier rapport
                            </Link>
                        </div>
                    ) : (
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Exercice</th>
                                    <th>Statut</th>
                                    <th>Émissions</th>
                                    <th>Date</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {recentReports.map(report => (
                                    <tr key={report.id}>
                                        <td>
                                            <Link to={`/reports/${report.id}`}>
                                                {report.fiscal_year}
                                            </Link>
                                        </td>
                                        <td>{getStatusBadge(report.status)}</td>
                                        <td>{formatCO2(report.total_co2_kg)}</td>
                                        <td>{new Date(report.created_at).toLocaleDateString('fr-FR')}</td>
                                        <td>
                                            <button 
                                                onClick={() => setReportToDelete(report)}
                                                className="text-red-500 hover:text-red-700 font-bold"
                                                title="Supprimer le rapport"
                                            >
                                                ✕
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>

            <ConfirmModal 
                isOpen={reportToDelete !== null}
                title="Supprimer le rapport"
                message={`Êtes-vous sûr de vouloir supprimer le rapport pour l'exercice ${reportToDelete?.fiscal_year} ? Cette action est irréversible et supprimera toutes les données associées.`}
                confirmLabel="Supprimer définitivement"
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
