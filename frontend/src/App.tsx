import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Accounts from './pages/Accounts'
import AccountDetail from './pages/AccountDetail'
import Transcripts from './pages/Transcripts'
import TranscriptDetail from './pages/TranscriptDetail'
import Opportunities from './pages/Opportunities'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/accounts" element={<Accounts />} />
        <Route path="/accounts/:id" element={<AccountDetail />} />
        <Route path="/transcripts" element={<Transcripts />} />
        <Route path="/transcripts/:id" element={<TranscriptDetail />} />
        <Route path="/opportunities" element={<Opportunities />} />
      </Routes>
    </Layout>
  )
}

export default App
