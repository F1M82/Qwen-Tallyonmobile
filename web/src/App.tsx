import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Vouchers from './pages/Vouchers'
import VoucherEntry from './pages/VoucherEntry'
import Reconciliation from './pages/Reconciliation'
import Parties from './pages/Parties'
import Reports from './pages/Reports'
import Compliance from './pages/Compliance'
import Settings from './pages/Settings'
import ConnectorStatus from './components/ConnectorStatus'

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <Routes>
      <Route path="/login" element={
        isAuthenticated ? <Navigate to="/dashboard" /> : <Login />
      } />
      
      <Route path="/" element={
        isAuthenticated ? <Layout /> : <Navigate to="/login" />
      }>
        <Route index element={<Navigate to="/dashboard" />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="vouchers" element={<Vouchers />} />
        <Route path="vouchers/new" element={<VoucherEntry />} />
        <Route path="vouchers/:id" element={<VoucherEntry />} />
        <Route path="reconciliation" element={<Reconciliation />} />
        <Route path="parties" element={<Parties />} />
        <Route path="reports" element={<Reports />} />
        <Route path="compliance" element={<Compliance />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" />} />
    </Routes>
  )
}

export default App
