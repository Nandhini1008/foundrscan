import React from 'react';
import Navbar from '../components/common/Navbar';
import AuthForm from '../components/auth/AuthForm';
import Footer from '../components/landing/Footer';

const LoginPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Navbar />
      <AuthForm type="login" />
      <Footer />
    </div>
  );
};

export default LoginPage;