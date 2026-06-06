import { useState, useEffect } from 'react'
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useReports } from '../contexts/ReportsContext'
import logo from '../assets/logo.png'

export default function Layout() {
    const { user, logout } = useAuth()
    const { hasNoReports, isProcessing, latestReport } = useReports()
    const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light')
    const location = useLocation()
    const navigate = useNavigate()

    // Forcer la navigation si un rapport est en cours de traitement
    useEffect(() => {
        if (isProcessing && latestReport?.id) {
            const targetPath = `/reports/${latestReport.id}`
            const currentPath = location.pathname.toLowerCase().replace(/\/$/, '')
            const allowedPaths = ['/logout', '/credits', '/academy']
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

    const toggleTheme = () => {
        setTheme(theme === 'light' ? 'dark' : 'light')
    }

    return (
        <div className="layout">
            <aside className="sidebar">
                <div className="sidebar-logo">
                    <img src={logo} alt="LedgerCarbon" style={{ width: '32px', height: '32px', objectFit: 'contain' }} />
                    <span className="brand-text">Ledger<span>Carbon</span></span>
                </div>

                <nav>
                    <ul className="sidebar-nav">
                        {/* On ne montre le Dashboard que s'il y a des rapports et qu'on n'est pas en processing */}
                        {!hasNoReports && !isProcessing && (
                            <li>
                                <NavLink to="/" end>
                                    📊 Dashboard
                                </NavLink>
                            </li>
                        )}
                        
                        {/* On masque le Nouveau rapport en mode processing */}
                        {!isProcessing && (
                            <li>
                                <NavLink to="/upload">
                                    📤 Nouveau rapport
                                </NavLink>
                            </li>
                        )}

                        {/* On masque Mes rapports s'il n'y a pas de rapports ou en mode processing */}
                        {!hasNoReports && !isProcessing && (
                            <li>
                                <NavLink to="/reports">
                                    📋 Mes rapports
                                </NavLink>
                            </li>
                        )}
                        
                        <li>
                            <NavLink to="/credits">
                                💳 Crédits
                            </NavLink>
                        </li>
                        <li>
                            <NavLink to="/academy">
                                📚 Academy
                            </NavLink>
                        </li>
                    </ul>
                </nav>

                <div style={{ marginTop: 'auto', padding: '20px' }}>
                    <div style={{ marginBottom: '10px', fontSize: '0.9rem', opacity: 0.8, color: 'var(--text-primary)' }}>
                        👤 {user?.username}
                    </div>
                    
                    <button
                        onClick={toggleTheme}
                        className="btn btn-secondary"
                        style={{ width: '100%', marginBottom: '10px', padding: '8px', fontSize: '0.9rem' }}
                    >
                        {theme === 'light' ? '🌙 Mode Nuit' : '☀️ Mode Jour'}
                    </button>

                    <button
                        onClick={logout}
                        className="btn btn-secondary"
                        style={{ width: '100%', padding: '8px', fontSize: '0.9rem' }}
                    >
                        🚪 Déconnexion
                    </button>
                </div>
            </aside>

            <main className="main-content bg-bgPrimary">
                <Outlet />
            </main>
        </div>
    )
}
