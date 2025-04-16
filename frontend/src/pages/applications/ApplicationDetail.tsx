import React, {useEffect, useState} from 'react';
import {useNavigate, useParams} from 'react-router-dom';
import {Alert, Button, Card, Descriptions, Divider, Space, Tag, Typography} from 'antd';
import {CheckOutlined, CloseOutlined, LikeOutlined, RollbackOutlined} from '@ant-design/icons';
import './ApplicationDetail.css';

const {Title, Text} = Typography;

interface Response {
    question_id: number;
    answer_text: string;
    question_text: string;
    question_order?: number;
}

interface ApplicationDetail {
    id: number;
    form_id: number;
    user_id: string;
    form_name: string;
    club_id: string;
    submitted_at: string;
    status: string;
    responses: Response[];
    endorser_ids: string[];
    endorser_count: number;
}

const ApplicationDetail: React.FC = () => {
    const {formId, applicationId} = useParams<{ formId: string, applicationId: string }>();
    const navigate = useNavigate();
    const [application, setApplication] = useState<ApplicationDetail | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [actionLoading, setActionLoading] = useState<boolean>(false);
    const [isClubMember, setIsClubMember] = useState<boolean>(false);

    useEffect(() => {
        const fetchApplicationDetail = async () => {
            try {
                setLoading(true);

                // Fetch application details
                const response = await fetch(`/api/applications/${applicationId}`);
                if (!response.ok) {
                    throw new Error(`Failed to fetch application: ${response.statusText}`);
                }

                const data = await response.json();
                setApplication(data);

                // Check if the user is a club member by fetching user club info
                const userClubResponse = await fetch('/api/user/user_club_info');
                if (userClubResponse.ok) {
                    const userClubs = await userClubResponse.json();
                    // Check if the user is a member of this club
                    const isMember = userClubs.some((club: any) => club.cid === data.club_id);
                    setIsClubMember(isMember);
                }

                setLoading(false);
            } catch (err) {
                console.error('Error fetching application details:', err);
                setError(err instanceof Error ? err.message : 'An error occurred');
                setLoading(false);
            }
        };

        if (applicationId) {
            fetchApplicationDetail();
        }
    }, [applicationId]);

    const handleStatusUpdate = async (newStatus: string) => {
        try {
            setActionLoading(true);
            const response = await fetch(`/api/applications/${applicationId}/status`, {
                method: 'PUT', headers: {
                    'Content-Type': 'application/json',
                }, body: JSON.stringify({
                    status: newStatus
                }),
            });

            if (!response.ok) {
                throw new Error(`Failed to update status: ${response.statusText}`);
            }

            // Refresh application data after status update
            const updatedApp = await fetch(`/api/applications/${applicationId}`);
            const updatedData = await updatedApp.json();
            setApplication(updatedData);
            setActionLoading(false);
        } catch (err) {
            console.error('Error updating application status:', err);
            setError(err instanceof Error ? err.message : 'An error occurred');
            setActionLoading(false);
        }
    };

    const handleEndorse = async () => {
        try {
            setActionLoading(true);
            const response = await fetch(`/api/applications/${applicationId}/endorse`, {
                method: 'PUT',
            });

            if (!response.ok) {
                throw new Error(`Failed to endorse application: ${response.statusText}`);
            }

            // Refresh application data after endorsement
            const updatedApp = await fetch(`/api/applications/${applicationId}`);
            const updatedData = await updatedApp.json();
            setApplication(updatedData);
            setActionLoading(false);
        } catch (err) {
            console.error('Error endorsing application:', err);
            setError(err instanceof Error ? err.message : 'An error occurred');
            setActionLoading(false);
        }
    };

    if (loading) {
        return <div className="loading">Loading application details...</div>;
    }

    if (error) {
        return <Alert message={error} type="error"/>;
    }

    if (!application) {
        return <Alert message="Application not found" type="error"/>;
    }

    const statusColor = application.status === 'ongoing' ? 'gold' : application.status === 'accepted' ? 'green' : application.status === 'rejected' ? 'red' : 'blue';

    return (<div className="application-detail-container">
            <Card className="application-detail-card">
                <div className="application-detail-header">
                    <Button
                        icon={<RollbackOutlined/>}
                        onClick={() => navigate(`/forms/${formId}/applications`)}
                    >
                        Back to Applications
                    </Button>
                </div>

                <Title level={2}>Application Details</Title>
                <Descriptions bordered className="application-info">
                    <Descriptions.Item label="Form" span={3}>{application.form_name}</Descriptions.Item>
                    <Descriptions.Item label="Applicant ID" span={3}>{application.user_id}</Descriptions.Item>
                    <Descriptions.Item label="Status">
                        <Tag color={statusColor}>{application.status.toUpperCase()}</Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="Endorsements">{application.endorser_count}</Descriptions.Item>
                    <Descriptions.Item label="Submitted Date">
                        {new Date(application.submitted_at).toLocaleString()}
                    </Descriptions.Item>
                </Descriptions>

                <Divider orientation="left">Responses</Divider>

                <div className="application-responses">
                    {application.responses.map((response, index) => (<Card key={index} className="response-card">
                            <div className="question">
                                <Text strong>Q: {response.question_text}</Text>
                            </div>
                            <div className="answer">
                                <Text>A: {response.answer_text}</Text>
                            </div>
                        </Card>))}
                </div>

                {/* Club member actions */}
                {isClubMember && (<>
                        <Divider orientation="left">Actions</Divider>
                        <Space className="application-actions">
                            <Button
                                type="primary"
                                icon={<CheckOutlined/>}
                                onClick={() => handleStatusUpdate('accepted')}
                                loading={actionLoading}
                                disabled={application.status === 'accepted'}
                            >
                                Accept
                            </Button>
                            <Button
                                danger
                                icon={<CloseOutlined/>}
                                onClick={() => handleStatusUpdate('rejected')}
                                loading={actionLoading}
                                disabled={application.status === 'rejected'}
                            >
                                Reject
                            </Button>
                            <Button
                                icon={<LikeOutlined/>}
                                onClick={handleEndorse}
                                loading={actionLoading}
                                disabled={application.endorser_ids.includes(application.user_id)}
                            >
                                Endorse
                            </Button>
                        </Space>
                    </>)}
            </Card>
        </div>);
};

export default ApplicationDetail;