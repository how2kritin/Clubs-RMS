// src/components/ClubCard.tsx
import React from "react";
import placeholder from "../assets/placeholder.jpg";
import { Link } from "react-router-dom";

// Define the expected props for the ClubCard
interface ClubCardProps {
  cid: string; // Unique key for the card, typically used in lists
  logo: string | null | undefined; // Path to the logo image, can be null/undefined
  name: string;
  tagline: string | null | undefined; // Tagline, can be null/undefined
}

const ClubCard: React.FC<ClubCardProps> = ({ logo, name, tagline, cid }) => {
  // Basic error handling or placeholder for missing logo
  const logoSrc = logo
    ? `http://clubs.iiit.ac.in/files/download?filename=${encodeURIComponent(logo)}`
    : placeholder;
  console.log(logoSrc);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden transform transition duration-300 hover:scale-105">
      <div className="p-4 text-center">
        {/* Logo */}
        <img
          src={logoSrc}
          alt={`${name} logo`}
          className="w-20 h-20 rounded-full object-cover mx-auto mb-3 border border-gray-200 dark:border-gray-700"
          // onError={(e) => {
          //     const img = e.currentTarget;
          //     img.onerror = null;        // avoid infinite loop
          //     img.src = placeholder;     // this is now a valid URL
          // }}
        />
        {/* Club Name */}
        <h3
          className="text-lg font-semibold text-gray-900 dark:text-white mb-1 truncate"
          title={name}
        >
          {name}
        </h3>
        {/* Tagline (only if it exists) */}
        {/* {tagline && (
                    <p className="text-sm text-gray-600 dark:text-gray-400 italic">
                        {tagline}
                    </p>
                )} */}
        {/* Add a link or button here if cards should be clickable */}
        <Link to={`/club/${cid}`}>View Details</Link>
      </div>
    </div>
  );
};

export default ClubCard;

