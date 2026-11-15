import React, { useState } from 'react';
import { Lock, Mail, User as UserIcon, Eye, EyeOff, AlertCircle, ArrowRight, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface SignupPageProps {
  onSwitchToLogin: () => void;
}

export const SignupPage: React.FC<SignupPageProps> = ({ onSwitchToLogin }) => {
  const { signup } = useAuth();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    const cleanName = fullName.trim();
    const cleanEmail = email.trim();

    if (cleanName.length < 2) {
      setErrorMessage('Full name must be at least 2 characters long.');
      return;
    }

    if (!cleanEmail.includes('@') || !cleanEmail.includes('.')) {
      setErrorMessage('Please enter a valid academic or professional email address.');
      return;
    }

    if (password.length < 8) {
      setErrorMessage('Password must be at least 8 characters in length.');
      return;
    }

    if (password !== confirmPassword) {
      setErrorMessage('Passwords do not match. Please verify your entry.');
      return;
    }

    try {
      setIsSubmitting(true);
      await signup({
        fullName: cleanName,
        email: cleanEmail,
        password,
      });
    } catch (err: any) {
      setErrorMessage(err.message || 'Registration failed. The email address may already be registered.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        width: '100vw',
        backgroundColor: 'var(--color-surface)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'var(--space-xl)',
        fontFamily: 'var(--font-family)',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '460px',
          backgroundColor: 'var(--color-bg)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-sm)',
          boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: 'var(--space-lg) var(--space-xl)',
            borderBottom: '1px solid var(--color-border)',
            backgroundColor: 'var(--color-bg)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: 'var(--space-xs)' }}>
            <span
              style={{
                width: '8px',
                height: '8px',
                backgroundColor: 'var(--color-primary)',
                display: 'inline-block',
              }}
            />
            <span
              style={{
                fontSize: '11px',
                fontWeight: 600,
                letterSpacing: '0.05em',
                textTransform: 'uppercase',
                color: 'var(--color-text-secondary)',
              }}
            >
              EarthSage AI Workstation
            </span>
            <span
              style={{
                fontSize: '10px',
                color: 'var(--color-text-muted)',
                border: '1px solid var(--color-border)',
                padding: '1px 4px',
                borderRadius: '2px',
                marginLeft: 'auto',
              }}
            >
              Registration
            </span>
          </div>

          <h1
            style={{
              fontSize: '16px',
              fontWeight: 600,
              color: 'var(--color-text-primary)',
              margin: '6px 0 2px 0',
            }}
          >
            Create Researcher Account
          </h1>
          <p
            style={{
              fontSize: '12px',
              color: 'var(--color-text-muted)',
              lineHeight: 1.4,
            }}
          >
            Register your credentials to execute Mann-Kendall trend analyses, manage climatological inquiries, and generate formal PDF reports.
          </p>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} style={{ padding: 'var(--space-xl)' }}>
          {errorMessage && (
            <div
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '8px',
                padding: '10px 12px',
                backgroundColor: 'var(--color-error-subtle)',
                border: '1px solid var(--color-error-border)',
                color: 'var(--color-error)',
                borderRadius: 'var(--radius-xs)',
                fontSize: '12px',
                marginBottom: 'var(--space-lg)',
              }}
            >
              <AlertCircle size={15} style={{ flexShrink: 0, marginTop: '1px' }} />
              <div>{errorMessage}</div>
            </div>
          )}

          {/* Full Name */}
          <div style={{ marginBottom: 'var(--space-md)' }}>
            <label
              htmlFor="fullName"
              style={{
                display: 'block',
                fontSize: '11px',
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '0.03em',
                color: 'var(--color-text-secondary)',
                marginBottom: '6px',
              }}
            >
              Full Name & Academic Title
            </label>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                border: '1px solid var(--color-border)',
                backgroundColor: 'var(--color-bg)',
                borderRadius: 'var(--radius-xs)',
                padding: '0 10px',
              }}
            >
              <UserIcon size={14} style={{ color: 'var(--color-text-muted)', marginRight: '8px' }} />
              <input
                id="fullName"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Dr. Sarah Khan"
                required
                autoComplete="name"
                style={{
                  width: '100%',
                  padding: '8px 0',
                  border: 'none',
                  outline: 'none',
                  fontSize: '12px',
                  color: 'var(--color-text-primary)',
                  backgroundColor: 'transparent',
                }}
              />
            </div>
          </div>

          {/* Email */}
          <div style={{ marginBottom: 'var(--space-md)' }}>
            <label
              htmlFor="signupEmail"
              style={{
                display: 'block',
                fontSize: '11px',
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '0.03em',
                color: 'var(--color-text-secondary)',
                marginBottom: '6px',
              }}
            >
              Institutional Email
            </label>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                border: '1px solid var(--color-border)',
                backgroundColor: 'var(--color-bg)',
                borderRadius: 'var(--radius-xs)',
                padding: '0 10px',
              }}
            >
              <Mail size={14} style={{ color: 'var(--color-text-muted)', marginRight: '8px' }} />
              <input
                id="signupEmail"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="sarah.khan@earthscience.org"
                required
                autoComplete="email"
                style={{
                  width: '100%',
                  padding: '8px 0',
                  border: 'none',
                  outline: 'none',
                  fontSize: '12px',
                  color: 'var(--color-text-primary)',
                  backgroundColor: 'transparent',
                }}
              />
            </div>
          </div>

          {/* Password */}
          <div style={{ marginBottom: 'var(--space-md)' }}>
            <label
              htmlFor="signupPassword"
              style={{
                display: 'block',
                fontSize: '11px',
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '0.03em',
                color: 'var(--color-text-secondary)',
                marginBottom: '6px',
              }}
            >
              Password (Minimum 8 characters)
            </label>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                border: '1px solid var(--color-border)',
                backgroundColor: 'var(--color-bg)',
                borderRadius: 'var(--radius-xs)',
                padding: '0 10px',
              }}
            >
              <Lock size={14} style={{ color: 'var(--color-text-muted)', marginRight: '8px' }} />
              <input
                id="signupPassword"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter secure password"
                required
                autoComplete="new-password"
                style={{
                  width: '100%',
                  padding: '8px 0',
                  border: 'none',
                  outline: 'none',
                  fontSize: '12px',
                  color: 'var(--color-text-primary)',
                  backgroundColor: 'transparent',
                }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  color: 'var(--color-text-muted)',
                  display: 'flex',
                  alignItems: 'center',
                  padding: '4px',
                }}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff size={14} /> : <Eye size={14} />}
              </button>
            </div>
          </div>

          {/* Confirm Password */}
          <div style={{ marginBottom: 'var(--space-xl)' }}>
            <label
              htmlFor="confirmPassword"
              style={{
                display: 'block',
                fontSize: '11px',
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '0.03em',
                color: 'var(--color-text-secondary)',
                marginBottom: '6px',
              }}
            >
              Confirm Password
            </label>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                border: '1px solid var(--color-border)',
                backgroundColor: 'var(--color-bg)',
                borderRadius: 'var(--radius-xs)',
                padding: '0 10px',
              }}
            >
              <Lock size={14} style={{ color: 'var(--color-text-muted)', marginRight: '8px' }} />
              <input
                id="confirmPassword"
                type={showPassword ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Re-enter password"
                required
                autoComplete="new-password"
                style={{
                  width: '100%',
                  padding: '8px 0',
                  border: 'none',
                  outline: 'none',
                  fontSize: '12px',
                  color: 'var(--color-text-primary)',
                  backgroundColor: 'transparent',
                }}
              />
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting}
            style={{
              width: '100%',
              padding: '10px 16px',
              backgroundColor: isSubmitting ? 'var(--color-text-muted)' : 'var(--color-primary)',
              color: 'var(--color-text-inverse)',
              borderRadius: 'var(--radius-xs)',
              fontSize: '12px',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              transition: 'background-color 0.15s ease',
            }}
          >
            {isSubmitting ? (
              <span>Creating Account & Initializing Workstation...</span>
            ) : (
              <>
                <span>Complete Registration & Launch Station</span>
                <ArrowRight size={14} />
              </>
            )}
          </button>
        </form>

        {/* Footer Switch to Login */}
        <div
          style={{
            padding: 'var(--space-md) var(--space-xl)',
            backgroundColor: 'var(--color-surface)',
            borderTop: '1px solid var(--color-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '12px',
          }}
        >
          <span style={{ color: 'var(--color-text-secondary)' }}>Already hold research credentials?</span>
          <button
            onClick={onSwitchToLogin}
            style={{
              color: 'var(--color-primary)',
              fontWeight: 600,
              fontSize: '12px',
              textDecoration: 'underline',
            }}
          >
            Sign In
          </button>
        </div>
      </div>

      {/* Security note */}
      <div
        style={{
          marginTop: 'var(--space-lg)',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '11px',
          color: 'var(--color-text-muted)',
        }}
      >
        <ShieldCheck size={13} style={{ color: 'var(--color-success)' }} />
        <span>Passwords secured via bcrypt (12 rounds). Zero plaintext storage.</span>
      </div>
    </div>
  );
};

