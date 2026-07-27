import React, { useState, useEffect } from 'react';
import MatchCard from './components/MatchCard';
import TrendPanel from './components/TrendPanel';
import ArbScanner from './components/ArbScanner';

function App() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [scanning, setScanning] = useState(false);
  
  // State for tab navigation: 'matches' or 'arbitrage'
  const [activeTab, setActiveTab] = useState('matches');
  
  // State to track which match is currently active/selected
  const [selectedMatchId, setSelectedMatchId] = useState(null);

  // Helper function to fetch matches from the database
  const fetchMatches = () => {
    fetch('http://127.0.0.1:8000/api/matches/')
      .then((response) => {
        if (!response.ok) throw new Error('Network error');
        return response.json();
      })
      .then((data) => {
        setMatches(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchMatches();
  }, []);

  // Handler to call the live endpoint
  const handleScanLiveOdds = async () => {
    setScanning(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/api/matches/fetch-live', {
        method: 'POST',
      });
      const data = await response.json();
      
      if (response.ok) {
        alert(`Success! Sync status:\n- Matches synchronized: ${data.matches_synchronized}\n- New price movements logged: ${data.new_price_movements_logged}`);
        fetchMatches(); // Re-fetch matches to display any new games!
      } else {
        alert(`Error: ${data.detail}`);
      }
    } catch (err) {
      alert(`Failed to contact server: ${err.message}`);
    } finally {
      setScanning(false);
    }
  };

  if (loading) return <div style={{ padding: '40px', color: '#fff', backgroundColor: '#1a1a1a', minHeight: '100vh' }}>Loading live games...</div>;
  if (error) return <div style={{ padding: '40px', color: 'red', backgroundColor: '#1a1a1a', minHeight: '100vh' }}>Error: {error}</div>;

  return (
    <div style={{ padding: '40px', fontFamily: 'sans-serif', backgroundColor: '#1a1a1a', color: '#fff', minHeight: '100vh' }}>
      
      {/* --- DASHBOARD HEADER WITH SCAN BUTTON --- */}
      <header style={{ marginBottom: '20px', borderBottom: '1px solid #333', paddingBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ margin: 0, color: '#4caf50' }}>🏆 Sports Analytics & Arbitrage</h1>
          <p style={{ color: '#aaa', margin: '5px 0 0 0' }}>Data Pipeline: Connected to FastAPI Backend</p>
        </div>
        
        <button 
          onClick={handleScanLiveOdds} 
          disabled={scanning}
          style={{
            backgroundColor: scanning ? '#555' : '#4caf50',
            color: '#fff',
            border: 'none',
            padding: '12px 24px',
            borderRadius: '4px',
            cursor: scanning ? 'not-allowed' : 'pointer',
            fontWeight: 'bold',
            transition: 'background-color 0.2s'
          }}
        >
          {scanning ? '🔄 Scanning Live Odds...' : '📡 Scan Live Odds'}
        </button>
      </header>

      {/* --- NAVIGATION TABS --- */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '30px' }}>
        <button
          onClick={() => {
            setActiveTab('matches');
            setSelectedMatchId(null); // Reset trend view when switching tabs
          }}
          style={{
            padding: '10px 20px',
            backgroundColor: activeTab === 'matches' ? '#4caf50' : '#2d2d2d',
            color: '#fff',
            border: activeTab === 'matches' ? 'none' : '1px solid #444',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: 'bold',
            transition: 'all 0.2s'
          }}
        >
          🏈 Match Dashboard
        </button>

        <button
          onClick={() => setActiveTab('arbitrage')}
          style={{
            padding: '10px 20px',
            backgroundColor: activeTab === 'arbitrage' ? '#4caf50' : '#2d2d2d',
            color: '#fff',
            border: activeTab === 'arbitrage' ? 'none' : '1px solid #444',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: 'bold',
            transition: 'all 0.2s'
          }}
        >
          ⚡ Arbitrage Scanner
        </button>
      </div>

      {/* --- MAIN CONTENT AREA --- */}
      {activeTab === 'matches' ? (
        /* TAB 1: MATCH DASHBOARD & TRENDS */
        selectedMatchId ? (
          <TrendPanel 
            matchId={selectedMatchId} 
            onBack={() => setSelectedMatchId(null)} 
          />
        ) : (
          <>
            <h2>🏟️ Live & Upcoming Matches ({matches.length})</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              {matches.map((game) => (
                <MatchCard 
                  key={game.id} 
                  game={game} 
                  onSelect={(id) => setSelectedMatchId(id)} 
                />
              ))}
            </div>
          </>
        )
      ) : (
        /* TAB 2: ARBITRAGE SCANNER */
        <ArbScanner />
      )}

    </div>
  );
}

export default App;