# Worky UI - Project Management Platform

A modern React-based UI for the Worky project management platform with multi-theme support and internationalization.

## Features

✅ **Authentication** - JWT-based login with protected routes
✅ **6 Themes** - Snow, Greenery, Water, Dracula, Dark, Black & White
✅ **2 Languages** - English and Telugu (తెలుగు)
✅ **Dashboard** - Overview with stats and recent tasks
✅ **Project Management** - Clients, Programs, Projects hierarchy
✅ **Task Management** - Full task lifecycle with assignments
✅ **Planning Views** - Gantt Chart, Kanban Board, Sprint Board
✅ **Bug Tracking** - Report and track bugs with severity/priority
✅ **Reports** - Utilization, Engagement, Occupancy forecasts
✅ **User Management** - Admin-only user administration
✅ **Profile** - User preferences and theme/language settings

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development
- **Tailwind CSS** for styling
- **React Router** for navigation
- **Zustand** for state management
- **i18next** for internationalization
- **Axios** for API calls

## Getting Started

### Install Dependencies

```bash
cd ui
npm install
```

### Run Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

## Demo Credentials

- **Email**: admin@datalegos.com
- **Password**: password

## Dummy API Mode

The app currently runs with dummy data (see `src/services/api.ts`). To switch to real API:

1. Set `USE_DUMMY_DATA = false` in `src/services/api.ts`
2. Ensure the backend API is running at `http://localhost:8000`

## Theme System

Themes are CSS-based using CSS variables. Each theme file is in `public/themes/`:

- `snow.css` - Clean white theme
- `greenery.css` - Nature-inspired green theme
- `water.css` - Ocean blue theme
- `dracula.css` - Dark theme with red accents
- `dark.css` - Material dark theme
- `blackwhite.css` - High contrast monochrome

## Internationalization

Translations are in `src/i18n.ts`. Currently supports:
- English (en)
- Telugu (te)

## Project Structure

```
ui/
├── public/
│   └── themes/          # Theme CSS files
├── src/
│   ├── components/
│   │   ├── auth/        # Authentication components
│   │   └── layout/      # Layout components (Sidebar, Header)
│   ├── contexts/        # React contexts (Auth, Theme, Language)
│   ├── pages/           # Page components
│   ├── services/        # API service layer
│   ├── App.tsx          # Main app component
│   ├── i18n.ts          # Internationalization config
│   └── main.tsx         # Entry point
├── package.json
├── vite.config.ts
└── tailwind.config.js
```

## Available Pages

- `/login` - Login page
- `/dashboard` - Dashboard with stats
- `/clients` - Client management
- `/projects` - Project list and details
- `/tasks` - Task management
- `/gantt` - Gantt chart view
- `/kanban` - Kanban board
- `/sprint` - Sprint board
- `/bugs` - Bug tracking
- `/reports` - Report generation
- `/users` - User management (Admin only)
- `/profile` - User profile and preferences

## Next Steps

To connect to a real backend:

1. Implement the FastAPI backend (see `../api/`)
2. Update `USE_DUMMY_DATA` flag in `src/services/api.ts`
3. Configure proper authentication endpoints
4. Add real-time updates with WebSockets
5. Implement drag-and-drop for Kanban board
6. Add chart libraries for Gantt and reports
7. Implement file upload for documentation

## Notes

This is a functional UI prototype with dummy data to demonstrate the flow and user experience. All interactive elements are in place, and the theme/language switching works in real-time.
