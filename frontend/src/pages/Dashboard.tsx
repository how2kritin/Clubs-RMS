// src/pages/Dashboard.tsx
import React, { useState, useEffect } from "react";
import ClubCard from "../components/ClubCard.jsx";

// Define the structure of a Club object (reuse or define if not already shared)
interface Club {
  cid: string;
  name: string;
  category?: string | null;
  tagline?: string | null;
  description?: string | null;
  logo?: string | null;
  banner?: string | null;
  email?: string | null;
  socials?: Record<string, any> | null;
}

const Dashboard: React.FC = () => {
  // State for user's clubs
  const [myClubs, setMyClubs] = useState<Club[]>([]);
  const [isLoadingMyClubs, setIsLoadingMyClubs] = useState<boolean>(true);
  const [errorMyClubs, setErrorMyClubs] = useState<string | null>(null);

  // State for recommended clubs
  const [recommendedClubs, setRecommendedClubs] = useState<Club[]>([]);
  const [isLoadingRecommendations, setIsLoadingRecommendations] =
    useState<boolean>(true);
  const [errorRecommendations, setErrorRecommendations] = useState<
    string | null
  >(null);

  useEffect(() => {
    // --- Fetch User's Clubs ---
    const fetchMyClubs = async () => {
      setIsLoadingMyClubs(true);
      setErrorMyClubs(null);
      try {
        const response = await fetch("/api/user/user_club_info", {
          method: "GET",
          credentials: "include", // Send cookies
          headers: { "Content-Type": "application/json" },
        });
        if (!response.ok) {
          let errorDetail = `Error ${response.status}`;
          try {
            const data = await response.json();
            errorDetail = data.detail || errorDetail;
          } catch (e) {
            /* ignore */
          }
          throw new Error(`Failed to fetch user's clubs: ${errorDetail}`);
        }
        const data: Club[] = await response.json();
        setMyClubs(data);
      } catch (err: any) {
        console.error("Error fetching user's clubs:", err);
        setErrorMyClubs(err.message);
      } finally {
        setIsLoadingMyClubs(false);
      }
    };

    // --- Fetch Recommended Clubs ---
    const fetchRecommendations = async () => {
      setIsLoadingRecommendations(true);
      setErrorRecommendations(null);
      try {
        const response = await fetch("/recommendations/clubs", {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        });
        if (!response.ok) {
          let errorDetail = `Error ${response.status}`;
          try {
            const data = await response.json();
            errorDetail = data.detail || errorDetail;
          } catch (e) {
            /* ignore */
          }
          throw new Error(`Failed to fetch recommendations: ${errorDetail}`);
        }
        // const data: Club[] = await response.json();
        const data: Club[] = [];
        setRecommendedClubs(data);
        console.log("Fetched recommendations:", data); // Keep console log for verification
      } catch (err: any) {
        console.error("Error fetching recommendations:", err);
        setErrorRecommendations(err.message);
      } finally {
        setIsLoadingRecommendations(false);
      }
    };

    // Fetch both sets of data when component mounts
    fetchMyClubs();
    fetchRecommendations();
  }, []); // Empty dependency array ensures this runs only once on mount

  // Helper function to render a section (My Clubs or Recommendations)
  const renderClubSection = (
    title: string,
    clubs: Club[],
    isLoading: boolean,
    error: string | null,
  ) => {
    return (
      <section className="mb-10">
        <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-gray-200 border-b pb-2">
          {title}
        </h2>
        {isLoading && (
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        )}
        {error && (
          <p className="text-red-600 dark:text-red-400">Error: {error}</p>
        )}
        {!isLoading &&
          !error &&
          (clubs.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {clubs.map((club) => (
                <ClubCard
                  key={`${title}-${club.cid}`}
                  name={club.name}
                  logo={club.logo}
                  tagline={club.tagline}
                  cid={club.cid}
                />
              ))}
            </div>
          ) : (
            <p className="text-gray-600 dark:text-gray-400">
              {title === "My Clubs"
                ? "You are not currently in any clubs listed here."
                : "No recommendations available at the moment."}
            </p>
          ))}
      </section>
    );
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-8 text-center text-gray-900 dark:text-white">
        Dashboard
      </h1>

      {/* Render My Clubs Section */}
      {renderClubSection("My Clubs", myClubs, isLoadingMyClubs, errorMyClubs)}

      {/* Render Recommended Clubs Section */}
      {renderClubSection(
        "Recommended Clubs",
        recommendedClubs,
        isLoadingRecommendations,
        errorRecommendations,
      )}
    </div>
  );
};

export default Dashboard;
