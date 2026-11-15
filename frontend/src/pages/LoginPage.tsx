import React, { useState } from 'react';
import { Lock, Mail, Eye, EyeOff, AlertCircle, ArrowRight, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface LoginPageProps {
  onSwitchToSignup: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onSwitchToSignup }) => {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    const cleanEmail = email.trim();
    if (!cleanEmail || !password) {
      setErrorMessage('Please provide both email address and password.');
      return;
    }

    try {
      setIsSubmitting(true);
      await login({ email: cleanEmail, password });
    } catch (err: any) {
      setErrorMessage(err.message || 'Authentication failed. Please verify your credentials.');
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
          maxWidth: '420px',
          backgroundColor: 'var(--color-bg)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-sm)',
          boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
          overflow: 'hidden',
        }}
      >
        {/* Top Header Bar */}
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
              v1.0 Auth
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
            Researcher Sign In
          </h1>
          <p
            style={{
              fontSize: '12px',
              color: 'var(--color-text-muted)',
              lineHeight: 1.4,
            }}
          >
            Authenticate to access NASA POWER satellite reanalysis datasets, statistical trend pipelines, and private investigations.
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

          {/* Email Field */}
          <div style={{ marginBottom: 'var(--space-lg)' }}>
            <label
              htmlFor="email"
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
              Email Address
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
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="researcher@earthscience.org"
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

          {/* Password Field */}
          <div style={{ marginBottom: 'var(--space-xl)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
              <label
                htmlFor="password"
                style={{
                  fontSize: '11px',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  letterSpacing: '0.03em',
                  color: 'var(--color-text-secondary)',
                }}
              >
                Password
              </label>
            </div>
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
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter account password"
                required
                autoComplete="current-password"
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
              <span>Authenticating Session...</span>
            ) : (
              <>
                <span>Sign In to Workstation</span>
                <ArrowRight size={14} />
              </>
            )}
          </button>
        </form>

        {/* Footer Switch to Signup */}
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
          <span style={{ color: 'var(--color-text-secondary)' }}>Need research station access?</span>
          <button
            onClick={onSwitchToSignup}
            style={{
              color: 'var(--color-primary)',
              fontWeight: 600,
              fontSize: '12px',
              textDecoration: 'underline',
            }}
          >
            Register Account
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
        <span>Protected with bcrypt-12, short-lived JWT, and HttpOnly session cookies.</span>
      </div>
    </div>
  );
};

