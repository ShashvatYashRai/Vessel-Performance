import { useState, useRef, useEffect } from "react";
import { NavLink, Outlet, useNavigate, Link } from "react-router-dom";
import ScrollToTop from "@/components/ScrollToTop";
import { useAuth } from "@/hooks/useAuth";
import { LogOut, ChevronDown, Shield, Mail } from "lucide-react";

// ── Navigation Links ────────────────────────────────────────────────────────

const NAV_LINKS = [
  { to: "/", label: "Home", end: true },
  { to: "/dashboard", label: "Dashboard", end: false },
  { to: "/upload", label: "Upload Reports", end: false },
  { to: "/route-planner", label: "Route Planner", end: false },
] as const;

// ── Layout ──────────────────────────────────────────────────────────────────

export default function AppLayout() {
  const { user, token, logout, loading } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  // Close dropdown on click outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleLogout = () => {
    logout();
    setDropdownOpen(false);
    navigate("/login");
  };

  return (
    <div className="dark min-h-screen bg-background text-foreground flex flex-col">
      <ScrollToTop />

      {/* ── Top Navigation ──────────────────────────────────────────────── */}
      <header className="border-b border-border/50 backdrop-blur-sm bg-background/80 sticky top-0 z-20">
        <div className="max-w-[1400px] mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          {/* Brand */}
          <NavLink to="/" className="flex items-center gap-2.5 group">
            <img 
              src="/logo.png" 
              className="h-8 w-auto object-contain transition-transform duration-200 group-hover:scale-105" 
              alt="VPRO Maritime Analytics Platform Logo" 
            />
            <div>
              <h1 className="text-sm font-bold tracking-tight leading-none">
                VPRO
              </h1>
              <p className="text-[10px] text-muted-foreground mt-0.5 hidden sm:block">
                Voyage Performance &amp; Route Optimization
              </p>
            </div>
          </NavLink>

          {/* Navigation & User Profile */}
          <div className="flex items-center gap-4">
            <nav className="flex items-center gap-0.5">
              {NAV_LINKS.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  end={link.end ?? false}
                  id={`nav-${link.label.toLowerCase().replace(/\s+/g, "-")}`}
                  className={({ isActive }) =>
                    `relative px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200 ${
                      isActive
                        ? "text-foreground font-semibold bg-[hsl(210,70%,50%)]/10"
                        : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      {link.label}
                      {/* Active accent underline */}
                      {isActive && (
                        <span className="absolute bottom-0 left-2 right-2 h-[2px] rounded-full bg-[hsl(210,70%,50%)] shadow-[0_0_8px_hsl(210,70%,50%/0.4)]" />
                      )}
                    </>
                  )}
                </NavLink>
              ))}
            </nav>

            <div className="h-4 w-[1px] bg-border/50 hidden sm:block" />

            {loading ? (
              <div className="h-8 w-8 rounded-full border border-border/45 animate-pulse bg-muted/30" />
            ) : token && user ? (
              <div className="relative" ref={dropdownRef}>
                <button
                  onClick={() => setDropdownOpen(!dropdownOpen)}
                  className="flex items-center gap-1.5 focus:outline-none group p-1 rounded-lg hover:bg-muted/30 transition-all duration-200 cursor-pointer"
                  id="profile-dropdown-trigger"
                >
                  <div className="h-8 w-8 rounded-full bg-gradient-to-br from-[hsl(210,70%,55%)] to-[hsl(210,70%,40%)] flex items-center justify-center text-white font-bold text-xs shadow-[0_0_10px_hsl(210,70%,50%/0.25)] border border-[hsl(210,70%,50%)]/20 transition-transform duration-200 group-hover:scale-105">
                    {user.username.slice(0, 2).toUpperCase()}
                  </div>
                  <ChevronDown className={`h-3.5 w-3.5 text-muted-foreground transition-transform duration-200 ${dropdownOpen ? 'rotate-180' : ''}`} />
                </button>

                {dropdownOpen && (
                  <div className="absolute right-0 mt-2 w-56 rounded-xl border border-border/40 bg-popover/95 backdrop-blur-md p-1 shadow-2xl z-30 transition-all duration-200 animate-in fade-in slide-in-from-top-2">
                    {/* User Info Header */}
                    <div className="px-3 py-2 border-b border-border/30 mb-1">
                      <p className="text-xs font-semibold text-foreground truncate" id="profile-username">
                        {user.username}
                      </p>
                      <div className="flex items-center gap-1 mt-0.5 text-[10px] text-muted-foreground truncate">
                        <Mail className="h-2.5 w-2.5 shrink-0" />
                        <span className="truncate">{user.email}</span>
                      </div>
                      <div className="mt-1.5 inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-[hsl(210,70%,50%)]/10 border border-[hsl(210,70%,50%)]/20 text-[9px] font-medium text-[hsl(210,70%,55%)]">
                        <Shield className="h-2.5 w-2.5" />
                        <span className="capitalize">{user.role}</span>
                      </div>
                    </div>

                    {/* Actions */}
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium text-destructive hover:bg-destructive/10 transition-colors duration-150 text-left cursor-pointer"
                      id="logout-button"
                    >
                      <LogOut className="h-3.5 w-3.5" />
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  id="nav-login"
                  className="px-3 py-1.5 text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-muted/50 rounded-md transition-all duration-200"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  id="nav-register"
                  className="px-3 py-1.5 text-xs font-semibold text-white bg-[hsl(210,70%,50%)] hover:bg-[hsl(210,70%,55%)] rounded-md shadow-[0_2px_8px_hsl(210,70%,50%/0.2)] hover:shadow-[0_2px_12px_hsl(210,70%,50%/0.3)] transition-all duration-200"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* ── Main Viewport ───────────────────────────────────────────────── */}
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}

