import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCRMAuth } from '../../contexts/CRMAuthContext';
import { crmAPI } from '../../services/api';
import Card from '../../components/Card';
import Button from '../../components/Button';
import { formatCRMDate } from '../../utils/crmDateUtils';
import './CRMRafflesList.css';

export default function CRMRafflesList() {
  const navigate = useNavigate();
  const { user, loading: authLoading } = useCRMAuth();
  const [raffles, setRaffles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !user) {
      // Redirect to login if not authenticated
      navigate('/login');
    } else if (!authLoading && user) {
      loadRaffles();
    }
  }, [authLoading, user, navigate]);

  const loadRaffles = async () => {
    try {
      setLoading(true);
      const data = await crmAPI.getRaffles();
      setRaffles(data);
    } catch (error) {
      console.error('Error loading raffles:', error);
    } finally {
      setLoading(false);
    }
  };


  if (authLoading || loading) {
    return (
      <div className="crm-raffles-list">
        <div className="crm-page-header">
          <Button onClick={() => navigate('/')} variant="secondary">
            ← Back to Home
          </Button>
          <h1>Raffles</h1>
        </div>
        <Card>
          <div className="loading">Loading raffles...</div>
        </Card>
      </div>
    );
  }

  return (
    <div className="crm-raffles-list">
      <div className="crm-page-header">
        <Button onClick={() => navigate('/')} variant="secondary">
          ← Back to Home
        </Button>
        <h1>All Raffles</h1>
      </div>

      {raffles.length === 0 ? (
        <Card>
          <div className="empty-state">No raffles found</div>
        </Card>
      ) : (
        <div className="raffles-grid">
          {raffles.map((raffle) => (
            <Card
              key={raffle.id}
              onClick={() => navigate(`/raffles/${raffle.id}`)}
              style={{ cursor: 'pointer' }}
            >
              <div className="raffle-card">
                <div className="raffle-header">
                  <h3>{raffle.name}</h3>
                  <div className="raffle-status">
                    {raffle.is_finished ? (
                      <span className="status-badge finished">Finished</span>
                    ) : raffle.is_active ? (
                      <span className="status-badge active">Active</span>
                    ) : (
                      <span className="status-badge inactive">Inactive</span>
                    )}
                  </div>
                </div>
                <p className="raffle-description">{raffle.description}</p>
                <div className="raffle-info">
                  <div className="info-row">
                    <span className="info-label">Prize:</span>
                    <span className="info-value">{raffle.prize?.name}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Entries:</span>
                    <span className="info-value">{raffle.entries_count || 0}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Start At:</span>
                    <span className="info-value">{formatCRMDate(raffle.start_at)}</span>
                  </div>
                  {raffle.draw_date && (
                    <div className="info-row">
                      <span className="info-label">Draw Date:</span>
                      <span className="info-value">{formatCRMDate(raffle.draw_date)}</span>
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

