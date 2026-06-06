import { createContext, useContext, useState, useEffect } from 'react'
import type { ReactNode } from 'react'
import { api } from '../services/api'

export interface Report {
    id: number
    fiscal_year: string
    status: string
    progress_percent?: number
    total_co2_kg: number | null
    created_at: string
}

interface ReportsContextType {
    reports: Report[]
    latestReport: Report | null
    loading: boolean
    hasNoReports: boolean
    isProcessing: boolean
    refreshReports: () => Promise<void>
}

const ReportsContext = createContext<ReportsContextType | undefined>(undefined)

export function ReportsProvider({ children }: { children: ReactNode }) {
    const [reports, setReports] = useState<Report[]>([])
    const [loading, setLoading] = useState(true)

    const refreshReports = async () => {
        try {
            const response = await api.get<any>('/reports/')
            const reportsList = Array.isArray(response) ? response : response.results || []
            // Tri par date décroissante pour avoir le plus récent en premier
            const sorted = reportsList.sort((a: Report, b: Report) => 
                new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
            )
            setReports(sorted)
        } catch (error) {
            console.error('Failed to load reports in context:', error)
        } finally {
            setLoading(false)
        }
    }

    // Chargement initial
    useEffect(() => {
        refreshReports()
    }, [])

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
    }, [isProcessing, isFailed])

    return (
        <ReportsContext.Provider value={{
            reports,
            latestReport,
            loading,
            hasNoReports,
            isProcessing,
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
