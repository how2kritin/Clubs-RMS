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
