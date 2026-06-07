import { useState, useEffect } from 'react'
import { api } from '../services/api'

interface User {
    id: number
    username: string
    email: string
    cabinet_name: string | null
    role: string
}

interface UserSelectionModalProps {
    isOpen: boolean
    onClose: () => void
    onSelect: (userId: number) => void
    cabinetId?: number | null
}

export default function UserSelectionModal({ isOpen, onClose, onSelect, cabinetId }: UserSelectionModalProps) {
    const [users, setUsers] = useState<User[]>([])
    const [search, setSearch] = useState('')
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        if (!isOpen) return
        
        const fetchUsers = async () => {
            setLoading(true)
            try {
                let url = '/superadmin/users/'
                if (cabinetId) {
                    url += `?cabinet_id=${cabinetId}`
                }
                const res = await api.get<any>(url)
                setUsers(res.results || res || [])
            } catch (err) {
                console.error("Failed to fetch users", err)
            } finally {
                setLoading(false)
            }
        }
        
        fetchUsers()
    }, [isOpen, cabinetId])

    if (!isOpen) return null

    const filteredUsers = users.filter(u => 
        u.username.toLowerCase().includes(search.toLowerCase()) || 
        u.email.toLowerCase().includes(search.toLowerCase())
    )

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
            <div className="bg-white dark:bg-gray-900 rounded-2xl w-full max-w-lg shadow-2xl border border-gray-200 dark:border-gray-800 overflow-hidden flex flex-col max-h-[80vh]">
                <div className="p-4 border-b border-gray-200 dark:border-gray-800 flex justify-between items-center bg-gray-50/50 dark:bg-gray-800/30">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                        <span className="text-purple-500">🕵️</span> Sélectionner un utilisateur
                    </h3>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
                
                <div className="p-4 border-b border-gray-200 dark:border-gray-800">
                    <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <svg className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                            </svg>
                        </div>
                        <input
                            type="text"
                            className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent sm:text-sm"
                            placeholder="Rechercher par nom ou email..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                    </div>
                </div>

                <div className="overflow-y-auto p-2 flex-1 custom-scrollbar">
                    {loading ? (
                        <div className="p-8 text-center text-gray-500">Chargement...</div>
                    ) : filteredUsers.length === 0 ? (
                        <div className="p-8 text-center text-gray-500">Aucun utilisateur trouvé.</div>
                    ) : (
                        <div className="space-y-1">
                            {filteredUsers.map(user => (
                                <button
                                    key={user.id}
                                    onClick={() => onSelect(user.id)}
                                    className="w-full text-left px-4 py-3 rounded-xl hover:bg-purple-50 dark:hover:bg-purple-500/10 transition-colors border border-transparent hover:border-purple-200 dark:hover:border-purple-500/20 group"
                                >
                                    <div className="flex justify-between items-center">
                                        <div>
                                            <div className="font-bold text-gray-900 dark:text-white group-hover:text-purple-600 dark:group-hover:text-purple-400">
                                                {user.username}
                                            </div>
                                            <div className="text-xs text-gray-500">{user.email}</div>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-xs font-semibold bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 px-2 py-1 rounded-md mb-1 inline-block">
                                                {user.role}
                                            </div>
                                            <div className="text-[10px] text-gray-400 uppercase tracking-wider">
                                                {user.cabinet_name || 'Sans Cabinet'}
                                            </div>
                                        </div>
                                    </div>
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
