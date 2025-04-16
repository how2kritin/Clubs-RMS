// frontend/src/pages/ApplyToForm.tsx
import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "./ApplyToForm.css";

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

const ApplyToForm: React.FC = () => {
  const { formId } = useParams<{ formId: string }>();
  const navigate = useNavigate();
  const [form, setForm] = useState<FormDetails | null>(null);
  const [responses, setResponses] = useState<{ question_id: number; answer_text: string }[]>([]);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [userInfo, setUserInfo] = useState<any>(null);
  const [isDeadlinePassed, setIsDeadlinePassed] = useState<boolean>(false);

  useEffect(() => {
    // Fetch form details when component mounts
    const fetchForm = async () => {
      try {
        const response = await fetch(`/api/recruitment/forms/${formId}`, {credentials: 'include'});

        if (!response.ok) {
          throw new Error(`Error ${response.status}: Failed to fetch form`);
        }

        const data: FormDetails = await response.json();
        setForm(data);

        // Initialize responses array
        const initialResponses = data.questions.map(question => ({
          question_id: question.id,
          answer_text: ""
        }));
        setResponses(initialResponses);

        // Check if deadline has passed
        if (data.deadline) {
          const currentDate = new Date();
          const deadlineDate = new Date(data.deadline);
          setIsDeadlinePassed(currentDate > deadlineDate);
        }
      } catch (error) {
        console.error("Error fetching form:", error);
        setError("Failed to load form. Please try again later.");
      }
    };

    // Fetch user info for autofill
    const fetchUserInfo = async () => {
      try {
        const response = await fetch("/api/application/autofill-details", {credentials: 'include'});

        if (!response.ok) {
          throw new Error(`Error ${response.status}: Failed to fetch user info`);
        }

        const data = await response.json();
        setUserInfo(data);
      } catch (error) {
        console.error("Error fetching user info:", error);
        // Non-blocking error - we can still continue without autofill info
      }
    };

    if (formId) {
      fetchForm();
      fetchUserInfo();
    }
  }, [formId]);

  const handleResponseChange = (questionId: number, value: string) => {
    const newResponses = responses.map(response =>
      response.question_id === questionId
        ? { ...response, answer_text: value }
        : response
    );
    setResponses(newResponses);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (isDeadlinePassed) {
      setError("The deadline for this application has passed.");
      return;
    }

    // Check if all required fields are filled
    const emptyResponses = responses.filter(response => response.answer_text.trim() === "");
    if (emptyResponses.length > 0) {
      setError("Please fill in all fields before submitting.");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const payload = {
        form_id: formId,
        responses: responses
      };

      const response = await fetch("/api/application/submit-application", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload),
        credentials: "include"
      });

      if (!response.ok) {
        let errorMessage = `Error ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          // Ignore JSON parse errors
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      setSuccess("Application submitted successfully!");

      // Navigate to applications list after a short delay
      setTimeout(() => {
        navigate(-1);
      }, 2000);

    } catch (error: any) {
      console.error("Error submitting application:", error);
      setError(error.message || "Failed to submit application. Please try again later.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (error && !form) {
    return (
      <div className="container mx-auto p-4 text-center">
        <div className="bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 p-4 rounded-md">
          {error}
        </div>
        <button
          onClick={() => navigate(-1)}
          className="mt-4 px-4 py-2 bg-gray-300 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-md hover:bg-gray-400 dark:hover:bg-gray-600 transition-colors"
        >
          Go Back
        </button>
      </div>
    );
  }

  if (!form) {
    return (
      <div className="container mx-auto p-4 text-center">
        <p className="text-gray-600 dark:text-gray-400">Loading form...</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 max-w-3xl">
      <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-white mb-6">
          {form.name}
        </h1>

        {form.deadline && (
          <div className={`mb-4 p-3 rounded-md ${
            isDeadlinePassed ? 
            "bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300" : 
            "bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300"
          }`}>
            <p>
              <span className="font-semibold">Deadline:</span>{" "}
              {new Date(form.deadline).toLocaleString()}
              {isDeadlinePassed && " (Deadline has passed)"}
            </p>
          </div>
        )}

        {error && (
          <div className="mb-4 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 p-3 rounded-md">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-4 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 p-3 rounded-md">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {form.questions
            .sort((a, b) => (a.question_order || 0) - (b.question_order || 0))
            .map((question) => {
              const response = responses.find(r => r.question_id === question.id);

              return (
                <div key={question.id} className="mb-6">
                  <label
                    htmlFor={`question-${question.id}`}
                    className="block text-gray-700 dark:text-gray-300 font-medium mb-2"
                  >
                    {question.question_text}
                  </label>
                  <textarea
                    id={`question-${question.id}`}
                    value={response?.answer_text || ""}
                    onChange={(e) => handleResponseChange(question.id, e.target.value)}
                    className="w-full px-3 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 transition-colors"
                    rows={4}
                    disabled={isSubmitting || isDeadlinePassed}
                    placeholder={`Enter your response ${isDeadlinePassed ? "(Deadline passed)" : ""}`}
                  ></textarea>
                </div>
              );
            })}

          <div className="flex justify-between mt-8">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="px-4 py-2 bg-gray-300 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-md hover:bg-gray-400 dark:hover:bg-gray-600 transition-colors"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className={`px-6 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors ${
                (isSubmitting || isDeadlinePassed) ? 
                "opacity-50 cursor-not-allowed" : ""
              }`}
              disabled={isSubmitting || isDeadlinePassed}
            >
              {isSubmitting ? "Submitting..." : "Submit Application"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ApplyToForm;