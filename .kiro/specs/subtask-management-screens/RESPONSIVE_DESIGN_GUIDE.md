# Responsive Design Visual Guide

## Layout Transformations

### 1. Hierarchy Filter Bar

#### Mobile (< 640px)
```
┌─────────────────────────────────┐
│ Client: [Select...        ▼]    │
│ Program: [Select...       ▼]    │
│ Project: [Select...       ▼]    │
│ Use Case: [Select...      ▼]    │
│ User Story: [Select...    ▼]    │
│ Task: [Select...          ▼]    │
└─────────────────────────────────┘
```
- Vertical stacking
- Full width selects
- No arrow separators
- Smaller text (12px)

#### Desktop (≥ 640px)
```
┌──────────────────────────────────────────────────────────────────┐
│ Client: [Select ▼] → Program: [Select ▼] → Project: [Select ▼] │
│ → Use Case: [Select ▼] → User Story: [Select ▼] → Task: [▼]    │
└──────────────────────────────────────────────────────────────────┘
```
- Horizontal layout with wrapping
- Arrow separators visible
- Compact spacing
- Larger text (14px)

### 2. Search and Filter Bar

#### Mobile (< 640px)
```
┌─────────────────────────────────┐
│ [Search subtasks...          ] │
│ [All Status              ▼]    │
│ [+ New Subtask              ]  │
└─────────────────────────────────┘
```
- Vertical stacking
- Full width elements
- Touch-friendly spacing

#### Desktop (≥ 640px)
```
┌──────────────────────────────────────────────────────────┐
│ [Search subtasks...        ] [All Status ▼] [+ New...]  │
└──────────────────────────────────────────────────────────┘
```
- Horizontal layout
- Search takes flex-1
- Compact button text

### 3. Subtasks List

#### Mobile/Tablet (< 1024px) - Card Layout
```
┌─────────────────────────────────────────┐
│ ┌─────────────────────────────────────┐ │
│ │ Implement login form      [Done]    │ │
│ │ Create authentication UI            │ │
│ │                                     │ │
│ │ Assigned: John Doe  Phase: Dev     │ │
│ │ Est. Hours: 8.0     Duration: 2d   │ │
│ │ Points: 5.0                         │ │
│ └─────────────────────────────────────┘ │
│ ┌─────────────────────────────────────┐ │
│ │ Fix validation bug    [In Progress] │ │
│ │ Address form validation issues      │ │
│ │                                     │ │
│ │ Assigned: Jane Smith Phase: QA     │ │
│ │ Est. Hours: 4.0      Duration: 1d  │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```
- Card-based layout
- Status badge aligned right
- 2-column grid for metadata
- Truncated descriptions
- Easy to scan on small screens

#### Desktop (≥ 1024px) - Table Layout
```
┌────────────────────────────────────────────────────────────────────────────┐
│ Title                  │ Status      │ Assigned  │ Phase │ Est.H │ Dur │ Pts│
├────────────────────────┼─────────────┼───────────┼───────┼───────┼─────┼────┤
│ Implement login form   │ [Done]      │ John Doe  │ Dev   │ 8.0   │ 2   │ 5.0│
│ Create auth UI         │             │           │       │       │     │    │
├────────────────────────┼─────────────┼───────────┼───────┼───────┼─────┼────┤
│ Fix validation bug     │ [Progress]  │ Jane Smith│ QA    │ 4.0   │ 1   │ -  │
│ Address form issues    │             │           │       │       │     │    │
└────────────────────────────────────────────────────────────────────────────┘
```
- Full table with all columns
- Horizontal scroll if needed
- Abbreviated headers
- Hover effects on rows

### 4. Subtask Form Modal

#### Mobile (< 640px)
```
┌─────────────────────────────────┐
│ Create New Subtask          [×] │
├─────────────────────────────────┤
│ ┌─────────────────────────────┐ │
│ │ Creating subtask under:     │ │
│ │ Acme → Web → Portal → ...  │ │
│ └─────────────────────────────┘ │
│                                 │
│ Title *                         │
│ [Enter subtask title        ]  │
│                                 │
│ Task *                          │
│ [Select a task          ▼]     │
│                                 │
│ Description                     │
│ [                           ]  │
│ [                           ]  │
│                                 │
│ Status *                        │
│ [To Do                  ▼]     │
│                                 │
│ Phase                           │
│ [Select a phase         ▼]     │
│                                 │
│ Assigned To                     │
│ [Unassigned             ▼]     │
│                                 │
│ Estimated Hours *               │
│ [0.0                        ]  │
│                                 │
│ Duration Days *                 │
│ [1                          ]  │
│                                 │
│ Scrum Points                    │
│ [Optional                   ]  │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ [Create                   ] │ │
│ │ [Cancel                   ] │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```
- Single column layout
- Full width inputs
- Stacked buttons (Create on top)
- Larger touch targets
- More vertical spacing

