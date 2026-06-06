import React from 'react';

interface ConfirmModalProps {
    isOpen: boolean;
    title: string;
    message: string;
    confirmLabel?: string;
    cancelLabel?: string;
    onConfirm: () => void;
    onCancel: () => void;
}

export default function ConfirmModal({
    isOpen,
    title,
    message,
    confirmLabel = "Confirmer",
    cancelLabel = "Annuler",
    onConfirm,
    onCancel
}: ConfirmModalProps) {
    if (!isOpen) return null;

    return (
        <div className="modal-overlay" style={{ zIndex: 1000 }} role="dialog" aria-modal="true" aria-labelledby="modal-title">
            <div className="modal-content" style={{ maxWidth: '450px', padding: '24px', borderRadius: '12px' }}>
                <div className="modal-header" style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h2 id="modal-title" style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>{title}</h2>
                    <button className="modal-close" onClick={onCancel} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }} aria-label="Fermer">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                </div>
                <div className="modal-body" style={{ color: 'var(--text-secondary)', marginBottom: '24px', lineHeight: '1.5' }}>
                    <p>{message}</p>
                </div>
                <div className="modal-footer" style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                    <button className="btn btn-secondary" onClick={onCancel}>
                        {cancelLabel}
                    </button>
                    <button className="btn btn-error" onClick={onConfirm} style={{ backgroundColor: '#dc2626', color: 'white', border: 'none', padding: '0.5rem 1rem', borderRadius: '0.375rem', cursor: 'pointer' }}>
                        {confirmLabel}
                    </button>
                </div>
            </div>
        </div>
    );
}
