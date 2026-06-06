import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

interface MatrixPoint {
    topic: string;
    impact: number;
    financial: number;
    is_material: boolean;
}

interface MaterialityMatrixProps {
    reportId: number;
}

export default function MaterialityMatrix({ reportId }: MaterialityMatrixProps) {
    const [matrixData, setMatrixData] = useState<MatrixPoint[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        loadData();
    }, [reportId]);

    const loadData = async () => {
        setLoading(true);
        setError('');
        try {
            const response = await api.get<{ data: { computed_matrix?: MatrixPoint[] } }>(`/reports/${reportId}/materiality-assessment/`);
            if (response && response.data && response.data.computed_matrix) {
                setMatrixData(response.data.computed_matrix);
            } else {
                setMatrixData([]);
            }
        } catch (err: any) {
            if (err?.message !== 'Not found' && !err?.message?.includes('404')) {
                setError('Erreur lors du chargement de la matrice.');
            }
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="p-8 text-center text-gray-500">Chargement de la matrice...</div>;
    }

    if (error) {
        return <div className="p-8 text-center text-red-500">{error}</div>;
    }

    if (matrixData.length === 0) {
        return (
            <div className="card" style={{ marginTop: '32px', textAlign: 'center', color: 'var(--text-secondary)', padding: '32px' }}>
                <p>Aucune donnée disponible. Veuillez d'abord remplir le questionnaire IRO et le sauvegarder.</p>
            </div>
        );
    }

    const materialTopics = matrixData.filter(d => d.is_material);

    return (
        <div className="card" style={{ marginTop: '32px' }}>
            <div className="card-header">
                <h2>Matrice de Double Matérialité</h2>
                <button onClick={loadData} className="btn btn-secondary btn-sm">
                    ↻ Rafraîchir
                </button>
            </div>
            
            <div className="flex flex-col lg:flex-row gap-8 mt-8">
                {/* Matrice Graph */}
                <div className="flex-1 relative pb-12 pl-12">
                    <div className="relative w-full aspect-square border-l-2 border-b-2 border-gray-800">
                        {/* Axes labels */}
                        <div className="absolute -left-16 top-1/2 -rotate-90 origin-center font-semibold text-gray-600 whitespace-nowrap">
                            Matérialité d'Impact
                        </div>
                        <div className="absolute -bottom-16 left-1/2 -translate-x-1/2 font-semibold text-gray-600 whitespace-nowrap">
                            Matérialité Financière
                        </div>

                        {/* Grid lines & Thresholds */}
                        <div className="absolute left-0 right-0 top-1/2 border-t-2 border-dashed border-gray-400 z-0"></div> {/* 2.5 on Y axis */}
                        <div className="absolute top-0 bottom-0 left-1/2 border-l-2 border-dashed border-gray-400 z-0"></div> {/* 2.5 on X axis */}

                        {/* Background Zones */}
                        <div className="absolute top-0 right-0 w-1/2 h-1/2 bg-red-50/50 z-0"></div> {/* Top right */}
                        <div className="absolute top-0 left-0 w-1/2 h-1/2 bg-yellow-50/50 z-0"></div> {/* Top left */}
                        <div className="absolute bottom-0 right-0 w-1/2 h-1/2 bg-yellow-50/50 z-0"></div> {/* Bottom right */}
                        
                        {/* Data Points */}
                        {matrixData.map((point, idx) => {
                            // Scale 1 to 4 -> 0% to 100%
                            const xPercent = ((point.financial - 1) / 3) * 100;
                            const yPercent = ((point.impact - 1) / 3) * 100;
                            
                            const colors: Record<string, string> = {
                                "Environnement": "#10b981",
                                "Social": "#3b82f6",
                                "Gouvernance": "#8b5cf6"
                            };
                            const colorClass = colors[point.topic] || "#6b7280";

                            return (
                                <div 
                                    key={idx}
                                    className="absolute w-4 h-4 rounded-full -translate-x-1/2 translate-y-1/2 cursor-pointer hover:scale-125 transition-transform z-10 shadow-md"
                                    style={{ left: `${Math.max(0, Math.min(100, xPercent))}%`, bottom: `${Math.max(0, Math.min(100, yPercent))}%`, backgroundColor: colorClass }}
                                    title={`${point.topic}\nImpact: ${point.impact}\nFinancier: ${point.financial}`}
                                >
                                    <span className="absolute top-5 left-1/2 -translate-x-1/2 text-xs font-semibold whitespace-nowrap bg-white/80 px-1 rounded shadow-sm">
                                        {point.topic}
                                    </span>
                                </div>
                            );
                        })}
                        
                        {/* Axis Min/Max Labels */}
                        <div className="absolute text-xs text-gray-500 font-bold" style={{ bottom: '-24px', left: '0' }}>1</div>
                        <div className="absolute text-xs text-gray-500 font-bold" style={{ bottom: '-24px', right: '0' }}>4</div>
                        <div className="absolute text-xs text-gray-500 font-bold" style={{ left: '-24px', bottom: '0' }}>1</div>
                        <div className="absolute text-xs text-gray-500 font-bold" style={{ left: '-24px', top: '0' }}>4</div>
                    </div>
                </div>

                {/* Legend & Results */}
                <div className="w-full lg:w-80 flex flex-col gap-4">
                    <div className="card bg-gray-50">
                        <h4 className="font-semibold mb-4">Enjeux Matériels (Prioritaires)</h4>
                        {materialTopics.length > 0 ? (
                            <ul className="list-none p-0 m-0">
                                {materialTopics.map((topic, idx) => (
                                    <li key={idx} className="flex items-center gap-2 mb-2 p-2 bg-white rounded border border-gray-200">
                                        <span className="text-xl">⚠️</span> {topic.topic}
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <p className="text-sm text-gray-500">Aucun enjeu n'a franchi le seuil de matérialité (2.5).</p>
                        )}
                        <p className="text-xs text-gray-400 mt-4">
                            * Selon la CSRD, un enjeu est matériel s'il franchit le seuil d'impact OU le seuil financier.
                        </p>
                    </div>

                    <div className="card">
                        <h4 className="font-semibold mb-4">Scores détaillés</h4>
                        <div>
                            {matrixData.map((point, idx) => (
                                <div key={idx} className="mb-4">
                                    <div className="font-semibold text-sm mb-1">{point.topic}</div>
                                    <div className="flex justify-between text-xs text-gray-600 mb-1">
                                        <span>Impact: <strong>{point.impact}</strong></span>
                                        <span>Financier: <strong>{point.financial}</strong></span>
                                    </div>
                                    {/* Mini progress bars */}
                                    <div className="flex flex-col gap-1">
                                        <div className="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
                                            <div className="h-full rounded-full" style={{ width: `${((point.impact)/4)*100}%`, backgroundColor: '#818cf8' }}></div>
                                        </div>
                                        <div className="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
                                            <div className="h-full rounded-full" style={{ width: `${((point.financial)/4)*100}%`, backgroundColor: '#60a5fa' }}></div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
