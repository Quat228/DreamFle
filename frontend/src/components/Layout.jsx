import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { raffleAPI } from '../services/api';
import CountdownPrompt from './CountdownPrompt';
import './Layout.css';

export default function Layout({ children }) {
  const location = useLocation();
  const { user, loading } = useAuth();
  const [countdownRaffle, setCountdownRaffle] = useState(null);
  const pollingIntervalRef = useRef(null);
  const scheduledPromptRef = useRef(null);

  const navItems = [
    { path: '/', label: 'Raffles', icon: '🎰' },
    { path: '/shop', label: 'Shop', icon: '🛒' },
    { path: '/entries', label: 'My Entries', icon: '🎫' },
    { path: '/previous-raffles', label: 'Previous', icon: '🏆' },
    { path: '/profile', label: 'Profile', icon: '👤' },
  ];

  const checkActiveRaffleState = async () => {
    try {
      const state = await raffleAPI.getActiveRaffleState();
      
      if (!state.active) {
        // No active raffle, clear countdown
        setCountdownRaffle(null);
        if (scheduledPromptRef.current) {
          clearTimeout(scheduledPromptRef.current);
          scheduledPromptRef.current = null;
        }
        return;
      }
      
      // Only show countdown for COUNTDOWN status
      if (state.status === "COUNTDOWN" && state.seconds_left > 0) {
        // Clear any scheduled prompt
        if (scheduledPromptRef.current) {
          clearTimeout(scheduledPromptRef.current);
          scheduledPromptRef.current = null;
        }
        
        // Get raffle name for display
        try {
          const raffle = await raffleAPI.getRaffle(state.raffle_id);
          setCountdownRaffle({
            id: state.raffle_id,
            name: raffle.name,
            startAt: raffle.start_at,
            secondsLeft: state.seconds_left,
          });
        } catch (err) {
          console.error('Error getting raffle details:', err);
        }
      } else if (state.status === "FINISHING" || state.status === "FINISHED") {
        // Hide countdown when raffle is finishing or finished
        setCountdownRaffle(null);
        if (scheduledPromptRef.current) {
          clearTimeout(scheduledPromptRef.current);
          scheduledPromptRef.current = null;
        }
      }
    } catch (error) {
      console.error('Error checking active raffle state:', error);
    }
  };

  // Poll for active raffle state
  useEffect(() => {
    if (!loading) {
      checkActiveRaffleState();
      
      // Poll based on status:
      // OPEN -> every 30 seconds
      // COUNTDOWN -> every 1 second
      // FINISHING -> every 1 second
      // FINISHED -> stop polling
      const poll = async () => {
        await checkActiveRaffleState();
        
        // Determine next poll interval based on current state
        let interval = 30000; // Default 30 seconds for OPEN
        if (countdownRaffle) {
          interval = 1000; // 1 second for COUNTDOWN/FINISHING
        }
        
        pollingIntervalRef.current = setTimeout(poll, interval);
      };
      
      // Start polling with initial interval
      const initialInterval = countdownRaffle ? 1000 : 30000;
      pollingIntervalRef.current = setTimeout(poll, initialInterval);
    }

    return () => {
      if (pollingIntervalRef.current) {
        clearTimeout(pollingIntervalRef.current);
      }
      if (scheduledPromptRef.current) {
        clearTimeout(scheduledPromptRef.current);
      }
    };
  }, [loading, countdownRaffle]);

  // Hide countdown if user navigates to live page
  useEffect(() => {
    if (location.pathname.includes('/live')) {
      setCountdownRaffle(null);
      // Clear scheduled prompt when navigating to live page
      if (scheduledPromptRef.current) {
        clearTimeout(scheduledPromptRef.current);
        scheduledPromptRef.current = null;
      }
    }
  }, [location.pathname]);

  const handleDismissCountdown = () => {
    setCountdownRaffle(null);
    // Clear scheduled prompt when dismissing
    if (scheduledPromptRef.current) {
      clearTimeout(scheduledPromptRef.current);
      scheduledPromptRef.current = null;
    }
  };

  // Show loading screen while authenticating
  if (loading) {
    return (
      <div className="layout">
        <div className="layout-content" style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          minHeight: '100vh',
          padding: '20px'
        }}>
          <div className="loading">Authenticating...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="layout">
      <div className="layout-content">{children}</div>
      {countdownRaffle && (
        <CountdownPrompt
          raffleId={countdownRaffle.id}
          raffleName={countdownRaffle.name}
          startAt={countdownRaffle.startAt}
          onDismiss={handleDismissCountdown}
        />
      )}
      <nav className="bottom-nav">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </Link>
        ))}
      </nav>
      <footer className="site-footer"></footer>
    </div>
  );
}

