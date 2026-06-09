import { useState, useEffect, useCallback } from 'react'
import { api } from '../services/api'
import Tooltip from './Tooltip'

interface TopEmittersDashboardProps {
    reportId: number
    onUpdate?: () => void
    filterPendingData?: boolean
}

interface CarbonEntry {
    id: number
    fec_line_number: number
    compte_num: string
    compte_lib: string
    ecriture_lib: string
    amount: string | number
    co2_kg: string | number
    dqr: number
    emission_factor_name: string
    emission_factor: number | null
    physical_quantity: string | number | null
    physical_unit: string | null
    requires_physical_data?: boolean
}

interface EmissionFactor {
    id: number
    name: string
    category: string
    value_kg_co2_per_unit: string | number
    unit: string
}

export default function TopEmittersDashboard({ reportId, onUpdate, filterPendingData = false }: TopEmittersDashboardProps) {
    const [entries, setEntries] = useState<CarbonEntry[]>([])
    const [factors, setFactors] = useState<EmissionFactor[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    
    // Edit state
    const [editingEntryId, setEditingEntryId] = useState<number | null>(null)
    const [editQuantity, setEditQuantity] = useState<string>('')
    const [editFactorId, setEditFactorId] = useState<number | null>(null)
    const [saving, setSaving] = useState(false)

    const loadData = useCallback(async () => {
        setLoading(true)
        setError('')
        try {
            // Fetch top 50 emitters, passing pending_physical if we want to filter them at the DB level
            // This ensures we get 50 *pending* emitters instead of fetching the top 50 overall and finding 0 pending among them.
            const url = filterPendingData 
                ? `/reports/${reportId}/entries/?ordering=-co2_kg&pending_physical=true`
                : `/reports/${reportId}/entries/?ordering=-co2_kg`
                
            const entriesData = await api.get<CarbonEntry[] | {results: CarbonEntry[]}>(url)
            let results = Array.isArray(entriesData) ? entriesData : (entriesData as any).results || []
            
            setEntries(results.slice(0, 50))

            // Fetch physical emission factors
            const factorsData = await api.get<EmissionFactor[] | {results: EmissionFactor[]}>(`/reports/emission-factors/physical/`)
            const fResults = Array.isArray(factorsData) ? factorsData : (factorsData as any).results || []
            setFactors(fResults)
        } catch (err) {
            console.error(err)
            setError('Erreur lors du chargement des postes d\'émission')
        } finally {
            setLoading(false)
        }
    }, [reportId, filterPendingData])

    useEffect(() => {
        loadData()
    }, [loadData])

    const startEditing = (entry: CarbonEntry) => {
        setEditingEntryId(entry.id)
        setEditQuantity(entry.physical_quantity ? String(entry.physical_quantity) : '')
        setEditFactorId(entry.emission_factor)
    }

    const cancelEditing = () => {
        setEditingEntryId(null)
        setEditQuantity('')
        setEditFactorId(null)
    }

    const saveEntry = async (entryId: number) => {
        if (!editQuantity || isNaN(Number(editQuantity)) || !editFactorId) {
            alert('Veuillez saisir une quantité valide et sélectionner un facteur d\'émission.')
            return
        }

        const selectedFactor = factors.find(f => f.id === editFactorId)
        if (!selectedFactor) return

        setSaving(true)
        try {
            await api.patch(`/reports/${reportId}/entries/${entryId}/`, {
                physical_quantity: Number(editQuantity),
                physical_unit: selectedFactor.unit,
                emission_factor_id: selectedFactor.id
            })
            
            // Reload local data
            await loadData()
            
            // Notify parent
            if (onUpdate) {
                onUpdate()
            }
            
            cancelEditing()
        } catch (err) {
            console.error(err)
            alert('Erreur lors de la mise à jour.')
        } finally {
            setSaving(false)
        }
    }

    const formatNumber = (num: string | number | null) => {
        if (num === null || num === undefined) return '—'
        const n = typeof num === 'string' ? parseFloat(num) : num
        return new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 2 }).format(n)
    }

    const getDqrBadgeClass = (dqr: number) => {
        if (dqr === 1) return 'badge badge-success'
        if (dqr === 2) return 'badge badge-info'
        if (dqr === 3) return 'badge badge-warning'
        return 'badge badge-error'
    }

    if (loading && entries.length === 0) {
        return <div className="p-6 text-center"><span className="spinner"></span> Chargement...</div>
    }

    if (error) {
        return <div className="alert alert-error">{error}</div>
    }

    return (
        <div className="top-emitters">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-semibold">Top Émetteurs</h3>
                <p className="text-gray-500">La loi de Pareto : concentrez vos efforts sur ces lignes à fort impact.</p>
            </div>
            
            <div className="overflow-x-auto">
                <table className="table">
                    <thead>
                        <tr className="border-b-2 border-gray-200 text-left">
                            <th className="py-3 px-2">Ligne</th>
                            <th className="py-3 px-2">Compte</th>
                            <th className="py-3 px-2">Libellé</th>
                            <th className="py-3 px-2 text-right">Montant net</th>
                            <th className="py-3 px-2 text-right">Émissions (kgCO2e)</th>
                            <th className="py-3 px-2 text-center">DQR</th>
                            <th className="py-3 px-2">
                                <div className="flex items-center gap-1">
                                    Facteur / Quantité Physique
                                    <Tooltip content="Pour les énergies (Scope 1 & 2), le calcul basé sur l'euro dépensé est trop imprécis. Vous devez saisir la quantité réelle consommée (ex: Litres de carburant, kWh d'électricité) visible sur vos factures.">
                                        <span className="cursor-help text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                                            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                        </span>
                                    </Tooltip>
                                </div>
                            </th>
                            <th className="py-3 px-2 text-right">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {entries.map(entry => (
                            <tr key={entry.id}>
                                <td className="py-3 px-2 text-gray-500">#{entry.fec_line_number}</td>
                                <td className="py-3 px-2 font-medium">{entry.compte_num}</td>
                                <td className="py-3 px-2 max-w-xs break-words" title={entry.ecriture_lib || entry.compte_lib}>
                                    {entry.ecriture_lib || entry.compte_lib}
                                </td>
                                <td className="py-3 px-2 text-right">
                                    {formatNumber(entry.amount)} €
                                </td>
                                <td className="py-3 px-2 text-right font-bold">
                                    {formatNumber(entry.co2_kg)}
                                </td>
                                <td className="py-3 px-2 text-center">
                                    <span className={getDqrBadgeClass(entry.dqr)} title={`Score qualité: ${entry.dqr}`}>
                                        {entry.dqr}
                                    </span>
                                </td>
                                <td className="py-3 px-2">
                                    {editingEntryId === entry.id ? (
                                        <div className="flex gap-2 items-center">
                                            <input 
                                                type="number" 
                                                step="0.01"
                                                className="form-control w-24 px-2 py-1" 
                                                placeholder="Quantité"
                                                value={editQuantity}
                                                onChange={(e) => setEditQuantity(e.target.value)}
                                            />
                                            <select 
                                                className="form-control max-w-[200px] px-2 py-1"
                                                value={editFactorId || ''}
                                                onChange={(e) => setEditFactorId(Number(e.target.value))}
                                            >
                                                <option value="" disabled>Choisir un facteur...</option>
                                                {factors.map(f => (
                                                    <option key={f.id} value={f.id}>
                                                        {f.name} ({f.unit})
                                                    </option>
                                                ))}
                                            </select>
                                        </div>
                                    ) : (
                                        <div>
                                            <div className="text-sm text-gray-800 dark:text-gray-200">
                                                {entry.emission_factor_name}
                                            </div>
                                            {entry.physical_quantity && entry.physical_unit && (
                                                <div className="text-xs text-green-600 font-medium mt-1">
                                                    ✓ {formatNumber(entry.physical_quantity)} {entry.physical_unit}
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </td>
                                <td className="py-3 px-2 text-right">
                                    {editingEntryId === entry.id ? (
                                        <div className="flex gap-1 justify-end">
                                            <button 
                                                className="btn px-2 py-1 text-sm" 
                                                onClick={cancelEditing}
                                                disabled={saving}
                                            >
                                                Annuler
                                            </button>
                                            <button 
                                                className="btn btn-primary px-2 py-1 text-sm" 
                                                onClick={() => saveEntry(entry.id)}
                                                disabled={saving}
                                            >
                                                {saving ? '...' : 'Valider'}
                                            </button>
                                        </div>
                                    ) : (
                                        <button 
                                            className="btn px-2 py-1 text-sm"
                                            onClick={() => startEditing(entry)}
                                        >
                                            ✎ Unité Phys.
                                        </button>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            {entries.length === 0 && !loading && (
                <div className="p-6 text-center text-gray-500">
                    Aucune entrée trouvée.
                </div>
            )}
        </div>
    )
}
