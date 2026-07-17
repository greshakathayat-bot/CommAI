import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api',
})

export interface SalesRep {
  id: string
  name: string
  email: string
  territory: string | null
  created_at: string
}

export interface Client {
  id: string
  company_name: string
  industry: string | null
  website: string | null
  created_at: string
}

export interface Account {
  id: string
  account_name: string
  stage: string
  notes: string | null
  sales_rep_id: string
  client_id: string
  created_at: string
  updated_at: string
  client?: Client
  sales_rep?: SalesRep
}

export interface Transcript {
  id: string
  title: string
  meeting_date: string
  raw_text: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  account_id: string
  sales_rep_id: string
  created_at: string
}

export interface ClientUpdate {
  id: string
  transcript_id: string
  category: string
  summary: string
  verbatim_quote: string | null
  speaker: string | null
  priority: string
  created_at: string
}

export interface Opportunity {
  id: string
  transcript_id: string
  title: string
  description: string
  matched_product: string | null
  matched_capability: string | null
  confidence_score: number
  status: string
  agent_reasoning: string | null
  created_at: string
}

// ── Endpoints ──────────────────────────────────────────────────────────────

export const getAccounts = () =>
  api.get<Account[]>('/accounts/').then(r => r.data)

export const getAccount = (id: string) =>
  api.get<Account>(`/accounts/${id}`).then(r => r.data)

export const getClients = () =>
  api.get<Client[]>('/clients/').then(r => r.data)

export const getSalesReps = () =>
  api.get<SalesRep[]>('/sales-reps/').then(r => r.data)

export const getTranscripts = (accountId?: string) =>
  api.get<Transcript[]>('/transcripts/', { params: accountId ? { account_id: accountId } : {} }).then(r => r.data)

export const getTranscript = (id: string) =>
  api.get<Transcript>(`/transcripts/${id}`).then(r => r.data)

export const getTranscriptUpdates = (transcriptId: string) =>
  api.get<ClientUpdate[]>(`/transcripts/${transcriptId}/updates`).then(r => r.data)

export const getTranscriptOpportunities = (transcriptId: string) =>
  api.get<Opportunity[]>(`/transcripts/${transcriptId}/opportunities`).then(r => r.data)

export const getAllOpportunities = () =>
  api.get<Opportunity[]>('/agent/opportunities').then(r => r.data)

export const analyzeTranscript = (transcriptId: string) =>
  api.post<{ message: string; transcript_id: string }>('/agent/analyze', { transcript_id: transcriptId })
    .then(r => r.data)
