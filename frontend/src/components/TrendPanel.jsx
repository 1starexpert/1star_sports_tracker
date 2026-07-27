import React, { useState, useEffect } from 'react'
import { API_URL } from '../config';

function TrendPanel({ matchId, onBack }) {
  const [historyData, setHistoryData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    // Fetch chronological odds timeline for this specific match
    fetch(`${API_URL}/api/matches/${matchId}/history`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to fetch history (Status: ${response.status})`)
        }
        return response.json()
      })
      .then((data) => {
        setHistoryData(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [matchId])

  if (loading) {
    return (
      <div style={{ backgroundColor: '#2d2d2d', padding: '30px', borderRadius: '8px', color: '#fff' }}>
        <p>🔄 Loading historical lines for {matchId}...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ backgroundColor: '#2d2d2d', padding: '30px', borderRadius: '8px', color: 'red' }}>
        <button onClick={onBack} style={{ marginBottom: '20px', cursor: 'pointer' }}>⬅️ Back</button>
        <p>❌ Error loading trends: {error}</p>
        <p style={{ color: '#aaa', fontSize: '0.9rem' }}>
          Tip: Make sure the endpoint parameter name matches the variable name in your FastAPI route!
        </p>
      </div>
    )
  }

  const { match, history, history_count } = historyData

  return (
    <div style={{ backgroundColor: '#2d2d2d', padding: '30px', borderRadius: '8px' }}>
      <button
        onClick={onBack}
        style={{
          backgroundColor: '#555',
          color: '#fff',
          border: 'none',
          padding: '8px 16px',
          borderRadius: '4px',
          cursor: 'pointer',
          marginBottom: '20px'
        }}
      >
        ⬅️ Back to All Matches
      </button>

      <div style={{ marginBottom: '25px' }}>
        <span style={{ fontSize: '0.85rem', color: '#4caf50', fontWeight: 'bold', textTransform: 'uppercase' }}>
          NFL Futures Analysis
        </span>
        <h2 style={{ margin: '5px 0 10px 0', color: '#fff' }}>
          {match.away_team} @ {match.home_team}
        </h2>
        <p style={{ color: '#aaa', margin: 0 }}>
          Scheduled: {new Date(match.commence_time).toLocaleString()}
        </p>
      </div>

      <h3 style={{ color: '#4caf50', borderBottom: '1px solid #444', paddingBottom: '8px' }}>
        📈 Historical Moneyline Movements ({history_count} data points tracked)
      </h3>

      {history_count === 0 ? (
        <p style={{ color: '#888', fontStyle: 'italic', padding: '20px 0' }}>
          No historical odds logged for this matchup yet. Run the /seed-history endpoint to populate dev data!
        </p>
      ) : (
        <div style={{ overflowX: 'auto', marginTop: '15px' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', color: '#ddd' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #555', color: '#aaa' }}>
                <th style={{ padding: '10px' }}>Date Tracked</th>
                <th style={{ padding: '10px' }}>Sportsbook</th>
                <th style={{ padding: '10px' }}>Team</th>
                <th style={{ padding: '10px' }}>American Odds</th>
              </tr>
            </thead>
            <tbody>
              {history.map((record, index) => (
                <tr key={record.id || index} style={{ borderBottom: '1px solid #444' }}>
                  <td style={{ padding: '10px' }}>
                    {new Date(record.fetched_at).toLocaleString(undefined, {
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </td>
                  <td style={{ padding: '10px', fontWeight: 'bold' }}>{record.sportsbook}</td>
                  <td style={{ padding: '10px' }}>{record.team_name}</td>
                  <td style={{
                    padding: '10px',
                    color: record.price > 0 ? '#4caf50' : '#ff4d4d',
                    fontWeight: 'bold'
                  }}>
                    {record.price > 0 ? `+${record.price}` : record.price}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default TrendPanel