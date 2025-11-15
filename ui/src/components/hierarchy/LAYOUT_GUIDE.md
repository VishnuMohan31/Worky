# Hierarchy Navigation - Responsive Layout Guide

## Visual Layout Reference

### Desktop Layout (≥ 1024px)
```
┌─────────────────────────────────────────────────────────────────┐
│ Breadcrumb: Client > Program > Project > Use Case              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌────────────────────┐  ┌──────────┐          │
│  │          │  │                    │  │          │          │
│  │  Parent  │  │      Current       │  │ Children │          │
│  │  Pane    │  │      Entity        │  │  Pane    │          │
│  │          │  │                    │  │          │          │
│  │  [Card]  │  │  ┌──────────────┐ │  │  [Card]  │          │
│  │          │  │  │   Details    │ │  │  [Card]  │          │
│  │          │  │  └──────────────┘ │  │  [Card]  │          │
│  │          │  │                    │  │  [Card]  │          │
│  │          │  │  ┌──────────────┐ │  │  [Card]  │          │
│  │          │  │  │  Statistics  │ │  │  [Card]  │          │
│  │          │  │  └──────────────┘ │  │          │          │
│  │          │  │                    │  │          │          │
│  └──────────┘  └────────────────────┘  └──────────┘          │
│                                                                 │
│  250px min     400px min (2x)         250px min               │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**
- Three-column grid layout
- All context visible simultaneously
- Optimal for multitasking
- Maximum productivity

---

### Tablet Layout (768px - 1023px)
```
┌───────────────────────────────────────────────────────┐
│ Breadcrumb: Client > Program > Project > Use Case    │
├───────────────────────────────────────────────────────┤
│                                                       │
│  ┌────────────────────────┐  ┌──────────────┐       │
│  │                        │  │              │       │
│  │      Current           │  │   Children   │       │
│  │      Entity            │  │   Pane       │       │
│  │                        │  │              │       │
│  │  ┌──────────────────┐ │  │   [Card]     │       │
│  │  │    Details       │ │  │   [Card]     │       │
│  │  └──────────────────┘ │  │   [Card]     │       │
│  │                        │  │   [Card]     │       │
│  │  ┌──────────────────┐ │  │   [Card]     │       │
│  │  │   Statistics     │ │  │   [Card]     │       │
│  │  └──────────────────┘ │  │              │       │
│  │                        │  │              │       │
│  └────────────────────────┘  └──────────────┘       │
│                                                       │
│  300px min (2x)              250px min               │
└───────────────────────────────────────────────────────┘
```

**Features:**
- Two-column layout
- Parent hidden (use breadcrumb)
- Balanced view
- Good for focused work

---

### Mobile Layout (≤ 767px)

#### Tab View - Current Entity
```
┌─────────────────────────────────────┐
│ Breadcrumb: ... > Project > Use... │
├─────────────────────────────────────┤
│ [← Parent] [Current] [Children →]  │ ← Mobile Tabs
├─────────────────────────────────────┤
│                                     │
│  ┌───────────────────────────────┐ │
│  │                               │ │
│  │        Entity Details         │ │
│  │                               │ │
│  │  Name: User Authentication    │ │
│  │  Status: In Progress          │ │
│  │  Priority: High               │ │
│  │                               │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │                               │ │
│  │        Statistics             │ │
│  │                               │ │
│  │  ▓▓▓▓▓▓▓▓░░░░ 60%            │ │
│  │                               │ │
│  │  To Do: 5                     │ │
│  │  In Progress: 3               │ │
│  │  Done: 12                     │ │
│  │                               │ │
│  └───────────────────────────────┘ │
│                                     │
│                                     │
│                          ┌────┐    │
│                          │ + │    │ ← FAB
│                          └────┘    │
└─────────────────────────────────────┘
```

#### Tab View - Children List
```
┌─────────────────────────────────────┐
│ Breadcrumb: ... > Project > Use... │
├─────────────────────────────────────┤
│ [← Parent] [Current] [Children →]  │ ← Active Tab
├─────────────────────────────────────┤
│                                     │
│  ┌───────────────────────────────┐ │
│  │ Task 1: Design database       │ │
│  │ Status: Done | Phase: Dev     │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ Task 2: Implement auth        │ │
│  │ Status: In Progress | Dev     │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ Task 3: Create UI mockups     │ │
│  │ Status: To Do | Phase: Design │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ Task 4: Setup CI/CD           │ │
│  │ Status: In Progress | Dev     │ │
│  └───────────────────────────────┘ │
│                                     │
│                          ┌────┐    │
│                          │ + │    │ ← FAB
│                          └────┘    │
└─────────────────────────────────────┘
```

**Features:**
- Single-column layout
- Tab-based navigation
- Full-screen content
- Touch-optimized
- Floating action button

---

### Mobile Landscape (≤ 767px, landscape)
```
┌───────────────────────────────────────────────────────────┐
│ Breadcrumb: ... > Project > Use Case                     │
├───────────────────────────────────────────────────────────┤
│ [← Parent] [Current] [Children →]                        │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────────┐  ┌─────────────────────┐       │
│  │   Entity Details    │  │    Statistics       │       │
│  │                     │  │                     │       │
│  │  Name: Auth         │  │  ▓▓▓▓▓▓░░░░ 60%    │       │
│  │  Status: Active     │  │                     │       │
│  │  Priority: High     │  │  To Do: 5           │  ┌─┐  │
│  │                     │  │  In Progress: 3     │  │+│  │
│  │                     │  │  Done: 12           │  └─┘  │
│  └─────────────────────┘  └─────────────────────┘       │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

