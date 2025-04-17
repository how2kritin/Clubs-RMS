// CreateRouter.tsx
import React from "react";
import { createBrowserRouter, Navigate } from "react-router-dom";
import LandingPage from "./pages/LandingPage.tsx";
import UserProfile from "./pages/UserProfile.tsx";
import CreateForm from "./pages/forms/CreateForm.tsx";
import ScheduleInterviews from "./pages/interviews/ScheduleInterviews.tsx";
import CalendarLoader from "./pages/calendar/Calendar.tsx";
import Dashboard from "./pages/Dashboard.tsx";
import NotFound from "./pages/NotFound.tsx";
import { useAuth } from "./AuthProvider.tsx";
import Navbar from "./layout/Navbar.tsx";
import ClubForms from "./pages/forms/ClubForms.tsx";
import FormView from "./pages/forms/FormView.tsx";
import RecommendationsPage from "./pages/RecommendationsPage.tsx";
import ClubsPage from "./pages/ClubsPage.tsx";
import ApplyToForm from "./pages/applications/ApplyToForm.tsx";
import FormApplicationsOverview from "./pages/applications/FormApplicationsOverview.tsx";
import ApplicationDetail from "./pages/applications/ApplicationDetail.tsx";
import UserApplications from "./pages/applications/UserApplications.tsx";

const LoadingPage: React.FC = () => {
  return (
    <div className="flex items-center justify-center h-screen bg-blue-50 dark:bg-gray-900 transition-colors duration-300">
      <div className="flex flex-col items-center space-y-4">
        <div className="w-16 h-16 border-4 border-blue-500 border-dashed rounded-full animate-spin dark:border-blue-400"></div>
        <p className="text-blue-700 dark:text-blue-300 text-lg font-medium">
          Loading, please wait...
        </p>
      </div>
    </div>
  );
};

// ProtectedRoute component to guard private routes
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isLoggedIn } = useAuth();
  console.log("isLoggedIn", isLoggedIn);
  if (isLoggedIn === null) {
    return <LoadingPage />;
  } else if (isLoggedIn === true) {
    return (
      <>
        <Navbar /> {/* Render the Navbar here, inside the ProtectedRoute */}
        {children}
      </>
    );
  } else {
    // isLoggedIn === false
    return <Navigate to="/" />;
  }
};

const PageLayout = ({
  customPage: CustomPage,
}: {
  customPage: React.ComponentType;
}) => {
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
      ),
    },
    {
      path: "/clubs",
      element: (
        <ProtectedRoute>
          <PageLayout customPage={ClubsPage} />
        </ProtectedRoute>
      ),
    },
    {
      path: "/recommendations",
      element: (
        <ProtectedRoute>
          <PageLayout customPage={RecommendationsPage} />
        </ProtectedRoute>
      ),
    },
    {
      path: "/profile",
      element: (
        <ProtectedRoute>
          <PageLayout customPage={UserProfile} />
        </ProtectedRoute>
      ),
    },
    {
      path: "/create_form/:clubId",
      element: (
        <ProtectedRoute>
          <PageLayout customPage={CreateForm} />
        </ProtectedRoute>
      ),
    },
    {
      path: "/club/:clubId",
      element: (
        <ProtectedRoute>
          <PageLayout customPage={ClubForms} />
        </ProtectedRoute>
      ),
    },
    {
      path: "/form/:formId",
      element: (
        <ProtectedRoute>
          <PageLayout customPage={FormView} />
        </ProtectedRoute>
      ),
    },
    {
      path: "/apply/:formId",
      element: (
        <ProtectedRoute>
          <PageLayout customPage={ApplyToForm} />
        </ProtectedRoute>
      ),
    },
    {
      path: "/forms/:formId/applications",
      element: (
        <ProtectedRoute>
          <PageLayout customPage={FormApplicationsOverview} />
        </ProtectedRoute>
      ),
    },
    {
      path: "/forms/:formId/applications/:applicationId",
      element: (
        <ProtectedRoute>
          <PageLayout customPage={ApplicationDetail} />
        </ProtectedRoute>
      ),
    },
    {
      path: "/my-applications",
      element: (
        <ProtectedRoute>
          <PageLayout customPage={UserApplications} />
        </ProtectedRoute>
      ),
    },
    {
      path: "/schedule_interviews",
      element: (
        <ProtectedRoute>
          <PageLayout customPage={ScheduleInterviews} />
        </ProtectedRoute>
      ),
    },
    {
      path: "/calendar",
      element: (
        <ProtectedRoute>
          <PageLayout customPage={CalendarLoader} />
        </ProtectedRoute>
      ),
    },
    { path: "*", element: <NotFound /> },
  ];

  return createBrowserRouter(routes);
};
