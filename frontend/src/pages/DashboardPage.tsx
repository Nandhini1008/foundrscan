import React from 'react';
import Navbar from '../components/common/Navbar';
import Dashboard from '../components/dashboard/Dashboard';

const DashboardPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Navbar />
      <Dashboard />
    </div>
  );
};

export default DashboardPage;