// CreateRouter.tsx
import React, { useContext } from "react";
import { createBrowserRouter, Navigate } from "react-router-dom";
import LandingPage from "./pages/LandingPage.tsx";
import UserProfile from "./pages/UserProfile.tsx";
import Dashboard from "./pages/Dashboard.tsx";
import NotFound from "./pages/NotFound.tsx";
import { AuthContext } from "./AuthProvider.tsx";

// ProtectedRoute component to guard private routes
const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const { isLoggedIn } = useContext(AuthContext);
  console.log("isLoggedIn", isLoggedIn);
  if (!isLoggedIn) {
    return <Navigate to="/" />;
  }
  return children;
};

const PageLayout = ({ navbarPage, customPage: CustomPage }: { navbarPage: string, customPage: any }) => {
  return (
    <div>
      <CustomPage />
    </div>
  );
};

export const CreateRouter = () => {
  const routes = [
    { path: "/", element: <LandingPage /> },
    {
      path: "/Dashboard",
      element: (
        <ProtectedRoute>
          <PageLayout navbarPage="Dashboard" customPage={Dashboard} />
        </ProtectedRoute>
      )
    },
    {
      path: "/profile",
      element: (
        <ProtectedRoute>
          <PageLayout navbarPage="User Profile" customPage={UserProfile} />
        </ProtectedRoute>
      )
    },
    { path: "*", element: <NotFound /> },
  ];

  return createBrowserRouter(routes);
};
