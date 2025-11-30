import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useCRMAuth } from '../contexts/CRMAuthContext';

/**
 * Protected route component for CRM
 * Redirects to login if user is not authenticated
 */
export default function ProtectedCRMRoute({ children }) {
  const { authenticated, loading } = useCRMAuth();
  const location = useLocation();

  // Show loading while checking authentication
  if (loading) {
    return (
      <div className="crm-layout">
        <div className="crm-loading">Loading...</div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  // Save the attempted location so we can redirect back after login
  if (!authenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // User is authenticated, render the protected component
  return <>{children}</>;
}

