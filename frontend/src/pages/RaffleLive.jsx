import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { raffleAPI } from '../services/api';
import Roulette from '../components/Roulette';
import Card from '../components/Card';
import Button from '../components/Button';
import './RaffleLive.css';

export default function RaffleLive() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { loading: authLoading } = useAuth();
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const rouletteRef = useRef(null);
  const pollingTimeoutRef = useRef(null);

  useEffect(() => {
    if (!authLoading) {
      loadStatus();
    }
  }, [id, authLoading]);

  useEffect(() => {
    // Start polling based on status
    if (status) {
      startPolling();
    }

    return () => {
      stopPolling();
    };
  }, [id, status]);

  useEffect(() => {
    // Start roulette spinning when we have entry IDs and status is COUNTDOWN
    if (status && status.status === "COUNTDOWN" && status.entry_ids && status.entry_ids.length > 0 && rouletteRef.current) {
      rouletteRef.current.start();
    }

    // Stop roulette on winner if FINISHING or FINISHED
    if (status && (status.status === "FINISHING" || status.status === "FINISHED") && status.winner && status.winner.entry_id && rouletteRef.current) {
      rouletteRef.current.stopOnEntry(status.winner.entry_id);
    }

    return () => {
      if (rouletteRef.current) {
        rouletteRef.current.reset();
      }
    };
  }, [status]);

  const loadStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await raffleAPI.getLiveRaffleStatus(id);
      setStatus(data);
    } catch (err) {
      console.error('Error loading live raffle status:', err);
      setError('Failed to load raffle status');
    } finally {
      setLoading(false);
    }
  };

  const startPolling = () => {
    stopPolling(); // Clear any existing polling
    
    if (!status) return;
    
    // Determine polling interval based on status
    let interval;
    if (status.status === "OPEN") {
      interval = 30000; // 30 seconds
    } else if (status.status === "COUNTDOWN") {
      interval = 1000; // 1 second
    } else if (status.status === "FINISHING") {
      interval = 1000; // 1 second
    } else if (status.status === "FINISHED") {
      // Stop polling for FINISHED
      return;
    } else {
      interval = 30000; // Default to 30 seconds
    }
    
    const poll = async () => {
      try {
        const data = await raffleAPI.getLiveRaffleStatus(id);
        setStatus(data);
        
        // Continue polling if not FINISHED
        if (data.status !== "FINISHED") {
          pollingTimeoutRef.current = setTimeout(poll, interval);
        }
      } catch (err) {
        console.error('Error polling live raffle status:', err);
        // Retry after interval on error
        pollingTimeoutRef.current = setTimeout(poll, interval);
      }
    };
    
    pollingTimeoutRef.current = setTimeout(poll, interval);
  };

  const stopPolling = () => {
    if (pollingTimeoutRef.current) {
      clearTimeout(pollingTimeoutRef.current);
      pollingTimeoutRef.current = null;
    }
  };

  const handleBackToRaffle = () => {
    navigate(`/raffle/${id}`);
  };

  if (loading && !status) {
    return (
      <div className="raffle-live">
        <Card>
          <div className="loading">Loading live raffle...</div>
        </Card>
      </div>
    );
  }

  if (error && !status) {
    return (
      <div className="raffle-live">
        <Card>
          <div className="error-state">
            <p>{error}</p>
            <Button onClick={() => navigate('/')}>Go Back</Button>
          </div>
        </Card>
      </div>
    );
  }

  if (!status) {
    return null;
  }

  return (
    <div className="raffle-live">
      <div className="live-header">
        <h1>🎰 Live Raffle Selection</h1>
        <div className="raffle-name">{status.raffle_name}</div>
      </div>

      <Card>
        <Roulette 
          ref={rouletteRef}
          entryIds={status.entry_ids || []}
          entryQuantities={status.entry_quantities || {}}
        />
      </Card>

      {(status.status === "FINISHING" || status.status === "FINISHED") && status.winner && (
        <Card>
          <div className="winner-announcement">
            <h2>🎉 Winner Selected!</h2>
            <div className="winner-info">
              <div className="winner-label">Entry ID:</div>
              <div className="winner-value">{status.winner.entry_id}</div>
              {status.winner.user && (
                <>
                  <div className="winner-label">Winner:</div>
                  <div className="winner-value">{status.winner.user}</div>
                </>
              )}
            </div>
            <Button onClick={handleBackToRaffle} fullWidth>
              View Raffle Details
            </Button>
          </div>
        </Card>
      )}

      {status.status === "COUNTDOWN" && (
        <Card>
          <div className="status-info">
            <div className="status-label">Status:</div>
            <div className="status-value">Raffle starting soon...</div>
          </div>
        </Card>
      )}

      {status.status === "OPEN" && (
        <Card>
          <div className="status-info">
            <div className="status-label">Status:</div>
            <div className="status-value">Raffle is open for entries</div>
          </div>
        </Card>
      )}

      <div className="live-footer">
        <Button onClick={handleBackToRaffle} variant="secondary">
          Back to Raffle
        </Button>
      </div>
    </div>
  );
}

