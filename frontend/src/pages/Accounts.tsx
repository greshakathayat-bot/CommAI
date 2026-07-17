import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Grid,
  Column,
  ClickableTile,
  Tag,
  SkeletonText,
  Search,
} from '@carbon/react'
import { getAccounts } from '../api/client'
import type { Account } from '../api/client'

const STAGE_COLOR: Record<string, 'blue' | 'green' | 'teal' | 'purple' | 'gray'> = {
  discovery: 'blue',
  proposal: 'teal',
  qualified: 'green',
  closed_won: 'green',
  closed_lost: 'gray',
}

export default function Accounts() {
  const [accounts, setAccounts] = useState<Account[]>([])
  const [filtered, setFiltered] = useState<Account[]>([])
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')

  useEffect(() => {
    getAccounts()
      .then(data => {
        setAccounts(data)
        setFiltered(data)
      })
      .finally(() => setLoading(false))
  }, [])

  const handleSearch = (val: string) => {
    setQuery(val)
    const q = val.toLowerCase()
    setFiltered(accounts.filter(a =>
      a.account_name.toLowerCase().includes(q) ||
      a.client?.company_name?.toLowerCase().includes(q) ||
      a.client?.industry?.toLowerCase().includes(q) ||
      a.sales_rep?.name?.toLowerCase().includes(q)
    ))
  }

  return (
    <div style={{ padding: '2rem' }}>
      <h1 className="cds--type-productive-heading-05" style={{ marginBottom: '0.5rem' }}>
        Accounts
      </h1>
      <p className="cds--type-body-long-01" style={{ marginBottom: '1.5rem', color: '#525252' }}>
        All client accounts and their current deal stages.
      </p>

      <div style={{ maxWidth: '400px', marginBottom: '2rem' }}>
        <Search
          labelText="Search accounts"
          placeholder="Search by account, client, or rep…"
          value={query}
          onChange={e => handleSearch(e.target.value)}
        />
      </div>

      <Grid narrow>
        {loading
          ? Array.from({ length: 6 }).map((_, i) => (
              <Column key={i} sm={4} md={4} lg={4}>
                <div style={{ marginBottom: '1rem' }}>
                  <ClickableTile style={{ minHeight: '140px' }}>
                    <SkeletonText paragraph lineCount={4} />
                  </ClickableTile>
                </div>
              </Column>
            ))
          : filtered.map(account => (
              <Column key={account.id} sm={4} md={4} lg={4}>
                <div style={{ marginBottom: '1rem' }}>
                  <ClickableTile
                    as={Link}
                    to={`/accounts/${account.id}`}
                    style={{ minHeight: '140px' }}
                  >
                    <p className="cds--type-productive-heading-02" style={{ marginBottom: '0.5rem' }}>
                      {account.account_name}
                    </p>
                    {account.client && (
                      <p className="cds--type-label-01" style={{ color: '#525252', marginBottom: '0.25rem' }}>
                        {account.client.company_name}
                      </p>
                    )}
                    {account.client?.industry && (
                      <p className="cds--type-label-01" style={{ color: '#8d8d8d', marginBottom: '0.75rem' }}>
                        {account.client.industry}
                      </p>
                    )}
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                      <Tag type={STAGE_COLOR[account.stage] ?? 'gray'} size="sm">
                        {account.stage}
                      </Tag>
                      {account.sales_rep && (
                        <Tag type="cool-gray" size="sm">
                          {account.sales_rep.name}
                        </Tag>
                      )}
                    </div>
                  </ClickableTile>
                </div>
              </Column>
            ))}
      </Grid>

      {!loading && filtered.length === 0 && (
        <p className="cds--type-body-long-01" style={{ color: '#525252' }}>
          No accounts match your search.
        </p>
      )}
    </div>
  )
}
