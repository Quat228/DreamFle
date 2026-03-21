import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './CountdownPrompt.css';

export default function CountdownPrompt({ raffleId, raffleName, startAt, onDismiss }) {
  const navigate = useNavigate();
  const [timeUntilStart, setTimeUntilStart] = useState(null);

  useEffect(() => {
    if (!startAt) return;

    const updateCountdown = () => {
      const now = new Date();
      const start = new Date(startAt);
      const diff = Math.max(0, Math.floor((start - now) / 1000)); // seconds
      setTimeUntilStart(diff);

      // Auto-dismiss when raffle starts
      if (diff === 0 && onDismiss) {
        onDismiss();
      }
    };

    updateCountdown();
    const interval = setInterval(updateCountdown, 1000);

    return () => clearInterval(interval);
  }, [startAt, onDismiss]);

  const formatTime = (seconds) => {
    if (seconds <= 0) return '0:00';
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const handleGoToLive = () => {
    navigate(`/raffle/${raffleId}/live`);
    if (onDismiss) {
      onDismiss();
    }
  };

  if (timeUntilStart === null || timeUntilStart <= 0) {
    return null;
  }

  return (
    <div className="countdown-prompt">
      <div className="countdown-content">
        <div className="countdown-info">
          <div className="countdown-title">
            🎰 Raffle Starting Soon!
          </div>
          <div className="countdown-raffle-name">{raffleName}</div>
          <div className="countdown-timer">
            Starts in: <span className="timer-value">{formatTime(timeUntilStart)}</span>
          </div>
        </div>
        <button 
          className="countdown-button"
          onClick={handleGoToLive}
        >
          Watch Live
        </button>
      </div>
    </div>
  );
}




