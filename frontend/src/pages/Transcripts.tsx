import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Grid,
  Column,
  ClickableTile,
  Tag,
  SkeletonText,
  Select,
  SelectItem,
} from '@carbon/react'
import { getTranscripts, getAccounts } from '../api/client'
import type { Transcript, Account } from '../api/client'

export default function Transcripts() {
  const [transcripts, setTranscripts] = useState<Transcript[]>([])
  const [accounts, setAccounts] = useState<Account[]>([])
  const [accountFilter, setAccountFilter] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getTranscripts(), getAccounts()])
      .then(([t, a]) => {
        setTranscripts(t)
        setAccounts(a)
      })
      .finally(() => setLoading(false))
  }, [])

  const handleFilterChange = (accountId: string) => {
    setAccountFilter(accountId)
    setLoading(true)
    getTranscripts(accountId || undefined)
      .then(setTranscripts)
      .finally(() => setLoading(false))
  }

  const accountName = (accountId: string) =>
    accounts.find(a => a.id === accountId)?.account_name ?? 'Unknown Account'

  return (
    <div style={{ padding: '2rem' }}>
      <h1 className="cds--type-productive-heading-05" style={{ marginBottom: '0.5rem' }}>
        Transcripts
      </h1>
      <p className="cds--type-body-long-01" style={{ marginBottom: '1.5rem', color: '#525252' }}>
        Meeting transcripts awaiting or completed AI analysis.
      </p>

      <div style={{ maxWidth: '300px', marginBottom: '2rem' }}>
        <Select
          id="account-filter"
          labelText="Filter by account"
          value={accountFilter}
          onChange={e => handleFilterChange(e.target.value)}
        >
          <SelectItem value="" text="All accounts" />
          {accounts.map(a => (
            <SelectItem key={a.id} value={a.id} text={a.account_name} />
          ))}
        </Select>
      </div>

      <Grid narrow>
        {loading
          ? Array.from({ length: 5 }).map((_, i) => (
              <Column key={i} sm={4} md={8} lg={8}>
                <div style={{ marginBottom: '1rem' }}>
                  <ClickableTile style={{ minHeight: '100px' }}>
                    <SkeletonText paragraph lineCount={3} />
                  </ClickableTile>
                </div>
              </Column>
            ))
          : transcripts.map(t => (
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
                    <p className="cds--type-label-01" style={{ color: '#8d8d8d', marginTop: '0.25rem' }}>
                      {accountName(t.account_id)}
                    </p>
                  </ClickableTile>
                </div>
              </Column>
            ))}
      </Grid>

      {!loading && transcripts.length === 0 && (
        <p className="cds--type-body-long-01" style={{ color: '#525252' }}>
          No transcripts found for this filter.
        </p>
      )}
    </div>
  )
}
