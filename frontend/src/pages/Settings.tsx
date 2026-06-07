import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'

interface Cabinet {
    id: number
    name: string
    siret: string
    plan: string
}

interface Member {
    id: number
    username: string
    email: string
    first_name: string
    last_name: string
    role: string
    is_cabinet_admin: boolean
    can_consume_credits: boolean
}

export default function Settings() {
    const { user: currentUser } = useAuth()
    const [members, setMembers] = useState<Member[]>([])
    const [loading, setLoading] = useState(true)
    const [cabinet, setCabinet] = useState<Cabinet | null>(null)
    const [isSaving, setIsSaving] = useState(false)
    const [message, setMessage] = useState<{type: 'success' | 'error', text: string} | null>(null)

    // Form state for inviting new member
    const [newMemberEmail, setNewMemberEmail] = useState('')

    useEffect(() => {
        loadData()
    }, [])

    const loadData = async () => {
        try {
            setLoading(true)
            const [usersRes, userMeRes] = await Promise.all([
                api.get<Member[]>('/users/'),
                api.get<any>('/users/me/')
            ])
            setMembers(usersRes)
            if (userMeRes.cabinet) {
                setCabinet(userMeRes.cabinet)
            }
        } catch (error) {
            console.error("Erreur lors du chargement des paramètres", error)
        } finally {
            setLoading(false)
        }
    }

    const toggleCreditConsumption = async (memberId: number, currentStatus: boolean) => {
        try {
            await api.patch(`/users/${memberId}/`, {
                can_consume_credits: !currentStatus
            })
            // Update local state
            setMembers(members.map(m => 
                m.id === memberId ? { ...m, can_consume_credits: !currentStatus } : m
            ))
            showMessage('success', 'Permissions mises à jour avec succès.')
        } catch (error) {
            showMessage('error', 'Erreur lors de la mise à jour des permissions.')
        }
    }

    const handleInvite = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!newMemberEmail) return
        
        setIsSaving(true)
        try {
            // Dans une vraie app, on appellerait un endpoint d'invitation
            // Pour l'instant on simule la création
            const newUser = await api.post<Member>('/users/', {
                username: newMemberEmail.split('@')[0],
                email: newMemberEmail,
                can_consume_credits: false
            })
            setMembers([...members, newUser])
            setNewMemberEmail('')
            showMessage('success', 'Invitation envoyée avec succès.')
        } catch (error) {
            showMessage('error', 'Impossible d\'inviter ce collaborateur. Vérifiez que l\'email n\'est pas déjà utilisé.')
        } finally {
            setIsSaving(false)
        }
    }

    const showMessage = (type: 'success' | 'error', text: string) => {
        setMessage({ type, text })
        setTimeout(() => setMessage(null), 3000)
    }

    if (loading) {
        return (
            <div className="min-h-full flex flex-col items-center justify-center p-8">
                <div className="w-12 h-12 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin mb-4"></div>
                <p className="text-gray-500 font-medium">Chargement des paramètres...</p>
            </div>
        )
    }

    return (
        <div className="min-h-full p-8 max-w-5xl mx-auto space-y-8 animate-in fade-in duration-500">
            {/* Header */}
            <header>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white tracking-tight">Paramètres</h1>
                <p className="text-gray-500 dark:text-gray-400 mt-1">Gérez votre profil, votre cabinet et vos collaborateurs.</p>
            </header>

            {message && (
                <div className={`p-4 rounded-xl flex items-center gap-3 animate-in slide-in-from-top-2 ${
                    message.type === 'success' 
                        ? 'bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20' 
                        : 'bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-500/20'
                }`}>
                    <span>{message.type === 'success' ? '✓' : '⚠️'}</span>
                    <span className="font-medium">{message.text}</span>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Profile & Cabinet */}
                <div className="lg:col-span-1 space-y-6">
                    {/* Profil */}
                    <div className="bg-white dark:bg-[#151b2b] rounded-2xl border border-gray-100 dark:border-gray-800 p-6 shadow-sm">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white text-2xl font-bold shadow-lg">
                                {currentUser?.username.charAt(0).toUpperCase()}
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-gray-900 dark:text-white">{currentUser?.username}</h2>
                                <p className="text-sm text-gray-500 dark:text-gray-400">{currentUser?.email || 'Aucun email'}</p>
                            </div>
                        </div>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Rôle</label>
                                <div className="text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-800/50 px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700">
                                    {currentUser?.is_cabinet_admin ? 'Administrateur Cabinet' : 'Collaborateur'}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Cabinet */}
                    {cabinet && (
                        <div className="bg-white dark:bg-[#151b2b] rounded-2xl border border-gray-100 dark:border-gray-800 p-6 shadow-sm">
                            <div className="flex items-center gap-3 mb-6">
                                <span className="text-2xl">🏢</span>
                                <h2 className="text-xl font-bold text-gray-900 dark:text-white">Mon Cabinet</h2>
                            </div>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nom du Cabinet</label>
                                    <div className="text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-800/50 px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700">
                                        {cabinet.name}
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">SIRET</label>
                                    <div className="text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-800/50 px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700">
                                        {cabinet.siret || 'Non renseigné'}
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Plan actuel</label>
                                    <div className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-100 dark:bg-indigo-500/20 text-indigo-800 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/30 uppercase tracking-wider">
                                        {cabinet.plan}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Right Column: Team Management */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="bg-white dark:bg-[#151b2b] rounded-2xl border border-gray-100 dark:border-gray-800 p-6 shadow-sm flex flex-col h-full">
                        <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center gap-3">
                                <span className="text-2xl">👥</span>
                                <h2 className="text-xl font-bold text-gray-900 dark:text-white">Équipe & Autorisations</h2>
                            </div>
                            <span className="text-sm text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 px-3 py-1 rounded-full">
                                {members.length} membre{members.length > 1 ? 's' : ''}
                            </span>
                        </div>

                        {/* Invite Form */}
                        {currentUser?.is_cabinet_admin && (
                            <form onSubmit={handleInvite} className="mb-8 p-4 bg-gray-50 dark:bg-gray-800/30 rounded-xl border border-gray-200 dark:border-gray-700/50 flex gap-3 items-end">
                                <div className="flex-1">
                                    <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Inviter un collaborateur</label>
                                    <input 
                                        type="email" 
                                        id="email"
                                        placeholder="adresse@cabinet.com" 
                                        value={newMemberEmail}
                                        onChange={(e) => setNewMemberEmail(e.target.value)}
                                        className="w-full bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 outline-none transition-shadow"
                                    />
                                </div>
                                <button 
                                    type="submit" 
                                    disabled={!newMemberEmail || isSaving}
                                    className="px-5 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 text-white font-medium rounded-lg shadow-sm transition-colors"
                                >
                                    {isSaving ? 'Envoi...' : 'Inviter'}
                                </button>
                            </form>
                        )}

                        {/* Members List */}
                        <div className="flex-1 -mx-6 px-6 overflow-y-auto">
                            <div className="space-y-4">
                                {members.map((member) => (
                                    <div key={member.id} className="flex items-center justify-between p-4 rounded-xl border border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-white/[0.02] transition-colors">
                                        <div className="flex items-center gap-4">
                                            <div className="w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-gray-600 dark:text-gray-300 font-bold">
                                                {member.username.charAt(0).toUpperCase()}
                                            </div>
                                            <div>
                                                <div className="flex items-center gap-2">
                                                    <h3 className="font-medium text-gray-900 dark:text-white">
                                                        {member.first_name && member.last_name ? `${member.first_name} ${member.last_name}` : member.username}
                                                    </h3>
                                                    {member.is_cabinet_admin && (
                                                        <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400 rounded-sm">
                                                            Admin
                                                        </span>
                                                    )}
                                                </div>
                                                <p className="text-sm text-gray-500 dark:text-gray-400">{member.email || 'Pas d\'email'}</p>
                                            </div>
                                        </div>
                                        
                                        <div className="flex items-center gap-4">
                                            <div className="flex flex-col items-end">
                                                <span className="text-xs text-gray-500 dark:text-gray-400 mb-1">Droit d'utiliser des LedgerCoins</span>
                                                <button 
                                                    onClick={() => currentUser?.is_cabinet_admin ? toggleCreditConsumption(member.id, member.can_consume_credits) : null}
                                                    disabled={!currentUser?.is_cabinet_admin || member.id === currentUser?.id}
                                                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-[#151b2b] ${
                                                        member.can_consume_credits ? 'bg-emerald-500' : 'bg-gray-300 dark:bg-gray-600'
                                                    } ${(!currentUser?.is_cabinet_admin || member.id === currentUser?.id) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                                                >
                                                    <span className="sr-only">Autoriser l'utilisation de crédits</span>
                                                    <span 
                                                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                                                            member.can_consume_credits ? 'translate-x-6' : 'translate-x-1'
                                                        }`}
                                                    />
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
