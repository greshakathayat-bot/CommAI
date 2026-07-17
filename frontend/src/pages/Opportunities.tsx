import { useEffect, useState } from 'react'
import {
  Grid,
  Column,
  Tile,
  Tag,
  SkeletonText,
  Select,
  SelectItem,
} from '@carbon/react'
import { getAllOpportunities } from '../api/client'
import type { Opportunity } from '../api/client'

export default function Opportunities() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [filtered, setFiltered] = useState<Opportunity[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('')
  const [confidenceFilter, setConfidenceFilter] = useState('')

  useEffect(() => {
    getAllOpportunities()
      .then(data => {
        setOpportunities(data)
        setFiltered(data)
      })
      .finally(() => setLoading(false))
  }, [])

  const applyFilters = (status: string, confidence: string) => {
    let result = opportunities
    if (status) result = result.filter(o => o.status === status)
    if (confidence === 'high') result = result.filter(o => o.confidence_score >= 0.7)
    if (confidence === 'medium') result = result.filter(o => o.confidence_score >= 0.4 && o.confidence_score < 0.7)
    if (confidence === 'low') result = result.filter(o => o.confidence_score < 0.4)
    setFiltered(result)
  }

  const handleStatusChange = (val: string) => {
    setStatusFilter(val)
    applyFilters(val, confidenceFilter)
  }

  const handleConfidenceChange = (val: string) => {
    setConfidenceFilter(val)
    applyFilters(statusFilter, val)
  }

  return (
    <div style={{ padding: '2rem' }}>
      <h1 className="cds--type-productive-heading-05" style={{ marginBottom: '0.5rem' }}>
        Opportunities
      </h1>
      <p className="cds--type-body-long-01" style={{ marginBottom: '1.5rem', color: '#525252' }}>
        AI-identified solution opportunities ranked by confidence score.
      </p>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', flexWrap: 'wrap' }}>
        <div style={{ minWidth: '200px' }}>
          <Select
            id="status-filter"
            labelText="Filter by status"
            value={statusFilter}
            onChange={e => handleStatusChange(e.target.value)}
          >
            <SelectItem value="" text="All statuses" />
            <SelectItem value="identified" text="Identified" />
            <SelectItem value="qualified" text="Qualified" />
            <SelectItem value="proposed" text="Proposed" />
            <SelectItem value="closed_won" text="Closed Won" />
            <SelectItem value="closed_lost" text="Closed Lost" />
          </Select>
        </div>
        <div style={{ minWidth: '200px' }}>
          <Select
            id="confidence-filter"
            labelText="Filter by confidence"
            value={confidenceFilter}
            onChange={e => handleConfidenceChange(e.target.value)}
          >
            <SelectItem value="" text="All confidence levels" />
            <SelectItem value="high" text="High (≥70%)" />
            <SelectItem value="medium" text="Medium (40–69%)" />
            <SelectItem value="low" text="Low (<40%)" />
          </Select>
        </div>
      </div>

      {loading ? (
        <Grid narrow>
          {Array.from({ length: 6 }).map((_, i) => (
            <Column key={i} sm={4} md={8} lg={8}>
              <Tile style={{ marginBottom: '1rem', minHeight: '140px' }}>
                <SkeletonText paragraph lineCount={4} />
              </Tile>
            </Column>
          ))}
        </Grid>
      ) : filtered.length === 0 ? (
        <Tile>
          <p className="cds--type-body-long-01" style={{ color: '#525252' }}>
            No opportunities found. Analyze transcripts to discover opportunities.
          </p>
        </Tile>
      ) : (
        <Grid narrow>
          {filtered.map(opp => (
            <Column key={opp.id} sm={4} md={8} lg={8}>
              <Tile style={{ marginBottom: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                  <p className="cds--type-productive-heading-02">{opp.title}</p>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <Tag
                      type={opp.confidence_score >= 0.7 ? 'green' : opp.confidence_score >= 0.4 ? 'teal' : 'gray'}
                      size="sm"
                    >
                      {Math.round(opp.confidence_score * 100)}% match
                    </Tag>
                    <Tag type="cool-gray" size="sm">{opp.status}</Tag>
                  </div>
                </div>

                <p className="cds--type-body-long-01" style={{ marginBottom: '0.75rem' }}>
                  {opp.description}
                </p>

                {opp.matched_product && (
                  <p className="cds--type-label-01" style={{ color: '#525252', marginBottom: '0.25rem' }}>
                    <strong>Product:</strong> {opp.matched_product}
                  </p>
                )}
                {opp.matched_capability && (
                  <p className="cds--type-label-01" style={{ color: '#525252', marginBottom: '0.25rem' }}>
                    <strong>Capability:</strong> {opp.matched_capability}
                  </p>
                )}
                {opp.agent_reasoning && (
                  <details style={{ marginTop: '0.75rem' }}>
                    <summary className="cds--type-label-01" style={{ cursor: 'pointer', color: '#0f62fe' }}>
                      AI Reasoning
                    </summary>
                    <p className="cds--type-body-short-01" style={{ marginTop: '0.5rem', color: '#525252' }}>
                      {opp.agent_reasoning}
                    </p>
                  </details>
                )}
              </Tile>
            </Column>
          ))}
        </Grid>
      )}
    </div>
  )
}
