import { createBrowserRouter } from "react-router-dom";
import AppLayout from "@/layouts/AppLayout";
import HomePage from "@/pages/HomePage";
import DashboardPage from "@/pages/DashboardPage";
import UploadReportPage from "@/pages/UploadReportPage";
import RoutePlannerPage from "@/pages/RoutePlannerPage";
import NotFoundPage from "@/pages/NotFoundPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import ProtectedRoute from "@/components/ProtectedRoute";
import ErrorPage from "@/pages/ErrorPage";

/**
 * Centralized route configuration.
 *
 * Adding a new page is a single entry in the `children` array —
 * no structural rewrites needed.
 */
export const router = createBrowserRouter([
  {
    element: <AppLayout />,
    errorElement: <ErrorPage />,
    children: [
      { index: true, element: <HomePage /> },
      { path: "login", element: <LoginPage /> },
      { path: "register", element: <RegisterPage /> },
      
      // Guarded Routes
      {
        element: <ProtectedRoute />,
        children: [
          { path: "dashboard", element: <DashboardPage /> },
          { path: "route-planner", element: <RoutePlannerPage /> },
          { path: "upload", element: <UploadReportPage /> },
        ],
      },
      
      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);
