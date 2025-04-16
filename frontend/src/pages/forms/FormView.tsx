import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "./FormView.css";

interface Question {
  id: number;
  question_text: string;
  question_order?: number;
}

interface FormDetails {
  id: string;
  name: string;
  deadline?: string;
  questions: Question[];
  club_id?: string; // For club member/admin check
}

function FormView() {
  const { formId } = useParams<{ formId: string }>();
  const navigate = useNavigate();
  const [form, setForm] = useState<FormDetails | null>(null);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  // State for managing the form's name and deadline in addition to questions.
  const [editedName, setEditedName] = useState<string>("");
  const [editedDeadline, setEditedDeadline] = useState<string>("");
  const [editedQuestions, setEditedQuestions] = useState<Question[]>([]);
  const [isClubMember, setIsClubMember] = useState<boolean>(false);
  const [isClubAdmin, setIsClubAdmin] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    async function fetchForm() {
      try {
        setIsLoading(true);
        const response = await fetch(`/api/recruitment/forms/${formId}`);
        const data: FormDetails = await response.json();
        setForm(data);
        setEditedQuestions(data.questions);
        setEditedName(data.name);
        // Convert the deadline to a datetime-local string format if it's set.
        if (data.deadline) {
          const dt = new Date(data.deadline);
          const isoLocal = dt.toISOString().slice(0, 16);
          setEditedDeadline(isoLocal);
        } else {
          setEditedDeadline("");
        }

        // Check if the user is a club member.
        if (data.club_id) {
          const clubInfoResponse = await fetch("/api/user/user_club_info", {
            credentials: "include",
          });
          if (clubInfoResponse.ok) {
            const clubsData = await clubInfoResponse.json();
            const isMember =
              Array.isArray(clubsData) &&
              clubsData.some((club: any) => club.cid === data.club_id);
            setIsClubMember(isMember);
          }

          // Check if the user is a club admin.
          const clubAdminResponse = await fetch(
            `/api/user/user_role/${data.club_id}`,
            {
              credentials: "include",
            },
          );
          if (clubAdminResponse.ok) {
            const adminData = await clubAdminResponse.json();
            setIsClubAdmin(adminData.is_admin);
          }
        }

        setIsLoading(false);
      } catch (error) {
        console.error("Error fetching form:", error);
        setIsLoading(false);
      }
    }

    if (formId) {
      fetchForm();
    }
  }, [formId]);

  const handleQuestionChange = (index: number, value: string) => {
    const newQuestions = [...editedQuestions];
    newQuestions[index].question_text = value;
    setEditedQuestions(newQuestions);
  };

  const handleAddQuestion = () => {
    const newQuestion: Question = {
      id: Date.now(), // temporary id.
      question_text: "",
    };
    setEditedQuestions([...editedQuestions, newQuestion]);
  };

  const handleRemoveQuestion = (index: number) => {
    const newQuestions = editedQuestions.filter((_, i) => i !== index);
    setEditedQuestions(newQuestions);
  };

  const handleSave = async () => {
    const payload = {
      name: editedName,
      // If the deadline field is empty, send null.
      deadline: editedDeadline ? new Date(editedDeadline).toISOString() : null,
      questions: editedQuestions.map((q, index) => ({
        question_text: q.question_text,
        question_order: index + 1,
      })),
    };

    try {
      const response = await fetch(`/api/recruitment/forms/${formId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        console.error("Error updating form");
      } else {
        const updatedForm: FormDetails = await response.json();
        console.log("Form updated successfully:", updatedForm);
        setForm(updatedForm);
        setEditedQuestions(updatedForm.questions);
        setIsEditing(false);
      }
    } catch (error) {
      console.error("Error updating form:", error);
    }
  };

  const handleDelete = async () => {
    // Confirm deletion before sending request.
    if (!window.confirm("Are you sure you want to delete this form?")) return;

    try {
      const response = await fetch(`/api/recruitment/forms/${formId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        console.error("Error deleting form");
      } else {
        console.log("Form deleted successfully");
        // Redirect to the landing page.
        navigate("/dashboard");
      }
    } catch (error) {
      console.error("Error deleting form:", error);
    }
  };

  // Handler to navigate to the application form
  const handleApply = () => {
    navigate(`/apply/${formId}`);
  };

  // Handler to navigate to applications list
  const handleViewApplications = () => {
    navigate(`/forms/${formId}/applications`);
  };

  if (isLoading) {
    return <p>Loading...</p>;
  }

  if (!form) {
    return <p>Form not found</p>;
  }

  // Check if deadline has passed
  const isDeadlinePassed = form.deadline
    ? new Date() > new Date(form.deadline)
    : false;

  return (
    <div className="form-view">
      {isEditing ? (
        <div>
          {/* Editable form header inputs */}
          <div className="form-header-edit">
            <label>
              <strong>Form Name:</strong>{" "}
              <input
                type="text"
                value={editedName}
                onChange={(e) => setEditedName(e.target.value)}
                placeholder="Enter form name"
              />
            </label>
            <label>
              <strong>Deadline:</strong>{" "}
              <input
                type="datetime-local"
                value={editedDeadline}
                onChange={(e) => setEditedDeadline(e.target.value)}
              />
            </label>
          </div>

          <h3>Questions</h3>
          <ul className="questions-list">
            {editedQuestions.map((q, index) => (
              <li key={q.id || index}>
                <strong>{index + 1}. </strong>
                <input
                  type="text"
                  value={q.question_text}
                  onChange={(e) => handleQuestionChange(index, e.target.value)}
                  placeholder="Enter question text..."
                />
                <button
                  className="remove-btn"
                  onClick={() => handleRemoveQuestion(index)}
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
          <div className="action-buttons">
            <button onClick={handleAddQuestion} className="add-btn">
              Add Question
            </button>
          </div>
          <div className="edit-buttons">
            <button onClick={handleSave}>Save</button>
            <button
              onClick={() => {
                // Reset all changes.
                setEditedName(form.name);
                if (form.deadline) {
                  const dt = new Date(form.deadline);
                  const isoLocal = dt.toISOString().slice(0, 16);
                  setEditedDeadline(isoLocal);
                } else {
                  setEditedDeadline("");
                }
                setEditedQuestions(form.questions);
                setIsEditing(false);
              }}
            >
              Cancel
            </button>
            {isClubAdmin && (
              <button onClick={handleDelete} className="delete-btn">
                Delete Form
              </button>
            )}
          </div>
        </div>
      ) : (
        <div>
          <h2>{form.name}</h2>
          <p>
            <strong>Deadline:</strong>{" "}
            {form.deadline
              ? new Date(form.deadline).toLocaleString()
              : "No deadline set"}
          </p>

          {/* Action buttons for form */}
          <div className="form-action-buttons">
            {(isClubMember || isClubAdmin) && (
              <button
                className="view-applications-btn"
                onClick={handleViewApplications}
              >
                View Applications
              </button>
            )}
            <button
              className="apply-btn"
              onClick={handleApply}
              disabled={isDeadlinePassed}
            >
              {isDeadlinePassed ? "Deadline Passed" : "Apply to Form"}
            </button>
            {(isClubAdmin || isClubMember) && (
              <button
                className="edit-form-btn"
                onClick={() => setIsEditing(true)}
              >
                Edit Form
              </button>
            )}
            {isClubAdmin && (
              <button onClick={handleDelete} className="delete-btn">
                Delete Form
              </button>
            )}
          </div>

          <h3>Questions</h3>
          <ul className="questions-list">
            {form.questions.map((q) => (
              <li key={q.id}>
                <strong>{q.question_order}. </strong>
                {q.question_text}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default FormView;
