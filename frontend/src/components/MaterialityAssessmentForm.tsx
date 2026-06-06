import { useState, useEffect } from 'react'
import { api } from '../services/api'

interface Question {
  id: string
  text: string
  description?: string
  type: 'boolean' | 'scale' | 'text'
}

interface Step {
  title: string
  description: string
  questions: Question[]
}

const WIZARD_STEPS: Step[] = [
  {
    title: "1. Impacts Environnementaux (E)",
    description: "Évaluez les impacts de votre entreprise sur l'environnement.",
    questions: [
      { id: "E1_1", text: "Votre entreprise a-t-elle un impact significatif sur le changement climatique (émissions GES directes ou indirectes) ?", type: "scale" },
      { id: "E2_1", text: "Générez-vous une pollution de l'air, de l'eau ou des sols au-delà des seuils réglementaires minimums ?", type: "scale" },
      { id: "E3_1", text: "Quelle est l'intensité de votre consommation en eau dans des zones de stress hydrique ?", type: "scale" },
    ]
  },
  {
    title: "2. Impacts Sociaux (S)",
    description: "Évaluez les impacts sociaux, incluant votre main d'œuvre et les communautés affectées.",
    questions: [
      { id: "S1_1", text: "Y a-t-il des risques identifiés concernant les conditions de travail dans votre chaîne de valeur ?", type: "scale" },
      { id: "S2_1", text: "Avez-vous des politiques d'égalité des chances et de non-discrimination en place ?", type: "boolean" },
    ]
  },
  {
    title: "3. Gouvernance (G)",
    description: "Évaluez vos processus de gouvernance et d'éthique des affaires.",
    questions: [
      { id: "G1_1", text: "Avez-vous mis en place un code de conduite éthique strict ?", type: "boolean" },
      { id: "G2_1", text: "Quel est votre niveau d'exposition aux risques de corruption selon vos marchés ?", type: "scale" },
    ]
  }
]

interface MaterialityAssessmentFormProps {
  reportId: number
}

