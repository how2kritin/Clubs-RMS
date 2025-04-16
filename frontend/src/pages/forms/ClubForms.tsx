import { useState, useEffect, useCallback } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import "./ClubForms.css";

interface FormSummary {
  id: string;
  name: string;
}

function ClubForms() {
  const { clubId } = useParams<{ clubId: string }>();
  const navigate = useNavigate();
  const [forms, setForms] = useState<FormSummary[]>([]);
  const [isSubscribed, setIsSubscribed] = useState<boolean | null>(null);
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch forms
  useEffect(() => {
    if (!clubId) return;
    fetch(`/api/recruitment/forms/club/${clubId}`)
      .then((res) => res.json())
      .then(setForms)
      .catch(() => setError("Failed to load forms"))
      .finally(() => setLoading(false));
  }, [clubId]);

  // Fetch subscription status and role
  useEffect(() => {
    if (!clubId) return;

    const fetchAll = async () => {
      try {
        const [subRes, roleRes] = await Promise.all([
          fetch(`/api/club/is_subscribed/${clubId}`),
          fetch(`/api/user/user_role/${clubId}`),
        ]);

        if (!subRes.ok || !roleRes.ok) throw new Error("Failed");

        const [subscribed, roleData] = await Promise.all([
          subRes.json(),
          roleRes.json(),
        ]);

        setIsSubscribed(subscribed);
        setIsAdmin(roleData.is_admin || false);
      } catch {
        setError("Failed to load user info");
      } finally {
        setLoading(false);
      }
    };

    fetchAll();
  }, [clubId]);

  const toggleSubscription = useCallback(async () => {
    if (!clubId) return;
    setActionLoading(true);
    try {
      const endpoint = isSubscribed ? "unsubscribe" : "subscribe";
      const res = await fetch(`/api/club/${endpoint}/${clubId}`, {
        method: "POST",
      });
      if (!res.ok) throw new Error("Action failed");
      setIsSubscribed(!isSubscribed);
    } catch {
      setError("Could not update subscription");
    } finally {
      setActionLoading(false);
    }
  }, [clubId, isSubscribed]);

  if (loading) return <p>Loading...</p>;
  if (error) return <p className="error">{error}</p>;

  return (
    <div className="club-forms">
      <h2>Forms for Club {clubId}</h2>
      <div className="button-row">
        <button
          className={`subscribe-button ${
            isSubscribed ? "unsubscribe" : "subscribe"
          }`}
          onClick={toggleSubscription}
          disabled={actionLoading}
        >
          {actionLoading
            ? isSubscribed
              ? "Unsubscribing..."
              : "Subscribing..."
            : isSubscribed
              ? "Unsubscribe"
              : "Subscribe"}
        </button>

        {isAdmin && (
          <button
            className="create-form-button"
            onClick={() => navigate(`/create_form/${clubId}`)}
          >
            Create Form
          </button>
        )}
      </div>
      {forms.length > 0 ? (
        <ul className="forms-list">
          {forms.map((form) => (
            <li key={form.id}>
              <Link to={`/form/${form.id}`}>{form.name}</Link>
            </li>
          ))}
        </ul>
      ) : (
        <p>No forms available.</p>
      )}
    </div>
  );
}

export default ClubForms;
