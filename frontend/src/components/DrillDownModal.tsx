import { useState, useEffect } from 'react'
import { api } from '../services/api'

interface CarbonEntry {
    id: number
    fec_line_number: number
    ecriture_date: string | null
    compte_num: string
    ecriture_lib: string
    amount: string | number
    co2_kg: string | number
    emission_factor_name: string
    emission_factor_category: string
    emission_factor_value: string | number
}

interface PaginatedResponse {
    count: number
    next: string | null
    previous: string | null
    results: CarbonEntry[]
}

interface DrillDownModalProps {
    reportId: number
    isOpen: boolean
    onClose: () => void
    initialFilter?: { scope?: number; category?: string }
}

export default function DrillDownModal({ reportId, isOpen, onClose, initialFilter }: DrillDownModalProps) {
    const [entries, setEntries] = useState<CarbonEntry[]>([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [page, setPage] = useState(1)
    const [totalPages, setTotalPages] = useState(1)
    const [totalCount, setTotalCount] = useState(0)

    useEffect(() => {
        if (isOpen) {
            loadEntries(1)
        }
    }, [isOpen, initialFilter])

    const loadEntries = async (pageNum: number) => {
        setLoading(true)
        setError('')
        try {
            let url = `/reports/${reportId}/entries/?page=${pageNum}`
            if (initialFilter?.scope) {
                url += `&scope=${initialFilter.scope}`
            }
            if (initialFilter?.category) {
                url += `&category=${encodeURIComponent(initialFilter.category)}`
            }
            
            const data = await api.get<PaginatedResponse>(url)
            setEntries(data.results)
            setTotalCount(data.count)
            // Calculate total pages using the API count and our known page size of 50
            setTotalPages(Math.max(1, Math.ceil(data.count / 50)))
            setPage(pageNum)
        } catch (err) {
            console.error(err)
            setError('Erreur lors du chargement des détails.')
        } finally {
            setLoading(false)
        }
    }

    const formatNumber = (num: string | number | null) => {
        if (num === null || num === undefined) return '—'
        const n = typeof num === 'string' ? parseFloat(num) : num
        return new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 2 }).format(n)
    }

    const formatDate = (dateString: string | null) => {
        if (!dateString) return '—'
        const d = new Date(dateString)
        return isNaN(d.getTime()) ? dateString : d.toLocaleDateString('fr-FR')
    }

    if (!isOpen) return null

    return (
        <div style={{ position: 'fixed', inset: 0, zIndex: 50, display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'rgba(0, 0, 0, 0.5)', backdropFilter: 'blur(4px)', padding: '16px' }}>
            <div className="card" style={{ width: '100%', maxWidth: '1152px', maxHeight: '90vh', display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' }}>
                <div style={{ padding: '24px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: 'var(--bg-tertiary)' }}>
                    <h2 className="text-2xl font-bold text-gray-800">
                        Détail des écritures
                        {initialFilter?.scope && ` - Scope ${initialFilter.scope}`}
                        {initialFilter?.category && ` - ${initialFilter.category}`}
                    </h2>
                    <button 
                        onClick={onClose}
                        className="text-gray-500 hover:text-gray-800 focus:outline-none"
                    >
                        ✕
                    </button>
                </div>
                
                <div style={{ padding: '24px', flex: 1, overflow: 'auto' }}>
                    {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">{error}</div>}
                    
                    {loading ? (
                        <div className="flex justify-center items-center py-12">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                        </div>
                    ) : (
                        <div>
                            <div style={{ marginBottom: '16px', fontSize: '0.875rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
                                {totalCount} ligne(s) trouvée(s)
                            </div>
                            <div style={{ overflowX: 'auto', border: '1px solid var(--border-subtle)', borderRadius: '8px' }}>
                                <table className="table" style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                                    <thead style={{ backgroundColor: 'var(--bg-tertiary)' }}>
                                        <tr>
                                            <th className="px-4 py-3 text-left font-semibold text-gray-700 uppercase tracking-wider">Date</th>
                                            <th className="px-4 py-3 text-left font-semibold text-gray-700 uppercase tracking-wider">Libellé</th>
                                            <th className="px-4 py-3 text-left font-semibold text-gray-700 uppercase tracking-wider">Compte</th>
                                            <th className="px-4 py-3 text-right font-semibold text-gray-700 uppercase tracking-wider">Montant</th>
                                            <th className="px-4 py-3 text-left font-semibold text-gray-700 uppercase tracking-wider">Facteur ADEME</th>
                                            <th className="px-4 py-3 text-right font-semibold text-gray-700 uppercase tracking-wider">CO2 (kg)</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {entries.length === 0 ? (
                                            <tr>
                                                <td colSpan={6} className="px-4 py-8 text-center text-gray-500 italic">
                                                    Aucune écriture trouvée.
                                                </td>
                                            </tr>
                                        ) : (
                                            entries.map(entry => (
                                                <tr key={entry.id} className="hover:bg-blue-50 transition-colors">
                                                    <td className="px-4 py-3 whitespace-nowrap text-gray-600">{formatDate(entry.ecriture_date)}</td>
                                                    <td className="px-4 py-3 text-gray-800" title={entry.ecriture_lib}>
                                                        <div className="truncate max-w-xs">{entry.ecriture_lib || `Ligne ${entry.fec_line_number}`}</div>
                                                    </td>
                                                    <td className="px-4 py-3 whitespace-nowrap font-mono text-gray-600">{entry.compte_num}</td>
                                                    <td className="px-4 py-3 whitespace-nowrap text-right font-medium">{formatNumber(entry.amount)} €</td>
                                                    <td className="px-4 py-3">
                                                        <div className="text-gray-800 font-medium">{entry.emission_factor_name}</div>
                                                        <div className="text-xs text-gray-500">{formatNumber(entry.emission_factor_value)} kgCO2/€</div>
                                                    </td>
                                                    <td className="px-4 py-3 whitespace-nowrap text-right font-bold text-primary-700">
                                                        {formatNumber(entry.co2_kg)}
                                                    </td>
                                                </tr>
                                            ))
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </div>
                
                {/* Pagination */}
                <div style={{ padding: '16px 24px', borderTop: '1px solid var(--border-subtle)', backgroundColor: 'var(--bg-tertiary)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <button 
                        onClick={() => loadEntries(page - 1)} 
                        disabled={page <= 1 || loading}
                        className="btn btn-secondary"
                    >
                        ← Précédent
                    </button>
                    <span style={{ color: 'var(--text-secondary)', fontWeight: 500 }}>
                        Page {page} / {totalPages || 1}
                    </span>
                    <button 
                        onClick={() => loadEntries(page + 1)} 
                        disabled={page >= totalPages || loading}
                        className="btn btn-secondary"
                    >
                        Suivant →
                    </button>
                </div>
            </div>
        </div>
    )
}
