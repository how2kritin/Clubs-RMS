import React, {useEffect, useState} from 'react';
import {useNavigate, useParams} from 'react-router-dom';
import {Alert, Button, Card, Descriptions, Divider, message, Modal, Space, Tag, Typography} from 'antd';
import {
    CheckOutlined, CloseOutlined, DeleteOutlined, DislikeOutlined, LikeOutlined, RollbackOutlined
} from '@ant-design/icons';
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
    const [endorseActionLoading, setEndorseActionLoading] = useState<boolean>(false);
    const [isClubMember, setIsClubMember] = useState<boolean>(false);
    const [isClubAdmin, setIsClubAdmin] = useState<boolean>(false);
    const [currentUserId, setCurrentUserId] = useState<string>('');
    const [isDeleteModalVisible, setIsDeleteModalVisible] = useState<boolean>(false);
    const [statusUpdateError, setStatusUpdateError] = useState<string | null>(null);

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

            const clubAdminResponse = await fetch(`/api/user/user_role/${data.club_id}`, {
                credentials: "include",
            },);

            if (clubAdminResponse.ok) {
                const adminData = await clubAdminResponse.json();
                setIsClubAdmin(adminData.is_admin);
            }

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

    useEffect(() => {
        if (applicationId) {
            fetchApplicationDetail();
        }
    }, [applicationId]);

    const handleStatusUpdate = async (newStatus: string) => {
        try {
            setActionLoading(true);
            setStatusUpdateError(null);

            const response = await fetch(`/api/application/${applicationId}/status`, {
                method: 'PUT', headers: {
                    'Content-Type': 'application/json',
                }, body: JSON.stringify({
                    status: newStatus
                }),
            });

            // Parse the response for detailed error messages
            const responseData = await response.json();

            if (!response.ok) {
                // Handle specific error cases
                if (response.status === 400) {
                    if (responseData.detail) {
                        setStatusUpdateError(responseData.detail);
                        throw new Error(responseData.detail);
                    } else {
                        throw new Error(`Bad Request: ${response.statusText}`);
                    }
                } else {
                    throw new Error(`Failed to update status: ${response.statusText}`);
                }
            }

            message.success(`Application ${newStatus} successfully!`);
            await fetchApplicationDetail();
        } catch (err) {
            console.error('Error updating application status:', err);
            const errorMessage = err instanceof Error ? err.message : 'Failed to update status';
            setStatusUpdateError(errorMessage);
            message.error(errorMessage);
        } finally {
            setActionLoading(false);
        }
    };

    const handleEndorse = async () => {
        try {
            setEndorseActionLoading(true);
            const response = await fetch(`/api/application/${applicationId}/endorse`, {
                method: 'PUT',
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Failed to endorse application: ${response.statusText}`);
            }

            message.success('Application endorsed successfully');
            await fetchApplicationDetail();
        } catch (err) {
            console.error('Error endorsing application:', err);
            message.error(err instanceof Error ? err.message : 'Failed to endorse application');
        } finally {
            setEndorseActionLoading(false);
        }
    };

    const handleWithdrawEndorsement = async () => {
        try {
            setEndorseActionLoading(true);
            const response = await fetch(`/api/application/${applicationId}/withdraw-endorsement`, {
                method: 'PUT',
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Failed to withdraw endorsement: ${response.statusText}`);
            }

            message.success('Endorsement withdrawn successfully');
            await fetchApplicationDetail();
        } catch (err) {
            console.error('Error withdrawing endorsement:', err);
            message.error(err instanceof Error ? err.message : 'Failed to withdraw endorsement');
        } finally {
            setEndorseActionLoading(false);
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
                const errorData = await response.json();
                throw new Error(errorData.detail || `Failed to delete application: ${response.statusText}`);
            }

            message.success('Application deleted successfully');
            setIsDeleteModalVisible(false);
            navigate('/my-applications');
        } catch (err) {
            console.error('Error deleting application:', err);
            message.error(err instanceof Error ? err.message : 'Failed to delete application');
            setIsDeleteModalVisible(false);
        } finally {
            setActionLoading(false);
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

    // Check if the current user has already endorsed this application
    const hasEndorsed = application.endorser_ids?.includes(currentUserId) || false;

    return (<div className="application-detail-container">
            <Card className="application-detail-card">
                <div className="application-detail-header">
                    <Space>
                        <Button
                            icon={<RollbackOutlined/>}
                            onClick={() => navigate(-1)}
                        >
                            Back to Applications
                        </Button>
                    </Space>
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

                {statusUpdateError && (<Alert
                        message="Status Update Error"
                        description={statusUpdateError}
                        type="error"
                        showIcon
                        closable
                        className="status-update-error"
                        onClose={() => setStatusUpdateError(null)}
                        style={{marginTop: '16px', marginBottom: '16px'}}
                    />)}

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
                            {isClubAdmin && (<><Button
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
                            </Button></>)}

                            {hasEndorsed ? (<Button
                                    danger
                                    icon={<DislikeOutlined/>}
                                    onClick={handleWithdrawEndorsement}
                                    loading={endorseActionLoading}
                                >
                                    Withdraw Endorsement
                                </Button>) : (<Button
                                    type="default"
                                    icon={<LikeOutlined/>}
                                    onClick={handleEndorse}
                                    loading={endorseActionLoading}
                                >
                                    Endorse
                                </Button>)}
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