import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  Grid,
  Column,
  Tile,
  ClickableTile,
  Tag,
  SkeletonText,
  Breadcrumb,
  BreadcrumbItem,
  Button,
  InlineNotification,
} from '@carbon/react'
import { ArrowRight } from '@carbon/icons-react'
import { getAccount, getTranscripts } from '../api/client'
import type { Account, Transcript } from '../api/client'

const STAGE_COLOR: Record<string, 'blue' | 'green' | 'teal' | 'purple' | 'gray'> = {
  discovery: 'blue',
  proposal: 'teal',
  qualified: 'green',
  closed_won: 'green',
  closed_lost: 'gray',
}

export default function AccountDetail() {
  const { id } = useParams<{ id: string }>()
  const [account, setAccount] = useState<Account | null>(null)
  const [transcripts, setTranscripts] = useState<Transcript[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    Promise.all([getAccount(id), getTranscripts(id)])
      .then(([a, t]) => {
        setAccount(a)
        setTranscripts(t)
      })
      .catch(() => setError('Could not load account details.'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return (
      <div style={{ padding: '2rem' }}>
        <SkeletonText paragraph lineCount={8} />
      </div>
    )
  }

  if (error || !account) {
    return (
      <div style={{ padding: '2rem' }}>
        <InlineNotification kind="error" title="Error" subtitle={error ?? 'Account not found'} />
      </div>
    )
  }

  return (
    <div style={{ padding: '2rem' }}>
      <Breadcrumb style={{ marginBottom: '1rem' }}>
        <BreadcrumbItem>
          <Link to="/accounts">Accounts</Link>
        </BreadcrumbItem>
        <BreadcrumbItem isCurrentPage>{account.account_name}</BreadcrumbItem>
      </Breadcrumb>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
        <h1 className="cds--type-productive-heading-05">{account.account_name}</h1>
        <Tag type={STAGE_COLOR[account.stage] ?? 'gray'}>{account.stage}</Tag>
      </div>

      {account.client && (
        <p className="cds--type-body-long-01" style={{ color: '#525252', marginBottom: '1.5rem' }}>
          {account.client.company_name} · {account.client.industry}
          {account.client.website && (
            <> · <a href={account.client.website} target="_blank" rel="noopener noreferrer">{account.client.website}</a></>
          )}
        </p>
      )}

      {/* ── Account Details ───────────────────────────────────────────────── */}
      <Grid narrow style={{ marginBottom: '2rem' }}>
        <Column sm={4} md={8} lg={8}>
          <Tile>
            <h2 className="cds--type-productive-heading-02" style={{ marginBottom: '1rem' }}>Account Notes</h2>
            <p className="cds--type-body-long-01">
              {account.notes ?? 'No notes recorded.'}
            </p>
          </Tile>
        </Column>
        <Column sm={4} md={4} lg={4}>
          <Tile>
            <h2 className="cds--type-productive-heading-02" style={{ marginBottom: '1rem' }}>Details</h2>
            <dl style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem 1rem' }}>
              <dt className="cds--type-label-01" style={{ color: '#525252' }}>Sales Rep</dt>
              <dd className="cds--type-body-short-01">{account.sales_rep?.name ?? '—'}</dd>
              <dt className="cds--type-label-01" style={{ color: '#525252' }}>Territory</dt>
              <dd className="cds--type-body-short-01">{account.sales_rep?.territory ?? '—'}</dd>
              <dt className="cds--type-label-01" style={{ color: '#525252' }}>Stage</dt>
              <dd className="cds--type-body-short-01">{account.stage}</dd>
              <dt className="cds--type-label-01" style={{ color: '#525252' }}>Industry</dt>
              <dd className="cds--type-body-short-01">{account.client?.industry ?? '—'}</dd>
            </dl>
          </Tile>
        </Column>
      </Grid>

      {/* ── Transcripts ───────────────────────────────────────────────────── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2 className="cds--type-productive-heading-03">Meeting Transcripts ({transcripts.length})</h2>
        <Button
          as={Link}
          to="/transcripts"
          kind="ghost"
          size="sm"
          renderIcon={ArrowRight}
        >
          View all
        </Button>
      </div>

      {transcripts.length === 0 ? (
        <Tile>
          <p className="cds--type-body-long-01" style={{ color: '#525252' }}>No transcripts for this account yet.</p>
        </Tile>
      ) : (
        <Grid narrow>
          {transcripts.map(t => (
            <Column key={t.id} sm={4} md={8} lg={8}>
              <div style={{ marginBottom: '1rem' }}>
                <ClickableTile as={Link} to={`/transcripts/${t.id}`}>
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
                    {new Date(t.meeting_date).toLocaleDateString('en-US', { dateStyle: 'long' })}
                  </p>
                </ClickableTile>
              </div>
            </Column>
          ))}
        </Grid>
      )}
    </div>
  )
}
