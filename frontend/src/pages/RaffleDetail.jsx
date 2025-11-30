import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { raffleAPI } from '../services/api';
import Card from '../components/Card';
import Button from '../components/Button';
import { formatLongDate, getTimeUntil } from '../utils/dateUtils';
import './RaffleDetail.css';

export default function RaffleDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, refreshUser, loading: authLoading } = useAuth();
  const [raffle, setRaffle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [entering, setEntering] = useState(false);
  const [transparency, setTransparency] = useState(null);
  const [showTransparency, setShowTransparency] = useState(false);

  useEffect(() => {
    // Only load raffle after auth is complete
    if (!authLoading) {
      loadRaffle();
    }
  }, [id, authLoading]);

  const loadRaffle = async () => {
    try {
      setLoading(true);
      const data = await raffleAPI.getRaffle(id);
      setRaffle(data);
      
      // Load transparency data if raffle is finished
      if (data.is_finished) {
        try {
          const transparencyData = await raffleAPI.getTransparency(id);
          setTransparency(transparencyData);
        } catch (error) {
          console.error('Error loading transparency data:', error);
        }
      }
    } catch (error) {
      console.error('Error loading raffle:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const getDaysUntilDraw = (drawDate) => {
    if (!drawDate) return null;
    const timeUntil = getTimeUntil(drawDate);
    if (!timeUntil) return 0;
    return timeUntil.days;
  };

  const handleEnter = async () => {
    if (!user) {
      alert('Please authenticate first');
      return;
    }

    const cost = parseFloat(raffle.cost_tokens);
    if (user.token_balance < cost) {
      alert('Insufficient tokens! Please purchase more in the shop.');
      navigate('/shop');
      return;
    }

    if (!confirm(`Enter this raffle for ${cost} tokens?`)) {
      return;
    }

    try {
      setEntering(true);
      await raffleAPI.enterRaffle(id);
      await refreshUser();
      alert('Successfully entered the raffle!');
      navigate('/entries');
    } catch (error) {
      console.error('Error entering raffle:', error);
      alert(error.response?.data?.detail || 'Failed to enter raffle');
    } finally {
      setEntering(false);
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
      <div className="raffle-detail">
        <div className="loading">Loading raffle details...</div>
      </div>
    );
  }

  if (!raffle) {
    return (
      <div className="raffle-detail">
        <Card>
          <div className="error-state">
            <p>Raffle not found</p>
            <Button onClick={() => navigate('/')}>Go Back</Button>
          </div>
        </Card>
      </div>
    );
  }

  const canEnter = user && parseFloat(user.token_balance || 0) >= parseFloat(raffle.cost_tokens || 0);
  const isFinished = raffle.is_finished;
  const isActive = raffle.is_active && !isFinished;

  return (
    <div className="raffle-detail">
      {raffle.prize?.image && (
        <div className="raffle-hero-image">
          <img src={raffle.prize.image} alt={raffle.prize.name} />
          {raffle.prize.rarity && (
            <span
              className="rarity-badge-large"
              style={{ backgroundColor: getRarityColor(raffle.prize.rarity) }}
            >
              {raffle.prize.rarity.toUpperCase()}
            </span>
          )}
        </div>
      )}

      <Card>
        <div className="raffle-header">
          <h1>{raffle.name}</h1>
          {!isActive && (
            <span className={`status-badge ${isFinished ? 'finished' : 'inactive'}`}>
              {isFinished ? 'Finished' : 'Inactive'}
            </span>
          )}
        </div>
        <p className="raffle-description">{raffle.description}</p>
      </Card>

      <Card>
        <h3>Prize Details</h3>
        <div className="prize-info">
          <div className="prize-name">{raffle.prize?.name}</div>
          {raffle.prize?.description && (
            <p className="prize-description">{raffle.prize.description}</p>
          )}
          {raffle.prize?.value_estimate && (
            <div className="prize-value">
              Estimated value: ${parseFloat(raffle.prize.value_estimate).toFixed(2)}
            </div>
          )}
        </div>
      </Card>

      <Card>
        <h3>Raffle Information</h3>
        <div className="info-grid">
          <div className="info-item">
            <span className="info-label">Entry Cost</span>
            <span className="info-value">{raffle.cost_tokens} tokens</span>
          </div>
          {raffle.min_participants_to_unlock && (
            <div className="info-item">
              <span className="info-label">Min Participants</span>
              <span className="info-value">{raffle.min_participants_to_unlock}</span>
            </div>
          )}
          {raffle.entries_count !== undefined && (
            <div className="info-item">
              <span className="info-label">Current Entries</span>
              <span className="info-value">{raffle.entries_count}</span>
            </div>
          )}
          {raffle.type?.name && (
            <div className="info-item">
              <span className="info-label">Type</span>
              <span className="info-value">{raffle.type.name}</span>
            </div>
          )}
        </div>
        
        {/* Unlock Status */}
        {raffle.type?.code === 'unlockable' && raffle.min_participants_to_unlock && (
          <div style={{ marginTop: '16px', padding: '12px', background: 'var(--tg-theme-bg-color, #f5f5f5)', borderRadius: '8px' }}>
            {raffle.is_unlocked ? (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <span style={{ fontSize: '20px' }}>🔓</span>
                  <strong style={{ color: '#4caf50' }}>Unlocked!</strong>
                </div>
                {raffle.draw_date && (
                  <div style={{ fontSize: '14px', color: 'var(--tg-theme-hint-color, #666)' }}>
                    Draw date: {formatLongDate(raffle.draw_date)}
                    {getDaysUntilDraw(raffle.draw_date) !== null && getDaysUntilDraw(raffle.draw_date) > 0 && (
                      <span style={{ display: 'block', marginTop: '4px', fontWeight: '600' }}>
                        Draw in {getDaysUntilDraw(raffle.draw_date)} day{getDaysUntilDraw(raffle.draw_date) !== 1 ? 's' : ''}
                      </span>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <span style={{ fontSize: '20px' }}>🔒</span>
                  <strong>Locked</strong>
                </div>
                <div style={{ fontSize: '14px', color: 'var(--tg-theme-hint-color, #666)' }}>
                  Progress: {raffle.entries_count || 0} / {raffle.min_participants_to_unlock} participants
                  <div style={{ marginTop: '8px', width: '100%', height: '8px', background: 'var(--tg-theme-hint-color, #e0e0e0)', borderRadius: '4px', overflow: 'hidden' }}>
                    <div 
                      style={{ 
                        height: '100%', 
                        background: 'var(--tg-theme-button-color, #3390ec)',
                        width: `${Math.min(100, ((raffle.entries_count || 0) / raffle.min_participants_to_unlock) * 100)}%`,
                        transition: 'width 0.3s'
                      }}
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </Card>
      
      {/* Winner and Transparency Info */}
      {isFinished && raffle.winner && (
        <Card>
          <h3>Winner</h3>
          <div style={{ padding: '12px', background: 'var(--tg-theme-bg-color, #f5f5f5)', borderRadius: '8px', marginTop: '12px' }}>
            <div style={{ fontSize: '18px', fontWeight: '700', marginBottom: '8px' }}>
              🎉 {raffle.winner.username}
            </div>
            {transparency && (
              <div style={{ marginTop: '16px' }}>
                <Button 
                  variant="secondary" 
                  onClick={() => setShowTransparency(!showTransparency)}
                  style={{ marginBottom: '12px' }}
                >
                  {showTransparency ? 'Hide' : 'Show'} Transparency Data
                </Button>
                {showTransparency && (
                  <div style={{ 
                    padding: '12px', 
                    background: 'var(--tg-theme-secondary-bg-color, #ffffff)', 
                    borderRadius: '8px',
                    fontSize: '12px',
                    fontFamily: 'monospace',
                    wordBreak: 'break-all',
                    overflowWrap: 'break-word',
                    maxWidth: '100%'
                  }}>
                    <div style={{ marginBottom: '8px', wordBreak: 'break-word' }}>
                      <strong>Selection Method:</strong> {transparency.selection_method}
                    </div>
                    <div style={{ marginBottom: '8px', wordBreak: 'break-all', overflowWrap: 'break-word' }}>
                      <strong>Seed:</strong> <span style={{ display: 'block', marginTop: '4px' }}>{transparency.selection_seed}</span>
                    </div>
                    <div style={{ marginBottom: '8px', wordBreak: 'break-all', overflowWrap: 'break-word' }}>
                      <strong>Hash:</strong> <span style={{ display: 'block', marginTop: '4px' }}>{transparency.selection_hash}</span>
                    </div>
                    <div style={{ marginBottom: '8px', wordBreak: 'break-word' }}>
                      <strong>Timestamp:</strong> {formatLongDate(transparency.selection_timestamp)}
                    </div>
                    <div style={{ marginBottom: '8px', wordBreak: 'break-word' }}>
                      <strong>Total Entries:</strong> {transparency.total_entries}
                    </div>
                    {transparency.verification_instructions && (
                      <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid var(--tg-theme-hint-color, #e0e0e0)', wordBreak: 'break-word' }}>
                        <strong>Verification Steps:</strong>
                        <ol style={{ marginTop: '8px', paddingLeft: '20px' }}>
                          {Object.values(transparency.verification_instructions).map((step, idx) => (
                            <li key={idx} style={{ marginBottom: '4px', wordBreak: 'break-word' }}>{step}</li>
                          ))}
                        </ol>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </Card>
      )}

      {isActive && (
        <div className="action-section">
          {!user ? (
            <Button fullWidth onClick={() => navigate('/profile')}>
              Authenticate to Enter
            </Button>
          ) : !canEnter ? (
            <div>
              <Button fullWidth variant="secondary" onClick={() => navigate('/shop')}>
                Get More Tokens
              </Button>
              <p className="insufficient-tokens">
                You need {raffle.cost_tokens} tokens. You have {parseFloat(user.token_balance || 0).toFixed(2)}.
              </p>
            </div>
          ) : (
            <Button
              fullWidth
              onClick={handleEnter}
              disabled={entering}
            >
              {entering ? 'Entering...' : `Enter Raffle (${raffle.cost_tokens} tokens)`}
            </Button>
          )}
        </div>
      )}
    </div>
  );
}



