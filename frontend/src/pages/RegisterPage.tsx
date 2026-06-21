import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import { Lock, Mail, User, Eye, EyeOff, ShieldAlert, CheckCircle2, ArrowRight } from "lucide-react";

export default function RegisterPage() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !email || !password) {
      setError("Please fill in all required fields.");
      return;
    }

    setError(null);
    setSubmitting(true);

    try {
      await axios.post(`${import.meta.env.VITE_API_URL}/auth/register`, {
        username,
        email,
        password,
        // role is intentionally omitted; backend defaults to "user"
      });

      setSuccess(true);
      setTimeout(() => {
        navigate("/login");
      }, 2000);
    } catch (err: any) {
      console.error("Registration failed:", err);
      const msg = err.response?.data?.detail || "Registration failed. Please try again.";
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[85vh] px-4">
      <div className="w-full max-w-[420px] backdrop-blur-md bg-card/30 border border-border/40 p-8 rounded-xl shadow-2xl relative overflow-hidden transition-all duration-300 hover:border-border/60">
        {/* Glow decorative overlays */}
        <div className="absolute -top-16 -left-16 w-32 h-32 bg-[hsl(210,70%,50%)]/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-16 -right-16 w-32 h-32 bg-[hsl(210,70%,50%)]/5 rounded-full blur-3xl pointer-events-none" />

        {/* Header */}
        <div className="text-center mb-8 relative">
          <div className="inline-flex items-center justify-center h-12 w-12 rounded-lg bg-[hsl(210,70%,50%)]/10 border border-[hsl(210,70%,50%)]/20 mb-3 shadow-[0_0_15px_hsl(210,70%,50%/0.15)]">
            <User className="h-6 w-6 text-[hsl(210,70%,50%)]" />
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">Create Account</h2>
          <p className="text-xs text-muted-foreground mt-1.5">
            Register for access to VPRO Voyage Performance analysis tools
          </p>
        </div>

        {/* Success Alert */}
        {success && (
          <div className="flex items-start gap-2.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs p-3.5 rounded-lg mb-6 animate-pulse">
            <CheckCircle2 className="h-4 w-4 shrink-0 mt-0.5 text-emerald-400" />
            <div>
              <p className="font-semibold">Registration Successful!</p>
              <p className="mt-0.5 opacity-90">Redirecting to sign in screen...</p>
            </div>
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <div className="flex items-start gap-2.5 bg-destructive/10 border border-destructive/20 text-destructive text-xs p-3.5 rounded-lg mb-6 animate-shake animate-duration-300">
            <ShieldAlert className="h-4 w-4 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Registration Error</p>
              <p className="mt-0.5 opacity-90">{error}</p>
            </div>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Username */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-muted-foreground" htmlFor="username">Username</label>
            <div className="relative">
              <User className="absolute left-3.5 top-3 h-4 w-4 text-muted-foreground/60" />
              <input
                id="username"
                type="text"
                placeholder="seafarer101"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={submitting || success}
                className="w-full bg-background/50 border border-border/50 rounded-lg py-2.5 pl-10 pr-4 text-sm focus:outline-none focus:border-[hsl(210,70%,50%)] focus:ring-1 focus:ring-[hsl(210,70%,50%)] transition-all duration-200"
              />
            </div>
          </div>

          {/* Email */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-muted-foreground" htmlFor="email">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-3 h-4 w-4 text-muted-foreground/60" />
              <input
                id="email"
                type="email"
                placeholder="user@vpro.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={submitting || success}
                className="w-full bg-background/50 border border-border/50 rounded-lg py-2.5 pl-10 pr-4 text-sm focus:outline-none focus:border-[hsl(210,70%,50%)] focus:ring-1 focus:ring-[hsl(210,70%,50%)] transition-all duration-200"
              />
            </div>
          </div>

          {/* Password */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-muted-foreground" htmlFor="password">Password</label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3 h-4 w-4 text-muted-foreground/60" />
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={submitting || success}
                className="w-full bg-background/50 border border-border/50 rounded-lg py-2.5 pl-10 pr-10 text-sm focus:outline-none focus:border-[hsl(210,70%,50%)] focus:ring-1 focus:ring-[hsl(210,70%,50%)] transition-all duration-200"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
                className="absolute right-3 top-3 h-4 w-4 text-muted-foreground/60 hover:text-foreground transition-colors"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={submitting || success}
            className="w-full mt-6 bg-[hsl(210,70%,50%)] hover:bg-[hsl(210,70%,55%)] text-white text-sm font-semibold py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-all duration-200 shadow-[0_4px_12px_hsl(210,70%,50%/0.2)] hover:shadow-[0_4px_20px_hsl(210,70%,50%/0.3)] disabled:opacity-50 disabled:pointer-events-none group"
          >
            {submitting ? (
              <span className="h-4 w-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
            ) : (
              <>Register Account <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" /></>
            )}
          </button>
        </form>

        {/* Footer */}
        <div className="mt-8 pt-6 border-t border-border/30 text-center">
          <p className="text-xs text-muted-foreground">
            Already have an account? <Link to="/login" className="text-[hsl(210,70%,50%)] font-semibold hover:underline">Sign In</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
