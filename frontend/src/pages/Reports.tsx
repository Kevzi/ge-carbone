import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'

interface Report {
    id: number
    fiscal_year: number
    status: string
    total_co2_kg: number | null
    created_at: string
    client_name: string
}

// DRF paginated response
interface PaginatedResponse<T> {
    count: number
    results: T[]
}

export default function Reports() {
    const [reports, setReports] = useState<Report[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [filter, setFilter] = useState<string>('all')

    useEffect(() => {
        loadReports()
    }, [])

    const loadReports = async () => {
        try {
            const response = await api.get<PaginatedResponse<Report> | Report[]>('/reports/')
            // Handle both paginated and non-paginated responses
            if (Array.isArray(response)) {
                setReports(response)
            } else if (response && 'results' in response) {
                setReports(response.results)
            } else {
                setReports([])
            }
        } catch (err) {
            console.error('Failed to load reports:', err)
            setError('Impossible de charger les rapports')
            setReports([])
        } finally {
            setLoading(false)
        }
    }

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

    const formatCO2 = (kg: number | string | null | undefined) => {
        if (kg === null || kg === undefined) return '—'
        const num = typeof kg === 'string' ? parseFloat(kg) : kg
        if (isNaN(num)) return '—'
        if (num >= 1000) {
            return `${(num / 1000).toFixed(2)} t CO₂`
        }
        return `${num.toFixed(2)} kg CO₂`
    }

    const filteredReports = reports.filter(report =>
        filter === 'all' || report.status === filter
    )

    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Chargement...</p>
            </div>
        )
    }

    return (
        <div className="reports-page">
            <header className="page-header">
                <div>
                    <h1>📋 Mes rapports</h1>
                    <p>Historique de vos bilans carbone</p>
                </div>
                <Link to="/upload" className="btn btn-primary">
                    + Nouveau rapport
                </Link>
            </header>

            {error && (
                <div className="alert alert-error">{error}</div>
            )}

            {/* Filters */}
            <div className="filters-bar">
                <div className="filter-tabs">
                    <button
                        className={`filter-tab ${filter === 'all' ? 'active' : ''}`}
                        onClick={() => setFilter('all')}
                    >
                        Tous ({reports.length})
                    </button>
                    <button
                        className={`filter-tab ${filter === 'completed' ? 'active' : ''}`}
                        onClick={() => setFilter('completed')}
                    >
                        Terminés ({reports.filter(r => r.status === 'completed').length})
                    </button>
                    <button
                        className={`filter-tab ${filter === 'processing' ? 'active' : ''}`}
                        onClick={() => setFilter('processing')}
                    >
                        En cours ({reports.filter(r => r.status === 'processing').length})
                    </button>
                </div>
            </div>

            {/* Reports List */}
            {filteredReports.length === 0 ? (
                <div className="empty-state card">
                    <div className="empty-icon">📊</div>
                    <h3>Aucun rapport</h3>
                    <p>Importez un fichier FEC pour générer votre premier bilan carbone</p>
                    <Link to="/upload" className="btn btn-primary">
                        Créer un rapport
                    </Link>
                </div>
            ) : (
                <div className="reports-grid">
                    {filteredReports.map(report => (
                        <Link
                            key={report.id}
                            to={`/reports/${report.id}`}
                            className="report-card card"
                        >
                            <div className="report-card-header">
                                <span className="report-year">{report.fiscal_year}</span>
                                {getStatusBadge(report.status)}
                            </div>

                            <div className="report-card-body">
                                <div className="report-company">{report.client_name || 'Client'}</div>

                                {report.status === 'completed' && (
                                    <div className="report-emissions">
                                        <span className="emissions-value">{formatCO2(report.total_co2_kg)}</span>
                                        <span className="emissions-label">Émissions totales</span>
                                    </div>
                                )}

                                {report.status === 'processing' && (
                                    <div className="report-processing">
                                        <div className="processing-bar"></div>
                                        <span>Analyse en cours...</span>
                                    </div>
                                )}
                            </div>

                            <div className="report-card-footer">
                                <span className="report-date">
                                    {new Date(report.created_at).toLocaleDateString('fr-FR', {
                                        day: 'numeric',
                                        month: 'long',
                                        year: 'numeric'
                                    })}
                                </span>
                                <span className="report-arrow">→</span>
                            </div>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    )
}
