import React from 'react'

function MatchCard({ game, onSelect }) {
  const formattedTime = new Date(game.commence_time).toLocaleString()

  return (
    <div 
      style={{ 
        backgroundColor: '#2d2d2d', 
        padding: '20px', 
        borderRadius: '8px', 
        borderLeft: '5px solid #4caf50',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
      }}
    >
      <h3 style={{ margin: '0 0 10px 0', color: '#fff' }}>
        {game.away_team} @ {game.home_team}
      </h3>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '0.85rem', color: '#888' }}>
          🗓️ {formattedTime}
        </span>
        <button 
          style={{
            backgroundColor: '#4caf50',
            color: 'white',
            border: 'none',
            padding: '6px 12px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
          onClick={() => onSelect(game.id)} // Triggers state change in parent App.jsx
        >
          View Trends
        </button>
      </div>
    </div>
  )
}

export default MatchCard