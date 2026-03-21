import React from 'react';
import { useCRMAuth } from '../contexts/CRMAuthContext';
import './CRMLayout.css';

export default function CRMLayout({ children }) {
  const { loading, authenticated } = useCRMAuth();

  if (loading) {
    return (
      <div className="crm-layout">
        <div className="crm-loading">Loading...</div>
      </div>
    );
  }

  if (!authenticated) {
    return <>{children}</>;
  }

  return (
    <div className="crm-layout">
      <div className="crm-container">
        {children}
      </div>
    </div>
  );
}







