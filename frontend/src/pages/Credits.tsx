import { useState, useEffect } from 'react'
import { api } from '../services/api'

interface CreditPack {
    id: number
    name: string
    credits: number
    price_euros: number  // Match Django field name
    description: string
}

interface CreditTransaction {
    id: number
    transaction_type: string
    credits: number
    balance_after: number
    amount_euros: number | null
    user_name: string | null
    status: string
    created_at: string
}

interface CreditBalance {
    balance: number
    last_purchase_at: string | null
    alert_threshold: number
    is_low: boolean
}

// DRF paginated response
interface PaginatedResponse<T> {
    count: number
    results: T[]
}

export default function Credits() {
    const [packs, setPacks] = useState<CreditPack[]>([])
    const [transactions, setTransactions] = useState<CreditTransaction[]>([])
    const [balance, setBalance] = useState<CreditBalance | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [purchasing, setPurchasing] = useState<number | null>(null)

    const loadCreditsData = async () => {
        setError('')

        // Load each independently to avoid all-or-nothing failure
        try {
            const packsResponse = await api.get<PaginatedResponse<CreditPack> | CreditPack[]>('/credits/packs/')
            if (Array.isArray(packsResponse)) {
                setPacks(packsResponse)
            } else if (packsResponse && 'results' in packsResponse) {
                setPacks(packsResponse.results)
            }
        } catch {
            console.log('Packs API not available')
        }

        try {
            const balanceData = await api.get<CreditBalance>('/credits/balance/')
            setBalance(balanceData)
        } catch {
            console.log('Balance API not available')
        }

        try {
            const txResponse = await api.get<PaginatedResponse<CreditTransaction> | CreditTransaction[]>('/credits/transactions/')
            if (Array.isArray(txResponse)) {
                setTransactions(txResponse)
            } else if (txResponse && 'results' in txResponse) {
                setTransactions(txResponse.results)
            }
        } catch {
            console.log('Transactions API not available')
        }

        setLoading(false)
    }

    useEffect(() => {
        loadCreditsData()
    }, [])

    const handlePurchase = async (packId: number) => {
        setPurchasing(packId)
        try {
            const response = await api.post<{ checkout_url: string }>('/credits/purchase/', {
                credit_pack_id: packId,
                success_url: window.location.origin + '/credits?success=true',
                cancel_url: window.location.origin + '/credits?canceled=true'
            })

            // eslint-disable-next-line react-hooks/immutability
            window.location.href = response.checkout_url
        } catch (err) {
            console.error('Failed to initiate purchase:', err)
            setError('Impossible de créer la session de paiement')
            setPurchasing(null)
        }
    }

    const getTransactionIcon = (type: string) => {
        switch (type) {
            case 'purchase': return '💳'
            case 'consumption': return '📊'
            case 'refund': return '↩️'
            case 'adjustment': return '🎁'
            default: return '•'
        }
    }

    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Chargement...</p>
            </div>
        )
    }

    return (
        <div className="credits-page">
            <header className="page-header">
                <h1>💳 Gestion des crédits</h1>
                <p>Achetez des crédits pour générer vos rapports carbone</p>
            </header>

            {error && (
                <div className="alert alert-error">{error}</div>
            )}

            {/* Balance Card */}
            <div className="balance-card card">
                <div className="balance-main">
                    <div className="balance-info">
                        <span className="balance-label">Solde actuel</span>
                        <span className="balance-value">{balance?.balance ?? 0}</span>
                        <span className="balance-unit">crédits</span>
                    </div>
                    <div className="balance-icon">💎</div>
                </div>
                <div className="balance-stats">
                    <div className="balance-stat">
                        <span className="stat-value">{balance?.is_low ? '⚠️' : '✓'}</span>
                        <span className="stat-label">{balance?.is_low ? 'Solde bas' : 'Solde OK'}</span>
                    </div>
                    <div className="balance-stat">
                        <span className="stat-value">1</span>
                        <span className="stat-label">crédit = 1 rapport</span>
                    </div>
                </div>
            </div>

            {/* Credit Packs */}
            <section className="packs-section">
                <h2>Recharger vos crédits</h2>
                {packs.length === 0 ? (
                    <div className="empty-state-small">
                        <p>Aucun pack disponible pour le moment</p>
                    </div>
                ) : (
                    <div className="packs-grid">
                        {packs.map((pack, index) => (
                            <div
                                key={pack.id}
                                className={`pack-card card ${index === 1 ? 'pack-popular' : ''}`}
                            >
                                {index === 1 && (
                                    <div className="pack-badge">Populaire</div>
                                )}
                                <div className="pack-name">{pack.name}</div>
                                <div className="pack-credits">
                                    <span className="credits-number">{pack.credits}</span>
                                    <span className="credits-label">crédits</span>
                                </div>
                                <div className="pack-price">
                                    <span className="price-value">{pack.price_euros}</span>
                                    <span className="price-currency">€</span>
                                </div>
                                <div className="pack-perunit">
                                    {(pack.price_euros / pack.credits).toFixed(2)}€ / crédit
                                </div>
                                <button
                                    className={`btn ${index === 1 ? 'btn-primary' : 'btn-secondary'}`}
                                    onClick={() => handlePurchase(pack.id)}
                                    disabled={purchasing === pack.id}
                                >
                                    {purchasing === pack.id ? 'Redirection...' : 'Acheter'}
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </section>

            {/* Transactions History */}
            <section className="transactions-section card">
                <h2>Historique des transactions</h2>

                {transactions.length === 0 ? (
                    <div className="empty-state-small">
                        <p>Aucune transaction pour le moment</p>
                    </div>
                ) : (
                    <div className="transactions-list">
                        {transactions.map(tx => (
                            <div key={tx.id} className="transaction-row">
                                <div className="tx-icon">{getTransactionIcon(tx.transaction_type)}</div>
                                <div className="tx-info">
                                    <span className="tx-description">
                                        {tx.transaction_type === 'purchase' ? 'Achat de crédits' :
                                            tx.transaction_type === 'consumption' ? 'Utilisation' :
                                                tx.transaction_type === 'refund' ? 'Remboursement' : 'Ajustement'}
                                    </span>
                                    <span className="tx-date">
                                        {new Date(tx.created_at).toLocaleDateString('fr-FR', {
                                            day: 'numeric',
                                            month: 'long',
                                            year: 'numeric'
                                        })}
                                    </span>
                                </div>
                                <div className={`tx-amount ${tx.credits >= 0 ? 'positive' : 'negative'}`}>
                                    {tx.credits >= 0 ? '+' : ''}{tx.credits}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </section>

            {/* Info */}
            <div className="info-card card">
                <h3>ℹ️ Comment fonctionnent les crédits ?</h3>
                <ul>
                    <li>🔒 <strong>1 crédit = 1 analyse FEC</strong> — Rapport carbone complet CSRD</li>
                    <li>📅 <strong>Validité illimitée</strong> — Vos crédits n'expirent jamais</li>
                    <li>🔄 <strong>Remboursement</strong> — Crédit remboursé en cas d'erreur de traitement</li>
                    <li>🏢 <strong>Devis sur mesure</strong> — Contactez-nous pour des volumes importants</li>
                </ul>
            </div>
        </div>
    )
}
