import React, {useEffect, useState} from 'react';
import {useNavigate, useParams} from 'react-router-dom';
import {Alert, Button, Card, Descriptions, Divider, Modal, Space, Tag, Typography} from 'antd';
import {CheckOutlined, CloseOutlined, DeleteOutlined, LikeOutlined, RollbackOutlined} from '@ant-design/icons';
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
    user_email: string;
    is_club_member: boolean;
}

const ApplicationDetail: React.FC = () => {
    const {formId, applicationId} = useParams<{ formId: string, applicationId: string }>();
    const navigate = useNavigate();
    const [application, setApplication] = useState<ApplicationDetail | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [actionLoading, setActionLoading] = useState<boolean>(false);
    const [isClubMember, setIsClubMember] = useState<boolean>(false);
    const [currentUserId, setCurrentUserId] = useState<string>('');
    const [isDeleteModalVisible, setIsDeleteModalVisible] = useState<boolean>(false);

    useEffect(() => {
        const fetchApplicationDetail = async () => {
            try {
                setLoading(true);

                // Fetch application details
                const response = await fetch(`/api/application/${applicationId}`);
                if (!response.ok) {
                    throw new Error(`Failed to fetch application: ${response.statusText}`);
                }

                const data = await response.json();
                setApplication(data);
                setIsClubMember(data?.is_club_member);

                // Get current user information to check if they're the applicant
                const userInfoResponse = await fetch('/api/application/autofill-details');
                if (userInfoResponse.ok) {
                    const userData = await userInfoResponse.json();
                    setCurrentUserId(userData.user_id);
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
            const response = await fetch(`/api/application/${applicationId}/status`, {
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
            const updatedApp = await fetch(`/api/application/${applicationId}`);
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
            const response = await fetch(`/api/application/${applicationId}/endorse`, {
                method: 'PUT',
            });

            if (!response.ok) {
                throw new Error(`Failed to endorse application: ${response.statusText}`);
            }

            // Refresh application data after endorsement
            const updatedApp = await fetch(`/api/application/${applicationId}`);
            const updatedData = await updatedApp.json();
            setApplication(updatedData);
            setActionLoading(false);
        } catch (err) {
            console.error('Error endorsing application:', err);
            setError(err instanceof Error ? err.message : 'An error occurred');
            setActionLoading(false);
        }
    };

    const showDeleteConfirm = () => {
        setIsDeleteModalVisible(true);
    };

    const handleDeleteConfirm = async () => {
        try {
            setActionLoading(true);
            const response = await fetch(`/api/application/${applicationId}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                throw new Error(`Failed to delete application: ${response.statusText}`);
            }

            setIsDeleteModalVisible(false);
            // Navigate back to my applications page
            navigate('/my-applications');
        } catch (err) {
            console.error('Error deleting application:', err);
            setError(err instanceof Error ? err.message : 'An error occurred');
            setActionLoading(false);
            setIsDeleteModalVisible(false);
        }
    };

    const handleDeleteCancel = () => {
        setIsDeleteModalVisible(false);
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

    // Check if current user is the application creator and if application is ongoing
    const isApplicationCreator = currentUserId === application.user_id;
    const isOngoing = application.status === 'ongoing';
    const canDelete = isApplicationCreator && isOngoing;

    return (<div className="application-detail-container">
            <Card className="application-detail-card">
                <div className="application-detail-header">
                    <Button
                        icon={<RollbackOutlined/>}
                        onClick={() => navigate(-1)}
                    >
                        Back to Applications
                    </Button>
                </div>

                <Title level={2}>Application Details</Title>
                <Descriptions bordered column={3} className="application-info">
                    <Descriptions.Item label="Form" span={3}>{application.form_name}</Descriptions.Item>
                    <Descriptions.Item label="Applicant ID" span={3}>{application.user_id}</Descriptions.Item>
                    <Descriptions.Item label="Email" span={2}>{application.user_email}</Descriptions.Item>
                    <Descriptions.Item label="Status" span={1}>
                        <Tag color={statusColor}>{application.status.toUpperCase()}</Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="Endorsements" span={1}>{application.endorser_count}</Descriptions.Item>
                    <Descriptions.Item label="Submitted Date" span={2}>
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
                        <Divider orientation="left">Club Member Actions</Divider>
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
                                disabled={application.endorser_ids.includes(currentUserId)}
                            >
                                Endorse
                            </Button>
                        </Space>
                    </>)}

                {/* Application creator actions */}
                {canDelete && (<>
                        <Divider orientation="left">Applicant Actions</Divider>
                        <Space className="application-actions">
                            <Button
                                danger
                                icon={<DeleteOutlined/>}
                                onClick={showDeleteConfirm}
                                loading={actionLoading}
                            >
                                Delete Application
                            </Button>
                        </Space>
                    </>)}
            </Card>

            {/* Delete confirmation modal */}
            <Modal
                title="Delete Application"
                open={isDeleteModalVisible}
                onOk={handleDeleteConfirm}
                onCancel={handleDeleteCancel}
                okText="Yes, Delete"
                cancelText="Cancel"
                okButtonProps={{danger: true, loading: actionLoading}}
            >
                <p>Are you sure you want to delete this application?</p>
                <p>This action cannot be undone.</p>
            </Modal>
        </div>);
};

export default ApplicationDetail;