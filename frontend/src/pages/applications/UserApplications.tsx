import React, {useEffect, useState} from 'react';
import {Alert, Button, Card, Table, Tag, Typography} from 'antd';
import {EyeOutlined} from '@ant-design/icons';
import {useNavigate} from 'react-router-dom';
import './UserApplications.css';

const {Title} = Typography;

interface UserApplication {
    id: number;
    form_id: number;
    form_name: string;
    club_id: string;
    club_name: string;
    status: string;
    endorser_ids: string[];
    endorser_count: number;
    submitted_at: string;
}

const UserApplications: React.FC = () => {
    const navigate = useNavigate();
    const [applications, setApplications] = useState<UserApplication[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchUserApplications = async () => {
            try {
                setLoading(true);
                const response = await fetch('/api/application/user');

                if (!response.ok) {
                    throw new Error(`Failed to fetch applications: ${response.statusText}`);
                }

                const data = await response.json();
                setApplications(data);
                setLoading(false);
            } catch (err) {
                console.error('Error fetching user applications:', err);
                setError(err instanceof Error ? err.message : 'An error occurred');
                setLoading(false);
            }
        };

        fetchUserApplications();
    }, []);

    console.log(applications)

    const columns = [{
        title: 'Club', dataIndex: 'club_name', key: 'club_name',
    }, {
        title: 'Form', dataIndex: 'form_name', key: 'form_name',
    }, {
        title: 'Status', dataIndex: 'status', key: 'status', render: (status: string) => {
            const color = status === 'ongoing' ? 'gold' : status === 'accepted' ? 'green' : status === 'rejected' ? 'red' : 'blue';

            return <Tag color={color}>{status.toUpperCase()}</Tag>;
        },
    }, {
        title: 'Endorsements', dataIndex: 'endorser_count', key: 'endorser_count',
    }, {
        title: 'Submitted At',
        dataIndex: 'submitted_at',
        key: 'submitted_at',
        render: (date: string) => new Date(date).toLocaleString(),
    }, {
        title: 'Actions', key: 'actions', render: (_: any, record: UserApplication) => (<Button
                type="primary"
                icon={<EyeOutlined/>}
                size="small"
                onClick={() => navigate(`/forms/${record.form_id}/applications/${record.id}`)}
            >
                View
            </Button>),
    },];

    if (loading) {
        return <div className="loading">Loading your applications...</div>;
    }

    if (error) {
        return <Alert message={error} type="error"/>;
    }

    return (<div className="user-applications-container">
            <Card className="user-applications-card">
                <Title level={2}>My Applications</Title>

                {applications.length === 0 ? (<Alert
                        message="No applications found"
                        description="You haven't submitted any applications yet."
                        type="info"
                    />) : (<Table
                        dataSource={applications}
                        columns={columns}
                        rowKey="id"
                        pagination={{pageSize: 10}}
                    />)}
            </Card>
        </div>);
};

export default UserApplications;