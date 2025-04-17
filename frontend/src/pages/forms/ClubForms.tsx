import {useCallback, useEffect, useState} from "react";
import {Link, useNavigate, useParams} from "react-router-dom";
import "./ClubForms.css";
// Import icons from React Icons
import {FaDiscord, FaEnvelope, FaGlobe, FaInstagram, FaLinkedin, FaYoutube} from "react-icons/fa";
import {FaX} from "react-icons/fa6";

interface FormSummary {
    id: string;
    name: string;
}

interface Club {
    cid: string;
    name: string;
    category?: string | null;
    tagline?: string | null;
    description?: string | null;
    logo?: string | null;
    banner?: string | null;
    email?: string | null;
    socials?: {
        website?: string;
        instagram?: string;
        youtube?: string;
        twitter?: string;
        linkedin?: string;
        discord?: string;
        otherLinks?: string[];
    } | null;
}

function ClubForms() {
    const {clubId} = useParams<{ clubId: string }>();
    const navigate = useNavigate();
    const [forms, setForms] = useState<FormSummary[]>([]);
    const [isSubscribed, setIsSubscribed] = useState<boolean | null>(null);
    const [isAdmin, setIsAdmin] = useState<boolean>(false);
    const [loading, setLoading] = useState<boolean>(true);
    const [actionLoading, setActionLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [club, setClub] = useState<Club | null>(null);
    const [clubLoading, setClubLoading] = useState<boolean>(true);
    const [clubError, setClubError] = useState<string | null>(null);

    // Fetch club details
    useEffect(() => {
        if (!clubId) return;

        setClubLoading(true);
        fetch(`/api/club/${clubId}`)
            .then((res) => {
                if (!res.ok) throw new Error("Failed to load club details");
                return res.json();
            })
            .then((data) => setClub(data))
            .catch((err) => setClubError(err.message || "Failed to load club details"))
            .finally(() => setClubLoading(false));
    }, [clubId]);

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
                const [subRes, roleRes] = await Promise.all([fetch(`/api/club/is_subscribed/${clubId}`), fetch(`/api/user/user_role/${clubId}`),]);

                if (!subRes.ok || !roleRes.ok) throw new Error("Failed");

                const [subscribed, roleData] = await Promise.all([subRes.json(), roleRes.json(),]);

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

    const renderClubOverview = () => {
        if (clubLoading) return <p className="loading-text">Loading club details...</p>;
        if (clubError) return <p className="error">{clubError}</p>;
        if (!club) return <p className="error">Club not found</p>;

        const logoSrc = club.logo ? `http://clubs.iiit.ac.in/files/download?filename=${encodeURIComponent(club.logo)}` : "/placeholder.jpg";

        const bannerSrc = club.banner ? `http://clubs.iiit.ac.in/files/download?filename=${encodeURIComponent(club.banner)}` : null;

        return (<div className="club-overview">
            {bannerSrc && (<div className="club-banner">
                <img src={bannerSrc} alt={`${club.name} banner`}/>
            </div>)}

            <div className="club-header">
                <div className="club-logo">
                    <img src={logoSrc} alt={`${club.name} logo`}/>
                </div>
                <div className="club-info">
                    <h1>{club.name}</h1>
                    {club.tagline && <p className="club-tagline">{club.tagline}</p>}
                    {club.category && <span className="club-category">{club.category}</span>}
                </div>
            </div>

            {club.description && (<div className="club-description">
                <h3>About</h3>
                <p>{club.description}</p>
            </div>)}

            {club.socials && Object.keys(club.socials).some(key => club.socials?.[key as keyof typeof club.socials]) && (
                <div className="club-socials">
                    <h3>Connect With Us</h3>
                    <div className="social-links">
                        {club.socials.website && (
                            <a href={club.socials.website} target="_blank" rel="noopener noreferrer"
                               className="social-link">
                                <FaGlobe className="social-icon"/> Website
                            </a>)}
                        {club.socials.discord && (
                            <a href={club.socials.discord} target="_blank" rel="noopener noreferrer"
                               className="social-link">
                                <FaDiscord className="social-icon"/> Discord
                            </a>)}
                        {club.socials.instagram && (
                            <a href={club.socials.instagram} target="_blank" rel="noopener noreferrer"
                               className="social-link">
                                <FaInstagram className="social-icon"/> Instagram
                            </a>)}
                        {club.socials.youtube && (
                            <a href={club.socials.youtube} target="_blank" rel="noopener noreferrer"
                               className="social-link">
                                <FaYoutube className="social-icon"/> YouTube
                            </a>)}
                        {club.socials.twitter && (
                            <a href={club.socials.twitter} target="_blank" rel="noopener noreferrer"
                               className="social-link">
                                <FaX className="social-icon"/> X
                            </a>)}
                        {club.socials.linkedin && (
                            <a href={club.socials.linkedin} target="_blank" rel="noopener noreferrer"
                               className="social-link">
                                <FaLinkedin className="social-icon"/> LinkedIn
                            </a>)}
                    </div>
                </div>)}

            <div className="club-footer">
                {club.email && (<div className="club-contact">
                    <FaEnvelope className="contact-icon"/>
                    <a href={`mailto:${club.email}`}>{club.email}</a>
                </div>)}
            </div>
        </div>);
    };

    if (loading && clubLoading) return <p className="loading-text">Loading...</p>;

    return (<div className="club-page-container">
        {/* Club Overview Section */}
        <section className="club-overview-section">
            {renderClubOverview()}
        </section>

        {/* Forms Section */}
        <section className="club-forms-section">
            <div className="club-forms">
                <h2>Recruitment Forms</h2>
                <div className="button-row">
                    <button
                        className={`subscribe-button ${isSubscribed ? "unsubscribe" : "subscribe"}`}
                        onClick={toggleSubscription}
                        disabled={actionLoading}
                    >
                        {actionLoading ? isSubscribed ? "Unsubscribing..." : "Subscribing..." : isSubscribed ? "Unsubscribe" : "Subscribe"}
                    </button>

                    {isAdmin && (<button
                        className="create-form-button"
                        onClick={() => navigate(`/create_form/${clubId}`)}
                    >
                        Create Form
                    </button>)}
                </div>
                {error && <p className="error">{error}</p>}
                {forms.length > 0 ? (<ul className="forms-list">
                    {forms.map((form) => (<li key={form.id}>
                        <Link to={`/form/${form.id}`}>{form.name}</Link>
                    </li>))}
                </ul>) : (<p>No forms available.</p>)}
            </div>
        </section>
    </div>);
}

export default ClubForms;