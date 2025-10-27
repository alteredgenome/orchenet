# OrcheNet Frontend

React-based web interface for OrcheNet network device orchestration platform.

## Setup

1. Install dependencies:
```bash
npm install
# or
pnpm install
```

2. Create `.env` file:
```
VITE_API_URL=http://localhost:8000
```

3. Run development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Project Structure

```
frontend/
├── src/
│   ├── components/    # Reusable UI components
│   ├── views/         # Page components
│   ├── stores/        # State management
│   ├── services/      # API services
│   ├── App.jsx        # Main application component
│   └── main.jsx       # Entry point
├── index.html         # HTML template
├── vite.config.js     # Vite configuration
└── package.json       # Dependencies
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Development

The frontend communicates with the backend API running on port 8000. Make sure the backend is running before starting the frontend.

API calls are proxied through Vite's dev server to avoid CORS issues during development.
