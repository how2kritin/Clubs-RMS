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

// Define the structure for user profile data
interface UserProfileData {
  name: string;
  rollNumber: string;
  email: string;
  hobbies: string;
  skills: string[];
  gender: 'Male' | 'Female' | 'Other' | 'Prefer not to say' | '';
  batch: 'UG1' | 'UG2' | 'UG3' | 'UG4' | 'UG5' | 'PG1' | 'PG2' | 'PHD' | '';
  profilePicture: string; // Store the path/URL of the selected picture
}

function UserProfile() {
  // --- State ---
  const [isEditing, setIsEditing] = useState(false);
  const [userProfile, setUserProfile] = useState<UserProfileData>({
    // Initial dummy data (replace with fetched data later)
    name: 'Rohit Sharma',
    rollNumber: '202300001',
    email: 'rohit.sharma@students.iiit.ac.in',
    hobbies: 'Cricket, Reading, Coding',
    skills: ['React', 'Python', 'FastAPI', 'TailwindCSS'],
    gender: 'Male',
    batch: 'UG2',
    profilePicture: profilePictures[0], // Default to the first picture
  });

  // State to hold changes during editing
  const [editedProfile, setEditedProfile] = useState<UserProfileData>(userProfile);
  // State for the new skill input
  const [newSkill, setNewSkill] = useState('');

  // --- Effects ---
  // Reset editedProfile whenever userProfile changes (e.g., after saving)
  // or when switching out of edit mode without saving (if a cancel button was added)
  useEffect(() => {
    setEditedProfile(userProfile);
  }, [userProfile]);

  // --- Handlers ---
  const handleEditToggle = () => {
    if (isEditing) {
      // "Done" button clicked - Save changes
      // TODO: Add API call here to save data to the backend
      console.log('Saving profile:', editedProfile);
      setUserProfile(editedProfile); // Update the main profile state
      setIsEditing(false);
    } else {
      // "Edit Profile" button clicked - Start editing
      setEditedProfile(userProfile); // Ensure edit state starts fresh
      setIsEditing(true);
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setEditedProfile((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleProfilePicSelect = (pic: string) => {
    if (isEditing) {
      setEditedProfile((prev) => ({
        ...prev,
        profilePicture: pic,
      }));
    }
  };

  const handleAddSkill = () => {
    if (newSkill.trim() && !editedProfile.skills.includes(newSkill.trim())) {
      setEditedProfile((prev) => ({
        ...prev,
        skills: [...prev.skills, newSkill.trim()],
      }));
      setNewSkill(''); // Clear input field
    }
  };

  const handleRemoveSkill = (skillToRemove: string) => {
    setEditedProfile((prev) => ({
      ...prev,
      skills: prev.skills.filter((skill) => skill !== skillToRemove),
    }));
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
            src={currentProfile.profilePicture}
            alt="User profile"
            className="profile-picture-main"
          />
          {isEditing && (
            <div className="profile-picture-options">
              {profilePictures.map((pic, index) => (
                <img
                  key={index}
                  src={pic}
                  alt={`Profile option ${index + 1}`}
                  className={`profile-picture-thumb ${
                    currentProfile.profilePicture === pic ? 'selected' : ''
                  }`}
                  onClick={() => handleProfilePicSelect(pic)}
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
              <p>{userProfile.name}</p>
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
              <p>{userProfile.rollNumber}</p>
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
              <p>{userProfile.email}</p>
            )}
          </div>

          <div className="profile-field">
            <label htmlFor="gender">Gender</label>
            {isEditing ? (
              <select
                id="gender"
                name="gender"
                value={editedProfile.gender}
                onChange={handleInputChange}
              >
                <option value="">Select Gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
                <option value="Prefer not to say">Prefer not to say</option>
              </select>
            ) : (
              <p>{userProfile.gender || 'Not specified'}</p>
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