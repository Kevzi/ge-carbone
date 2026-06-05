import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function Layout() {
    const { user, logout } = useAuth()

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
                    <div style={{ marginBottom: '10px', fontSize: '0.9rem', opacity: 0.8 }}>
                        {user?.username}
                    </div>
                    <button
                        onClick={logout}
                        className="btn btn-secondary"
                        style={{ width: '100%' }}
                    >
                        Déconnexion
                    </button>
                </div>
            </aside>

            <main className="main-content">
                <Outlet />
            </main>
        </div>
    )
}
