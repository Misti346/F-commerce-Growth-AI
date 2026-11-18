
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function ForgotPasswordPage() {
  const { forgotPassword } = useAuth();
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();

    console.log("FORGOT PASSWORD SUBMIT CLICKED");
    console.log("Email entered:", email);

    setIsSubmitting(true);
    setError('');
    setMessage('');

    try {
      console.log("Sending forgot password API request...");

      const response = await forgotPassword(email);

      console.log("API RESPONSE:", response);

      setMessage(
        response.message || 'If an account exists, a reset email has been sent.'
      );
    } catch (err) {
      console.error("FORGOT PASSWORD ERROR:", err);
      console.error("ERROR RESPONSE:", err.response?.data);

      setError(
        err.response?.data?.message || 'Unable to process reset request.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4 py-10">
      <div className="w-full max-w-lg rounded-3xl border border-slate-200 bg-white p-8 shadow-soft">
        <h1 className="text-3xl font-bold text-slate-900">
          Forgot password
        </h1>

        <p className="mt-2 text-sm text-slate-500">
          Enter your email address to receive a password reset link.
        </p>

        {error && (
          <div className="mt-5 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
            {error}
          </div>
        )}

        {message && (
          <div className="mt-5 rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-6 space-y-5">
          <label className="block space-y-2 text-sm font-medium text-slate-700">
            <span>Email</span>

            <div className="relative">
              <Mail className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-slate-400" />

              <input
                type="email"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="w-full rounded-xl border border-slate-200 bg-white py-2.5 pl-10 pr-3 text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
                placeholder="you@example.com"
              />
            </div>
          </label>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-xl bg-brand-600 px-4 py-3 font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSubmitting ? 'Sending...' : 'Send reset instruction'}
          </button>
        </form>

        <div className="mt-6 text-sm text-slate-500">
          Back to{' '}
          <Link to="/login" className="font-semibold text-brand-600 hover:text-brand-700">
            Login
          </Link>
        </div>
      </div>
    </div>
  );
}
