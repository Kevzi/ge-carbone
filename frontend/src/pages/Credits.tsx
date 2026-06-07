import { useState, useEffect } from 'react'
import { api } from '../services/api'

interface CreditPack {
    id: number
    name: string
    credits: number
    price_euros: number
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
            window.location.href = response.checkout_url
        } catch (err) {
            console.error('Failed to initiate purchase:', err)
            setError('Impossible de créer la session de paiement')
            setPurchasing(null)
        }
    }

    const getTransactionIcon = (type: string) => {
        switch (type) {
            case 'purchase': return <span className="text-green-500">💳</span>
            case 'consumption': return <span className="text-blue-500">📊</span>
            case 'refund': return <span className="text-purple-500">↩️</span>
            case 'adjustment': return <span className="text-orange-500">🎁</span>
            default: return <span className="text-gray-500">•</span>
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <span className="ml-3 text-lg text-gray-600 dark:text-gray-400">Chargement...</span>
            </div>
        )
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <header className="mb-10">
                <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white">🪙 Gestion des LedgerCoins</h1>
                <p className="mt-2 text-lg text-gray-600 dark:text-gray-400">
                    Achetez des LedgerCoins pour générer vos rapports carbone et suivez votre consommation.
                </p>
            </header>

            {error && (
                <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded-md">
                    <p className="text-red-700">{error}</p>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Balance & Info */}
                <div className="lg:col-span-1 space-y-8">
                    {/* Balance Card */}
                    <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl shadow-lg p-6 text-white overflow-hidden relative">
                        <div className="absolute -right-4 -top-4 opacity-10 text-9xl">💎</div>
                        <div className="relative z-10">
                            <h2 className="text-blue-100 text-sm font-medium uppercase tracking-wider mb-2">Solde Actuel</h2>
                            <div className="flex items-end gap-2 mb-6">
                                <span className="text-5xl font-black">{balance?.balance ?? 0}</span>
                                <span className="text-blue-200 mb-1 text-lg">LedgerCoins</span>
                            </div>
                            
                            <div className="bg-white/10 rounded-xl p-4 backdrop-blur-sm">
                                <div className="flex justify-between items-center mb-2">
                                    <span className="text-sm text-blue-100">Statut du compte</span>
                                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${balance?.is_low ? 'bg-red-500/20 text-red-200' : 'bg-green-500/20 text-green-200'}`}>
                                        {balance?.is_low ? '⚠️ Solde bas' : '✓ Solde OK'}
                                    </span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-blue-100">Équivalence</span>
                                    <span className="text-sm font-medium">1 LedgerCoin = 1 rapport</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Info Card */}
                    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                            <span>ℹ️</span> Comment ça marche ?
                        </h3>
                        <ul className="space-y-3 text-sm text-gray-600 dark:text-gray-300">
                            <li className="flex items-start gap-2">
                                <span className="text-blue-500 mt-0.5">🔒</span>
                                <span><strong>1 LedgerCoin = 1 analyse FEC</strong> permettant de générer un rapport carbone complet CSRD.</span>
                            </li>
                            <li className="flex items-start gap-2">
                                <span className="text-blue-500 mt-0.5">📅</span>
                                <span><strong>Validité illimitée</strong>, vos LedgerCoins n'expirent jamais.</span>
                            </li>
                            <li className="flex items-start gap-2">
                                <span className="text-blue-500 mt-0.5">🔄</span>
                                <span><strong>Remboursement garanti</strong> (1 LedgerCoin recrédité) en cas d'erreur de traitement.</span>
                            </li>
                        </ul>
                    </div>
                </div>

                {/* Right Column: Packs & Transactions */}
                <div className="lg:col-span-2 space-y-8">
                    {/* Credit Packs */}
                    <section className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Recharger vos LedgerCoins</h2>
                        
                        {packs.length === 0 ? (
                            <div className="text-center py-10 bg-gray-50 dark:bg-gray-900/50 rounded-xl border border-dashed border-gray-200 dark:border-gray-700">
                                <p className="text-gray-500 dark:text-gray-400">Aucun pack disponible pour le moment</p>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                                {packs.map((pack, index) => {
                                    const isPopular = index === 1; // Assuming 2nd pack is popular
                                    return (
                                        <div key={pack.id} className={`relative p-5 rounded-2xl border-2 transition-all ${isPopular ? 'border-blue-500 bg-blue-50/50 dark:bg-blue-900/10' : 'border-gray-100 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-700'}`}>
                                            {isPopular && (
                                                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-500 text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                                                    Populaire
                                                </div>
                                            )}
                                            
                                            <h3 className="text-lg font-semibold text-gray-900 dark:text-white text-center mb-1">{pack.name}</h3>
                                            
                                            <div className="text-center mb-4">
                                                <div className="flex items-baseline justify-center gap-1">
                                                    <span className="text-3xl font-black text-gray-900 dark:text-white">{pack.credits}</span>
                                                    <span className="text-sm font-medium text-gray-500">LC</span>
                                                </div>
                                            </div>
                                            
                                            <div className="text-center mb-6">
                                                <span className="text-2xl font-bold text-gray-900 dark:text-white">{pack.price_euros}€</span>
                                                <div className="text-xs text-gray-500 mt-1">
                                                    soit {(pack.price_euros / pack.credits).toFixed(2)}€ / LedgerCoin
                                                </div>
                                            </div>
                                            
                                            <button
                                                className={`w-full py-2.5 px-4 rounded-xl font-medium transition-colors focus:ring-2 focus:ring-offset-2 ${
                                                    isPopular 
                                                        ? 'bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500' 
                                                        : 'bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white focus:ring-gray-500'
                                                }`}
                                                onClick={() => handlePurchase(pack.id)}
                                                disabled={purchasing === pack.id}
                                            >
                                                {purchasing === pack.id ? 'Redirection...' : 'Acheter'}
                                            </button>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </section>

                    {/* Transactions History */}
                    <section className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Historique des transactions</h2>

                        {transactions.length === 0 ? (
                            <div className="text-center py-10 bg-gray-50 dark:bg-gray-900/50 rounded-xl border border-dashed border-gray-200 dark:border-gray-700">
                                <p className="text-gray-500 dark:text-gray-400">Aucune transaction pour le moment</p>
                            </div>
                        ) : (
                            <div className="overflow-hidden">
                                <ul className="divide-y divide-gray-100 dark:divide-gray-700/50">
                                    {transactions.map(tx => (
                                        <li key={tx.id} className="py-4 flex items-center justify-between">
                                            <div className="flex items-center gap-4">
                                                <div className="h-10 w-10 rounded-full bg-gray-50 dark:bg-gray-900 flex items-center justify-center text-xl">
                                                    {getTransactionIcon(tx.transaction_type)}
                                                </div>
                                                <div>
                                                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                                                        {tx.transaction_type === 'purchase' ? 'Achat de LedgerCoins' :
                                                            tx.transaction_type === 'consumption' ? 'Analyse FEC' :
                                                                tx.transaction_type === 'refund' ? 'Remboursement' : 'Ajustement manuel'}
                                                    </p>
                                                    <p className="text-xs text-gray-500 dark:text-gray-400">
                                                        {new Date(tx.created_at).toLocaleDateString('fr-FR', {
                                                            day: 'numeric',
                                                            month: 'long',
                                                            year: 'numeric',
                                                            hour: '2-digit',
                                                            minute: '2-digit'
                                                        })}
                                                    </p>
                                                </div>
                                            </div>
                                            <div className={`text-base font-bold ${tx.credits >= 0 ? 'text-green-600 dark:text-green-400' : 'text-gray-900 dark:text-white'}`}>
                                                {tx.credits >= 0 ? '+' : ''}{tx.credits}
                                            </div>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </section>
                </div>
            </div>
        </div>
    )
}
