import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useCRMAuth } from '../../contexts/CRMAuthContext';
import { crmAPI } from '../../services/api';
import Card from '../../components/Card';
import Button from '../../components/Button';
import { formatLongDate } from '../../utils/dateUtils';
import { utcToLocalInput, localInputToUTC, formatCRMDate, getAdminTimezone } from '../../utils/crmDateUtils';
import './CRMRaffleDetail.css';

export default function CRMRaffleDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { loading: authLoading, authenticated } = useCRMAuth();
  const [raffle, setRaffle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [newStartAt, setNewStartAt] = useState('');
  const [message, setMessage] = useState(null);

  useEffect(() => {
    if (!authLoading && !authenticated) {
      // Redirect to login if not authenticated
      navigate('/login');
    } else if (!authLoading && authenticated) {
      loadRaffle();
    }
  }, [id, authLoading, authenticated, navigate]);

  const loadRaffle = async () => {
    try {
      setLoading(true);
      const data = await crmAPI.getRaffle(id);
      setRaffle(data);
      if (data.start_at) {
        // Convert UTC to local timezone for input field
        setNewStartAt(utcToLocalInput(data.start_at));
      }
    } catch (error) {
      console.error('Error loading raffle:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStartTime = async () => {
    if (!newStartAt) {
      setMessage({ type: 'error', text: 'Please select a new start time' });
      return;
    }

    try {
      setUpdating(true);
      setMessage(null);
      
      // Convert local timezone input to UTC ISO string
      const utcISOString = localInputToUTC(newStartAt);
      
      const result = await crmAPI.updateRaffleStartTime(id, utcISOString);
      
      setMessage({
        type: 'success',
        text: result.message || 'Start time updated successfully!',
      });
      
      // Reload raffle to get updated data
      await loadRaffle();
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.error || error.response?.data?.detail || 'Failed to update start time',
      });
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="crm-raffle-detail">
        <div className="crm-page-header">
          <Button onClick={() => navigate('/raffles')} variant="secondary">
            ← Back to Raffles
          </Button>
          <h1>Raffle Details</h1>
        </div>
        <Card>
          <div className="loading">Loading raffle details...</div>
        </Card>
      </div>
    );
  }

  if (!raffle) {
    return (
      <div className="crm-raffle-detail">
        <div className="crm-page-header">
          <Button onClick={() => navigate('/raffles')} variant="secondary">
            ← Back to Raffles
          </Button>
          <h1>Raffle Details</h1>
        </div>
        <Card>
          <div className="error-state">Raffle not found</div>
        </Card>
      </div>
    );
  }

  return (
    <div className="crm-raffle-detail">
      <div className="crm-page-header">
        <Button onClick={() => navigate('/raffles')} variant="secondary">
          ← Back to Raffles
        </Button>
        <h1>{raffle.name}</h1>
      </div>

      <div className="raffle-detail-content">
        <Card>
          <h2>Raffle Information</h2>
          <div className="info-section">
            <div className="info-item">
              <span className="info-label">Status:</span>
              <span className="info-value">
                {raffle.is_finished ? 'Finished' : raffle.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Prize:</span>
              <span className="info-value">{raffle.prize?.name}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Entries:</span>
              <span className="info-value">{raffle.entries_count || 0}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Current Start At:</span>
              <span className="info-value">
                {raffle.start_at ? formatCRMDate(raffle.start_at) : 'Not set'}
              </span>
            </div>
            {raffle.draw_date && (
              <div className="info-item">
                <span className="info-label">Draw Date:</span>
                <span className="info-value">{formatCRMDate(raffle.draw_date)}</span>
              </div>
            )}
          </div>
        </Card>

        {!raffle.is_finished && (
          <Card>
            <h2>Update Start Time</h2>
            <div className="update-section">
              <div className="form-group">
                <label htmlFor="newStartAt">
                  New Start Time ({getAdminTimezone()}):
                </label>
                <input
                  id="newStartAt"
                  type="datetime-local"
                  value={newStartAt}
                  onChange={(e) => setNewStartAt(e.target.value)}
                  disabled={updating}
                  className="datetime-input"
                />
                <small style={{ color: '#666', fontSize: '12px', marginTop: '4px', display: 'block' }}>
                  Enter time in your local timezone. It will be converted to UTC automatically.
                </small>
              </div>
              
              {message && (
                <div className={`message ${message.type}`}>
                  {message.text}
                </div>
              )}
              
              <Button
                onClick={handleUpdateStartTime}
                disabled={updating || !newStartAt}
                fullWidth
              >
                {updating ? 'Updating...' : 'Update Start Time'}
              </Button>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}

