import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Eye, EyeOff, CheckCircle2 } from 'lucide-react';
import Input from '../common/Input';
import Button from '../common/Button';
import GlassmorphicCard from '../common/GlassmorphicCard';
import GradientText from '../common/GradientText';

import { auth, googleProvider, db } from '../../firebase'; // ✅ import Firebase setup
import { createUserWithEmailAndPassword, signInWithEmailAndPassword, signInWithPopup, onAuthStateChanged } from 'firebase/auth';
import { doc, setDoc, getDoc } from 'firebase/firestore';

interface AuthFormProps {
  type: 'login' | 'signup';
}

const AuthForm: React.FC<AuthFormProps> = ({ type }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
  
    try {
      if (type === 'signup') {
        // CREATE USER IN AUTH
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
  
        // ADD USER METADATA TO FIRESTORE
        await setDoc(doc(db, 'users', user.uid), {
          uid: user.uid,
          name,
          email: user.email,
          createdAt: new Date().toISOString(),
          lastLogin: new Date().toISOString(),
          provider: 'email',
          isActive: true
        });
  
        console.log('✅ Signup successful, user stored in Firestore');
  
      } else {
        // LOGIN USER
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
  
        // CHECK IF USER EXISTS IN FIRESTORE
        const userDocRef = doc(db, 'users', user.uid);
        const userDocSnap = await getDoc(userDocRef);
  
        if (!userDocSnap.exists()) {
          setError('User exists in auth but not in database. Please contact support.');
          return;
        }
  
        const userData = userDocSnap.data();
        if (!userData.isActive) {
          setError('Your account is inactive. Please contact support.');
          return;
        }
  
        // UPDATE LAST LOGIN
        await setDoc(userDocRef, {
          lastLogin: new Date().toISOString()
        }, { merge: true });
  
        console.log('✅ Login successful, Firestore updated');
      }
  
      setSuccess(true);
      setTimeout(() => {
        navigate('/chat', { replace: true });
      }, 1500);
  
    } catch (err: any) {
      console.error('❌ Auth error:', err);
      let errorMessage = 'An error occurred during authentication';
      let showSignupLink = false;
      
      switch (err.code) {
        case 'auth/user-not-found':
          errorMessage = 'No account found with this email. Please sign up first.';
          showSignupLink = true;
          break;
        case 'auth/wrong-password':
          errorMessage = 'Incorrect password';
          break;
        case 'auth/invalid-credential':
          errorMessage = 'Invalid email or password. Please check your credentials or sign up if you haven\'t already.';
          showSignupLink = true;
          break;
        case 'auth/email-already-in-use':
          errorMessage = 'An account already exists with this email';
          break;
        case 'auth/weak-password':
          errorMessage = 'Password should be at least 6 characters';
          break;
        case 'auth/invalid-email':
          errorMessage = 'Invalid email address';
          break;
        default:
          errorMessage = err.message;
      }
      setError(errorMessage);

      // Show error with signup link if needed
      return (
        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-md">
          <p className="text-red-500 text-sm">{errorMessage}</p>
          {showSignupLink && (
            <div className="mt-2">
              <Link
                to="/signup"
                className="text-sm text-purple-400 hover:text-purple-300 font-medium transition-colors"
              >
                Create an account →
              </Link>
            </div>
          )}
        </div>
      );
    } finally {
      setLoading(false);
    }
  };
  const handleGoogleLogin = async () => {
    setError('');
    setLoading(true);
    try {
      const result = await signInWithPopup(auth, googleProvider);
      const user = result.user;
      
      // Check if user exists in Firestore
      const userDocRef = doc(db, 'users', user.uid);
      const userDocSnap = await getDoc(userDocRef);
      
      if (!userDocSnap.exists()) {
        // If user doc doesn't exist:
        if (type === 'signup') {
          // If in signup mode, create the user doc
          console.log('⚠️ Google signup - new user, creating Firestore record');
          await setDoc(userDocRef, {
            uid: user.uid,
            name: user.displayName,
            email: user.email,
            createdAt: new Date().toISOString(),
            lastLogin: new Date().toISOString(),
            provider: 'google',
            isActive: true,
            photoURL: user.photoURL
          });
          console.log('✅ New Google user created in Firestore during signup');
        } else {
          // If in login mode, block login and show error
          console.log('❌ Google login - user not found in Firestore, blocking login');
          setError('No account found with this Google email. Please sign up first.');
          setLoading(false);
          // Optional: Consider signing out the Firebase user created by signInWithPopup
          // await auth.signOut();
          return;
        }
      } else {
        // User exists - check isActive status (applies to both login and signup if user already exists)
        const userData = userDocSnap.data();
        
        if (!userData?.isActive) {
          setError('Your account is inactive. Please contact support.');
          setLoading(false);
          // Optional: Consider signing out the Firebase user
          // await auth.signOut();
          return;
        }

        // Update last login time for existing users (applies to both login and signup if user already exists)
        console.log('✅ Existing Google user - updating last login');
        await setDoc(userDocRef, {
          lastLogin: new Date().toISOString()
        }, { merge: true });
        
      }
      
      // If we reached here, it means either a new user was created (signup) or an existing user
      // was found and is active (login or signup).
      console.log('✅ Google authentication successful, proceeding...');
      setSuccess(true);
      setTimeout(() => {
        navigate('/chat', { replace: true });
      }, 1500);

    } catch (err: any) {
      console.error('❌ Google auth error:', err);
      let errorMessage = 'An error occurred during Google authentication';
      let showSignupLink = false;
      
      if (err.code === 'auth/popup-closed-by-user') {
        errorMessage = 'Google sign-in was cancelled';
      } else if (err.code === 'auth/popup-blocked') {
        errorMessage = 'Pop-up was blocked by the browser';
      } else if (err.code === 'auth/invalid-credential') {
        errorMessage = 'Unable to sign in with Google. Please try signing up first.';
        showSignupLink = true;
      } else if (err.code === 'auth/account-exists-with-different-credential') {
        errorMessage = 'An account already exists with this email using a different sign-in method.';
        showSignupLink = true;
      }
      
      setError(errorMessage);

      // Show error with signup link if needed
      // Note: This error display logic is outside the main return block, so it might not render correctly here.
      // The main error rendering is handled in the JSX below.
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative">
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>

      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-blob"></div>
        <div className="absolute top-3/4 right-1/4 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-blob animation-delay-2000"></div>
      </div>

      <GlassmorphicCard className="w-full max-w-md p-8">
        {loading ? (
          <div className="text-center py-8">
            <div className="relative inline-block">
              <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-8 h-8 bg-purple-500 rounded-full animate-pulse"></div>
              </div>
            </div>
            <p className="mt-4 text-gray-300 text-lg font-medium">
              {type === 'login' ? 'Signing in...' : 'Creating your account...'}
            </p>
            <p className="mt-2 text-gray-400 text-sm">
              Please wait while we set up your account
            </p>
          </div>
        ) : success ? (
          <div className="text-center py-8">
            <div className="relative inline-block">
              <CheckCircle2 className="w-16 h-16 text-green-500 animate-bounce" />
            </div>
            <p className="mt-4 text-gray-300 text-lg font-medium">
              {type === 'login' ? 'Successfully signed in!' : 'Account created successfully!'}
            </p>
            <p className="mt-2 text-gray-400 text-sm">
              Redirecting you to the chat...
            </p>
          </div>
        ) : (
          <>
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold">
                {type === 'login' ? (
                  <>Welcome <GradientText>Back</GradientText></>
                ) : (
                  <>Join <GradientText>Founder Scan</GradientText></>
                )}
              </h2>
              <p className="text-gray-400 mt-2">
                {type === 'login'
                  ? 'Log in to continue validating your startup idea'
                  : 'Create an account to start validating your startup idea'}
              </p>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-md text-red-500 text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              {type === 'signup' && (
                <Input
                  label="Full Name"
                  type="text"
                  placeholder="Enter your name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  icon={<User className="h-5 w-5 text-gray-500" />}
                />
              )}

              <Input
                label="Email Address"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                icon={<Mail className="h-5 w-5 text-gray-500" />}
              />

              <div className="relative">
                <Input
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder={type === 'login' ? 'Enter your password' : 'Create a password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  icon={<Lock className="h-5 w-5 text-gray-500" />}
                />
                <button
                  type="button"
                  className="absolute right-3 top-[38px] text-gray-500 hover:text-white transition-colors"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5" />
                  ) : (
                    <Eye className="h-5 w-5" />
                  )}
                </button>
              </div>

              {type === 'login' && (
                <div className="flex justify-end">
                  <a href="#" className="text-sm text-purple-400 hover:text-purple-300 transition-colors">
                    Forgot password?
                  </a>
                </div>
              )}

              <Button type="submit" variant="primary" fullWidth disabled={loading}>
                {loading ? 'Please wait...' : type === 'login' ? 'Log In' : 'Create Account'}
              </Button>
            </form>

            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-700"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-gray-900 text-gray-400">Or continue with</span>
                </div>
              </div>

              <div className="mt-6 grid grid-cols-1 gap-3">
                <button
                  type="button"
                  onClick={handleGoogleLogin}
                  disabled={loading}
                  className="group relative flex justify-center py-2 px-4 border border-gray-700 rounded-md bg-gray-800/50 hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <div className="flex items-center">
                      <div className="w-5 h-5 border-2 border-purple-500 border-t-transparent rounded-full animate-spin mr-2"></div>
                      <span className="text-gray-300 text-sm">Connecting...</span>
                    </div>
                  ) : (
                    <span className="text-gray-300 text-sm">Google</span>
                  )}
                </button>
              </div>
            </div>

            <div className="mt-6 text-center text-sm">
              <p className="text-gray-400">
                {type === 'login' ? "Don't have an account? " : "Already have an account? "}
                <Link
                  to={type === 'login' ? '/signup' : '/login'}
                  className="text-purple-400 hover:text-purple-300 font-medium transition-colors"
                >
                  {type === 'login' ? 'Sign up' : 'Log in'}
                </Link>
              </p>
            </div>
          </>
        )}
      </GlassmorphicCard>

      <style>{`
        @keyframes blob {
          0% {
            transform: translate(0px, 0px) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
          100% {
            transform: translate(0px, 0px) scale(1);
          }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .bg-grid-pattern {
          background-image: 
            linear-gradient(rgba(30, 41, 59, 0.3) 1px, transparent 1px),
            linear-gradient(90deg, rgba(30, 41, 59, 0.3) 1px, transparent 1px);
          background-size: 40px 40px;
        }
      `}</style>
    </div>
  );
};

export default AuthForm;
