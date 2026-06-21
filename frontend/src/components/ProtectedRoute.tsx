import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";

export const ProtectedRoute: React.FC = () => {
  const { token, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        {/* Modern glowing spinner */}
        <div className="h-12 w-12 rounded-full border-4 border-muted border-t-[hsl(210,70%,50%)] animate-spin shadow-[0_0_15px_hsl(210,70%,50%/0.3)]"></div>
        <p className="text-sm text-muted-foreground animate-pulse">
          Verifying security session...
        </p>
      </div>
    );
  }

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
