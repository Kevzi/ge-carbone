import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import { api } from '../services/api'

interface User {
    id: number
    username: string
    email: string
    role: string
    cabinet?: {
        id: number
        name: string
    }
    credits_remaining: number
    is_superuser?: boolean
}

interface AuthContextType {
    user: User | null
    isAuthenticated: boolean
    loading: boolean
    login: (username: string, password: string) => Promise<boolean>
    logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [loading, setLoading] = useState(true)

    const checkAuth = async () => {
        const token = localStorage.getItem('access_token')
        if (token) {
            try {
                const userData = await api.get<User>('/users/me/')
                setUser(userData)
            } catch {
                localStorage.removeItem('access_token')
                localStorage.removeItem('refresh_token')
            }
        }
        setLoading(false)
    }

    useEffect(() => {
        checkAuth()
    }, [])

    const login = async (username: string, password: string): Promise<boolean> => {
        try {
            const response = await api.post<{ access: string, refresh: string }>('/auth/login/', { username, password })
            localStorage.setItem('access_token', response.access)
            localStorage.setItem('refresh_token', response.refresh)

            const userData = await api.get<User>('/users/me/')
            setUser(userData)
            return true
        } catch {
            return false
        }
    }

    const logout = () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        setUser(null)
    }

    return (
        <AuthContext.Provider value={{
            user,
            isAuthenticated: !!user,
            loading,
            login,
            logout
        }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}
