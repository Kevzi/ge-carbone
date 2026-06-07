import { Navigate, Outlet } from 'react'
import { useAuth } from '../contexts/AuthContext'

export function SuperAdminRoute() {
    const { user, isAuthenticated, loading } = useAuth()

    if (loading) {
        return <div className="flex h-screen items-center justify-center bg-gray-50 text-gray-400">Vérification des droits...</div>
    }

    if (!isAuthenticated || !user?.is_superuser) {
        return <Navigate to="/" replace />
    }

    return <Outlet />
}
