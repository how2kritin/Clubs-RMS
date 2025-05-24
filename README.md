# SE-project-3 : Clubs++@IIITH

## Overview

**Clubs++@IIITH** is a full-stack web application featuring a React + TypeScript + Vite frontend and a Python FastAPI backend. The system supports user authentication, club management, application processing, event calendars, recommendations, and interview scheduling — all with role-based access control for different user roles (non-member, club member, club admin).

---

## Features

- **User Authentication & Profile Management**
  - Login, logout, profile update, and view user info.
  - Role and club membership queries.

- **Club Management**
  - View all clubs, specific club info, subscribe/unsubscribe to clubs.
  - Check and manage club subscriptions.

- **Applications**
  - Submit applications, auto-fill details, check application status.
  - Club-based application review and endorsement.
  - Delete or withdraw applications.

- **Recruitment Forms**
  - Club admins can create, update, or delete recruitment forms.
  - Applicants can access and submit forms; clubs can view applicants.

- **Calendar**
  - View personal and club events.

- **Recommendations**
  - Personalized club recommendations.

- **Interviews**
  - Club admins can schedule interviews.

- **API Documentation**
  - Full API documentation available at the backend `/docs` route.

---

## Tech Stack

- **Frontend:** React, TypeScript, Vite, Ant Design, TailwindCSS, Axios, FullCalendar, Framer Motion
- **Backend:** Python 3.12, FastAPI, Uvicorn, SQLAlchemy, PostgreSQL (implied by psycopg2-binary), LDAP integration, JWT-based auth
- **DevOps:** Docker, Docker Compose

---

## Instructions to Run

### Prerequisites

- Docker & Docker Compose installed
- Node.js and npm (for local frontend development)

### Backend

Build and run everything using Docker Compose:

```bash
docker compose up --build
```

To get a shell in the backend container:

```bash
docker compose exec backend /bin/bash
```

To view API documentation, go to:  
`http://localhost:<backend-port>/docs`

### Frontend

For local development (from the `frontend` directory):

1. Install dependencies:

   ```bash
   npm i
   ```

2. Start the development server:

   ```bash
   npx vite
   ```

   The site will be available at `http://localhost:5173` (default Vite port).

---

## Project Structure (simplified)

```
SE-project-3/
├── backend/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── ... (FastAPI app code)
├── frontend/
│   ├── package.json
│   └── ... (React/Vite code)
├── README.md
└── ... (other files)
```

---

## Further Information

- For advanced configuration and deployment, see `backend/Dockerfile` and frontend scripts in `package.json`.
- The frontend uses Vite + TypeScript + React with TailwindCSS.
- The backend Dockerfile sets up a Python virtual environment and runs FastAPI with Uvicorn in reload mode for rapid development.

---

## Contribution

- Fork the repository and create a pull request for contributions.
- Please ensure code is linted and tested before submitting.

---

## Backend API Route Access Control Matrix

### Visit the backend `/docs` route to view all the API endpoints available.

