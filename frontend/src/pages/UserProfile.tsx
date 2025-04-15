import React, { useState, useEffect } from 'react';
import { Edit, Check, X, Plus, AlertCircle } from 'lucide-react'; // Import icons

// Import profile picture assets
import avatar1 from '../assets/bear.png';
import avatar2 from '../assets/cat.png';
import avatar3 from '../assets/chicken.png';
import avatar4 from '../assets/giraffe.png';
import avatar5 from '../assets/panda.png';

import './UserProfile.css'; // Import the CSS file

const profilePictures = [avatar1, avatar2, avatar3, avatar4, avatar5];

interface UserProfileData {
  name: string;
  rollNumber: string;
  email: string;
  hobbies: string;
  skills: string[];
  batch: string; // Keep as string, validation happens backend if needed
  profilePicture: number; // Stores index into profilePictures (0 to 4)
}

// Interface for the data sent to the backend API
interface UserProfileUpdatePayload {
    hobbies: string;
    skills: string[];
    profile_picture: number; // Use snake_case for backend consistency
}


function UserProfile() {
  // --- State ---
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(true); // Added loading state for initial fetch
  const [isSaving, setIsSaving] = useState(false); // Added saving state for update
  const [error, setError] = useState<string | null>(null); // Added error state
  const [userProfile, setUserProfile] = useState<UserProfileData | null>(null);
  const [editedProfile, setEditedProfile] = useState<UserProfileData | null>(null);
  const [newSkill, setNewSkill] = useState('');

  // --- Effects ---
  // Fetch user info on component mount
  useEffect(() => {
    async function fetchUserProfile() {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch('/api/user/user_info', {credentials: 'include'}); // Ensure cookie is sent
        if (!response.ok) {
           if (response.status === 401) {
               // Handle unauthorized access, maybe redirect to login
               setError("Unauthorized. Please log in.");
               // Optionally redirect: window.location.href = '/login';
           } else {
               throw new Error(`Network response was not ok (${response.status})`);
           }
        } else {
            const data = await response.json();
            // Map the API response
            const sanitizedData: UserProfileData = {
              name: `${data.first_name || ''} ${data.last_name || ''}`.trim() || 'N/A',
              rollNumber: data.roll_number || 'N/A',
              email: data.email || 'N/A',
              hobbies: data.hobbies || '',
              skills: data.skills || [],
              batch: data.batch || '',
              // Ensure profile_picture is a valid index, default to 0 if invalid/missing
              profilePicture: (typeof data.profile_picture === 'number' && data.profile_picture >= 0 && data.profile_picture < profilePictures.length)
                                ? data.profile_picture
                                : 0,
            };
            setUserProfile(sanitizedData);
            setEditedProfile(sanitizedData); // Initialize edited state
        }
      } catch (err) {
        console.error('Error fetching user info:', err);
        setError(err instanceof Error ? err.message : 'An unknown error occurred while fetching profile.');
      } finally {
        setIsLoading(false);
      }
    }
    fetchUserProfile();
  }, []);

  // Reset editedProfile if userProfile changes externally (less likely here, but good practice)
  useEffect(() => {
    if (userProfile && !isEditing) { // Only reset if not currently editing
      setEditedProfile(userProfile);
    }
  }, [userProfile, isEditing]);

  // --- Handlers ---
  const handleEditToggle = async () => {
    setError(null); // Clear previous errors
    if (isEditing) {
      // "Done" button clicked - save changes via API call
      if (!editedProfile) return; // Should not happen if logic is correct

      setIsSaving(true); // Indicate saving process start

      // Prepare only the fields that can be updated
      const payload: UserProfileUpdatePayload = {
        hobbies: editedProfile.hobbies,
        skills: editedProfile.skills,
        profile_picture: editedProfile.profilePicture // Map frontend state name to backend name
      };

      console.log('Saving profile with payload:', payload);

      try {
        const response = await fetch('/api/user/update_profile', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include', // Important to send session cookie
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          // Try to get error details from response body
          let errorDetail = `Failed to update profile (${response.status})`;
          try {
              const errorData = await response.json();
              errorDetail = errorData.detail || errorDetail;
          } catch (jsonError) {
              // Ignore if response is not JSON
          }
          throw new Error(errorDetail);
        }

        // Success! Update the main profile state with the edited data
        setUserProfile(editedProfile);
        setIsEditing(false); // Exit edit mode

      } catch (err) {
        console.error('Error updating profile:', err);
        setError(err instanceof Error ? err.message : 'An unknown error occurred during save.');
        // Keep isEditing true so user can see the error and potentially retry or fix input
      } finally {
        setIsSaving(false); // Indicate saving process end
      }

    } else {
      // "Edit Profile" button clicked - start editing
      if (userProfile) {
        setEditedProfile({...userProfile}); // Ensure edit state starts fresh with a copy
        setIsEditing(true);
      }
    }
  };

  // Only allow changing hobbies (textarea)
  const handleInputChange = (
    e: React.ChangeEvent<HTMLTextAreaElement> // Only need textarea now
  ) => {
    const { name, value } = e.target;
    if (editedProfile && name === 'hobbies') { // Only update hobbies
      setEditedProfile((prev) => prev && ({
        ...prev,
        hobbies: value,
      }));
    }
  };

  const handleProfilePicSelect = (index: number) => {
    if (isEditing && editedProfile) {
      setEditedProfile((prev) => prev && ({
        ...prev,
        profilePicture: index,
      }));
    }
  };

  const handleAddSkill = () => {
    if (editedProfile && newSkill.trim() && !editedProfile.skills.includes(newSkill.trim())) {
      setEditedProfile((prev) => prev && ({
        ...prev,
        skills: [...prev.skills, newSkill.trim()],
      }));
      setNewSkill(''); // Clear input field
    }
  };

  const handleRemoveSkill = (skillToRemove: string) => {
    if (editedProfile) {
      setEditedProfile((prev) => prev && ({
        ...prev,
        skills: prev.skills.filter((skill) => skill !== skillToRemove),
      }));
    }
  };

  // --- Render Helper ---
  const renderSkills = (skills: string[], editable: boolean) => (
    <div className="skills-container">
      {skills.map((skill) => (
        <span key={skill} className="skill-tag">
          {skill}
          {editable && (
            <button
              onClick={() => handleRemoveSkill(skill)}
              className="remove-skill-btn"
              aria-label={`Remove skill ${skill}`}
              disabled={isSaving} // Disable while saving
            >
              <X size={14} />
            </button>
          )}
        </span>
      ))}
      {editable && (
        <div className="add-skill-container">
          <input
            type="text"
            value={newSkill}
            onChange={(e) => setNewSkill(e.target.value)}
            placeholder="Add a skill"
            className="skill-input"
            onKeyDown={(e) => e.key === 'Enter' && handleAddSkill()}
            disabled={isSaving} // Disable while saving
          />
          <button
             onClick={handleAddSkill}
             className="add-skill-btn"
             aria-label="Add skill"
             disabled={isSaving} // Disable while saving
          >
            <Plus size={18} />
          </button>
        </div>
      )}
    </div>
  );

  // --- Loading and Error States ---
  if (isLoading) {
    return <div className="user-profile-page"><div className="loading-message">Loading profile...</div></div>;
  }

  // Handle case where initial fetch failed but wasn't just unauthorized
  if (!userProfile && error && !isLoading) {
      return <div className="user-profile-page"><div className="error-message">{error}</div></div>;
  }

  // Handle case where fetch succeeded but data is somehow null (shouldn't happen with current logic)
  if (!userProfile || !editedProfile) {
      return <div className="user-profile-page"><div className="error-message">Could not load profile data.</div></div>;
  }

  // Use editedProfile for display/inputs when editing, otherwise userProfile
  const currentDisplayProfile = isEditing ? editedProfile : userProfile;

  return (
    <div className="user-profile-page">
      <div className="profile-header">
        <h1 className="profile-title">User Profile</h1>
        <button
            onClick={handleEditToggle}
            className={`edit-button ${isSaving ? 'saving' : ''}`}
            disabled={isSaving} // Disable button while saving
        >
          {isSaving ? (
            <>Saving...</>
          ) : isEditing ? (
            <>
              <Check size={18} /> Done
            </>
          ) : (
            <>
              <Edit size={18} /> Edit Profile
            </>
          )}
        </button>
      </div>

       {/* Display Save Error */}
       {error && isEditing && (
            <div className="error-message-banner">
                <AlertCircle size={18} />
                <span>{error}</span>
            </div>
        )}


      <div className="profile-content">
        {/* --- Profile Picture Section --- */}
        <div className="profile-picture-section">
          <h2>Profile Picture</h2>
          <img
            // Use index from currentDisplayProfile to get the image source
            src={profilePictures[currentDisplayProfile.profilePicture]}
            alt="User profile"
            className="profile-picture-main"
          />
          {isEditing && (
            <div className="profile-picture-options">
              {profilePictures.map((picSrc, index) => (
                <img
                  key={index}
                  src={picSrc} // Use the imported source directly
                  alt={`Profile option ${index + 1}`}
                  className={`profile-picture-thumb ${
                    editedProfile.profilePicture === index ? 'selected' : '' // Always compare with editedProfile in edit mode
                  }`}
                  onClick={() => handleProfilePicSelect(index)} // Pass index
                />
              ))}
            </div>
          )}
        </div>

        {/* --- Profile Details Section --- */}
        <div className="profile-details-section">
          {/* Immutable Fields - Always display as text */}
          <div className="profile-field">
            <label>Name</label>
            <p>{userProfile.name || 'Not specified'}</p>
          </div>

          <div className="profile-field">
            <label>Roll Number</label>
            <p>{userProfile.rollNumber || 'Not specified'}</p>
          </div>

          <div className="profile-field">
            <label>Email</label>
            <p>{userProfile.email || 'Not specified'}</p>
          </div>

          <div className="profile-field">
            <label>Batch</label>
            <p>{userProfile.batch || 'Not specified'}</p>
          </div>

          {/* Mutable Fields */}
          <div className="profile-field">
            <label htmlFor="hobbies">Hobbies</label>
            {isEditing ? (
              <textarea
                id="hobbies"
                name="hobbies" // Keep name for potential future generic handlers
                value={editedProfile.hobbies}
                onChange={handleInputChange} // Use the restricted handler
                rows={3}
                disabled={isSaving} // Disable while saving
              />
            ) : (
              <p className="hobbies-text">{userProfile.hobbies || 'No hobbies listed.'}</p>
            )}
          </div>

          <div className="profile-field">
            <label>Skills</label>
            {/* Pass editedProfile.skills when editing, userProfile.skills otherwise */}
            {renderSkills(currentDisplayProfile.skills, isEditing)}
          </div>
        </div>
      </div>
    </div>
  );
}

export default UserProfile;