// CreateRouter.tsx
import React, { useContext } from "react";
import { createBrowserRouter, Navigate } from "react-router-dom";
import LandingPage from "./pages/LandingPage.tsx";
import UserProfile from "./pages/UserProfile.tsx";
import Dashboard from "./pages/Dashboard.tsx";
import NotFound from "./pages/NotFound.tsx";
import { AuthContext } from "./AuthProvider.tsx";
import Navbar from "./layout/Navbar.tsx";

// ProtectedRoute component to guard private routes
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isLoggedIn } = useContext(AuthContext);
  console.log("isLoggedIn", isLoggedIn);
  if (!isLoggedIn && localStorage.getItem("isLoggedIn") !== "true") {
    return <Navigate to="/" />;
  }
  return (
    <>
      <Navbar />  {/* Render the Navbar here, inside the ProtectedRoute */}
      {children}
    </>

  );
};

const PageLayout = ({ customPage: CustomPage }: { customPage: React.ComponentType }) => {
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
      path: "/dashboard",
      element: (
        <ProtectedRoute>
          <PageLayout customPage={Dashboard} />
        </ProtectedRoute>
      )
    },
    {
      path: "/profile",
      element: (
        <ProtectedRoute>
          <PageLayout customPage={UserProfile} />
        </ProtectedRoute>
      )
    },
    { path: "*", element: <NotFound /> },
  ];

  return createBrowserRouter(routes);
};
