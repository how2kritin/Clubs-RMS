import React, { useState, useEffect } from 'react';
import { Edit, Check, X, Plus } from 'lucide-react'; // Import icons

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
  batch: 'UG1' | 'UG2' | 'UG3' | 'UG4' | 'UG5' | 'PG1' | 'PG2' | 'PHD' | '';
  profilePicture: number; // Stores index into profilePictures (0 to 4)
}

function UserProfile() {
  // --- State ---
  const [isEditing, setIsEditing] = useState(false);
  const [userProfile, setUserProfile] = useState<UserProfileData | null>(null);
  // State to hold changes during editing
  const [editedProfile, setEditedProfile] = useState<UserProfileData | null>(null);
  // State for the new skill input
  const [newSkill, setNewSkill] = useState('');

  // --- Effects ---
  // Fetch user info on component mount
  useEffect(() => {
    async function fetchUserProfile() {
      try {
        const response = await fetch('/api/user/user_info');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        // Map the API response (with keys like first_name, last_name, roll_number, etc.)
        const sanitizedData: UserProfileData = {
          name: `${data.first_name || 'No First Name'} ${data.last_name || 'No Last Name'}`,
          rollNumber: data.roll_number || 'N/A',
          email: data.email || 'N/A',
          hobbies: data.hobbies || '',
          skills: data.skills || [],
          batch: data.batch || '',
          profilePicture: typeof data.profile_picture === 'number' ? data.profile_picture : 0,
        };
        setUserProfile(sanitizedData);
        setEditedProfile(sanitizedData);
      } catch (error) {
        console.error('Error fetching user info:', error);
      }
    }
    fetchUserProfile();
  }, []);

  // Reset editedProfile whenever userProfile changes
  useEffect(() => {
    if (userProfile) {
      setEditedProfile(userProfile);
    }
  }, [userProfile]);

  // --- Handlers ---
  const handleEditToggle = () => {
    if (isEditing) {
      // "Done" button clicked - save changes via API call
      // TODO: Add API call here to save changes to the backend.
      console.log('Saving profile:', editedProfile);
      if (editedProfile) {
        setUserProfile(editedProfile); // Update the main profile state
      }
      setIsEditing(false);
    } else {
      // "Edit Profile" button clicked - start editing
      if (userProfile) {
        setEditedProfile(userProfile); // Ensure edit state starts fresh
      }
      setIsEditing(true);
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    if (editedProfile) {
      setEditedProfile((prev) => prev && ({
        ...prev,
        [name]: value,
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
          />
          <button onClick={handleAddSkill} className="add-skill-btn" aria-label="Add skill">
            <Plus size={18} />
          </button>
        </div>
      )}
    </div>
  );

  if (!userProfile || !editedProfile) {
    return <div>Loading...</div>;
  }

  const currentProfile = isEditing ? editedProfile : userProfile;

  return (
    <div className="user-profile-page">
      <div className="profile-header">
        <h1 className="profile-title">User Profile</h1>
        <button onClick={handleEditToggle} className="edit-button">
          {isEditing ? (
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

      <div className="profile-content">
        {/* --- Profile Picture Section --- */}
        <div className="profile-picture-section">
          <h2>Profile Picture</h2>
          <img
            src={profilePictures[currentProfile.profilePicture]}
            alt="User profile"
            className="profile-picture-main"
          />
          {isEditing && (
            <div className="profile-picture-options">
              {profilePictures.map((_, index) => (
                <img
                  key={index}
                  src={profilePictures[index]}
                  alt={`Profile option ${index + 1}`}
                  className={`profile-picture-thumb ${
                    currentProfile.profilePicture === index ? 'selected' : ''
                  }`}
                  onClick={() => handleProfilePicSelect(index)}
                />
              ))}
            </div>
          )}
        </div>

        {/* --- Profile Details Section --- */}
        <div className="profile-details-section">
          <div className="profile-field">
            <label htmlFor="name">Name</label>
            {isEditing ? (
              <input
                type="text"
                id="name"
                name="name"
                value={editedProfile.name}
                onChange={handleInputChange}
              />
            ) : (
              <p>{userProfile.name || 'Not specified'}</p>
            )}
          </div>

          <div className="profile-field">
            <label htmlFor="rollNumber">Roll Number</label>
            {isEditing ? (
              <input
                type="text"
                id="rollNumber"
                name="rollNumber"
                value={editedProfile.rollNumber}
                onChange={handleInputChange}
              />
            ) : (
              <p>{userProfile.rollNumber || 'Not specified'}</p>
            )}
          </div>

          <div className="profile-field">
            <label htmlFor="email">Email</label>
            {isEditing ? (
              <input
                type="email"
                id="email"
                name="email"
                value={editedProfile.email}
                onChange={handleInputChange}
              />
            ) : (
              <p>{userProfile.email || 'Not specified'}</p>
            )}
          </div>

          <div className="profile-field">
            <label htmlFor="batch">Batch</label>
            {isEditing ? (
              <select
                id="batch"
                name="batch"
                value={editedProfile.batch}
                onChange={handleInputChange}
              >
                <option value="">Select Batch</option>
                <option value="UG1">UG1</option>
                <option value="UG2">UG2</option>
                <option value="UG3">UG3</option>
                <option value="UG4">UG4</option>
                <option value="UG5">UG5</option>
                <option value="PG1">PG1</option>
                <option value="PG2">PG2</option>
                <option value="PHD">PHD</option>
              </select>
            ) : (
              <p>{userProfile.batch || 'Not specified'}</p>
            )}
          </div>

          <div className="profile-field">
            <label htmlFor="hobbies">Hobbies</label>
            {isEditing ? (
              <textarea
                id="hobbies"
                name="hobbies"
                value={editedProfile.hobbies}
                onChange={handleInputChange}
                rows={3}
              />
            ) : (
              <p className="hobbies-text">{userProfile.hobbies || 'No hobbies listed.'}</p>
            )}
          </div>

          <div className="profile-field">
            <label>Skills</label>
            {renderSkills(currentProfile.skills, isEditing)}
          </div>
        </div>
      </div>
    </div>
  );
}

export default UserProfile;
