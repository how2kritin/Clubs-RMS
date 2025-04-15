// src/pages/ClubsPage.tsx
import React, { useState, useEffect } from 'react';
import ClubCard from '../components/ClubCard'; // Adjust path if needed

// Define the structure of a Club object based on your backend schema
interface Club {
  cid: string;
  name: string;
  category?: string | null;
  tagline?: string | null;
  description?: string | null;
  logo?: string | null;
  banner?: string | null;
  email?: string | null;
  socials?: Record<string, any> | null; // Or a more specific type if known
}

const ClubsPage: React.FC = () => {
  const [clubs, setClubs] = useState<Club[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchClubs = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch('/api/club/all_clubs', { 
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include', 
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data: Club[] = await response.json();
        setClubs(data);
      } catch (err: any) {
        console.error("Failed to fetch clubs:", err);
        setError(err.message || 'Failed to load clubs. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchClubs();
  }, []); // Empty dependency array means this runs once on mount

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold text-center mb-6 text-gray-900 dark:text-white">
        Explore Clubs
      </h1>

      {isLoading && (
        <div className="text-center text-gray-600 dark:text-gray-400">Loading clubs...</div>
      )}

      {error && (
        <div className="text-center text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900 p-3 rounded">
          Error: {error}
        </div>
      )}

      {!isLoading && !error && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {clubs.length > 0 ? (
            clubs.map((club) => (
              <ClubCard
                key={club.cid} // Use the unique club ID as the key
                name={club.name}
                logo={club.logo}
                tagline={club.tagline}
              />
            ))
          ) : (
            <div className="col-span-full text-center text-gray-600 dark:text-gray-400">
              No clubs found.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ClubsPage;