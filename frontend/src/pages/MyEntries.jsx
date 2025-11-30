import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { raffleAPI } from '../services/api';
import Card from '../components/Card';
import './MyEntries.css';

export default function MyEntries() {
  const navigate = useNavigate();
  const { user, loading: authLoading } = useAuth();
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Wait for auth to complete, then check if user exists
    if (!authLoading) {
      if (user) {
        loadEntries();
      } else {
        setLoading(false);
      }
    }
  }, [user, authLoading]);

  const loadEntries = async () => {
    try {
      setLoading(true);
      const data = await raffleAPI.getMyEntries();
      setEntries(data);
    } catch (error) {
      console.error('Error loading entries:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="my-entries">
        <Card>
          <div className="empty-state">
            <div className="empty-icon">🔐</div>
            <p>Please authenticate to view your entries</p>
          </div>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="my-entries">
        <div className="loading">Loading your entries...</div>
      </div>
    );
  }

  return (
    <div className="my-entries">
      <div className="entries-header">
        <h1>🎫 My Entries</h1>
        <p className="subtitle">Your raffle participations</p>
      </div>

      {entries.length === 0 ? (
        <Card>
          <div className="empty-state">
            <div className="empty-icon">🎲</div>
            <p>You haven't entered any raffles yet</p>
            <p className="empty-hint">Browse active raffles and enter to win!</p>
          </div>
        </Card>
      ) : (
        <div className="entries-list">
          {entries.map((entry) => (
            <Card
              key={entry.id}
              onClick={() => navigate(`/raffle/${entry.raffle.id}`)}
            >
              <div className="entry-card">
                <div className="entry-header">
                  <h3>{entry.raffle.name}</h3>
                  <span className="entry-date">
                    {new Date(entry.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="entry-prize">
                  <span className="prize-label">Prize:</span>
                  <span className="prize-name">{entry.raffle.prize?.name}</span>
                </div>
                <div className="entry-cost">
                  Cost: {entry.cost_tokens} tokens
                </div>
                {entry.raffle.is_finished && entry.raffle.winner && entry.raffle.winner.user && (
                  <div className={`entry-status ${entry.raffle.winner.user.id === user.id ? 'winner' : 'lost'}`}>
                    {entry.raffle.winner.user.id === user.id ? '🎉 You Won!' : '❌ Not Selected'}
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}



