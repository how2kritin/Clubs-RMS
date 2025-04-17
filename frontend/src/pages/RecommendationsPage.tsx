// src/pages/RecommendationsPage.tsx
import React, { useState, useEffect } from "react";

// Optional: Define a type for the club data based on your ClubOut schema
interface ClubRecommendation {
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

const RecommendationsPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [fetchAttempted, setFetchAttempted] = useState<boolean>(false);

  useEffect(() => {
    // Prevent fetching again if already attempted (e.g., due to React StrictMode double render in dev)
    if (fetchAttempted) return;

    const fetchRecommendations = async () => {
      setFetchAttempted(true); // Mark that we are starting the fetch
      setIsLoading(true);
      setError(null);
      console.log("Attempting to fetch recommendations...");

      try {
        const response = await fetch("/recommendations/clubs", {
          method: "GET",
          credentials: "include", // Send cookies
          headers: { "Content-Type": "application/json" },
        });
        // Log raw response status for debugging
        console.log("Response Status:", response.status, response.statusText);

        if (!response.ok) {
          // Try to get error details from response body if possible
          let errorDetail = `HTTP error! status: ${response.status}`;
          try {
            const errorData = await response.json();
            errorDetail = errorData.detail || JSON.stringify(errorData);
          } catch (jsonError) {
            // Ignore if response body is not JSON or empty
            console.log("Could not parse error response as JSON.");
          }
          throw new Error(errorDetail);
        }

        const data: ClubRecommendation[] = await response.json();

        // --- THE CORE REQUIREMENT ---
        console.log("Successfully fetched recommendations:", data);
        // --------------------------

        // You could store the data in state if you wanted to display it later
        // setRecommendations(data);
      } catch (err: any) {
        console.error("Failed to fetch recommendations:", err);
        setError(
          err.message ||
            "An unknown error occurred while fetching recommendations.",
        );
      } finally {
        setIsLoading(false);
      }
    };

    fetchRecommendations();

    // Add fetchAttempted to dependencies to respect the check (though empty array is common)
  }, [fetchAttempted]);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold text-center mb-6 text-gray-900 dark:text-white">
        Club Recommendations
      </h1>

      {isLoading && (
        <div className="text-center text-gray-600 dark:text-gray-400">
          Loading recommendations... (Check console)
        </div>
      )}

      {error && (
        <div className="text-center text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900 p-3 rounded">
          Error fetching recommendations: {error} (Check console for details)
        </div>
      )}

      {!isLoading && !error && (
        <div className="text-center text-green-700 dark:text-green-300">
          Recommendation data has been logged to the browser's developer
          console.
        </div>
      )}

      {/* Later, you could map over stored recommendations and display them */}
      {/* {recommendations && recommendations.map(club => <div key={club.cid}>{club.name}</div>)} */}
    </div>
  );
};

export default RecommendationsPage;
