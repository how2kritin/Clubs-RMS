# SE-project-3

## Run Instructions

### Backend

Build the container and run it:
```bash
docker compose up --build
```

To open a shell in the container, run

```bash
docker compose exec backend /bin/bash
```

### Frontend

Install dependencies:

```bash
npm i
```

Start the website:
```bash
npx vite
```

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