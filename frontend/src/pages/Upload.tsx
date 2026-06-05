import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../services/api'

export default function Upload() {
    const [file, setFile] = useState<File | null>(null)
    const [clientName, setClientName] = useState('')
    const [clientSiret, setClientSiret] = useState('')
    const [fiscalYear, setFiscalYear] = useState(new Date().getFullYear().toString())
    const [uploading, setUploading] = useState(false)
    const [error, setError] = useState('')
    const [dragOver, setDragOver] = useState(false)
    const fileInputRef = useRef<HTMLInputElement>(null)
    const navigate = useNavigate()

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        setDragOver(false)

        const droppedFile = e.dataTransfer.files[0]
        if (droppedFile) {
            validateAndSetFile(droppedFile)
        }
    }

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0]
        if (selectedFile) {
            validateAndSetFile(selectedFile)
        }
    }

    const validateAndSetFile = (file: File) => {
        setError('')

        // Check file extension
        const validExtensions = ['.txt', '.csv']
        const ext = file.name.toLowerCase().slice(file.name.lastIndexOf('.'))

        if (!validExtensions.includes(ext)) {
            setError('Format non supporté. Utilisez un fichier .txt ou .csv')
            return
        }

        // Check file size (max 50MB)
        if (file.size > 50 * 1024 * 1024) {
            setError('Fichier trop volumineux (max 50 Mo)')
            return
        }

        setFile(file)
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        if (!file) {
            setError('Veuillez sélectionner un fichier FEC')
            return
        }

        if (!clientName.trim()) {
            setError('Veuillez saisir le nom du client')
            return
        }

        setUploading(true)
        setError('')

        try {
            const response = await api.uploadFile<{ id: number }>('/reports/', file, {
                client_name: clientName.trim(),
                client_siret: clientSiret.trim(),
                fiscal_year: fiscalYear
            })

            navigate(`/reports/${response.id}`)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Échec de l\'upload')
        } finally {
            setUploading(false)
        }
    }

    const formatFileSize = (bytes: number) => {
        if (bytes < 1024) return `${bytes} o`
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} Ko`
        return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`
    }

    return (
        <div className="upload-page">
            <header className="page-header">
                <h1>📤 Nouveau rapport carbone</h1>
                <p>Importez votre fichier FEC pour générer un bilan carbone CSRD</p>
            </header>

            <div className="upload-container">
                <form onSubmit={handleSubmit}>
                    {error && (
                        <div className="alert alert-error">
                            {error}
                        </div>
                    )}

                    {/* Client Name */}
                    <div className="form-group">
                        <label htmlFor="clientName">Nom du client *</label>
                        <input
                            id="clientName"
                            type="text"
                            value={clientName}
                            onChange={(e) => setClientName(e.target.value)}
                            placeholder="Ex: SARL Dupont & Associés"
                            required
                        />
                    </div>

                    {/* Client SIRET (optional) */}
                    <div className="form-group">
                        <label htmlFor="clientSiret">SIRET (optionnel)</label>
                        <input
                            id="clientSiret"
                            type="text"
                            value={clientSiret}
                            onChange={(e) => setClientSiret(e.target.value)}
                            placeholder="123 456 789 00012"
                            maxLength={14}
                        />
                    </div>

                    {/* Fiscal Year */}
                    <div className="form-group">
                        <label htmlFor="fiscalYear">Exercice fiscal</label>
                        <select
                            id="fiscalYear"
                            value={fiscalYear}
                            onChange={(e) => setFiscalYear(e.target.value)}
                        >
                            {[...Array(5)].map((_, i) => {
                                const year = new Date().getFullYear() - i
                                return (
                                    <option key={year} value={year.toString()}>
                                        {year}
                                    </option>
                                )
                            })}
                        </select>
                    </div>

                    {/* Dropzone */}
                    <div
                        className={`dropzone ${dragOver ? 'dropzone-active' : ''} ${file ? 'dropzone-filled' : ''}`}
                        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
                        onDragLeave={() => setDragOver(false)}
                        onDrop={handleDrop}
                        onClick={() => fileInputRef.current?.click()}
                    >
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".txt,.csv"
                            onChange={handleFileSelect}
                            style={{ display: 'none' }}
                        />

                        {file ? (
                            <div className="dropzone-file">
                                <div className="file-icon">📄</div>
                                <div className="file-info">
                                    <span className="file-name">{file.name}</span>
                                    <span className="file-size">{formatFileSize(file.size)}</span>
                                </div>
                                <button
                                    type="button"
                                    className="file-remove"
                                    onClick={(e) => { e.stopPropagation(); setFile(null) }}
                                >
                                    ✕
                                </button>
                            </div>
                        ) : (
                            <div className="dropzone-placeholder">
                                <div className="dropzone-icon">📁</div>
                                <p className="dropzone-text">
                                    Glissez-déposez votre fichier FEC ici
                                </p>
                                <p className="dropzone-hint">
                                    ou cliquez pour sélectionner
                                </p>
                                <span className="dropzone-formats">
                                    Formats acceptés : .txt, .csv (max 50 Mo)
                                </span>
                            </div>
                        )}
                    </div>

                    {/* Info Card */}
                    <div className="info-card">
                        <h3>ℹ️ Qu'est-ce qu'un fichier FEC ?</h3>
                        <p>
                            Le Fichier des Écritures Comptables (FEC) est un export standardisé
                            de votre logiciel comptable, conforme à l'article A47 A-1 du LPF.
                        </p>
                        <ul>
                            <li>📊 18 colonnes obligatoires</li>
                            <li>📅 Format de date : AAAAMMJJ</li>
                            <li>💰 Montants : 2 décimales</li>
                        </ul>
                    </div>

                    {/* Submit */}
                    <button
                        type="submit"
                        className="btn btn-primary btn-lg"
                        disabled={!file || !clientName.trim() || uploading}
                        style={{ width: '100%' }}
                    >
                        {uploading ? (
                            <>
                                <span className="spinner"></span>
                                Traitement en cours...
                            </>
                        ) : (
                            '🚀 Générer le rapport'
                        )}
                    </button>

                    <p className="upload-cost">
                        💳 Ce rapport consommera <strong>1 crédit</strong>
                    </p>
                </form>
            </div>
        </div>
    )
}
