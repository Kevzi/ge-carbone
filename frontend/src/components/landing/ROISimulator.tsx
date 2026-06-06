import React, { useState, useEffect } from 'react';

const ROISimulator: React.FC = () => {
  const [volume, setVolume] = useState<number | ''>(50);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    setIsAnimating(true);
    const timer = setTimeout(() => setIsAnimating(false), 300);
    return () => clearTimeout(timer);
  }, [volume]);

  const handleVolumeChange = (val: string) => {
    if (val === '') {
      setVolume('');
      return;
    }
    let parsed = Math.floor(Number(val));
    if (parsed < 0) parsed = 0;
    if (parsed > 500) parsed = 500;
    setVolume(parsed);
  };

  const currentVolume = typeof volume === 'number' ? volume : 0;
  const costPerReport = 90;
  const pricePerReport = 1500;
  
  const marginPerReport = pricePerReport - costPerReport;
  const totalMargin = marginPerReport * currentVolume;

  const classicTimeHours = 15;
  const ledgerCarbonTimeHours = 0.5;

  const equivalentHourlyRate = (ledgerCarbonTimeHours > 0 && currentVolume > 0) 
    ? totalMargin / (ledgerCarbonTimeHours * currentVolume) 
    : 0;

  return (
    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-8 shadow-xl max-w-5xl mx-auto my-16 relative overflow-hidden group">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 pointer-events-none transition-opacity duration-500 group-hover:opacity-100 opacity-50"></div>
      
      <div className="text-center mb-10 relative z-10">
        <h3 className="text-3xl font-bold brand-text mb-4">Simulateur de ROI interactif</h3>
        <p className="text-[var(--text-secondary)]">Calculez instantanément votre marge et votre taux horaire équivalent avec LedgerCarbon.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-12 items-center relative z-10">
        {/* Input Section */}
        <div className="space-y-6">
          <label htmlFor="volume-input" className="block text-lg font-semibold mb-2">
            Volume estimé de rapports CSRD / an
          </label>
          <div className="flex items-center gap-4">
            <input 
              id="volume-slider"
              type="range" 
              min="1" 
              max="500" 
              value={currentVolume} 
              onChange={(e) => handleVolumeChange(e.target.value)}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
            <input 
              id="volume-input"
              type="number" 
              min="1" 
              max="500"
              value={volume}
              onChange={(e) => handleVolumeChange(e.target.value)}
              className="w-24 px-3 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded-lg text-center font-bold text-xl focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>
          <div className="bg-blue-500/10 border border-blue-500/20 p-4 rounded-xl mt-6">
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              💡 <span className="font-semibold text-blue-400">Hypothèses :</span><br/>
              Prix de facturation cible : {pricePerReport}€ / rapport<br/>
              Coût de génération LedgerCarbon : {costPerReport}€ / rapport
            </p>
          </div>
        </div>

        {/* Results Section */}
        <div className="space-y-6">
          <div className="bg-[var(--bg-primary)] p-6 rounded-xl border border-[var(--border-color)] transform transition-all hover:scale-105 hover:shadow-lg hover:shadow-blue-500/20 duration-300">
            <p className="text-sm text-[var(--text-secondary)] font-medium mb-1">Marge potentielle générée</p>
            <div className={`text-5xl font-extrabold brand-text text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300 ${isAnimating ? 'scale-105 opacity-80' : 'scale-100 opacity-100'}`}>
              {totalMargin.toLocaleString('fr-FR')} €
            </div>
          </div>
          
          <div className="bg-[var(--bg-primary)] p-6 rounded-xl border border-[var(--border-color)] transform transition-all hover:scale-105 hover:shadow-lg hover:shadow-green-500/20 duration-300 delay-75">
            <p className="text-sm text-[var(--text-secondary)] font-medium mb-1">Taux horaire équivalent</p>
            <div className={`text-5xl font-extrabold text-green-400 brand-text transition-all duration-300 ${isAnimating ? 'scale-105 opacity-80' : 'scale-100 opacity-100'}`}>
              {Math.round(equivalentHourlyRate).toLocaleString('fr-FR')} € / h
            </div>
            <p className="text-xs text-[var(--text-secondary)] mt-3 opacity-80">
              Basé sur {ledgerCarbonTimeHours}h de temps passé avec LedgerCarbon (contre {classicTimeHours}h en méthode classique).
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ROISimulator;