**Features:**
- Optimized for landscape
- Reduced padding
- Smaller components
- Better space utilization

---

## Component Breakdown

### Breadcrumb
```
┌─────────────────────────────────────────────────────┐
│ Client > Program > Project > Use Case > User Story │
│ ◄──────────────────────────────────────────────────►│
│                 (scrollable)                        │
└─────────────────────────────────────────────────────┘
```
- Horizontal scrolling
- Clickable items
- Current item highlighted
- Truncated on mobile

### Entity Card
```
┌─────────────────────────────────────┐
│ Task: Implement Authentication      │
│ ─────────────────────────────────── │
│ Status: In Progress  Phase: Dev     │
│ Assigned: John Doe   Due: Jan 20    │
└─────────────────────────────────────┘
```
- Touch-friendly (min 60px height)
- Clear visual hierarchy
- Status badges
- Hover/active states

### Statistics Panel
```
┌─────────────────────────────────────┐
│ Statistics                          │
│ ─────────────────────────────────── │
│                                     │
│ Completion: ▓▓▓▓▓▓▓▓░░░░ 60%       │
│                                     │
│ Status Distribution:                │
│ To Do:        5                     │
│ In Progress:  3                     │
│ Done:        12                     │
│                                     │
│ Phase Distribution:                 │
│ Development:  8                     │
│ Testing:      6                     │
│ Design:       4                     │
└─────────────────────────────────────┘
```
- Collapsible on mobile
- Visual progress bars
- Clear metrics
- Responsive grid

### Mobile Tabs
```
┌─────────────────────────────────────┐
│ [← Parent] [Current] [Children →]  │
│     ─────────────────               │
│         Active Tab                  │
└─────────────────────────────────────┘
```
- Dynamic visibility
- Active state indicator
- Touch-optimized
- Smooth transitions

### Floating Action Button (FAB)
```
                          ┌────┐
                          │ + │
                          └────┘
```
- Fixed bottom-right
- 56x56px (48x48px landscape)
- Primary action
- Mobile only

### Bottom Sheet
```
┌─────────────────────────────────────┐
│                                     │
│         (Backdrop)                  │
│                                     │
│  ┌─────────────────────────────┐   │
│  │         ─────               │   │ ← Handle
│  │                             │   │
│  │    Add New Task             │   │
│  │                             │   │
│  │  [Name Input]               │   │
│  │  [Description Input]        │   │
│  │  [Phase Selector]           │   │
│  │                             │   │
│  │  [Cancel]  [Create]         │   │
│  │                             │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```
- Slides from bottom
- Touch-friendly handle
- Backdrop for focus
- Max height: 80vh

---

## Interaction Patterns

### Desktop
- **Click** to navigate
- **Hover** for previews
- **Keyboard** navigation
- **Scroll** for lists

### Tablet
- **Tap** to navigate
- **Scroll** for lists
- **Swipe** for breadcrumb
- **Long press** for context

### Mobile
- **Tap** to navigate
- **Swipe** tabs (optional)
- **Pull** to refresh (optional)
- **Long press** for actions
- **Pinch** to zoom (optional)

---

## Spacing Guidelines

### Desktop
- Container padding: 16px
- Card padding: 16px
- Gap between columns: 8px
- Card margin: 8px

### Tablet
- Container padding: 12px
- Card padding: 12px
- Gap between columns: 8px
- Card margin: 8px

### Mobile
- Container padding: 8px
- Card padding: 12px
- Gap: 4px
- Card margin: 4px

---

## Typography Scale

### Desktop
- Title: 24px (xl)
- Heading: 18px (lg)
- Body: 16px (base)
- Small: 14px (sm)
- Tiny: 12px (xs)

### Tablet
- Title: 20px
- Heading: 16px
- Body: 16px
- Small: 14px
- Tiny: 12px

### Mobile
- Title: 18px
- Heading: 16px
- Body: 14px
- Small: 12px
- Tiny: 11px

---

## Color Usage

### Status Colors
- **Not Started**: Gray (#7F8C8D)
- **In Progress**: Blue (#3498DB)
- **Completed**: Green (#27AE60)
- **Blocked**: Red (#E74C3C)

### Phase Colors
- **Development**: Blue (#3498db)
- **Analysis**: Purple (#9b59b6)
- **Design**: Orange (#e67e22)
- **Testing**: Teal (#1abc9c)

### UI Colors
- **Primary**: Theme-specific
- **Background**: Theme-specific
- **Surface**: Theme-specific
- **Border**: Theme-specific
- **Text**: Theme-specific

---

## Animation Timing

### Transitions
- **Fast**: 0.15s (hover, active)
- **Normal**: 0.2s (default)
- **Slow**: 0.3s (modals, sheets)

### Animations
- **Skeleton**: 1.5s infinite
- **Slide**: 0.3s ease-out
- **Fade**: 0.2s ease-in-out

### Reduced Motion
- All animations: 0.01ms
- Instant transitions
- No skeleton animation

---

## Accessibility

### Touch Targets
- Minimum: 48x48px
- Recommended: 56x56px
- Spacing: 8px minimum

### Color Contrast
- Text: 4.5:1 minimum
- Large text: 3:1 minimum
- UI components: 3:1 minimum

### Focus Indicators
- Visible outline
- High contrast
- 2px minimum width

---

## Performance Targets

### Loading
- First Paint: < 1s
- Interactive: < 2s
- Full Load: < 3s

### Interactions
- Tap response: < 100ms
- Animation: 60fps
- Scroll: Smooth

### Bundle Size
- CSS: < 50KB
- JS: < 100KB (per component)
- Images: Optimized

---

**Last Updated:** 2025-01-13
**Version:** 1.0.0
