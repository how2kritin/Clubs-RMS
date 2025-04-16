import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Table, Tag, Button, Alert, Typography, Card } from 'antd';
import { EyeOutlined } from '@ant-design/icons';
import './FormApplicationsOverview.css';

const { Title } = Typography;

interface Application {
  id: number;
  user_id: string;
  user_name: string;
  user_email: string;
  form_id: number;
  form_name: string;
  status: string;
  endorser_ids: string[];
  endorser_count: number;
  submitted_at: string;
}


const FormApplicationsOverview: React.FC = () => {
  const { formId } = useParams<{ formId: string }>();
  const navigate = useNavigate();
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [formTitle, setFormTitle] = useState<string>('');

  useEffect(() => {
    const fetchFormAndApplications = async () => {
      try {
        setLoading(true);

        // First fetch the form details to get the title
        const formResponse = await fetch(`/api/recruitment/forms/${formId}`);
        if (!formResponse.ok) {
          throw new Error(`Failed to fetch form: ${formResponse.statusText}`);
        }
        const formData = await formResponse.json();
        setFormTitle(formData.name);

        // Then fetch the applications for this form - this is a new endpoint we need
        const applicationsResponse = await fetch(`/api/application/form/${formId}`);
        if (!applicationsResponse.ok) {
          throw new Error(`Failed to fetch applications: ${applicationsResponse.statusText}`);
        }
        const applicationsData = await applicationsResponse.json();
        setApplications(applicationsData);

        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err instanceof Error ? err.message : 'An error occurred');
        setLoading(false);
      }
    };

    if (formId) {
      fetchFormAndApplications();
    }
  }, [formId]);

  const columns = [
    {
      title: 'Applicant',
      dataIndex: 'user_name',
      key: 'user_name',
    },
    {
      title: 'Email',
      dataIndex: 'user_email',
      key: 'user_email',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const color =
          status === 'ongoing' ? 'gold' :
          status === 'accepted' ? 'green' :
          status === 'rejected' ? 'red' : 'blue';

        return <Tag color={color}>{status.toUpperCase()}</Tag>;
      },
    },
    {
      title: 'Endorsements',
      dataIndex: 'endorser_count',
      key: 'endorser_count',
    },
    {
      title: 'Submitted At',
      dataIndex: 'submitted_at',
      key: 'submitted_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: Application) => (
        <Button
          type="primary"
          icon={<EyeOutlined />}
          size="small"
          onClick={() => navigate(`/forms/${formId}/applications/${record.id}`)}
        >
          View
        </Button>
      ),
    },
  ];

  if (loading) {
    return <div className="loading">Loading applications...</div>;
  }

  if (error) {
    return <Alert message={error} type="error" />;
  }

  return (
    <div className="form-applications-container">
      <Card className="form-applications-card">
        <div className="form-applications-header">
          <Title level={2}>Applications for: {formTitle}</Title>
          <Button
            type="primary"
            onClick={() => navigate(`/form/${formId}`)}
          >
            Back to Form
          </Button>
        </div>

        {applications.length === 0 ? (
          <Alert
            message="No applications found"
            description="There are no applications submitted for this form yet."
            type="info"
          />
        ) : (
          <Table
            dataSource={applications}
            columns={columns}
            rowKey="id"
            pagination={{ pageSize: 10 }}
          />
        )}
      </Card>
    </div>
  );
};

export default FormApplicationsOverview;