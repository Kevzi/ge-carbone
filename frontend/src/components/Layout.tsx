import { useState, useEffect } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function Layout() {
    const { user, logout } = useAuth()
    const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light')

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
                    🌿 Ledger<span>Carbon</span>
                </div>

                <nav>
                    <ul className="sidebar-nav">
                        <li>
                            <NavLink to="/" end>
                                📊 Dashboard
                            </NavLink>
                        </li>
                        <li>
                            <NavLink to="/upload">
                                📤 Nouveau rapport
                            </NavLink>
                        </li>
                        <li>
                            <NavLink to="/reports">
                                📋 Mes rapports
                            </NavLink>
                        </li>
                        <li>
                            <NavLink to="/credits">
                                💳 Crédits
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
