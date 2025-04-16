// CreateRouter.tsx
import React from "react";
import { createBrowserRouter, Navigate } from "react-router-dom";
import LandingPage from "./pages/LandingPage.tsx";
import UserProfile from "./pages/UserProfile.tsx";
import ScheduleInterviews from "./pages/interviews/ScheduleInterviews.tsx";
import CalendarLoader from "./pages/calendar/Calendar.tsx";
import Dashboard from "./pages/Dashboard.tsx";
import NotFound from "./pages/NotFound.tsx";
import { useAuth } from "./AuthProvider.tsx";
import Navbar from "./layout/Navbar.tsx";
import ClubsPage from "./pages/ClubsPage.tsx";

// ProtectedRoute component to guard private routes
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isLoggedIn } = useAuth();
  console.log("isLoggedIn", isLoggedIn);
  if (isLoggedIn === null) {
    return <p>some loading component</p>
  } else if (isLoggedIn === true) {
    return <>
      <Navbar />  {/* Render the Navbar here, inside the ProtectedRoute */}
      {children}
    </>
  } else { // isLoggedIn === false
    return <Navigate to="/" />;
  }
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
      path: "/clubs",
      element: (
        <ProtectedRoute>
          <PageLayout customPage={ClubsPage} />
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
    {
      path: "/schedule_interviews",
      element: (
        <ProtectedRoute>
          <PageLayout customPage={ScheduleInterviews} />
        </ProtectedRoute>
      )
    },
    {
      path: "/calendar",
      element: (
        <ProtectedRoute>
          <PageLayout customPage={CalendarLoader} />
        </ProtectedRoute>
      )
    },
    { path: "*", element: <NotFound /> },
  ];

  return createBrowserRouter(routes);
};
