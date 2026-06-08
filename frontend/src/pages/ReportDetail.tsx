import { useState, useEffect, useCallback } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { api, API_BASE_URL } from '../services/api'
import { useReports } from '../contexts/ReportsContext'
import TopEmittersDashboard from '../components/TopEmittersDashboard'
import DrillDownModal from '../components/DrillDownModal'
import MaterialityAssessmentForm from '../components/MaterialityAssessmentForm'
import MaterialityMatrix from '../components/MaterialityMatrix'
import ConfirmModal from '../components/ConfirmModal'
import Tooltip from '../components/Tooltip'

interface Report {
    id: number
    fiscal_year: number
    client_name: string
    client_siret: string
    status: string
    progress_percent: number
    error_message: string
    total_co2_kg: string | number | null
    scope1_co2_kg: string | number | null
    scope2_co2_kg: string | number | null
    scope3_co2_kg: string | number | null
    average_dqr: string | number | null
    created_at: string
    completed_at: string | null
    category_breakdown?: { category: string; scope: number; co2: number }[]
    xbrl_validation_passed?: boolean
}

interface AuditEntry {
    id: number
    action: string
    user_name: string | null
    details: Record<string, unknown>
    created_at: string
}

const downloadFile = async (url: string, defaultFilename: string) => {
    try {
        const token = localStorage.getItem('access_token')
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`)
        }
        
        let filename = defaultFilename
        const contentDisposition = response.headers.get('Content-Disposition')
        if (contentDisposition && contentDisposition.includes('filename=')) {
            const match = contentDisposition.match(/filename="?([^"]+)"?/)
            if (match && match[1]) {
                filename = match[1]
            }
        }
        
        const blob = await response.blob()
        const objectUrl = window.URL.createObjectURL(blob)
        try {
            const a = document.createElement('a')
            a.href = objectUrl
            a.download = filename
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)
        } finally {
            window.URL.revokeObjectURL(objectUrl)
        }
    } catch (err) {
        console.error('Erreur de téléchargement:', err)
        throw err
    }
}

export default function ReportDetail() {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    if (!id) return <div>ID du rapport introuvable</div>
    const [report, setReport] = useState<Report | null>(null)
    const [auditTrail, setAuditTrail] = useState<AuditEntry[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [activeTab, setActiveTab] = useState<'summary' | 'audit' | 'top-emitters' | 'materiality'>('summary')
    const [drillDownModalOpen, setDrillDownModalOpen] = useState(false)
    const [drillDownFilter, setDrillDownFilter] = useState<{ scope?: number; category?: string } | undefined>()
    const [showDeleteModal, setShowDeleteModal] = useState(false)
    const [isGeneratingIXBRL, setIsGeneratingIXBRL] = useState(false)
    const [ixbrlMessage, setIxbrlMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null)

    const { reports } = useReports()

    useEffect(() => {
        if (id) {
            loadReport()
        }
    }, [id])

    const ctxReport = reports.find(r => r.id === Number(id))
    const displayStatus = ctxReport ? ctxReport.status : report?.status
    const displayProgress = ctxReport ? ctxReport.progress_percent : report?.progress_percent

    useEffect(() => {
        let interval: ReturnType<typeof setInterval>;
        const currentStatus = ctxReport?.status || report?.status;
        
        // If status changed from processing to completed in context, reload to get latest data
        if (ctxReport?.status === 'completed' && report?.status === 'processing') {
            loadReport()
            if (ixbrlMessage?.type === 'info') {
                setIxbrlMessage({ type: 'success', text: '✅ Génération et validation iXBRL terminées avec succès !' })
            }
        }
        
        // If we are generating ixbrl (status processing but not yet in context), or if report is processing, poll
        if (currentStatus === 'processing' || currentStatus === 'pending') {
            interval = setInterval(() => {
                loadReport()
                refreshReports() // Also sync context
            }, 3000)
        }
        
        return () => {
            if (interval) clearInterval(interval)
        }
    }, [ctxReport?.status, report?.status, loadReport, refreshReports])

    const loadReport = useCallback(async () => {
        setError('')
        setLoading(true)
        try {
            const reportData = await api.get<Report>(`/reports/${id}/`)
            setReport(reportData)

            // Try to load audit trail
            try {
                const auditResponse = await api.get<AuditEntry[] | { results: AuditEntry[] }>(`/reports/${id}/audit-trail/`)
                if (Array.isArray(auditResponse)) {
                    setAuditTrail(auditResponse)
                } else if (auditResponse && 'results' in auditResponse) {
                    setAuditTrail(auditResponse.results)
                }
            } catch {
                // Audit trail not critical
            }
        } catch (err) {
            console.error('Failed to load report:', err)
            setError('Impossible de charger le rapport')
        } finally {
            setLoading(false)
        }
    }, [id])

    const formatCO2 = (kg: number | string | null) => {
        if (kg === null || kg === undefined) return '0 kg'
        const num = typeof kg === 'string' ? parseFloat(kg) : kg;
        if (isNaN(num)) return '0 kg'
        if (num >= 1000) {
            return `${(num / 1000).toFixed(2)} t`
        }
        return `${num.toFixed(2)} kg`
    }

    const getStatusBadge = (status: string) => {
        const config: Record<string, { class: string; label: string }> = {
            'completed': { class: 'badge badge-success', label: 'Terminé' },
            'processing': { class: 'badge badge-warning', label: 'En cours' },
            'failed': { class: 'badge badge-error', label: 'Échec' },
            'pending': { class: 'badge badge-info', label: 'En attente' }
        }
        const c = config[status] || { class: 'badge', label: status }
        return <span className={c.class}>{c.label}</span>
    }

    const getActionLabel = (action: string) => {
        const labels: Record<string, string> = {
            'created': '📝 Rapport créé',
            'processing_started': '⚙️ Traitement démarré',
            'processing_completed': '✅ Traitement terminé',
            'processing_failed': '❌ Traitement échoué',
            'pdf_generated': '📄 PDF généré',
            'pdf_downloaded': '📥 PDF téléchargé'
        }
        return labels[action] || action
    }

    const openDrillDown = (scope?: number, category?: string) => {
        setDrillDownFilter({ scope, category })
        setDrillDownModalOpen(true)
    }

    const confirmDelete = async () => {
        try {
            await api.delete(`/reports/${id}/`);
            navigate('/reports');
        } catch (err) {
            console.error('Failed to delete report:', err);
            alert('Erreur lors de la suppression.');
        }
    }

    const generateIXBRL = async () => {
        try {
            setIsGeneratingIXBRL(true)
            setIxbrlMessage(null)
            await api.post(`/reports/${id}/ixbrl/`)
            setIxbrlMessage({ type: 'info', text: 'La génération et la validation iXBRL ESEF ont été lancées. Veuillez patienter...' })
            // Optimistically update status to trigger polling
            setReport(prev => prev ? { ...prev, status: 'processing' } : prev)
        } catch (err: any) {
            setIxbrlMessage({ type: 'error', text: 'Erreur lors de la génération iXBRL : ' + (err.message || 'Erreur inconnue') })
        } finally {
            setIsGeneratingIXBRL(false)
        }
    }

    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Chargement du rapport...</p>
            </div>
        )
    }

    if (error || !report) {
        return (
            <div className="alert alert-error m-4">
                {error || 'Rapport introuvable'}
            </div>
        )
    }

    return (
        <div className="report-detail">
            <header className="page-header flex justify-between items-start">
                <div>
                    <Link to="/reports" className="back-link">← Retour</Link>
                    <h1>Bilan carbone {report.fiscal_year}</h1>
                    <div className="report-meta">
                        <span>{report.client_name || 'Client'}</span>
                        {getStatusBadge(displayStatus || report.status)}
                    </div>
                </div>
                <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', justifyContent: 'flex-end', alignItems: 'center' }}>
                    {report.status === 'completed' && (
                        <>
                            <button
                                className="btn btn-secondary"
                                onClick={() => {
                                    const safeName = (report?.client_name || 'client').replace(/[^a-z0-9_-]/gi, '_')
                                    downloadFile(`${API_BASE_URL}/reports/${id}/export-csv/`, `piste_audit_${safeName}_${report?.fiscal_year}.csv`)
                                        .catch(() => setIxbrlMessage({ type: 'error', text: "Erreur lors du téléchargement de la piste d'audit" }))
                                }}
                            >
                                📊 Exporter Piste d'Audit (CSV)
                            </button>
                            <button
                                className="btn btn-primary"
                                onClick={() => {
                                    downloadFile(`${API_BASE_URL}/reports/${id}/pdf/`, `bilan-carbone-${report?.fiscal_year}.pdf`)
                                        .catch(() => setIxbrlMessage({ type: 'error', text: 'Erreur lors du téléchargement du PDF' }))
                                }}
                            >
                                📥 Télécharger PDF
                            </button>
                            {report.xbrl_validation_passed !== undefined && report.xbrl_validation_passed !== null ? (
                                <div className="flex flex-col items-center gap-2">
                                    <button
                                        className="btn btn-primary"
                                        onClick={() => {
                                            const safeName = (report?.client_name || 'client').replace(/[^a-z0-9_-]/gi, '_')
                                            downloadFile(`${API_BASE_URL}/reports/${id}/ixbrl/`, `esef-report-${safeName}-${report?.fiscal_year}.html`)
                                                .catch(() => setIxbrlMessage({ type: 'error', text: 'Erreur lors du téléchargement iXBRL' }))
                                        }}
                                        style={{ backgroundColor: '#10b981', color: 'white', borderColor: '#10b981' }}
                                    >
                                        📥 Télécharger iXBRL
                                    </button>
                                    {!report.xbrl_validation_passed && (
                                        <span className="text-xs text-orange-500 text-center max-w-[200px]">
                                            ⚠️ Le fichier a été généré mais contient des erreurs de validation Arelle.
                                        </span>
                                    )}
                                </div>
                            ) : (
                                <button
                                    className="btn btn-secondary"
                                    onClick={generateIXBRL}
                                    disabled={isGeneratingIXBRL}
                                >
                                    {isGeneratingIXBRL ? '⏳ Génération iXBRL ESEF...' : '⚙️ Générer iXBRL ESEF'}
                                </button>
                            )}
                        </>
                    )}
                    {displayStatus !== 'processing' && displayStatus !== 'pending' && (
                        <button 
                            className="btn btn-danger"
                            onClick={() => setShowDeleteModal(true)}
                        >
                            🗑️ Supprimer
                        </button>
                    )}
                </div>
            </header>

            {ixbrlMessage && (
                <div className={`alert alert-${ixbrlMessage.type === 'error' ? 'error' : 'info'}`} style={{ marginBottom: '24px' }}>
                    {ixbrlMessage.text}
                </div>
            )}

            {/* Processing Status */}
            {displayStatus === 'processing' && (
                <div className="card" style={{ marginBottom: '24px', padding: '24px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                        <span className="spinner"></span>
                        <span>Analyse en cours...</span>
                    </div>
                    <div style={{ background: 'var(--bg-tertiary)', borderRadius: '8px', height: '8px', overflow: 'hidden' }}>
                        <div
                            style={{
                                background: 'var(--accent-primary)',
                                height: '100%',
                                width: `${displayProgress || 0}%`,
                                transition: 'width 0.3s ease'
                            }}
                        />
                    </div>
                    <p style={{ marginTop: '8px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                        {displayProgress || 0}% complété
                    </p>
                </div>
            )}

            {/* Error Status */}
            {displayStatus === 'failed' && (
                <div className="alert alert-error" style={{ marginBottom: '24px' }}>
                    <strong>Erreur :</strong> {report.error_message || 'Une erreur est survenue'}
                </div>
            )}

            {/* Contenu affiché uniquement quand le traitement est terminé */}
            {displayStatus === 'completed' && (
                <>
                    {/* Scopes Summary */}
                    <div className="scopes-grid">
                        <div 
                            className="scope-card scope-1 cursor-pointer hover:shadow-lg transition-shadow border border-transparent hover:border-gray-300"
                            onClick={() => openDrillDown(1)}
                        >
                            <div className="scope-header">
                                <Tooltip content="Émissions directes provenant de sources détenues ou contrôlées (ex: véhicules de l'entreprise, chaudières).">
                                    <span className="scope-badge cursor-help">Scope 1</span>
                                </Tooltip>
                                <span className="scope-title">Émissions directes</span>
                            </div>
                            <div className="scope-value">{formatCO2(report.scope1_co2_kg)}</div>
                            <div className="scope-desc">Combustibles, véhicules <span className="text-xs text-blue-500 float-right" style={{cursor: 'pointer'}} onClick={() => openDrillDown(1)}>🔍 Détails</span></div>
                        </div>

                        <div 
                            className="scope-card scope-2 cursor-pointer hover:shadow-lg transition-shadow border border-transparent hover:border-gray-300"
                            onClick={() => openDrillDown(2)}
                        >
                            <div className="scope-header">
                                <Tooltip content="Émissions indirectes liées à la consommation d'électricité, de chaleur ou de vapeur achetée.">
                                    <span className="scope-badge cursor-help">Scope 2</span>
                                </Tooltip>
                                <span className="scope-title">Énergie indirecte</span>
                            </div>
                            <div className="scope-value">{formatCO2(report.scope2_co2_kg)}</div>
                            <div className="scope-desc">Électricité, chauffage <span className="text-xs text-blue-500 float-right" style={{cursor: 'pointer'}} onClick={() => openDrillDown(2)}>🔍 Détails</span></div>
                        </div>

                        <div 
                            className="scope-card scope-3 cursor-pointer hover:shadow-lg transition-shadow border border-transparent hover:border-gray-300"
                            onClick={() => openDrillDown(3)}
                        >
                            <div className="scope-header">
                                <Tooltip content="Autres émissions indirectes (ex: achats de biens/services, déplacements professionnels, déchets).">
                                    <span className="scope-badge cursor-help">Scope 3</span>
                                </Tooltip>
                                <span className="scope-title">Autres indirectes</span>
                            </div>
                            <div className="scope-value">{formatCO2(report.scope3_co2_kg)}</div>
                            <div className="scope-desc">Achats, déplacements <span className="text-xs text-blue-500 float-right" style={{cursor: 'pointer'}} onClick={() => openDrillDown(3)}>🔍 Détails</span></div>
                        </div>

                        <div className="scope-card scope-total">
                            <div className="scope-header">
                                <span className="scope-badge">Total</span>
                                <span className="scope-title">Émissions totales</span>
                            </div>
                            <div className="scope-value">{formatCO2(report.total_co2_kg)}</div>
                            <div className="scope-desc">CO₂ équivalent</div>
                        </div>
                    </div>

                    {report.category_breakdown && report.category_breakdown.length > 0 && (
                        <div className="card" style={{ marginBottom: '24px', padding: '24px' }}>
                            <h3 style={{ marginBottom: '16px', fontSize: '1.1rem' }}>Répartition par catégorie</h3>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
                                {report.category_breakdown.map((cat, idx) => (
                                    <div 
                                        key={idx} 
                                        className={`category-chip scope-${cat.scope} cursor-pointer hover:shadow-md transition-shadow border border-gray-200 rounded-lg p-3`}
                                        onClick={() => openDrillDown(cat.scope, cat.category)}
                                        style={{ display: 'flex', flexDirection: 'column', minWidth: '150px', background: 'var(--bg-secondary)' }}
                                    >
                                        <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '4px' }}>Scope {cat.scope}</span>
                                        <span style={{ fontSize: '0.95rem', fontWeight: 500, marginBottom: '4px' }}>{cat.category}</span>
                                        <span style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--accent-primary)' }}>{formatCO2(cat.co2)}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Tabs */}
                    <div className="tabs">
                        <button
                            className={`tab ${activeTab === 'summary' ? 'active' : ''}`}
                            onClick={() => setActiveTab('summary')}
                        >
                            📊 Informations
                        </button>
                        <button
                            className={`tab ${activeTab === 'top-emitters' ? 'active' : ''}`}
                            onClick={() => setActiveTab('top-emitters')}
                        >
                            🔝 Top Émetteurs
                        </button>
                        <button
                            className={`tab ${activeTab === 'audit' ? 'active' : ''}`}
                            onClick={() => setActiveTab('audit')}
                        >
                            📝 Historique
                        </button>
                        <button
                            className={`tab ${activeTab === 'materiality' ? 'active' : ''}`}
                            onClick={() => setActiveTab('materiality')}
                        >
                            🔍 Double Matérialité
                        </button>
                    </div>

                    {/* Tab Content */}
                    <div className="tab-content card">
                        {activeTab === 'summary' && (
                            <div className="summary-content">
                                <h3>Informations du rapport</h3>
                                <div className="info-grid">
                                    <div className="info-item">
                                        <span className="info-label">Client</span>
                                        <span className="info-value">{report.client_name}</span>
                                    </div>
                                    <div className="info-item">
                                        <span className="info-label">SIRET</span>
                                        <span className="info-value">{report.client_siret || '—'}</span>
                                    </div>
                                    <div className="info-item">
                                        <span className="info-label">Exercice fiscal</span>
                                        <span className="info-value">{report.fiscal_year}</span>
                                    </div>
                                    <div className="info-item">
                                        <span className="info-label">Statut</span>
                                        <span className="info-value">{getStatusBadge(displayStatus || report.status)}</span>
                                    </div>
                                    <div className="info-item">
                                        <span className="info-label">Créé le</span>
                                        <span className="info-value">
                                            {new Date(report.created_at).toLocaleString('fr-FR')}
                                        </span>
                                    </div>
                                    <div className="info-item">
                                        <span className="info-label">
                                            <Tooltip content="Data Quality Ratio (Score de qualité des données) : évalue la fiabilité des données d'émission selon la méthode GHG Protocol, de 1 (excellent) à 5 (faible).">
                                                <span className="cursor-help border-b border-dashed border-gray-400">Score DQR</span>
                                            </Tooltip>
                                        </span>
                                        <span className="info-value">{report.average_dqr ? Number(report.average_dqr).toFixed(2) : 'Non calculé'}</span>
                                    </div>
                                    <div className="info-item">
                                        <span className="info-label">Terminé le</span>
                                        <span className="info-value">
                                            {report.completed_at
                                                ? new Date(report.completed_at).toLocaleString('fr-FR')
                                                : '—'}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        )}

                        {activeTab === 'audit' && (
                            <div className="audit-content">
                                <div className="audit-timeline">
                                    {auditTrail.length === 0 ? (
                                        <p style={{ color: 'var(--text-muted)' }}>Aucune entrée d'historique</p>
                                    ) : (
                                        auditTrail.map(entry => (
                                            <div key={entry.id} className="audit-entry">
                                                <div className="audit-dot"></div>
                                                <div className="audit-body">
                                                    <div className="audit-action">{getActionLabel(entry.action)}</div>
                                                    {entry.user_name && (
                                                        <div className="audit-user">par {entry.user_name}</div>
                                                    )}
                                                    <div className="audit-time">
                                                        {new Date(entry.created_at).toLocaleString('fr-FR')}
                                                    </div>
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>
                        )}
                        
                        {activeTab === 'top-emitters' && (
                            <div className="top-emitters-content">
                                <TopEmittersDashboard reportId={Number(id)} onUpdate={loadReport} />
                            </div>
                        )}

                        {activeTab === 'materiality' && (
                            <div className="materiality-content">
                                <MaterialityAssessmentForm reportId={Number(id)} onUpdate={loadReport} />
                                <MaterialityMatrix reportId={Number(id)} key={report?.status} />
                            </div>
                        )}
                    </div>
                </>
            )}

            <DrillDownModal 
                reportId={Number(id)}
                isOpen={drillDownModalOpen}
                onClose={() => setDrillDownModalOpen(false)}
                initialFilter={drillDownFilter}
            />

            <ConfirmModal 
                isOpen={showDeleteModal}
                title="Supprimer le rapport"
                message={`Êtes-vous sûr de vouloir supprimer le rapport pour l'exercice ${report?.fiscal_year} ? Cette action est irréversible et supprimera toutes les données associées.`}
                confirmLabel="Supprimer définitivement"
                onConfirm={confirmDelete}
                onCancel={() => setShowDeleteModal(false)}
            />
        </div>
    )
}
