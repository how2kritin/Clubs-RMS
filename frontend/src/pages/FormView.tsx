import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
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
}

function FormView() {
  // Extract the formId from the URL parameters.
  const { formId } = useParams<{ formId: string }>();
  const [form, setForm] = useState<FormDetails | null>(null);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  // State for managing the form's name and deadline in addition to questions.
  const [editedName, setEditedName] = useState<string>("");
  const [editedDeadline, setEditedDeadline] = useState<string>("");
  const [editedQuestions, setEditedQuestions] = useState<Question[]>([]);

  useEffect(() => {
    async function fetchForm() {
      try {
        const response = await fetch(`/api/recruitment/forms/${formId}`);
        const data: FormDetails = await response.json();
        setForm(data);
        setEditedQuestions(data.questions);
        setEditedName(data.name);
        // Convert the deadline to a datetime-local string format if it's set.
        if (data.deadline) {
          // Remove seconds and milliseconds for a proper "datetime-local" input.
          const dt = new Date(data.deadline);
          const isoLocal = dt.toISOString().slice(0, 16);
          setEditedDeadline(isoLocal);
        } else {
          setEditedDeadline("");
        }
      } catch (error) {
        console.error("Error fetching form:", error);
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
    // Create a new question with a unique temporary id.
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
    // Build the payload including name and deadline, along with questions.
    const payload = {
      name: editedName,
      // If the deadline field is empty, don't send it
      deadline: editedDeadline ? new Date(editedDeadline).toISOString() : null,
      questions: editedQuestions.map((q, index) => ({
        question_text: q.question_text,
        question_order: index + 1,
      })),
    };

    try {
      const response = await fetch(`/api/recruitment/forms/${formId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
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

  if (!form) {
    return <p>Loading...</p>;
  }

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
          <h3>Questions</h3>
          <ul className="questions-list">
            {form.questions.map((q) => (
              <li key={q.id}>
                <strong>{q.question_order}. </strong>
                {q.question_text}
              </li>
            ))}
          </ul>
          <button onClick={() => setIsEditing(true)}>Edit Form</button>
        </div>
      )}
    </div>
  );
}

export default FormView;
