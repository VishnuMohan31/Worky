# Worky UI Developer Guide

## 🚀 Quick Start

### Installation
```bash
cd ui
npm install
npm run dev
```

The application will be available at `http://localhost:5173`

---

## 📁 Project Structure

```
ui/src/
├── components/          # Reusable UI components
│   ├── auth/           # Authentication components
│   ├── common/         # Common components (Modal, etc.)
│   ├── forms/          # Form components
│   └── layout/         # Layout components
├── contexts/           # React contexts (Auth, Theme, Language)
├── hooks/              # Custom React hooks
├── lib/                # Library configurations
├── pages/              # Page components
├── services/           # API services
├── stores/             # Zustand stores
├── types/              # TypeScript type definitions
├── App.tsx             # Main app component
├── main.tsx            # Entry point
└── index.css           # Global styles
```

---

## 🎨 Core Technologies

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Routing
- **React Query** - Data fetching & caching
- **Zustand** - State management
- **Axios** - HTTP client
- **i18next** - Internationalization

---

## 🔧 Key Patterns

### 1. Data Fetching with React Query

```typescript
import { useEntity } from '../hooks/useEntity'

function ProjectDetail({ id }: { id: string }) {
  const { data: project, isLoading, error } = useEntity('project', id)
  
  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>
  
  return <div>{project.name}</div>
}
```

### 2. Creating Entities

```typescript
import { useCreateEntity } from '../hooks/useEntity'

function CreateProject() {
  const createProject = useCreateEntity('project')
  
  const handleSubmit = async (data) => {
    await createProject.mutateAsync(data)
    // Cache is automatically invalidated
  }
  
  return <EntityForm onSubmit={handleSubmit} />
}
```

### 3. State Management with Zustand

```typescript
import { useHierarchyStore } from '../stores/hierarchyStore'

function HierarchyNav() {
  const { currentEntity, setCurrentEntity } = useHierarchyStore()
  
  return (
    <div>
      Current: {currentEntity?.name}
    </div>
  )
}
```

### 4. Using Forms

```typescript
import EntityForm from '../components/forms/EntityForm'
import Modal from '../components/common/Modal'

function CreateEntityModal({ isOpen, onClose, entityType }) {
  const createEntity = useCreateEntity(entityType)
  
  const handleSubmit = async (data) => {
    await createEntity.mutateAsync(data)
    onClose()
  }
  
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Create ${entityType}`}>
      <EntityForm
        onSubmit={handleSubmit}
        onCancel={onClose}
        entityType={entityType}
        isLoading={createEntity.isPending}
      />
    </Modal>
  )
}
```

---

## 🌐 API Service

### Using the API Service

```typescript
import api from '../services/api'

// Get entity
const project = await api.getEntity('project', 'proj-1')

// List entities
const projects = await api.getEntityList('project', { status: 'Active' })

// Create entity
const newProject = await api.createEntity('project', {
  name: 'New Project',
  status: 'Planning'
})

// Update entity
const updated = await api.updateEntity('project', 'proj-1', {
  status: 'In Progress'
})

// Delete entity
await api.deleteEntity('project', 'proj-1')

// Search
const results = await api.searchEntities('authentication')

// Get statistics
const stats = await api.getEntityStatistics('project', 'proj-1')
```

### Dummy Data Mode

Toggle between dummy data and real API:

```typescript
// In api.ts
const USE_DUMMY_DATA = true // Set to false for real API
```

---

## 🎯 Entity Types

Supported entity types:
- `client` - Top-level organization
- `program` - Collection of projects
- `project` - Specific initiative
- `usecase` - Functional requirement
- `userstory` - User-centric feature
- `task` - Unit of work
- `subtask` - Smaller work item

---

## 📝 TypeScript Types

All types are defined in `src/types/entities.ts`:

```typescript
import { Project, Task, EntityFormData } from '../types/entities'

const project: Project = {
  id: 'proj-1',
  name: 'My Project',
  status: 'In Progress',
  // ... other fields
}
```

---

## 🎨 Theming

Six themes available:
- Snow (light)
- Greenery (green-based)
- Water (blue-based)
- Dracula (red and black)
- Dark
- Black & White

```typescript
import { useTheme } from '../contexts/ThemeContext'

function ThemeSwitcher() {
  const { theme, setTheme } = useTheme()
  
  return (
    <select value={theme} onChange={(e) => setTheme(e.target.value)}>
      <option value="snow">Snow</option>
      <option value="dark">Dark</option>
      {/* ... other themes */}
    </select>
  )
}
```

---

## 🌍 Internationalization

Supported languages:
- English (en)
- Telugu (te)

```typescript
import { useTranslation } from 'react-i18next'

