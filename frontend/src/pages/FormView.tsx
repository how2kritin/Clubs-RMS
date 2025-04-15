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

  useEffect(() => {
    async function fetchForm() {
      // TODO: Replace with your actual API call, e.g.:
      const response = await fetch(`/api/recruitment/forms/${formId}`);
      const data = await response.json();
      setForm(data);

      // // Placeholder dummy data:
      // setForm({
      //   id: formId || "unknown",
      //   name: `Form ${formId}`,
      //   deadline: new Date().toISOString(),
      //   questions: [
      //     { id: 1, question_text: "What is your name?", question_order: 1 },
      //     { id: 2, question_text: "What is your role?", question_order: 2 },
      //     {
      //       id: 3,
      //       question_text: "Why are you interested?",
      //       question_order: 3,
      //     },
      //   ],
      // });
    }

    if (formId) {
      fetchForm();
    }
  }, [formId]);

  if (!form) {
    return <p>Loading...</p>;
  }

  return (
    <div className="form-view">
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
    </div>
  );
}

export default FormView;
