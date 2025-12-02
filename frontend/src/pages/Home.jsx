import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { raffleAPI } from '../services/api';
import Card from '../components/Card';
import Button from '../components/Button';
import { formatShortDate, getTimeUntil } from '../utils/dateUtils';
import './Home.css';

export default function Home() {
  const navigate = useNavigate();
  const { user, loading: authLoading } = useAuth();
  const [raffles, setRaffles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Only load raffles after auth is complete
    if (!authLoading) {
      loadRaffles();
    }
  }, [authLoading]);

  const loadRaffles = async () => {
    try {
      setLoading(true);
      const data = await raffleAPI.getRaffles();
      setRaffles(data);
    } catch (error) {
      console.error('Error loading raffles:', error);
    } finally {
      setLoading(false);
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
  
  const getDaysUntilDraw = (drawDate) => {
    if (!drawDate) return null;
    const timeUntil = getTimeUntil(drawDate);
    if (!timeUntil) return 0;
    return timeUntil.days;
  };

  // Always render header immediately - don't wait for anything
  return (
    <div className="home" style={{ minHeight: '200px' }}>
      <div className="home-header" style={{ padding: '20px 0' }}>
        <h1 style={{ margin: '0 0 8px 0', fontSize: '32px' }}>🎰 NFT Lottery</h1>
        <p className="subtitle" style={{ margin: 0 }}>Win amazing prizes!</p>
      </div>

      {loading ? (
        <Card>
          <div className="loading">Loading raffles...</div>
        </Card>
      ) : raffles.length === 0 ? (
          <Card>
            <div className="empty-state">
              <div className="empty-icon">🎲</div>
              <p>No active raffles at the moment</p>
              <p className="empty-hint">Check back later for new opportunities!</p>
            </div>
          </Card>
        ) : (
          <div className="raffles-list">
            {raffles.map((raffle) => (
              <Card
                key={raffle.id}
                onClick={() => navigate(`/shop?raffle=${raffle.id}`)}
              >
                <div className="raffle-card">
                  {raffle.prize?.image && (
                    <div className="raffle-image">
                      <img src={raffle.prize.image} alt={raffle.prize.name} />
                      {raffle.prize.rarity && (
                        <span
                          className="rarity-badge"
                          style={{ backgroundColor: getRarityColor(raffle.prize.rarity) }}
                        >
                          {raffle.prize.rarity}
                        </span>
                      )}
                    </div>
                  )}
                  <div className="raffle-info">
                    <h3>{raffle.name}</h3>
                    <p className="raffle-description">{raffle.description}</p>
                    <div className="raffle-prize">
                      <strong>Prize:</strong> {raffle.prize?.name}
                    </div>
                    <div className="raffle-meta">
                      {raffle.min_entries_to_unlock && (
                        <div className="meta-item">
                          <span className="meta-label">Min entries:</span>
                          <span className="meta-value">{raffle.min_entries_to_unlock}</span>
                        </div>
                      )}
                    </div>
                    {raffle.entries_count !== undefined && (
                      <div className="raffle-participants">
                        {raffle.entries_count} participant{raffle.entries_count !== 1 ? 's' : ''}
                      </div>
                    )}
                    
                    {/* Unlock Status for Unlockable Raffles */}
                    {raffle.type?.code === 'unlockable' && raffle.min_entries_to_unlock && (
                      <div style={{ 
                        marginTop: '12px', 
                        padding: '10px', 
                        background: 'var(--tg-theme-bg-color, #ffffff)', 
                        borderRadius: '8px',
                        fontSize: '13px'
                      }}>
                        {raffle.is_unlocked ? (
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                              <span>🔓</span>
                              <strong style={{ color: '#4caf50' }}>Unlocked</strong>
                            </div>
                            {raffle.draw_date && (
                              <div style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color, #666)' }}>
                                Draw: {formatShortDate(raffle.draw_date)}
                                {getDaysUntilDraw(raffle.draw_date) !== null && getDaysUntilDraw(raffle.draw_date) > 0 && (
                                  <span style={{ display: 'block', marginTop: '4px', fontWeight: '600' }}>
                                    In {getDaysUntilDraw(raffle.draw_date)} day{getDaysUntilDraw(raffle.draw_date) !== 1 ? 's' : ''}
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                        ) : (
                          <div>
                            <div style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color, #666)', marginBottom: '6px' }}>
                              Progress: {raffle.entries_count || 0} / {raffle.min_entries_to_unlock}
                            </div>
                            <div style={{ width: '100%', height: '6px', background: 'var(--tg-theme-hint-color, #e0e0e0)', borderRadius: '3px', overflow: 'hidden' }}>
                              <div 
                                style={{ 
                                  height: '100%', 
                                  background: 'var(--tg-theme-button-color, #3390ec)',
                                  width: `${Math.min(100, ((raffle.entries_count || 0) / raffle.min_entries_to_unlock) * 100)}%`,
                                  transition: 'width 0.3s'
                                }}
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
    </div>
  );
}

