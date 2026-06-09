import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import Reports from './pages/Reports'
import ReportDetail from './pages/ReportDetail'
import Credits from './pages/Credits'
import Landing from './pages/Landing'
import Academy from './pages/Academy'
import ApiPortal from './pages/ApiPortal'
import Settings from './pages/Settings'
import SuperAdminDashboard from './pages/superadmin/SuperAdminDashboard'
import { SuperAdminRoute } from './components/SuperAdminRoute'

// Static Pages
import ComingSoon from './pages/ComingSoon'
import Security from './pages/legal/Security'
import Privacy from './pages/legal/Privacy'
import CGV from './pages/legal/CGV'
import MentionsLegales from './pages/legal/MentionsLegales'
import Pricing from './pages/product/Pricing'
import About from './pages/company/About'
import { ReportsProvider } from './contexts/ReportsContext'
import './App.css'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Chargement...</p>
      </div>
    )
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/landing" />
}

function AppRoutes() {
  const { isAuthenticated } = useAuth()

  return (
    <Routes>
      <Route
        path="/landing"
        element={isAuthenticated ? <Navigate to="/" /> : <Landing />}
      />
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/" /> : <Login />}
      />
      
      {/* Static Public Routes */}
      <Route path="/legal/mentions-legales" element={<MentionsLegales />} />
      <Route path="/legal/cgv" element={<CGV />} />
      <Route path="/legal/privacy" element={<Privacy />} />
      <Route path="/legal/security" element={<Security />} />
      <Route path="/legal/cookies" element={<ComingSoon pageName="Politique des Cookies" />} />
      
      <Route path="/product/pricing" element={<Pricing />} />
      <Route path="/features/ingestion" element={<ComingSoon pageName="Ingestion FEC Automatique" />} />
      <Route path="/features/engine" element={<ComingSoon pageName="Moteur de calcul hybride" />} />
      <Route path="/features/audit" element={<ComingSoon pageName="Piste d'audit (Boîte de Verre)" />} />
      <Route path="/features/export" element={<ComingSoon pageName="Export réglementaire iXBRL" />} />
      <Route path="/solutions/experts-comptables" element={<ComingSoon pageName="Solution pour Experts-Comptables" />} />
      <Route path="/solutions/daf" element={<ComingSoon pageName="Solution pour les DAF & PME" />} />
      
      <Route path="/resources/blog" element={<ComingSoon pageName="Blog & Actualités CSRD" />} />
      <Route path="/resources/faq" element={<ComingSoon pageName="Centre d'aide & FAQ" />} />
      <Route path="/resources/case-studies" element={<ComingSoon pageName="Cas clients & Témoignages" />} />
      <Route path="/resources/a47" element={<ComingSoon pageName="Format A47 A-1 (Guide)" />} />
      
      <Route path="/company/about" element={<About />} />
      <Route path="/company/contact" element={<ComingSoon pageName="Nous Contacter" />} />
      <Route path="/company/partners" element={<ComingSoon pageName="Devenir Partenaire" />} />
      <Route path="/company/climate" element={<ComingSoon pageName="Nos engagements Climat" />} />
      
      <Route path="/status" element={<ComingSoon pageName="État des services" />} />

      <Route
        path="/"
        element={
          <PrivateRoute>
            <ReportsProvider>
              <Layout />
            </ReportsProvider>
          </PrivateRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="upload" element={<Upload />} />
        <Route path="reports" element={<Reports />} />
        <Route path="reports/:id" element={<ReportDetail />} />
        <Route path="credits" element={<Credits />} />
        <Route path="academy" element={<Academy />} />
        <Route path="developers" element={<ApiPortal />} />
        <Route path="settings" element={<Settings />} />
        
        <Route path="superadmin" element={<SuperAdminRoute />}>
          <Route index element={<SuperAdminDashboard />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
