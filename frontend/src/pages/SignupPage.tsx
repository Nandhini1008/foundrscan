import React from 'react';
import Navbar from '../components/common/Navbar';
import AuthForm from '../components/auth/AuthForm';
import Footer from '../components/landing/Footer';

const SignupPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Navbar />
      <AuthForm type="signup" />
      <Footer />
    </div>
  );
};

export default SignupPage;