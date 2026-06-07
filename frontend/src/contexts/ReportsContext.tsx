import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import type { ReactNode } from 'react'
import { api } from '../services/api'

export interface Report {
    id: number
    fiscal_year: string
    status: string
    progress_percent?: number
    total_co2_kg: number | null
    created_at: string
    client_name?: string
    average_dqr?: string | number
}

export interface PaginatedResponse<T> {
    count?: number
    next?: string | null
    previous?: string | null
    results: T[]
}

interface ReportsContextType {
    reports: Report[]
    latestReport: Report | null
    loading: boolean
    hasNoReports: boolean
    isProcessing: boolean
    error: string | null
    refreshReports: () => Promise<void>
}

const ReportsContext = createContext<ReportsContextType | undefined>(undefined)

export function ReportsProvider({ children }: { children: ReactNode }) {
    const [reports, setReports] = useState<Report[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    const refreshReports = useCallback(async () => {
        try {
            const response = await api.get<PaginatedResponse<Report> | Report[]>('/reports/')
            const reportsList = Array.isArray(response) ? response : response?.results || []
            // Tri par date décroissante pour avoir le plus récent en premier
            const sorted = reportsList.sort((a: Report, b: Report) => 
                (new Date(b.created_at).getTime() || 0) - (new Date(a.created_at).getTime() || 0)
            )
            setReports(sorted)
            setError(null)
        } catch (err) {
            console.error('Failed to load reports in context:', err)
            setError('Erreur lors du chargement des rapports')
        } finally {
            setLoading(false)
        }
    }, [])

    // Chargement initial
    useEffect(() => {
        refreshReports()
    }, [refreshReports])

    const latestReport = reports.length > 0 ? reports[0] : null
    const hasNoReports = reports.length === 0 && !loading
    const isProcessing = latestReport?.status === 'processing' || latestReport?.status === 'pending'
    const isFailed = latestReport?.status === 'failed'

    // Polling si processing
    useEffect(() => {
        let intervalId: ReturnType<typeof setInterval> | undefined

        if (isProcessing && !isFailed) {
            intervalId = setInterval(() => {
                refreshReports()
            }, 3000)
        }

        return () => {
            if (intervalId) {
                clearInterval(intervalId)
            }
        }
    }, [isProcessing, isFailed, refreshReports])

    return (
        <ReportsContext.Provider value={{
            reports,
            latestReport,
            loading,
            hasNoReports,
            isProcessing,
            error,
            refreshReports
        }}>
            {children}
        </ReportsContext.Provider>
    )
}

export function useReports() {
    const context = useContext(ReportsContext)
    if (context === undefined) {
        throw new Error('useReports must be used within a ReportsProvider')
    }
    return context
}
