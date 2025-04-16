import { useState, useEffect, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import "./ClubForms.css";

interface FormSummary {
  id: string;
  name: string;
}

function ClubForms() {
  const { clubId } = useParams<{ clubId: string }>();
  const [forms, setForms] = useState<FormSummary[]>([]);
  const [isSubscribed, setIsSubscribed] = useState<boolean | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch forms
  useEffect(() => {
    if (!clubId) return;
    fetch(`/api/recruitment/forms/club/${clubId}`)
      .then((res) => res.json())
      .then(setForms)
      .catch((err) => setError("Failed to load forms"))
      .finally(() => setLoading(false));
  }, [clubId]);

  // Fetch subscription status
  useEffect(() => {
    if (!clubId) return;
    fetch(`/api/club/is_subscribed/${clubId}`)
      .then((res) => {
        if (!res.ok) throw new Error("Not authorized");
        return res.json();
      })
      .then((status: boolean) => setIsSubscribed(status))
      .catch(() => setError("Failed to load subscription status"))
      .finally(() => setLoading(false));
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
