import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { raffleAPI } from '../services/api';
import Card from '../components/Card';
import Button from '../components/Button';
import { formatLongDate } from '../utils/dateUtils';
import './PreviousRaffles.css';

export default function PreviousRaffles() {
  const navigate = useNavigate();
  const { user, loading: authLoading } = useAuth();
  const [raffles, setRaffles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedRaffle, setExpandedRaffle] = useState(null);
  const [transparencyData, setTransparencyData] = useState({});

  useEffect(() => {
    if (!authLoading) {
      loadRaffles();
    }
  }, [authLoading]);

  const loadRaffles = async () => {
    try {
      setLoading(true);
      const data = await raffleAPI.getPreviousRaffles();
      setRaffles(data);
    } catch (error) {
      console.error('Error loading previous raffles:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTransparency = async (raffleId) => {
    if (transparencyData[raffleId]) {
      return; // Already loaded
    }

    try {
      const data = await raffleAPI.getTransparency(raffleId);
      setTransparencyData(prev => ({
        ...prev,
        [raffleId]: data,
      }));
    } catch (error) {
      console.error('Error loading transparency data:', error);
    }
  };

  const toggleTransparency = (raffleId) => {
    if (expandedRaffle === raffleId) {
      setExpandedRaffle(null);
    } else {
      setExpandedRaffle(raffleId);
      loadTransparency(raffleId);
    }
  };

  const getRarityColor = (rarity) => {
    const colors = {
      common: '#9e9e9e',
      uncommon: '#4caf50',
      rare: '#2196f3',
      epic: '#9c27b0',
      legendary: '#ff9800',
    };
    return colors[rarity] || colors.common;
  };

  if (loading) {
    return (
      <div className="previous-raffles">
        <div className="loading">Loading previous raffles...</div>
      </div>
    );
  }

  return (
    <div className="previous-raffles">
      <div className="raffles-header">
        <h1>🏆 Previous Raffles</h1>
        <p className="subtitle">Completed raffles and winners</p>
      </div>

      {raffles.length === 0 ? (
        <Card>
          <div className="empty-state">
            <div className="empty-icon">📜</div>
            <p>No previous raffles yet</p>
            <p className="empty-hint">Finished raffles will appear here</p>
          </div>
        </Card>
      ) : (
        <div className="raffles-list">
          {raffles.map((raffle) => (
            <Card key={raffle.id}>
              <div className="raffle-card">
                {raffle.prize?.image && (
                  <div className="raffle-image">
                    <img src={raffle.prize.image} alt={raffle.prize.name} />
                    {raffle.prize.rarity && (
                      <span
                        className="rarity-badge"
                        style={{ backgroundColor: getRarityColor(raffle.prize.rarity) }}
                      >
                        {raffle.prize.rarity.toUpperCase()}
                      </span>
                    )}
                  </div>
                )}

                <div className="raffle-header">
                  <h3>{raffle.name}</h3>
                  <span className={`status-badge ${raffle.is_finished ? 'finished' : 'inactive'}`}>
                    {raffle.is_finished ? 'Finished' : 'Inactive'}
                  </span>
                </div>

                <div className="raffle-info">
                  <div className="info-row">
                    <span className="info-label">Prize:</span>
                    <span className="info-value">{raffle.prize?.name}</span>
                  </div>
                  {raffle.entries_count !== undefined && (
                    <div className="info-row">
                      <span className="info-label">Total Entries:</span>
                      <span className="info-value">{raffle.entries_count}</span>
                    </div>
                  )}
                  {raffle.created_at && (
                    <div className="info-row">
                      <span className="info-label">Created:</span>
                      <span className="info-value">{formatLongDate(raffle.created_at)}</span>
                    </div>
                  )}
                </div>

                {raffle.winner && (
                  <div className="winner-section">
                    <div className="winner-header">
                      <span className="winner-icon">🎉</span>
                      <h4>Winner</h4>
                    </div>
                    <div className="winner-info">
                      <div className="winner-name">{raffle.winner.username}</div>
                      {raffle.winner.entry_id && (
                        <div className="winner-entry-id">
                          <span className="entry-id-label">Entry ID:</span>
                          <span className="entry-id-value">{raffle.winner.entry_id}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {raffle.is_finished && (
                  <div className="transparency-section">
                    <Button
                      variant="secondary"
                      onClick={() => toggleTransparency(raffle.id)}
                      style={{ width: '100%', marginTop: '12px' }}
                    >
                      {expandedRaffle === raffle.id ? 'Hide' : 'Show'} Transparency Data
                    </Button>
                    {expandedRaffle === raffle.id && transparencyData[raffle.id] && (
                      <div className="transparency-content">
                        <div className="transparency-item">
                          <strong>Selection Method:</strong> {transparencyData[raffle.id].selection_method}
                        </div>
                        {transparencyData[raffle.id].selection_seed && (
                          <div className="transparency-item">
                            <strong>Seed:</strong>
                            <div className="transparency-value">{transparencyData[raffle.id].selection_seed}</div>
                          </div>
                        )}
                        {transparencyData[raffle.id].selection_hash && (
                          <div className="transparency-item">
                            <strong>Hash:</strong>
                            <div className="transparency-value">{transparencyData[raffle.id].selection_hash}</div>
                          </div>
                        )}
                        {transparencyData[raffle.id].selection_timestamp && (
                          <div className="transparency-item">
                            <strong>Timestamp:</strong> {formatLongDate(transparencyData[raffle.id].selection_timestamp)}
                          </div>
                        )}
                        {transparencyData[raffle.id].total_entries !== undefined && (
                          <div className="transparency-item">
                            <strong>Total Entries:</strong> {transparencyData[raffle.id].total_entries}
                          </div>
                        )}
                        {transparencyData[raffle.id].verification_instructions && (
                          <div className="transparency-item">
                            <strong>Verification Steps:</strong>
                            <ol className="verification-steps">
                              {Object.values(transparencyData[raffle.id].verification_instructions).map((step, idx) => (
                                <li key={idx}>{step}</li>
                              ))}
                            </ol>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                <Button
                  variant="secondary"
                  onClick={() => navigate(`/raffle/${raffle.id}`)}
                  style={{ width: '100%', marginTop: '12px' }}
                >
                  View Details
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

