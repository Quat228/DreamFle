import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { raffleAPI } from '../services/api';
import Card from '../components/Card';
import Button from '../components/Button';
import './RaffleDetail.css';

export default function RaffleDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, refreshUser } = useAuth();
  const [raffle, setRaffle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [entering, setEntering] = useState(false);

  useEffect(() => {
    loadRaffle();
  }, [id]);

  const loadRaffle = async () => {
    try {
      setLoading(true);
      const data = await raffleAPI.getRaffle(id);
      setRaffle(data);
    } catch (error) {
      console.error('Error loading raffle:', error);
    } finally {
      setLoading(false);
    }
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
      </Card>

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

