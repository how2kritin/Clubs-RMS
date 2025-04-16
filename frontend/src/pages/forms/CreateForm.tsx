import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "./CreateForm.css";

interface Question {
  question_text: string;
  question_order?: number;
}

interface FormData {
  name: string;
  club_id?: string;
  deadline?: Date;
  questions: Question[];
}

function CreateForm() {
  const { clubId } = useParams<{ clubId: string }>();
  const navigate = useNavigate();

  const [formName, setFormName] = useState<string>("");
  const [deadline, setDeadline] = useState<string>("");
  const [questions, setQuestions] = useState<Question[]>([
    { question_text: "" },
  ]);
  const [isClubAdmin, setIsClubAdmin] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Check if the user is a club admin
  useEffect(() => {
    async function checkAdminStatus() {
      if (!clubId) return;
      try {
        const response = await fetch(`/api/user/user_admin/${clubId}`, {
          credentials: "include",
        });
        if (response.ok) {
          const adminData = await response.json();
          setIsClubAdmin(adminData.is_admin);
        }
      } catch (error) {
        console.error("Error checking admin status:", error);
      } finally {
        setIsLoading(false);
      }
    }

    checkAdminStatus();
  }, [clubId]);

  const addQuestion = () => {
    setQuestions([...questions, { question_text: "" }]);
  };

  const updateQuestion = (index: number, value: string) => {
    const newQuestions = [...questions];
    newQuestions[index].question_text = value;
    setQuestions(newQuestions);
  };

  const removeQuestion = (index: number) => {
    // Ensure at least one question remains.
    if (questions.length > 1) {
      const newQuestions = questions.filter((_, i) => i !== index);
      setQuestions(newQuestions);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const payload: FormData = {
      name: formName,
      club_id: clubId,
      deadline: deadline ? new Date(deadline) : undefined,
      questions: questions.map((q, index) => ({
        ...q,
        question_order: index + 1,
      })),
    };

    console.log("Payload to send:", payload);

    try {
      const response = await fetch("/api/recruitment/forms", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        console.error("Error creating form");
      } else {
        const data = await response.json();
        console.log("Form created successfully:", data);
        navigate(`/form/${data.id}`);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  if (isLoading) {
    return <p>Loading...</p>;
  }

  if (!isClubAdmin) {
    return (
      <p className="warning">Only club admins can create and delete forms.</p>
    );
  }

  return (
    <div className="create-form">
      <h2>Create a New Recruitment Form {clubId && `for Club ${clubId}`}</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-field">
          <label htmlFor="formName">Form Name:</label>
          <input
            id="formName"
            type="text"
            value={formName}
            onChange={(e) => setFormName(e.target.value)}
            placeholder="Enter Form Name"
            required
          />
        </div>
        <div className="form-field">
          <label htmlFor="deadline">Deadline:</label>
          <input
            id="deadline"
            type="datetime-local"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
            placeholder="Enter Deadline"
          />
        </div>
        <div className="form-field questions-container">
          <label>Questions:</label>
          {questions.map((q, index) => (
            <div key={index} className="question-item">
              <input
                type="text"
                value={q.question_text}
                onChange={(e) => updateQuestion(index, e.target.value)}
                placeholder={`Question ${index + 1}`}
                required
              />
              {questions.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeQuestion(index)}
                  className="remove-question-btn"
                >
                  Remove
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={addQuestion}
            className="add-question-btn"
          >
            Add Question
          </button>
        </div>
        <button type="submit" className="submit-btn">
          Create Form
        </button>
      </form>
    </div>
  );
}

export default CreateForm;
