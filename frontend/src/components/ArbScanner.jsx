import React, { useState, useEffect } from 'react'
import { API_URL } from '../config'

function ArbScanner() {
    const [bankroll, setBankroll] = useState(1000)
    const [arbs, setArbs] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    // Fetch real mathematical arbs from FastAPI backend
    const fetchArbitrage = () => {
        setLoading(true)
        fetch(`${API_URL}/api/matches/arbitrage`)
            .then((res) => {
                if (!res.ok) throw new Error('Failed to fetch arbitrage data')
                return res.json()
            })
            .then((data) => {
                setArbs(data)
                setLoading(false)
            })
            .catch((err) => {
                setError(err.message)
                setLoading(false)
            })
    }

    useEffect(() => {
        fetchArbitrage()
    }, [])

    if (loading) {
        return (
            <div style={{ padding: '30px', color: '#fff', textAlign: 'center' }}>
                🔍 Sifting through database odds across all sportsbooks...
            </div>
        )
    }

    if (error) {
        return (
            <div style={{ padding: '30px', color: 'red', textAlign: 'center' }}>
                ❌ Error loading arbitrage opportunities: {error}
            </div>
        )
    }

    return (
        <div style={{ maxWidth: '1000px', margin: '0 auto', color: '#fff' }}>
            {/* Header & Controls */}
            <div
                style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    backgroundColor: '#1e1e1e',
                    padding: '20px 25px',
                    borderRadius: '10px',
                    marginBottom: '25px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
                }}
            >
                <div>
                    <h2 style={{ margin: 0, color: '#4caf50', fontSize: '1.6rem' }}>
                        ⚡ Live Arbitrage Opportunities
                    </h2>
                    <p style={{ margin: '5px 0 0 0', color: '#aaa', fontSize: '0.9rem' }}>
                        Real-time market inefficiencies calculated directly from your database.
                    </p>
                </div>

                <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
                    <button
                        onClick={fetchArbitrage}
                        style={{
                            backgroundColor: '#2d2d2d',
                            border: '1px solid #444',
                            color: '#fff',
                            padding: '8px 14px',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontWeight: 'bold',
                        }}
                    >
                        🔄 Refresh
                    </button>

                    <div style={{ textAlign: 'right' }}>
                        <label
                            style={{
                                display: 'block',
                                fontSize: '0.8rem',
                                color: '#aaa',
                                marginBottom: '4px',
                                textTransform: 'uppercase',
                            }}
                        >
                            Total Bankroll ($)
                        </label>
                        <input
                            type="number"
                            value={bankroll}
                            onChange={(e) => setBankroll(Math.max(1, Number(e.target.value)))}
                            style={{
                                backgroundColor: '#2d2d2d',
                                border: '1px solid #4caf50',
                                color: '#fff',
                                padding: '8px 12px',
                                borderRadius: '6px',
                                fontSize: '1.1rem',
                                fontWeight: 'bold',
                                width: '120px',
                                textAlign: 'center',
                            }}
                        />
                    </div>
                </div>
            </div>

            {/* Arbitrage Opportunity Cards */}
            {arbs.length === 0 ? (
                <div
                    style={{
                        backgroundColor: '#1e1e1e',
                        padding: '40px',
                        textAlign: 'center',
                        borderRadius: '10px',
                        color: '#888',
                    }}
                >
                    <p style={{ fontSize: '1.2rem', margin: 0 }}>
                        🎯 No arbitrage opportunities currently exist in your database.
                    </p>
                    <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '8px' }}>
                        Tip: Click "Scan Live Odds" in the top bar to fetch market updates or add more bookmakers!
                    </p>
                </div>
            ) : (
                arbs.map((arb) => {
                    const S = arb.outcomes.reduce((acc, curr) => acc + curr.impliedProb, 0)
                    const expectedReturn = bankroll / S
                    const totalProfit = expectedReturn - bankroll

                    return (
                        <div
                            key={arb.id}
                            style={{
                                backgroundColor: '#252525',
                                border: '1px solid #333',
                                borderRadius: '10px',
                                padding: '20px',
                                marginBottom: '20px',
                                boxShadow: '0 4px 10px rgba(0,0,0,0.2)',
                            }}
                        >
                            {/* Card Header */}
                            <div
                                style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    borderBottom: '1px solid #3a3a3a',
                                    paddingBottom: '12px',
                                    marginBottom: '15px',
                                }}
                            >
                                <div>
                                    <span
                                        style={{
                                            fontSize: '0.75rem',
                                            color: '#888',
                                            textTransform: 'uppercase',
                                            fontWeight: 'bold',
                                        }}
                                    >
                                        {arb.sport}
                                    </span>
                                    <h3 style={{ margin: '4px 0 0 0', color: '#fff', fontSize: '1.25rem' }}>
                                        {arb.matchup}
                                    </h3>
                                </div>

                                <div style={{ textAlign: 'right' }}>
                                    <span
                                        style={{
                                            backgroundColor: '#1b432e',
                                            color: '#4caf50',
                                            padding: '6px 12px',
                                            borderRadius: '20px',
                                            fontWeight: 'bold',
                                            fontSize: '0.95rem',
                                            border: '1px solid #2e7d32',
                                        }}
                                    >
                                        +{arb.profitMargin.toFixed(2)}% Guaranteed ROI
                                    </span>
                                    <div style={{ color: '#4caf50', fontSize: '0.85rem', marginTop: '6px' }}>
                                        Net Profit: <strong>+${totalProfit.toFixed(2)}</strong>
                                    </div>
                                </div>
                            </div>

                            {/* Outcome Stake Breakdown */}
                            <div
                                style={{
                                    display: 'grid',
                                    gridTemplateColumns: '1fr 1fr',
                                    gap: '15px',
                                }}
                            >
                                {arb.outcomes.map((outcome, idx) => {
                                    const stake = (bankroll * (outcome.impliedProb / S)).toFixed(2)
                                    const payout = expectedReturn.toFixed(2)

                                    return (
                                        <div
                                            key={idx}
                                            style={{
                                                backgroundColor: '#1a1a1a',
                                                padding: '15px',
                                                borderRadius: '8px',
                                                borderLeft: '4px solid #4caf50',
                                            }}
                                        >
                                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                                <span style={{ fontWeight: 'bold', color: '#fff' }}>
                                                    {outcome.team}
                                                </span>
                                                <span style={{ color: '#4caf50', fontWeight: 'bold' }}>
                                                    {outcome.americanOdds}
                                                </span>
                                            </div>

                                            <div style={{ fontSize: '0.85rem', color: '#aaa', marginBottom: '10px' }}>
                                                Bookmaker: <strong style={{ color: '#fff' }}>{outcome.sportsbook}</strong>
                                            </div>

                                            <div
                                                style={{
                                                    display: 'flex',
                                                    justifyContent: 'space-between',
                                                    backgroundColor: '#2a2a2a',
                                                    padding: '8px 12px',
                                                    borderRadius: '6px',
                                                    fontSize: '0.9rem',
                                                }}
                                            >
                                                <span>
                                                    Wager Amount: <strong style={{ color: '#4caf50' }}>${stake}</strong>
                                                </span>
                                                <span style={{ color: '#aaa' }}>
                                                    Payout: ${payout}
                                                </span>
                                            </div>
                                        </div>
                                    )
                                })}
                            </div>
                        </div>
                    )
                })
            )}
        </div>
    )
}

export default ArbScanner