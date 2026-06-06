export const API_BASE_URL = 'http://localhost:8000/api/v1'

class ApiService {
    private getHeaders(): HeadersInit {
        const headers: HeadersInit = {
            'Content-Type': 'application/json',
        }

        const token = localStorage.getItem('access_token')
        if (token) {
            headers['Authorization'] = `Bearer ${token}`
        }

        return headers
    }

    async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
        const url = `${API_BASE_URL}${endpoint}`

        const response = await fetch(url, {
            ...options,
            headers: {
                ...this.getHeaders(),
                ...options.headers,
            },
        })

        if (response.status === 401) {
            // Try to refresh token
            const refreshed = await this.refreshToken()
            if (refreshed) {
                return this.request(endpoint, options)
            }
            // Redirect to login
            window.location.href = '/login'
        }

        if (!response.ok) {
            const error = await response.json().catch(() => ({}))
            throw new Error(error.detail || error.error || 'Request failed')
        }

        if (response.status === 204) {
            return null as unknown as T
        }

        return response.json()
    }

    async refreshToken(): Promise<boolean> {
        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) return false

        try {
            const response = await fetch(`${API_BASE_URL}/auth/refresh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: refreshToken }),
            })

            if (response.ok) {
                const data = await response.json()
                localStorage.setItem('access_token', data.access)
                return true
            }
        } catch {
            // Refresh failed
        }

        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        return false
    }

    get<T>(endpoint: string): Promise<T> {
        return this.request<T>(endpoint, { method: 'GET' })
    }

    post<T>(endpoint: string, data?: unknown): Promise<T> {
        return this.request<T>(endpoint, {
            method: 'POST',
            body: data ? JSON.stringify(data) : undefined,
        })
    }

    patch<T>(endpoint: string, data?: unknown): Promise<T> {
        return this.request<T>(endpoint, {
            method: 'PATCH',
            body: data ? JSON.stringify(data) : undefined,
        })
    }

    put<T>(endpoint: string, data?: unknown): Promise<T> {
        return this.request<T>(endpoint, {
            method: 'PUT',
            body: data ? JSON.stringify(data) : undefined,
        })
    }

    delete<T>(endpoint: string): Promise<T> {
        return this.request<T>(endpoint, { method: 'DELETE' })
    }

    async uploadFile<T>(endpoint: string, file: File, data: Record<string, string>): Promise<T> {
        const formData = new FormData()
        formData.append('file', file)
        Object.entries(data).forEach(([key, value]) => {
            formData.append(key, value)
        })

        const token = localStorage.getItem('access_token')
        const headers: HeadersInit = {}
        if (token) {
            headers['Authorization'] = `Bearer ${token}`
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers,
            body: formData,
        })

        if (!response.ok) {
            const error = await response.json().catch(() => ({}))
            throw new Error(error.detail || error.error || 'Upload failed')
        }

        return response.json()
    }
}

export const api = new ApiService()
