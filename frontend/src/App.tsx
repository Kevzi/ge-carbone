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
