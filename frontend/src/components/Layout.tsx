import { useState, useEffect, useRef } from 'react'
import { NavLink, Outlet, useLocation, useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useReports } from '../contexts/ReportsContext'
import logo from '../assets/logo.png'

export default function Layout() {
    const { user, logout } = useAuth()
    const { isProcessing, latestReport } = useReports()
    const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark')
    const [isProfileOpen, setIsProfileOpen] = useState(false)
    const profileRef = useRef<HTMLDivElement>(null)
    const location = useLocation()
    const navigate = useNavigate()
    
    const adminToken = localStorage.getItem('admin_access_token')

    const handleStopImpersonating = () => {
        const at = localStorage.getItem('admin_access_token')
        const rt = localStorage.getItem('admin_refresh_token')
        if (at && rt) {
            localStorage.setItem('access_token', at)
            localStorage.setItem('refresh_token', rt)
            localStorage.removeItem('admin_access_token')
            localStorage.removeItem('admin_refresh_token')
            window.location.href = '/superadmin'
        }
    }

    // Forcer la navigation si un rapport est en cours de traitement
    useEffect(() => {
        if (isProcessing && latestReport?.id) {
            const targetPath = `/reports/${latestReport.id}`
            const currentPath = location.pathname.toLowerCase().replace(/\/$/, '')
            const allowedPaths = ['/logout', '/credits', '/academy', '/developers', '/settings', '/superadmin']
            if (currentPath !== targetPath && !allowedPaths.includes(currentPath)) {
                navigate(targetPath, { replace: true })
            }
        }
    }, [isProcessing, latestReport?.id, location.pathname, navigate])

    useEffect(() => {
        if (theme === 'dark') {
            document.documentElement.classList.add('dark')
        } else {
            document.documentElement.classList.remove('dark')
        }
        localStorage.setItem('theme', theme)
    }, [theme])

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
                setIsProfileOpen(false)
            }
        }
        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    const toggleTheme = () => {
        setTheme(theme === 'light' ? 'dark' : 'light')
        setIsProfileOpen(false)
    }

    const navItemClass = ({ isActive }: { isActive: boolean }) =>
        `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
            isActive
                ? 'bg-blue-600/10 text-blue-500 border border-blue-500/20 shadow-[0_0_15px_rgba(59,130,246,0.1)]'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800/50'
        }`

    return (
        <div className="flex h-screen bg-gray-50 dark:bg-[#0B0F19] overflow-hidden selection:bg-blue-500/30">
            {/* Sidebar */}
            <aside className="w-72 flex-shrink-0 border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-[#0B0F19]/90 backdrop-blur-xl flex flex-col transition-all duration-300 relative z-20">
                {/* Logo Area */}
                <div className="h-20 flex items-center px-6 border-b border-gray-200 dark:border-gray-800">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 p-0.5 shadow-lg shadow-blue-500/20">
                            <div className="w-full h-full bg-white dark:bg-gray-900 rounded-[10px] flex items-center justify-center">
                                <img src={logo} alt="LedgerCarbon" className="w-6 h-6 object-contain" />
                            </div>
                        </div>
                        <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-400 tracking-tight">
                            Ledger<span className="text-blue-500">Carbon</span>
                        </span>
                    </div>
                </div>

                {/* Navigation */}
                <div className="flex-1 overflow-y-auto py-6 px-4 custom-scrollbar">
                    <nav className="space-y-8">
                        {/* Section Principale */}
                        <div>
                            <div className="px-4 mb-2 text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                                Menu Principal
                            </div>
                            <ul className="space-y-1">
                                {!isProcessing && (
                                    <li>
                                        <NavLink to="/" end className={navItemClass}>
                                            <span className="text-xl">📊</span>
                                            <span className="font-medium">Tableau de bord</span>
                                        </NavLink>
                                    </li>
                                )}
                                {!isProcessing && (
                                    <li>
                                        <NavLink to="/upload" className={navItemClass}>
                                            <span className="text-xl">📤</span>
                                            <span className="font-medium">Nouveau rapport</span>
                                        </NavLink>
                                    </li>
                                )}
                                {!isProcessing && (
                                    <li>
                                        <NavLink to="/reports" className={navItemClass}>
                                            <span className="text-xl">📋</span>
                                            <span className="font-medium">Mes rapports</span>
                                        </NavLink>
                                    </li>
                                )}
                                {/* Si processing, on affiche juste le lien vers le rapport en cours pour ne pas frustrer l'utilisateur s'il le cherche */}
                                {isProcessing && latestReport?.id && (
                                    <li>
                                        <NavLink to={`/reports/${latestReport.id}`} className={navItemClass}>
                                            <span className="text-xl animate-pulse">⏳</span>
                                            <span className="font-medium">Analyse en cours...</span>
                                        </NavLink>
                                    </li>
                                )}
                            </ul>
                        </div>

                        {/* Section Organisation (masquée si processing) */}
                        {!isProcessing && (
                            <div>
                                <div className="px-4 mb-2 text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                                    Organisation
                                </div>
                                <ul className="space-y-1">
                                    <li>
                                        <NavLink to="/settings" className={navItemClass}>
                                            <span className="text-xl">⚙️</span>
                                            <span className="font-medium">Paramètres</span>
                                        </NavLink>
                                    </li>
                                    <li>
                                        <NavLink to="/credits" className={navItemClass}>
                                            <span className="text-xl">🪙</span>
                                            <span className="font-medium">LedgerCoins</span>
                                        </NavLink>
                                    </li>
                                </ul>
                            </div>
                        )}

                        {/* Section Ressources (masquée si processing) */}
                        {!isProcessing && (
                            <div>
                                <div className="px-4 mb-2 text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                                    Ressources
                                </div>
                                <ul className="space-y-1">
                                    <li>
                                        <NavLink to="/academy" className={navItemClass}>
                                            <span className="text-xl">📚</span>
                                            <span className="font-medium">Academy</span>
                                        </NavLink>
                                    </li>
                                    <li>
                                        <NavLink to="/developers" className={navItemClass}>
                                            <span className="text-xl">👩‍💻</span>
                                            <span className="font-medium">API & Dév</span>
                                        </NavLink>
                                    </li>
                                </ul>
                            </div>
                        )}

                        {/* Super Admin Section */}
                        {user?.is_superuser && (
                            <div>
                                <div className="px-4 mb-2 text-xs font-bold text-purple-500 uppercase tracking-wider">
                                    God Mode
                                </div>
                                <ul className="space-y-1">
                                    <li>
                                        <NavLink to="/superadmin" className={({ isActive }) =>
                                            `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                                                isActive
                                                    ? 'bg-purple-600/10 text-purple-500 border border-purple-500/20 shadow-[0_0_15px_rgba(168,85,247,0.1)]'
                                                    : 'text-gray-600 dark:text-gray-400 hover:text-purple-600 dark:hover:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/20'
                                            }`
                                        }>
                                            <span className="text-xl">⚡</span>
                                            <span className="font-medium">Superviseur</span>
                                        </NavLink>
                                    </li>
                                </ul>
                            </div>
                        )}
                    </nav>
                </div>

                {/* Profile Section (Bottom) */}
                <div className="p-4 border-t border-gray-200 dark:border-gray-800" ref={profileRef}>
                    <div className="relative">
                        <button 
                            onClick={() => setIsProfileOpen(!isProfileOpen)}
                            className="w-full flex items-center gap-3 p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800/50 transition-colors"
                        >
                            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white font-bold shadow-lg">
                                {user?.username?.charAt(0)?.toUpperCase() || user?.email?.charAt(0)?.toUpperCase() || 'U'}
                            </div>
                            <div className="flex-1 text-left">
                                <div className="text-sm font-bold text-gray-900 dark:text-white truncate">
                                    {user?.username}
                                </div>
                                <div className="text-xs text-gray-500 dark:text-gray-400 truncate">
                                    {user?.email || 'Admin'}
                                </div>
                            </div>
                            <div className="text-gray-400">
                                <svg xmlns="http://www.w3.org/2000/svg" className={`h-5 w-5 transition-transform ${isProfileOpen ? 'rotate-180' : ''}`} viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                                </svg>
                            </div>
                        </button>

                        {/* Dropdown Menu */}
                        {isProfileOpen && (
                            <div className="absolute bottom-full left-0 w-full mb-2 bg-white dark:bg-gray-900 rounded-xl shadow-[0_8px_30px_rgb(0,0,0,0.12)] dark:shadow-[0_8px_30px_rgba(0,0,0,0.3)] border border-gray-100 dark:border-gray-800 overflow-hidden transform origin-bottom animate-in slide-in-from-bottom-2 fade-in duration-200 z-50">
                                <div className="p-2 space-y-1">
                                    <Link to="/settings" onClick={() => setIsProfileOpen(false)} className="flex items-center gap-3 w-full px-3 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-colors">
                                        <span>⚙️</span> Paramètres du compte
                                    </Link>
                                    <button onClick={toggleTheme} className="flex items-center gap-3 w-full px-3 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-colors text-left">
                                        <span>{theme === 'light' ? '🌙' : '☀️'}</span> {theme === 'light' ? 'Mode sombre' : 'Mode clair'}
                                    </button>
                                    <div className="h-px bg-gray-100 dark:bg-gray-800 my-1"></div>
                                    <button onClick={logout} className="flex items-center gap-3 w-full px-3 py-2.5 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 rounded-lg transition-colors text-left">
                                        <span>🚪</span> Déconnexion
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto relative z-10 custom-scrollbar flex flex-col">
                {adminToken && (
                    <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-6 py-3 shadow-lg flex items-center justify-between z-50 shrink-0">
                        <div className="flex items-center gap-3">
                            <span className="text-2xl">🕵️</span>
                            <div>
                                <div className="font-bold text-sm">Mode Impersonation Actif</div>
                                <div className="text-xs text-purple-200">Vous agissez en tant que {user?.username}</div>
                            </div>
                        </div>
                        <button 
                            onClick={handleStopImpersonating}
                            className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm font-bold transition-colors border border-white/20 shadow-sm backdrop-blur-sm flex items-center gap-2"
                        >
                            <span>⚡</span> Quitter et redevenir Admin
                        </button>
                    </div>
                )}
                <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-[0.02] dark:opacity-[0.05] pointer-events-none mix-blend-overlay"></div>
                <div className="h-full relative flex-1">
                    <Outlet />
                </div>
            </main>
        </div>
    )
}

