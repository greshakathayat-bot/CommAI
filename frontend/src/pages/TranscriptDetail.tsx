import { useEffect, useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  Grid,
  Column,
  Tile,
  Tag,
  SkeletonText,
  Breadcrumb,
  BreadcrumbItem,
  Button,
  Accordion,
  AccordionItem,
  InlineNotification,
  ProgressBar,
  Tabs,
  Tab,
  TabList,
  TabPanels,
  TabPanel,
} from '@carbon/react'
import { Analytics } from '@carbon/icons-react'
import {
  getTranscript,
  getTranscriptUpdates,
  getTranscriptOpportunities,
  analyzeTranscript,
} from '../api/client'
import type { Transcript, ClientUpdate, Opportunity } from '../api/client'

const CATEGORY_COLOR: Record<string, 'blue' | 'red' | 'teal' | 'purple' | 'gray' | 'green'> = {
  requirement: 'blue',
  feedback: 'teal',
  blocker: 'red',
  action_item: 'purple',
  context: 'gray',
}

const PRIORITY_COLOR: Record<string, 'red' | 'teal' | 'gray'> = {
  high: 'red',
  medium: 'teal',
  low: 'gray',
}

export default function TranscriptDetail() {
  const { id } = useParams<{ id: string }>()
  const [transcript, setTranscript] = useState<Transcript | null>(null)
  const [updates, setUpdates] = useState<ClientUpdate[]>([])
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [analyzeMsg, setAnalyzeMsg] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!id) return
    try {
      const [t, u, o] = await Promise.all([
        getTranscript(id),
        getTranscriptUpdates(id),
        getTranscriptOpportunities(id),
      ])
      setTranscript(t)
      setUpdates(u)
      setOpportunities(o)
    } catch {
      setError('Could not load transcript.')
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    load()
  }, [load])

  const handleAnalyze = async () => {
    if (!id) return
    setAnalyzing(true)
    setAnalyzeMsg(null)
    try {
      const res = await analyzeTranscript(id)
      setAnalyzeMsg(res.message)
      // If backend is offline the message will say so — stop immediately
      if (res.message.startsWith('Backend offline')) {
        setAnalyzing(false)
        return
      }
      // Poll for completion
      let attempts = 0
      const poll = setInterval(async () => {
        attempts++
        const t = await getTranscript(id)
        if (t.status === 'completed' || t.status === 'failed' || attempts > 30) {
          clearInterval(poll)
          setAnalyzing(false)
          await load()
        }
      }, 3000)
    } catch {
      setAnalyzeMsg('Failed to start analysis.')
      setAnalyzing(false)
    }
  }

  if (loading) {
    return (
      <div style={{ padding: '2rem' }}>
        <SkeletonText paragraph lineCount={10} />
      </div>
    )
  }

  if (error || !transcript) {
    return (
      <div style={{ padding: '2rem' }}>
        <InlineNotification kind="error" title="Error" subtitle={error ?? 'Transcript not found'} />
      </div>
    )
  }

  return (
    <div style={{ padding: '2rem' }}>
      <Breadcrumb style={{ marginBottom: '1rem' }}>
        <BreadcrumbItem><Link to="/transcripts">Transcripts</Link></BreadcrumbItem>
        <BreadcrumbItem isCurrentPage>{transcript.title}</BreadcrumbItem>
      </Breadcrumb>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
        <div>
          <h1 className="cds--type-productive-heading-05" style={{ marginBottom: '0.5rem' }}>
            {transcript.title}
          </h1>
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <Tag
              type={transcript.status === 'completed' ? 'green' : transcript.status === 'failed' ? 'red' : transcript.status === 'processing' ? 'teal' : 'gray'}
            >
              {transcript.status}
            </Tag>
            <span className="cds--type-body-short-01" style={{ color: '#525252' }}>
              {new Date(transcript.meeting_date).toLocaleDateString('en-US', { dateStyle: 'long' })}
            </span>
          </div>
        </div>
        <Button
          renderIcon={Analytics}
          onClick={handleAnalyze}
          disabled={analyzing}
          kind={transcript.status === 'completed' ? 'secondary' : 'primary'}
        >
          {analyzing ? 'Analyzing…' : transcript.status === 'completed' ? 'Re-analyze' : 'Run AI Analysis'}
        </Button>
      </div>

      {analyzing && (
        <ProgressBar
          label="AI analysis in progress…"
          helperText="Extracting updates and matching opportunities"
          style={{ marginBottom: '1.5rem' }}
        />
      )}

      {analyzeMsg && (
        <InlineNotification
          kind="info"
          title="Analysis"
          subtitle={analyzeMsg}
          style={{ marginBottom: '1.5rem' }}
        />
      )}

      <Tabs>
        <TabList aria-label="Transcript sections">
          <Tab>Raw Transcript</Tab>
          <Tab>Client Updates ({updates.length})</Tab>
          <Tab>Opportunities ({opportunities.length})</Tab>
        </TabList>
        <TabPanels>
          {/* ── Raw Text ─────────────────────────────────────────────────── */}
          <TabPanel>
            <Tile style={{ marginTop: '1rem' }}>
              <pre
                style={{
                  fontFamily: 'IBM Plex Mono, monospace',
                  fontSize: '0.8125rem',
                  lineHeight: '1.6',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  color: '#161616',
                }}
              >
                {transcript.raw_text}
              </pre>
            </Tile>
          </TabPanel>

          {/* ── Updates ──────────────────────────────────────────────────── */}
          <TabPanel>
            <div style={{ marginTop: '1rem' }}>
              {updates.length === 0 ? (
                <Tile>
                  <p className="cds--type-body-long-01" style={{ color: '#525252' }}>
                    No updates extracted yet. Run AI analysis to extract client updates.
                  </p>
                </Tile>
              ) : (
                <Accordion>
                  {updates.map(u => (
                    <AccordionItem
                      key={u.id}
                      title={
                        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                          <Tag type={CATEGORY_COLOR[u.category] ?? 'gray'} size="sm">{u.category}</Tag>
                          <Tag type={PRIORITY_COLOR[u.priority] ?? 'gray'} size="sm">{u.priority}</Tag>
                          <span className="cds--type-body-short-01">{u.summary}</span>
                        </div>
                      }
                    >
                      {u.verbatim_quote && (
                        <blockquote style={{
                          borderLeft: '3px solid #0f62fe',
                          paddingLeft: '1rem',
                          margin: '0 0 1rem 0',
                          fontStyle: 'italic',
                          color: '#525252',
                        }}>
                          "{u.verbatim_quote}"
                          {u.speaker && <footer style={{ marginTop: '0.25rem', fontSize: '0.75rem' }}>— {u.speaker}</footer>}
                        </blockquote>
                      )}
                      <p className="cds--type-body-long-01">{u.summary}</p>
                    </AccordionItem>
                  ))}
                </Accordion>
              )}
            </div>
          </TabPanel>

          {/* ── Opportunities ─────────────────────────────────────────────── */}
          <TabPanel>
            <div style={{ marginTop: '1rem' }}>
              {opportunities.length === 0 ? (
                <Tile>
                  <p className="cds--type-body-long-01" style={{ color: '#525252' }}>
                    No opportunities identified yet. Run AI analysis to discover opportunities.
                  </p>
                </Tile>
              ) : (
                <Grid narrow>
                  {opportunities.map(opp => (
                    <Column key={opp.id} sm={4} md={8} lg={8}>
                      <Tile style={{ marginBottom: '1rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                          <p className="cds--type-productive-heading-02">{opp.title}</p>
                          <Tag type={opp.confidence_score >= 0.7 ? 'green' : opp.confidence_score >= 0.4 ? 'teal' : 'gray'} size="sm">
                            {Math.round(opp.confidence_score * 100)}% match
                          </Tag>
                        </div>
                        <p className="cds--type-body-long-01" style={{ marginBottom: '0.75rem' }}>{opp.description}</p>
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
          </TabPanel>
        </TabPanels>
      </Tabs>
    </div>
  )
}