export default function MaterialityAssessmentForm({ reportId }: MaterialityAssessmentFormProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [answers, setAnswers] = useState<Record<string, any>>({})
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState({ text: '', type: '' })

  useEffect(() => {
    loadAssessment()
  }, [reportId])

  const loadAssessment = async () => {
    setLoading(true)
    try {
      const response = await api.get<any>(`/reports/${reportId}/materiality-assessment/`)
      if (response && response.data) {
        setAnswers(response.data)
      }
    } catch (err: any) {
      if (err.message !== 'Not found' && !err.message?.includes('404')) {
        console.error("Failed to load assessment:", err)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async (isFinal = false) => {
    setSaving(true)
    setMessage({ text: '', type: '' })
    try {
      // Check if it exists to know if we POST or PUT
      let exists = false
      try {
        await api.get(`/reports/${reportId}/materiality-assessment/`)
        exists = true
      } catch (e) {
        exists = false
      }

      if (exists) {
        await api.put(`/reports/${reportId}/materiality-assessment/`, { data: answers })
      } else {
        await api.post(`/reports/${reportId}/materiality-assessment/`, { data: answers })
      }
      
      setMessage({ text: isFinal ? 'Évaluation terminée et sauvegardée !' : 'Brouillon sauvegardé.', type: 'success' })
      if (!isFinal) {
         setTimeout(() => setMessage({text:'', type:''}), 3000)
      }
    } catch (err) {
      console.error(err)
      setMessage({ text: 'Erreur lors de la sauvegarde.', type: 'error' })
    } finally {
      setSaving(false)
    }
  }

  const handleNext = () => {
    if (currentStep < WIZARD_STEPS.length - 1) {
      setCurrentStep(c => c + 1)
      handleSave() // Autosave draft
    }
  }

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(c => c - 1)
    }
  }

  const handleAnswer = (questionId: string, value: any) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }))
  }

  if (loading) {
    return <div className="p-8 text-center"><span className="spinner"></span> Chargement du questionnaire...</div>
  }

  const step = WIZARD_STEPS[currentStep]

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-xl shadow-sm border border-gray-100">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Questionnaire IRO</h2>
        <p className="text-gray-600">Évaluation de la Double Matérialité (Impacts, Risques, Opportunités)</p>
      </div>

      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between mb-2">
          {WIZARD_STEPS.map((_, idx) => (
            <div key={idx} className={`text-sm font-medium ${idx === currentStep ? 'text-blue-600' : 'text-gray-400'}`}>
              Étape {idx + 1}
            </div>
          ))}
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className="h-full bg-blue-600 transition-all duration-300"
            style={{ width: `${((currentStep + 1) / WIZARD_STEPS.length) * 100}%` }}
          ></div>
        </div>
      </div>

      {/* Step Content */}
      <div className="mb-8 min-h-[300px]">
        <h3 className="text-xl font-semibold text-gray-800 mb-2">{step.title}</h3>
        <p className="text-gray-600 mb-6 pb-4 border-b">{step.description}</p>

        <div className="space-y-6">
          {step.questions.map(q => (
            <div key={q.id} className="p-4 bg-gray-50 rounded-lg border border-gray-100">
              <label className="block text-gray-800 font-medium mb-3">{q.text}</label>
              
              {q.type === 'boolean' && (
                <div className="flex gap-4">
                  <button 
                    onClick={() => handleAnswer(q.id, true)}
                    className={`px-6 py-2 rounded-md font-medium transition-colors ${answers[q.id] === true ? 'bg-blue-600 text-white' : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'}`}
                  >Oui</button>
                  <button 
                    onClick={() => handleAnswer(q.id, false)}
                    className={`px-6 py-2 rounded-md font-medium transition-colors ${answers[q.id] === false ? 'bg-blue-600 text-white' : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'}`}
                  >Non</button>
                </div>
              )}

              {q.type === 'scale' && (
                <div className="flex flex-col space-y-2">
                  <div className="flex justify-between text-xs text-gray-500 px-1">
                    <span>Faible</span>
                    <span>Modéré</span>
                    <span>Élevé</span>
                    <span>Critique</span>
                  </div>
                  <input 
                    type="range" 
                    min="1" max="4" 
                    step="1"
                    value={answers[q.id] || 1}
                    onChange={(e) => handleAnswer(q.id, parseInt(e.target.value))}
                    className="w-full accent-blue-600"
                  />
                  <div className="text-center font-bold text-blue-600">
                    {answers[q.id] === 1 && '1 - Faible'}
                    {answers[q.id] === 2 && '2 - Modéré'}
                    {answers[q.id] === 3 && '3 - Élevé'}
                    {answers[q.id] === 4 && '4 - Critique'}
                    {!answers[q.id] && '1 - Faible (Défaut)'}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Footer Controls */}
      <div className="flex justify-between items-center pt-6 border-t">
        <button 
          onClick={handlePrev}
          disabled={currentStep === 0}
          className="px-6 py-2 rounded-md text-gray-600 font-medium hover:bg-gray-100 disabled:opacity-50"
        >
          ← Précédent
        </button>
        
        <div className="flex items-center gap-4">
          {message.text && (
            <span className={`text-sm ${message.type === 'success' ? 'text-green-600' : 'text-red-600'}`}>
              {message.text}
            </span>
          )}
          
          {currentStep < WIZARD_STEPS.length - 1 ? (
            <button 
              onClick={handleNext}
              disabled={saving}
              className="px-6 py-2 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? 'Sauvegarde...' : 'Suivant →'}
            </button>
          ) : (
            <button 
              onClick={() => handleSave(true)}
              disabled={saving}
              className="px-6 py-2 bg-green-600 text-white rounded-md font-medium hover:bg-green-700 disabled:opacity-50"
            >
              {saving ? 'Sauvegarde...' : '✓ Terminer l\'évaluation'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