#### Desktop (≥ 640px)
```
┌───────────────────────────────────────────────────────┐
│ Create New Subtask                                [×] │
├───────────────────────────────────────────────────────┤
│ ┌───────────────────────────────────────────────────┐ │
│ │ Creating subtask under:                           │ │
│ │ Acme Corp → Web Platform → Customer Portal → ...│ │
│ └───────────────────────────────────────────────────┘ │
│                                                       │
│ Title *                                               │
│ [Enter subtask title                              ]  │
│                                                       │
│ Task *                                                │
│ [Select a task                                ▼]     │
│                                                       │
│ Description                                           │
│ [                                                 ]  │
│ [                                                 ]  │
│                                                       │
│ Status *              │ Phase                         │
│ [To Do            ▼]  │ [Select a phase        ▼]    │
│                                                       │
│ Assigned To                                           │
│ [Unassigned                                   ▼]     │
│                                                       │
│ Estimated Hours *     │ Duration Days *               │
│ [0.0              ]   │ [1                      ]    │
│                                                       │
│ Scrum Points                                          │
│ [Optional                                         ]  │
│                                                       │
│                           [Cancel]  [Create]         │
└───────────────────────────────────────────────────────┘
```
- Two-column grids for related fields
- Side-by-side buttons
- Optimal use of horizontal space
- Comfortable spacing

## Responsive Breakpoints

### Mobile First Approach
```
Base (Mobile)     sm (Tablet)      lg (Desktop)
< 640px          640px - 1023px    ≥ 1024px
───────────────────────────────────────────────
Card layout      Card layout       Table layout
Vertical stack   Vertical stack    Horizontal
Small text       Medium text       Medium text
Full width       Full width        Constrained
```

## Touch Target Sizes

### Mobile Requirements
- Minimum touch target: 44x44px
- Button padding: 16px horizontal, 8px vertical
- Input height: 40px minimum
- Spacing between targets: 8px minimum

### Implementation
```css
/* Mobile buttons */
px-4 py-2        /* 16px horizontal, 8px vertical */

/* Desktop buttons */
sm:px-6 sm:py-2  /* 24px horizontal, 8px vertical */

/* Inputs */
px-3 py-2        /* 12px horizontal, 8px vertical */
```

## Typography Scale

```
Element          Mobile    Desktop
─────────────────────────────────
Page Title       24px      30px
Subtitle         14px      16px
Labels           12px      14px
Input Text       14px      16px
Body Text        14px      16px
Small Text       12px      14px
```

## Color Coding

### Status Badges
- **Done**: Green background (#10B981), dark green text
- **In Progress**: Blue background (#3B82F6), dark blue text
- **To Do / Other**: Gray background (#6B7280), dark gray text

### Interactive Elements
- **Primary Action**: Blue (#3B82F6)
- **Hover State**: Darker blue (#2563EB)
- **Disabled**: Gray (#D1D5DB)
- **Focus Ring**: Blue (#3B82F6)

## Accessibility Features

### Keyboard Navigation
- Tab order follows visual order
- Focus visible on all interactive elements
- Escape key closes modal
- Enter submits forms

### Screen Reader Support
- Semantic HTML (table, form, button)
- ARIA labels on icon buttons
- Error messages announced
- Loading states announced

### Visual Accessibility
- Color contrast ratio ≥ 4.5:1 (WCAG AA)
- Text resizable up to 200%
- No information conveyed by color alone
- Focus indicators visible

## Performance Optimizations

### CSS-Only Responsive Design
- No JavaScript for layout changes
- Uses Tailwind's responsive utilities
- Minimal CSS bundle size

### Conditional Rendering
```tsx
{/* Desktop table */}
<div className="hidden lg:block">
  <table>...</table>
</div>

{/* Mobile cards */}
<div className="lg:hidden">
  {items.map(item => <Card />)}
</div>
```

### Benefits
- Cleaner DOM
- Better performance
- Easier to maintain
- Clear separation of concerns

## Testing Checklist

### Visual Testing
- [ ] Layout correct at 375px (iPhone SE)
- [ ] Layout correct at 768px (iPad)
- [ ] Layout correct at 1920px (Desktop)
- [ ] No horizontal scroll on mobile
- [ ] Text readable at all sizes
- [ ] Buttons easily tappable
- [ ] Forms usable on mobile

### Functional Testing
- [ ] All features work on mobile
- [ ] Touch interactions smooth
- [ ] Scrolling works correctly
- [ ] Modal fits on screen
- [ ] Form submission works
- [ ] Navigation works

### Cross-Browser Testing
- [ ] Chrome mobile
- [ ] Safari iOS
- [ ] Chrome desktop
- [ ] Safari macOS
- [ ] Firefox
- [ ] Edge

## Best Practices Applied

1. **Mobile-First Design**: Start with mobile, enhance for larger screens
2. **Progressive Enhancement**: Core functionality works everywhere
3. **Touch-Friendly**: Adequate spacing and target sizes
4. **Performance**: Minimal JavaScript, CSS-only responsive
5. **Accessibility**: WCAG AA compliant
6. **Consistency**: Follows existing patterns in the app
7. **Maintainability**: Clear, semantic class names
