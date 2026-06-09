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

// Static & Feature Pages
import ComingSoon from './pages/ComingSoon'
import Security from './pages/legal/Security'
import Privacy from './pages/legal/Privacy'
import CGV from './pages/legal/CGV'
import MentionsLegales from './pages/legal/MentionsLegales'
import Cookies from './pages/legal/Cookies'
import Pricing from './pages/product/Pricing'
import IngestionFEC from './pages/product/IngestionFEC'
import Engine from './pages/product/Engine'
import AuditTrail from './pages/product/AuditTrail'
import Export from './pages/product/Export'
import ExpertsComptables from './pages/solutions/ExpertsComptables'
import DAF from './pages/solutions/DAF'
import Blog from './pages/resources/Blog'
import FAQ from './pages/resources/FAQ'
import CaseStudies from './pages/resources/CaseStudies'
import A47Format from './pages/resources/A47Format'
import About from './pages/company/About'
import Contact from './pages/company/Contact'
import Partners from './pages/company/Partners'
import ClimateCommitments from './pages/company/ClimateCommitments'
import Status from './pages/Status'
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
      <Route path="/legal/cookies" element={<Cookies />} />
      
      <Route path="/product/pricing" element={<Pricing />} />
      <Route path="/features/ingestion" element={<IngestionFEC />} />
      <Route path="/features/engine" element={<Engine />} />
      <Route path="/features/audit" element={<AuditTrail />} />
      <Route path="/features/export" element={<Export />} />
      <Route path="/solutions/experts-comptables" element={<ExpertsComptables />} />
      <Route path="/solutions/daf" element={<DAF />} />
      
      <Route path="/resources/blog" element={<Blog />} />
      <Route path="/resources/faq" element={<FAQ />} />
      <Route path="/resources/case-studies" element={<CaseStudies />} />
      <Route path="/resources/a47" element={<A47Format />} />
      
      <Route path="/company/about" element={<About />} />
      <Route path="/company/contact" element={<Contact />} />
      <Route path="/company/partners" element={<Partners />} />
      <Route path="/company/climate" element={<ClimateCommitments />} />
      
      <Route path="/status" element={<Status />} />

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
