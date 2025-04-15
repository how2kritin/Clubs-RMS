import React, { useState } from "react";
import { useParams } from "react-router-dom";

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
  // Extract the clubId from the URL parameters.
  const { clubId } = useParams<{ clubId: string }>();

  const [formName, setFormName] = useState<string>("");
  // Store the deadline as a string to work with the datetime-local input.
  const [deadline, setDeadline] = useState<string>("");
  // Initialize with one question by default.
  const [questions, setQuestions] = useState<Question[]>([
    { question_text: "" },
  ]);

  // Function to add a new empty question field.
  const addQuestion = () => {
    setQuestions([...questions, { question_text: "" }]);
  };

  // Function to update a question field.
  const updateQuestion = (index: number, value: string) => {
    const newQuestions = [...questions];
    newQuestions[index].question_text = value;
    setQuestions(newQuestions);
  };

  // Handles form submission.
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Construct the payload following your backend's schema.
    const payload: FormData = {
      name: formName,
      club_id: clubId, // Received directly from the URL path.
      deadline: deadline ? new Date(deadline) : undefined,
      questions: questions.map((q, index) => ({
        ...q,
        question_order: index + 1, // Optionally set order of questions.
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
        // Handle error case
        console.error("Error creating form");
      } else {
        const data = await response.json();
        console.log("Form created successfully:", data);
        // Optionally clear the form or redirect the user.
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div className="create-form">
      <h2>Create a New Recruitment Form {clubId && `for Club ${clubId}`}</h2>
      <form onSubmit={handleSubmit}>
        <div>
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
        <div>
          <label htmlFor="deadline">Deadline:</label>
          <input
            id="deadline"
            type="datetime-local"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
            placeholder="Enter Deadline"
          />
        </div>
        <div>
          <label>Questions:</label>
          {questions.map((q, index) => (
            <div key={index}>
              <input
                type="text"
                value={q.question_text}
                onChange={(e) => updateQuestion(index, e.target.value)}
                placeholder={`Question ${index + 1}`}
                required
              />
            </div>
          ))}
          <button type="button" onClick={addQuestion}>
            Add Question
          </button>
        </div>
        <button type="submit">Create Form</button>
      </form>
    </div>
  );
}

export default CreateForm;