function MyComponent() {
  const { t, i18n } = useTranslation()
  
  return (
    <div>
      <h1>{t('welcome')}</h1>
      <button onClick={() => i18n.changeLanguage('te')}>
        Switch to Telugu
      </button>
    </div>
  )
}
```

---

## 🔐 Authentication

```typescript
import { useAuth } from '../contexts/AuthContext'

function ProtectedComponent() {
  const { user, logout } = useAuth()
  
  if (!user) return <Navigate to="/login" />
  
  return (
    <div>
      Welcome, {user.fullName}
      <button onClick={logout}>Logout</button>
    </div>
  )
}
```

---

## 🧪 Development Tools

### React Query DevTools

Automatically available in development mode. Press the React Query icon in the bottom-right corner to open.

### Zustand DevTools

Install Redux DevTools extension to inspect Zustand state.

---

## 📦 Adding New Components

### 1. Create Component

```typescript
// src/components/myfeature/MyComponent.tsx
export default function MyComponent() {
  return <div>My Component</div>
}
```

### 2. Add Route (if needed)

```typescript
// src/App.tsx
import MyComponent from './components/myfeature/MyComponent'

<Route path="myfeature" element={<MyComponent />} />
```

### 3. Add to Navigation (if needed)

```typescript
// src/components/layout/DashboardLayout.tsx
// Add navigation link
```

---

## 🐛 Debugging

### Check API Calls

```typescript
// Enable axios logging
apiClient.interceptors.request.use(config => {
  console.log('API Request:', config)
  return config
})
```

### Check React Query Cache

Use React Query DevTools to inspect:
- Cached queries
- Query states
- Mutations
- Cache invalidation

### Check Zustand State

Use Redux DevTools to inspect:
- Current state
- State changes
- Actions dispatched

---

## 🚀 Building for Production

```bash
# Build
npm run build

# Preview build
npm run preview
```

Build output will be in `dist/` directory.

---

## 📚 Best Practices

### 1. Always Use TypeScript Types

```typescript
// ✅ Good
const project: Project = await api.getEntity('project', id)

// ❌ Bad
const project = await api.getEntity('project', id)
```

### 2. Use React Query for Server State

```typescript
// ✅ Good - Automatic caching and refetching
const { data } = useEntity('project', id)

// ❌ Bad - Manual state management
const [project, setProject] = useState(null)
useEffect(() => {
  api.getEntity('project', id).then(setProject)
}, [id])
```

### 3. Use Zustand for UI State

```typescript
// ✅ Good - For UI state like navigation
const { currentEntity } = useHierarchyStore()

// ❌ Bad - Don't use for server data
const { projects } = useProjectStore() // Use React Query instead
```

### 4. Reuse Components

```typescript
// ✅ Good - Use generic components
<EntityForm entityType="project" />

// ❌ Bad - Don't create duplicate forms
<ProjectForm />
<TaskForm />
<BugForm />
```

### 5. Handle Loading and Error States

```typescript
// ✅ Good
const { data, isLoading, error } = useEntity('project', id)

if (isLoading) return <Spinner />
if (error) return <ErrorMessage error={error} />
return <ProjectView project={data} />

// ❌ Bad
const { data } = useEntity('project', id)
return <ProjectView project={data} /> // Might be undefined!
```

---

## 🆘 Common Issues

### Issue: "Module not found"
**Solution**: Run `npm install` to install dependencies

### Issue: "Type errors"
**Solution**: Check `src/types/entities.ts` for correct types

### Issue: "API not responding"
**Solution**: 
1. Check if API is running on port 8007
2. Or set `USE_DUMMY_DATA = true` in `api.ts`

### Issue: "React Query not working"
**Solution**: Ensure `QueryClientProvider` wraps your app in `App.tsx`

### Issue: "Zustand state not persisting"
**Solution**: Check browser localStorage is enabled

---

## 📞 Need Help?

- Check the consolidated task list: `.kiro/specs/consolidated-ui-tasks.md`
- Review Phase 1 completion: `.kiro/specs/PHASE_1_COMPLETION_SUMMARY.md`
- Check component examples in `src/components/`
- Review existing pages in `src/pages/`

---

## 🎉 Happy Coding!

You now have a solid foundation to build amazing features!