| Resource/Endpoint                                          | Non-Member (Authenticated)                  | Club Member                   | Club Admin                    | Anonymous |
|------------------------------------------------------------|---------------------------------------------|-------------------------------|-------------------------------|-----------|
| **General**                                                |                                             |                               |                               |           |
| GET /                                                      | ✓                                           | ✓                             | ✓                             | ✓         |
|                                                            |                                             |                               |                               |           |
| **User Authentication & Profile**                          |                                             |                               |                               |           |
| POST /api/user/login                                       | ✓                                           | ✓                             | ✓                             | ✓         |
| GET /api/user/login                                        | ✓                                           | ✓                             | ✓                             | ✓         |
| GET /api/user/user_info                                    | ✓                                           | ✓                             | ✓                             | ✗         |
| GET /api/user/user_role/{club_id}                          | ✓                                           | ✓                             | ✓                             | ✗         |
| GET /api/user/user_club_info                               | ✓                                           | ✓                             | ✓                             | ✗         |
| GET /api/user/is_authenticated                             | ✓                                           | ✓                             | ✓                             | ✓         |
| POST /api/user/logout                                      | ✓                                           | ✓                             | ✓                             | ✗         |
| PUT /api/user/update_profile                               | ✓                                           | ✓                             | ✓                             | ✗         |
|                                                            |                                             |                               |                               |           |
| **Clubs**                                                  |                                             |                               |                               |           |
| GET /api/club/all_clubs                                    | ✓                                           | ✓                             | ✓                             | ✓         |
| GET /api/club/{cid}                                        | ✓                                           | ✓                             | ✓                             | ✓         |
| GET /api/club/is_subscribed/{cid}                          | ✓                                           | ✓                             | ✓                             | ✗         |
| POST /api/club/subscribe/{cid}                             | ✓                                           | ✓                             | ✓                             | ✗         |
| POST /api/club/unsubscribe/{cid}                           | ✓                                           | ✓                             | ✓                             | ✗         |
|                                                            |                                             |                               |                               |           |
| **Applications**                                           |                                             |                               |                               |           |
| GET /api/application/autofill-details                      | ✓                                           | ✓                             | ✓                             | ✗         |
| POST /api/application/submit-application                   | ✓                                           | ✓ (other clubs), ✗ (own club) | ✓ (other clubs), ✗ (own club) | ✗         |
| GET /api/application/form/{form_id}                        | ✗                                           | ✓ (own club)                  | ✓ (own club)                  | ✗         |
| GET /api/application/user                                  | ✓                                           | ✓                             | ✓                             | ✗         |
| GET /api/application/{application_id}/status               | ✓ (if applicant)                            | ✓ (own club)                  | ✓ (own club)                  | ✗         |
| PUT /api/application/{application_id}/status               | ✗                                           | ✗                             | ✓ (own club)                  | ✗         |
| GET /api/application/{application_id}                      | ✓ (if applicant)                            | ✓ (own club)                  | ✓ (own club)                  | ✗         |
| DELETE /api/application/{application_id}                   | ✓ (if applicant, before approval/rejection) | ✗                             | ✗                             | ✗         |
| PUT /api/application/{application_id}/endorse              | ✗                                           | ✓ (own club)                  | ✓ (own club)                  | ✗         |
| PUT /api/application/{application_id}/withdraw-endorsement | ✗                                           | ✓ (if endorsed)               | ✓ (if endorsed)               | ✗         |
|                                                            |                                             |                               |                               |           |
| **Recruitment Forms**                                      |                                             |                               |                               |           |
| POST /api/recruitment/forms                                | ✗                                           | ✗                             | ✓ (own club)                  | ✗         |
| GET /api/recruitment/forms/club/{club_id}                  | ✓                                           | ✓                             | ✓                             | ✓         |
| GET /api/recruitment/forms/{form_id}                       | ✓                                           | ✓                             | ✓                             | ✓         |
| PUT /api/recruitment/forms/{form_id}                       | ✗                                           | ✓ (own club)                  | ✓ (own club)                  | ✗         |
| DELETE /api/recruitment/forms/{form_id}                    | ✗                                           | ✗                             | ✓ (own club)                  | ✗         |
| GET /api/recruitment/forms/{form_id}/applicants/emails     | ✗                                           | ✓ (own club)                  | ✓ (own club)                  | ✗         |
|                                                            |                                             |                               |                               |           |
| **Calendar**                                               |                                             |                               |                               |           |
| GET /api/calendar/events                                   | ✓ (own events)                              | ✓ (own + club)                | ✓ (own + club)                | ✗         |
|                                                            |                                             |                               |                               |           |
| **Recommendations**                                        |                                             |                               |                               |           |
| GET /api/recommendations/clubs                             | ✓                                           | ✓                             | ✓                             | ✗         |
|                                                            |                                             |                               |                               |           |
| **Interviews**                                             |                                             |                               |                               |           |
| POST /api/interviews/schedule_interviews                   | ✗                                           | ✗                             | ✓ (own club)                  | ✗         |
