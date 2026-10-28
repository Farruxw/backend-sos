# Smart SOS Frontend

Production-oriented React frontend for the FastAPI Smart SOS backend in the parent directory.

## Requirements

- Node.js 20+
- FastAPI backend running on port 8000

## Run

```bash
cd smart-sos-backend-py/frontend
npm install
cp .env.example .env
npm run dev
```

Open the URL printed by Vite, normally `http://localhost:5173`.

Build:

```bash
npm run build
npm run preview
```

## Backend configuration

```env
VITE_API_BASE_URL=http://localhost:8000
```

The frontend is integrated with the following real endpoints:

- `POST /api/calls`
- `GET /api/calls/active`
- `GET /api/calls/{id}`
- `POST /api/calls/{id}/assign`
- `POST /api/calls/{id}/reassign`
- `POST /api/calls/{id}/arrive`
- `POST /api/calls/{id}/done`
- `POST /api/calls/{id}/cancel`
- `GET /api/chat/{specialty}`
- `POST /api/chat/{specialty}`

## Backend gaps

The current backend does not expose these interfaces, so the frontend does not fabricate data for them:

- Authentication, registration, SMS verification, sessions, users, roles, or profiles
- Unit listing, unit details, team members, vehicles, or unit location updates
- Admin statistics, charts, audit logs, CSV export, and user/unit management
- Real-time WebSocket/SSE updates
- Separate doctor speciality data and medication catalog
- Medical profile and emergency contacts persistence

Live call polling is used as a practical alternative to WebSocket. Assignment selects a nearest available unit through the real backend dispatch endpoint.

## AI safety

Medical chat clearly states that it is an AI assistant, not a medical diagnosis or replacement for a real professional. AI conclusions are backend-generated or backend fallback-rule output; the frontend does not create fabricated AI results.
