import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Grid,
  Column,
  Tile,
  ClickableTile,
  Tag,
  SkeletonText,
  InlineNotification,
} from '@carbon/react'
import { getAccounts, getTranscripts, getAllOpportunities } from '../api/client'
import type { Account, Transcript, Opportunity } from '../api/client'

const STAGE_COLOR: Record<string, 'blue' | 'green' | 'teal' | 'purple' | 'gray'> = {
  discovery: 'blue',
  proposal: 'teal',
  qualified: 'green',
  'closed_won': 'green',
  'closed_lost': 'gray',
}

export default function Dashboard() {
  const [accounts, setAccounts] = useState<Account[]>([])
  const [transcripts, setTranscripts] = useState<Transcript[]>([])
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([getAccounts(), getTranscripts(), getAllOpportunities()])
      .then(([a, t, o]) => {
        setAccounts(a)
        setTranscripts(t)
        setOpportunities(o)
      })
      .catch(() => setError('Could not load data — is the backend running?'))
      .finally(() => setLoading(false))
  }, [])

  const pendingTranscripts = transcripts.filter(t => t.status === 'pending').length
  const completedTranscripts = transcripts.filter(t => t.status === 'completed').length
  const highConfidenceOpps = opportunities.filter(o => o.confidence_score >= 0.7).length

  return (
    <div style={{ padding: '2rem' }}>
      <h1 className="cds--type-productive-heading-05" style={{ marginBottom: '0.5rem' }}>
        Dashboard
      </h1>
      <p className="cds--type-body-long-01" style={{ marginBottom: '2rem', color: '#525252' }}>
        Sales intelligence overview — transcripts, accounts, and AI-identified opportunities.
      </p>

      {error && (
        <InlineNotification
          kind="error"
          title="Connection error"
          subtitle={error}
          style={{ marginBottom: '1.5rem' }}
        />
      )}

      {/* ── KPI Tiles ────────────────────────────────────────────────────── */}
      <Grid narrow style={{ marginBottom: '2rem' }}>
        {[
          { label: 'Active Accounts', value: loading ? '—' : accounts.length },
          { label: 'Total Transcripts', value: loading ? '—' : transcripts.length },
          { label: 'Pending Analysis', value: loading ? '—' : pendingTranscripts },
          { label: 'High-Confidence Opportunities', value: loading ? '—' : highConfidenceOpps },
        ].map(kpi => (
          <Column key={kpi.label} sm={2} md={2} lg={3}>
            <Tile style={{ minHeight: '100px' }}>
              {loading ? (
                <SkeletonText />
              ) : (
                <>
                  <p className="cds--type-productive-heading-06" style={{ marginBottom: '0.25rem' }}>
                    {kpi.value}
                  </p>
                  <p className="cds--type-label-01" style={{ color: '#525252' }}>
                    {kpi.label}
                  </p>
                </>
              )}
            </Tile>
          </Column>
        ))}
      </Grid>

      {/* ── Recent Accounts ───────────────────────────────────────────────── */}
      <h2 className="cds--type-productive-heading-03" style={{ marginBottom: '1rem' }}>
        Accounts
      </h2>
      <Grid narrow style={{ marginBottom: '2rem' }}>
        {loading
          ? Array.from({ length: 4 }).map((_, i) => (
              <Column key={i} sm={4} md={4} lg={4}>
                <Tile style={{ minHeight: '120px' }}>
                  <SkeletonText paragraph lineCount={3} />
                </Tile>
              </Column>
            ))
          : accounts.map(account => (
              <Column key={account.id} sm={4} md={4} lg={4}>
                <ClickableTile
                  as={Link}
                  to={`/accounts/${account.id}`}
                  style={{ minHeight: '120px' }}
                >
                  <p className="cds--type-productive-heading-02" style={{ marginBottom: '0.5rem' }}>
                    {account.account_name}
                  </p>
                  {account.client && (
                    <p className="cds--type-body-short-01" style={{ color: '#525252', marginBottom: '0.5rem' }}>
                      {account.client.company_name} · {account.client.industry}
                    </p>
                  )}
                  <Tag type={STAGE_COLOR[account.stage] ?? 'gray'} size="sm">
                    {account.stage}
                  </Tag>
                </ClickableTile>
              </Column>
            ))}
      </Grid>

      {/* ── Recent Transcripts ────────────────────────────────────────────── */}
      <h2 className="cds--type-productive-heading-03" style={{ marginBottom: '1rem' }}>
        Recent Transcripts
      </h2>
      <Grid narrow>
        {loading
          ? Array.from({ length: 3 }).map((_, i) => (
              <Column key={i} sm={4} md={8} lg={8}>
                <Tile style={{ marginBottom: '1rem' }}>
                  <SkeletonText paragraph lineCount={2} />
                </Tile>
              </Column>
            ))
          : transcripts.slice(0, 5).map(t => (
              <Column key={t.id} sm={4} md={8} lg={8}>
                <ClickableTile
                  as={Link}
                  to={`/transcripts/${t.id}`}
                  style={{ marginBottom: '1rem' }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <p className="cds--type-productive-heading-02">{t.title}</p>
                    <Tag
                      type={t.status === 'completed' ? 'green' : t.status === 'failed' ? 'red' : t.status === 'processing' ? 'teal' : 'gray'}
                      size="sm"
                    >
                      {t.status}
                    </Tag>
                  </div>
                  <p className="cds--type-body-short-01" style={{ color: '#525252', marginTop: '0.25rem' }}>
                    {new Date(t.meeting_date).toLocaleDateString('en-US', { dateStyle: 'medium' })}
                  </p>
                </ClickableTile>
              </Column>
            ))}
      </Grid>
    </div>
  )
}
