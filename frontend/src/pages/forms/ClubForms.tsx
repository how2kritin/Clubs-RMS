import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import "./ClubForms.css";

interface FormSummary {
  id: string;
  name: string;
}

function ClubForms() {
  const { clubId } = useParams<{ clubId: string }>();
  const [forms, setForms] = useState<FormSummary[]>([]);

  useEffect(() => {
    async function fetchForms() {
      const response = await fetch(`/api/recruitment/forms/club/${clubId}`);
      const data = await response.json();
      setForms(data);
    }

    if (clubId) {
      fetchForms();
    }
  }, [clubId]);

  return (
    <div className="club-forms">
      <h2>Forms for Club {clubId}</h2>
      <ul className="forms-list">
        {forms.map((form) => (
          <li key={form.id}>
            <Link to={`/form/${form.id}`}>{form.name}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ClubForms;
